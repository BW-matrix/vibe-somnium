"""Export a sanitized, auditable Markdown record from a runtime trace."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any


FORBIDDEN_EXPORT_MARKERS = (
    "auth.json",
    "codex-cli-home",
    "a2a_api_key",
    "openai_api_key",
    "authorization: bearer",
)

REDACTED_OUTPUT_FIELDS = {
    "run_nonce": "[redacted-run-nonce]",
    "run_id": "[redacted-run-id]",
}

PROJECTION_POLICY_FIELDS = (
    "included_refs",
    "excluded_refs",
    "redaction_rule",
    "compression_policy",
    "forbidden_downstream_use",
)

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _json_block(value: Any) -> str:
    return "```json\n" + json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n```"


def _content_hash(value: Any) -> str:
    serialized = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _table_row(values: list[Any]) -> str:
    return "| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |"


def _token_record(run: dict[str, Any]) -> dict[str, Any]:
    usage = run.get("token_usage") or {}
    return {
        "input": usage.get("input_tokens", 0),
        "output": usage.get("output_tokens", 0),
        "total": usage.get("total_tokens", 0),
        "exact": not usage.get("is_estimated", True),
        "source": usage.get("source", "unknown"),
    }


def _private_run_replacements(trace: dict[str, Any]) -> dict[str, str]:
    replacements: dict[str, str] = {}
    for field, marker in REDACTED_OUTPUT_FIELDS.items():
        private_value = trace.get(field)
        if isinstance(private_value, str) and private_value:
            replacements[private_value] = marker
    return replacements


def _portable_basename(value: Any) -> str:
    normalized = str(value or "unknown-fixture").replace("\\", "/")
    return PurePosixPath(normalized).name or "unknown-fixture"


def _sanitize_public_value(
    value: Any,
    replacements: dict[str, str],
) -> Any:
    if isinstance(value, dict):
        return {
            key: (
                REDACTED_OUTPUT_FIELDS[key]
                if key in REDACTED_OUTPUT_FIELDS
                else _sanitize_public_value(item, replacements)
            )
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_sanitize_public_value(item, replacements) for item in value]
    if isinstance(value, str):
        for private_value, marker in replacements.items():
            value = value.replace(private_value, marker)
    return value


def _scene_packet_payload(packet: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in packet.items() if key != "sealing_record"}


def _validate_exportable_real_trace(trace: dict[str, Any]) -> None:
    runs = trace.get("agent_runs")
    if not isinstance(runs, list) or not runs:
        raise ValueError("trace must contain at least one agent_runs item")
    required_states = {
        "runtime_mode": "world_driven",
        "llm_mode": "codex-cli",
        "final_decision": "allowed",
        "runtime_status": "finished",
    }
    for field, expected in required_states.items():
        if trace.get(field) != expected:
            raise ValueError(f"public real sample requires {field}={expected}")
    if not isinstance(trace.get("model"), str) or not trace["model"].strip():
        raise ValueError("public real sample requires a non-empty model id")
    transaction = trace.get("transaction")
    if not isinstance(transaction, dict) or transaction.get("status") != "committed":
        raise ValueError("public real sample requires a committed transaction")
    _validate_projection_evidence(trace, runs)
    if any(
        item.get("severity") == "block"
        for item in _walk_dicts(trace.get("validation"))
    ):
        raise ValueError("public real sample cannot contain a blocking validation result")

    sums = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
    for index, run in enumerate(runs):
        if not isinstance(run, dict) or run.get("mode") != "codex-cli":
            raise ValueError(f"agent_runs[{index}] is not a Codex CLI call")
        if run.get("error") not in (None, "") or not isinstance(
            run.get("parsed_output"), dict
        ):
            raise ValueError(f"agent_runs[{index}] is not a successful parsed call")
        usage = run.get("token_usage")
        if (
            not isinstance(usage, dict)
            or usage.get("is_estimated") is not False
            or usage.get("source") != "provider_usage"
        ):
            raise ValueError(f"agent_runs[{index}] lacks exact provider token usage")
        counts: dict[str, int] = {}
        for field in sums:
            value = usage.get(field)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"agent_runs[{index}] has an invalid {field}")
            counts[field] = value
            sums[field] += value
        if counts["total_tokens"] != counts["input_tokens"] + counts["output_tokens"]:
            raise ValueError(f"agent_runs[{index}] token arithmetic is inconsistent")

    totals = (trace.get("token_usage") or {}).get("totals")
    if not isinstance(totals, dict):
        raise ValueError("public real sample requires aggregate token totals")
    for field, expected in sums.items():
        if totals.get(field) != expected:
            raise ValueError(f"aggregate {field} does not match per-call usage")
    if totals.get("exact_agent_count") != len(runs) or totals.get(
        "estimated_agent_count"
    ) != 0:
        raise ValueError("public real sample requires exact usage for every call")

    packet = trace.get("scene_packet")
    if not isinstance(packet, dict) or packet.get("commit_status") != "committed":
        raise ValueError("public real sample requires a committed ScenePacket")
    sealing_record = packet.get("sealing_record")
    if not isinstance(sealing_record, dict):
        raise ValueError("public real sample requires a ScenePacket sealing_record")
    source_hashes = sealing_record.get("source_collection_sha256")
    if not isinstance(source_hashes, dict):
        raise ValueError("private ScenePacket lacks source collection hashes")
    for name in [
        "resolved_events",
        "state_deltas",
        "visibility_deltas",
        "publication_candidates",
        "canon_reveal_candidates",
    ]:
        if source_hashes.get(name) != _content_hash(packet.get(name, [])):
            raise ValueError(f"private ScenePacket collection hash is invalid: {name}")
    expected_private_hash = _content_hash(_scene_packet_payload(packet))
    if sealing_record.get("sealed_payload_sha256") != expected_private_hash:
        raise ValueError("private ScenePacket seal is invalid before sanitization")


def _validate_projection_evidence(
    trace: dict[str, Any], runs: list[dict[str, Any]]
) -> None:
    manifests = trace.get("projection_manifests")
    contracts = trace.get("projection_contracts")
    if not isinstance(manifests, list) or len(manifests) != len(runs):
        raise ValueError("public real sample requires one projection manifest per call")
    if not isinstance(contracts, list) or len(contracts) != len(runs):
        raise ValueError("public real sample requires one projection contract per call")

    manifest_by_id = _unique_records_by_id(manifests, "manifest_id", "manifest")
    contract_by_id = _unique_records_by_id(contracts, "contract_id", "contract")
    referenced_manifests: set[str] = set()
    referenced_contracts: set[str] = set()

    for index, run in enumerate(runs):
        if run.get("call_index") != index:
            raise ValueError(f"agent_runs[{index}] has a non-canonical call_index")
        manifest_id = run.get("projection_manifest_id")
        contract_id = run.get("projection_contract_id")
        if manifest_id not in manifest_by_id or contract_id not in contract_by_id:
            raise ValueError(f"agent_runs[{index}] lacks bound projection evidence")
        if manifest_id in referenced_manifests or contract_id in referenced_contracts:
            raise ValueError(f"agent_runs[{index}] reuses projection evidence")
        referenced_manifests.add(manifest_id)
        referenced_contracts.add(contract_id)

        manifest = manifest_by_id[manifest_id]
        contract = contract_by_id[contract_id]
        context = run.get("projected_context")
        if not isinstance(context, dict):
            raise ValueError(f"agent_runs[{index}] lacks its projected context")
        context_sha256 = _content_hash(context)
        recipient = {
            "role": run.get("agent_name"),
            "instance_id": run.get("agent_instance_id"),
        }
        projection_type = context.get("context_type")
        policy_id = f"{projection_type}.v0.1"
        if not isinstance(projection_type, str) or not projection_type:
            raise ValueError(f"agent_runs[{index}] context lacks a projection type")
        if manifest.get("recipient") != recipient or contract.get("recipient") != recipient:
            raise ValueError(f"agent_runs[{index}] projection recipient is inconsistent")
        if (
            manifest.get("projection_type") != projection_type
            or contract.get("projection_type") != projection_type
            or manifest.get("policy_id") != policy_id
            or contract.get("policy_id") != policy_id
        ):
            raise ValueError(f"agent_runs[{index}] projection policy is inconsistent")
        if (
            manifest.get("context_sha256") != context_sha256
            or contract.get("context_sha256") != context_sha256
        ):
            raise ValueError(f"agent_runs[{index}] projected context hash is inconsistent")
        if manifest.get("projection_contract_id") != contract_id:
            raise ValueError(f"agent_runs[{index}] manifest is bound to another contract")
        if manifest.get("projection_contract_sha256") != _content_hash(contract):
            raise ValueError(f"agent_runs[{index}] projection contract seal is invalid")

        contract_core = {key: value for key, value in contract.items() if key != "contract_id"}
        if contract_id != f"pc_{_content_hash(contract_core)[:16]}":
            raise ValueError(f"agent_runs[{index}] projection contract id is invalid")
        expected_manifest_id = f"pm_{_content_hash({'context_sha256': context_sha256, 'contract': contract})[:16]}"
        if manifest_id != expected_manifest_id:
            raise ValueError(f"agent_runs[{index}] projection manifest id is invalid")

        for field in PROJECTION_POLICY_FIELDS:
            if manifest.get(field) != contract.get(field):
                raise ValueError(
                    f"agent_runs[{index}] projection policy differs from its contract: {field}"
                )
        if contract.get("forbidden_downstream_use") != contract.get("excluded_refs"):
            raise ValueError(
                f"agent_runs[{index}] projection exclusions are not fail-closed"
            )
        for field in ["authority_basis", "visibility_basis"]:
            if not isinstance(manifest.get(field), str) or not manifest[field].strip():
                raise ValueError(
                    f"agent_runs[{index}] projection manifest lacks {field}"
                )

        anchors = contract.get("field_anchors")
        field_projections = manifest.get("field_projections")
        if not isinstance(anchors, dict) or not isinstance(field_projections, list):
            raise ValueError(f"agent_runs[{index}] lacks field projection evidence")
        records: dict[str, dict[str, Any]] = {}
        for record in field_projections:
            field = record.get("projected_field") if isinstance(record, dict) else None
            if not isinstance(field, str) or field in records:
                raise ValueError(f"agent_runs[{index}] has duplicate or invalid field evidence")
            records[field] = record
        if set(records) != set(context) or set(anchors) != set(context):
            raise ValueError(f"agent_runs[{index}] field projection coverage is incomplete")
        for field, value in context.items():
            record = records[field]
            anchor = anchors[field]
            if not isinstance(anchor, dict):
                raise ValueError(f"agent_runs[{index}] has an invalid field anchor")
            if record.get("value_sha256") != _content_hash(value):
                raise ValueError(f"agent_runs[{index}] field value hash is inconsistent")
            if record.get("mapping_mode") == "unanchored" or anchor.get(
                "mapping_mode"
            ) == "unanchored":
                raise ValueError(f"agent_runs[{index}] contains unanchored projection data")
            for key in [
                "source_path",
                "source_value_sha256",
                "projection_operation",
                "mapping_mode",
            ]:
                if record.get(key) != anchor.get(key):
                    raise ValueError(
                        f"agent_runs[{index}] field anchor differs from its manifest"
                    )
        _validate_leaf_projection_evidence(index, context, manifest, anchors)

    if referenced_manifests != set(manifest_by_id) or referenced_contracts != set(
        contract_by_id
    ):
        raise ValueError("projection evidence contains an unreferenced record")


def _validate_leaf_projection_evidence(
    call_index: int,
    context: dict[str, Any],
    manifest: dict[str, Any],
    anchors: dict[str, Any],
) -> None:
    expected: dict[str, tuple[str, Any]] = {}
    for field in sorted(context):
        for relative_path, _, value in _leaf_values(context[field]):
            expected[f"$.{field}{relative_path}"] = (field, value)

    leaf_projections = manifest.get("leaf_projections")
    if not isinstance(leaf_projections, list):
        raise ValueError(f"agent_runs[{call_index}] lacks leaf projection evidence")

    records: dict[str, dict[str, Any]] = {}
    for record in leaf_projections:
        path = record.get("projected_path") if isinstance(record, dict) else None
        if not isinstance(path, str) or not path or path in records:
            raise ValueError(
                f"agent_runs[{call_index}] has duplicate or invalid leaf evidence"
            )
        records[path] = record

    if set(records) != set(expected):
        raise ValueError(
            f"agent_runs[{call_index}] leaf projection coverage is incomplete"
        )

    for path, (field, value) in expected.items():
        record = records[path]
        anchor = anchors.get(field)
        if not isinstance(anchor, dict):
            raise ValueError(
                f"agent_runs[{call_index}] leaf evidence lacks a field anchor"
            )
        if record.get("value_sha256") != _content_hash(value):
            raise ValueError(
                f"agent_runs[{call_index}] leaf value hash is inconsistent"
            )

        source_tokens = record.get("source_tokens")
        if not isinstance(source_tokens, list) or not all(
            (
                isinstance(token, str)
                and bool(token)
                or isinstance(token, int)
                and not isinstance(token, bool)
                and token >= 0
            )
            for token in source_tokens
        ):
            raise ValueError(
                f"agent_runs[{call_index}] leaf source tokens are invalid"
            )
        expected_source_path = (
            f"{anchor.get('source_path')}{_relative_path_from_tokens(source_tokens)}"
        )
        if record.get("source_path") != expected_source_path:
            raise ValueError(
                f"agent_runs[{call_index}] leaf source path is not contract-bound"
            )

        source_hash = record.get("source_value_sha256")
        if not isinstance(source_hash, str) or not SHA256_PATTERN.fullmatch(source_hash):
            raise ValueError(
                f"agent_runs[{call_index}] leaf source hash is invalid"
            )
        if not source_tokens and source_hash != anchor.get("source_value_sha256"):
            raise ValueError(
                f"agent_runs[{call_index}] root leaf source hash is not contract-bound"
            )

        base_operation = anchor.get("projection_operation")
        allowed_operations = {
            base_operation,
            f"{base_operation}; derived_or_restructured_leaf",
        }
        if not isinstance(base_operation, str) or record.get(
            "projection_operation"
        ) not in allowed_operations:
            raise ValueError(
                f"agent_runs[{call_index}] leaf projection operation is not contract-bound"
            )


def _leaf_values(value: Any) -> list[tuple[str, list[str | int], Any]]:
    leaves: list[tuple[str, list[str | int], Any]] = []

    def walk(current: Any, suffix: str, tokens: list[str | int]) -> None:
        if isinstance(current, dict) and current:
            for key in sorted(current):
                walk(current[key], f"{suffix}.{key}", [*tokens, key])
            return
        if isinstance(current, list) and current:
            for index, item in enumerate(current):
                walk(item, f"{suffix}[{index}]", [*tokens, index])
            return
        leaves.append((suffix, tokens, current))

    walk(value, "", [])
    return leaves


def _relative_path_from_tokens(tokens: list[str | int]) -> str:
    return "".join(
        f"[{token}]" if isinstance(token, int) else f".{token}"
        for token in tokens
    )


def _unique_records_by_id(
    records: list[Any], id_field: str, label: str
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        record_id = record.get(id_field) if isinstance(record, dict) else None
        if not isinstance(record_id, str) or not record_id or record_id in indexed:
            raise ValueError(f"projection {label} ids must be non-empty and unique")
        indexed[record_id] = record
    return indexed


def _walk_dicts(value: Any):
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _walk_dicts(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk_dicts(item)


def _sanitize_and_reseal_scene_packet(
    packet: dict[str, Any], replacements: dict[str, str]
) -> dict[str, Any]:
    sanitized = _sanitize_public_value(packet, replacements)
    sealing_record = sanitized["sealing_record"]
    collection_names = [
        "resolved_events",
        "state_deltas",
        "visibility_deltas",
        "publication_candidates",
        "canon_reveal_candidates",
    ]
    sealing_record["source_collection_sha256"] = {
        name: _content_hash(sanitized.get(name, [])) for name in collection_names
    }
    sealing_record["sealed_payload_sha256"] = _content_hash(
        _scene_packet_payload(sanitized)
    )
    sealing_record["seal_scope"] = "sanitized_public_export"
    sealing_record["source_private_seal_verified"] = True
    return sanitized


def render_public_trace(trace: dict[str, Any]) -> str:
    _validate_exportable_real_trace(trace)
    runs = trace["agent_runs"]

    totals = (trace.get("token_usage") or {}).get("totals") or {}
    aggregate: dict[str, dict[str, int]] = defaultdict(
        lambda: {"calls": 0, "input": 0, "output": 0, "total": 0}
    )
    for run in runs:
        agent_name = str(run.get("agent_name", "unknown"))
        usage = _token_record(run)
        aggregate[agent_name]["calls"] += 1
        aggregate[agent_name]["input"] += int(usage["input"])
        aggregate[agent_name]["output"] += int(usage["output"])
        aggregate[agent_name]["total"] += int(usage["total"])

    replacements = _private_run_replacements(trace)
    fixture_name = _portable_basename(trace.get("fixture_path"))
    transaction = _sanitize_public_value(trace.get("transaction") or {}, replacements)
    scene_packet = _sanitize_and_reseal_scene_packet(trace["scene_packet"], replacements)
    lines = [
        "# World-Driven Real Codex Sample v0.2",
        "",
        "> This is a sanitized public export of one real isolated Codex CLI run. It preserves every model-agent's parsed output and token accounting while deliberately excluding prompts, projected context payloads, raw provider JSONL, local paths, private run identifiers, and authentication state.",
        "",
        "## Run Summary",
        "",
        _table_row(["Field", "Value"]),
        _table_row(["---", "---"]),
        _table_row(["Fixture", f"`{fixture_name}`"]),
        _table_row(["Runtime", f"`{trace.get('runtime_mode', 'unknown')}`"]),
        _table_row(["Provider mode", f"`{trace.get('llm_mode', 'unknown')}`"]),
        _table_row(["Model", f"`{trace.get('model', 'unknown')}`"]),
        _table_row(["Runtime status", f"`{trace.get('runtime_status', 'unknown')}`"]),
        _table_row(["Final decision", f"`{trace.get('final_decision', 'unknown')}`"]),
        _table_row(["Transaction", f"`{transaction.get('status', 'unknown')}`"]),
        _table_row(["Model calls", len(runs)]),
        _table_row(["Projection manifests", len(trace.get("projection_manifests") or [])]),
        _table_row(["Input tokens", totals.get("input_tokens", 0)]),
        _table_row(["Output tokens", totals.get("output_tokens", 0)]),
        _table_row(["Total tokens", totals.get("total_tokens", 0)]),
        _table_row(["Exact token records", totals.get("exact_agent_count", 0)]),
        _table_row(["Estimated token records", totals.get("estimated_agent_count", 0)]),
        "",
        "The provider reported exact usage for every call. Output counts include provider-reported reasoning tokens where the backend reports them that way; the runtime therefore validates the returned provider count rather than assuming visible JSON length equals billed output.",
        "",
        "## Per-Agent Token Totals",
        "",
        _table_row(["Agent", "Calls", "Input", "Output", "Total"]),
        _table_row(["---", "---:", "---:", "---:", "---:"]),
    ]
    for agent_name in sorted(aggregate):
        item = aggregate[agent_name]
        lines.append(
            _table_row(
                [
                    f"`{agent_name}`",
                    item["calls"],
                    item["input"],
                    item["output"],
                    item["total"],
                ]
            )
        )

    lines.extend(
        [
            "",
            "All outputs from every invoked model-agent are included. `Canon Steward` was not invoked because this fixture produced no executable canon-promotion step; v0.2 records canon candidates but does not yet run in-loop steward governance, so the export does not fabricate a placeholder response.",
            "",
            "## Call Sequence",
            "",
            "Each section below is the parsed output recorded for that model-agent call. The completed trace's downstream validators and Authority gates determine whether each output was accepted, repaired, or rejected; omitted prompts and projected contexts remain only in the private local trace.",
            "",
        ]
    )
    for index, run in enumerate(runs, start=1):
        usage = _token_record(run)
        parsed_output = _sanitize_public_value(run.get("parsed_output"), replacements)
        lines.extend(
            [
                f"### {index}. {run.get('agent_name', 'unknown')} / {run.get('protocol_stage', 'unknown')}",
                "",
                _table_row(["Field", "Value"]),
                _table_row(["---", "---"]),
                _table_row(
                    [
                        "Agent instance",
                        f"`{_sanitize_public_value(run.get('agent_instance_id', 'unknown'), replacements)}`",
                    ]
                ),
                _table_row(["Call index", run.get("call_index", index - 1)]),
                _table_row(["Input tokens", usage["input"]]),
                _table_row(["Output tokens", usage["output"]]),
                _table_row(["Total tokens", usage["total"]]),
                _table_row(["Count", "exact" if usage["exact"] else "estimated"]),
                _table_row(["Usage source", f"`{usage['source']}`"]),
                "",
                _json_block(parsed_output),
                "",
            ]
        )

    lines.extend(
        [
            "## Committed Result",
            "",
            "### Transaction",
            "",
            _json_block(transaction),
            "",
            "### Published Narration",
            "",
            _json_block(
                _sanitize_public_value(
                    trace.get("published_narration_segments") or [], replacements
                )
            ),
            "",
            "### Scene Packet",
            "",
            _json_block(scene_packet),
            "",
            "### Memory Handoff",
            "",
            _json_block(_sanitize_public_value(trace.get("memory_handoff"), replacements)),
            "",
            "### Audited Normalizations",
            "",
            _json_block(
                _sanitize_public_value(trace.get("normalization_records") or [], replacements)
            ),
            "",
            "## Export Boundary",
            "",
            "This artifact is evidence of one bounded run, not a claim that every future model output will pass. The executable fixtures, validators, Authority Judge gates, and scene-atomic transaction remain the actual enforcement surface. Candidate expiry aging and persistent cross-scene ledgers are not implemented in v0.2.",
            "",
        ]
    )
    return "\n".join(lines)


def _assert_sanitized(document: str, trace: dict[str, Any]) -> None:
    lowered = document.lower()
    leaked = [marker for marker in FORBIDDEN_EXPORT_MARKERS if marker in lowered]
    if leaked:
        raise ValueError(f"refusing export because sensitive marker(s) remain: {', '.join(leaked)}")
    leaked_run_fields = [
        field
        for field in REDACTED_OUTPUT_FIELDS
        if isinstance(trace.get(field), str)
        and trace[field]
        and trace[field] in document
    ]
    if leaked_run_fields:
        raise ValueError(
            "refusing export because private run identifier(s) remain: "
            + ", ".join(leaked_run_fields)
        )
    sensitive_patterns = {
        "windows absolute path": r"(?i)(?<![A-Za-z0-9_])[a-z]:[\\/]",
        "file URI": r"(?i)file://",
        "private key": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "OpenAI-style secret": r"\bsk-[A-Za-z0-9_-]{20,}\b",
        "GitHub-style secret": r"\bgh[opsu]_[A-Za-z0-9]{20,}\b",
    }
    matched = [name for name, pattern in sensitive_patterns.items() if re.search(pattern, document)]
    if matched:
        raise ValueError(
            "refusing export because sensitive pattern(s) remain: " + ", ".join(matched)
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path, help="private trace.json input")
    parser.add_argument("output", type=Path, help="public Markdown output")
    args = parser.parse_args()

    with args.trace.open("r", encoding="utf-8") as handle:
        trace = json.load(handle)
    document = render_public_trace(trace)
    _assert_sanitized(document, trace)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(document, encoding="utf-8", newline="\n")
    print(f"Exported {len(trace['agent_runs'])} agent calls to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
