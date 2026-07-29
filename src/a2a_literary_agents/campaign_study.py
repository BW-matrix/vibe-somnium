"""Two-scene continuity materialization and research telemetry.

The runtime remains scene-atomic. This module is the explicit campaign
boundary: only a committed ScenePacket, owner-specific memory deltas, and the
audited pressure ledger may cross from one scene into the next.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from copy import deepcopy
from typing import Any

from .json_util import stable_json


MAX_STUDY_ROUNDS = 100


def content_hash(value: Any) -> str:
    """Return the repository's canonical SHA-256 content hash."""

    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def materialize_scene_one(
    base_fixture: dict[str, Any], *, max_rounds: int = MAX_STUDY_ROUNDS
) -> dict[str, Any]:
    """Create the first scene fixture under the study's hard tick cap."""

    _validate_round_cap(max_rounds)
    fixture = deepcopy(base_fixture)
    fixture["max_world_ticks"] = max_rounds
    return fixture


def build_followup_fixture(
    scene_one_fixture: dict[str, Any],
    scene_two_template: dict[str, Any],
    scene_one_trace: dict[str, Any],
    *,
    max_rounds: int = MAX_STUDY_ROUNDS,
) -> dict[str, Any]:
    """Materialize Scene 2 from the committed outputs of Scene 1.

    No uncommitted runtime state, candidate material, raw private cognition, or
    prose is promoted through this handoff.
    """

    _validate_round_cap(max_rounds)
    _require_committed_scene(scene_one_trace)
    _require_trace_matches_fixture(scene_one_fixture, scene_one_trace)

    source_scene_id = scene_one_fixture.get("scene_id")
    target_scene_id = scene_two_template.get("scene_id")
    if not isinstance(source_scene_id, str) or not source_scene_id:
        raise ValueError("Scene 1 fixture requires a scene_id.")
    if not isinstance(target_scene_id, str) or not target_scene_id:
        raise ValueError("Scene 2 template requires a scene_id.")
    if source_scene_id == target_scene_id:
        raise ValueError("A follow-up scene must use a new scene_id.")

    packet = scene_one_trace["scene_packet"]
    runtime_state = scene_one_trace["runtime_state"]
    memory_handoff = scene_one_trace["memory_handoff"]
    packet_sha256 = content_hash(packet)
    runtime_state_sha256 = content_hash(runtime_state)

    fixture = deepcopy(scene_two_template)
    fixture["max_world_ticks"] = max_rounds

    prior_events = [
        _world_event_handoff_view(event)
        for event in packet.get("resolved_events", [])
        if isinstance(event, dict)
    ]
    prior_state_deltas = deepcopy(packet.get("state_deltas", []))
    world_state = deepcopy(fixture.get("world_state_ledger", {}))
    world_state["campaign_handoff"] = {
        "source_trace_id": scene_one_trace.get("trace_id"),
        "source_scene_id": source_scene_id,
        "source_packet_id": packet.get("packet_id"),
        "source_packet_sha256": packet_sha256,
        "source_runtime_state_sha256": runtime_state_sha256,
        "committed_event_history": prior_events,
        "world_state_delta_history": prior_state_deltas,
        "handoff_policy": (
            "committed objective and observable scene reality only; "
            "authorized interiority, candidates, and prose excluded"
        ),
    }
    fixture["world_state_ledger"] = world_state

    memory_by_owner: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for delta in memory_handoff.get("derived_memory_deltas", []):
        if not isinstance(delta, dict):
            continue
        owner_id = delta.get("owner_agent_id")
        if isinstance(owner_id, str):
            memory_by_owner[owner_id].append(deepcopy(delta))

    source_characters = scene_one_fixture.get("characters", {})
    target_characters = fixture.get("characters", {})
    if not isinstance(source_characters, dict) or not isinstance(
        target_characters, dict
    ):
        raise ValueError("Both scene fixtures require character maps.")
    unknown_memory_owners = sorted(set(memory_by_owner) - set(target_characters))
    if unknown_memory_owners:
        raise ValueError(
            "Scene 1 memory handoff names unknown Scene 2 owners: "
            + ", ".join(unknown_memory_owners)
        )
    memory_owner_by_id: dict[str, str] = {}
    for owner_id, target_character in target_characters.items():
        if not isinstance(target_character, dict):
            continue
        inherited = []
        source_character = source_characters.get(owner_id, {})
        if isinstance(source_character, dict):
            inherited.extend(deepcopy(source_character.get("private_memory", [])))
        inherited.extend(memory_by_owner.get(owner_id, []))
        inherited.extend(deepcopy(target_character.get("private_memory", [])))
        target_character["private_memory"] = _merge_records_strict(
            inherited,
            "delta_id",
            record_kind=f"private memory for {owner_id}",
        )
        for memory in target_character["private_memory"]:
            memory_id = memory.get("delta_id")
            if not isinstance(memory_id, str):
                continue
            prior_owner = memory_owner_by_id.get(memory_id)
            if prior_owner is not None and prior_owner != owner_id:
                raise ValueError(
                    f"Private memory id {memory_id} is shared by "
                    f"{prior_owner} and {owner_id}."
                )
            memory_owner_by_id[memory_id] = owner_id

    inherited_pressure = deepcopy(runtime_state.get("pressure_ledger", []))
    fixture["pressure_history"] = _dedupe_records(
        [
            *inherited_pressure,
            *deepcopy(fixture.get("pressure_history", [])),
        ],
        "pulse_id",
    )

    world_condition_refs = list(fixture.get("world_condition_registry", []))
    world_condition_refs.extend(
        event.get("event_id")
        for event in prior_events
        if isinstance(event.get("event_id"), str)
    )
    world_condition_refs.extend(
        delta.get("delta_id")
        for delta in prior_state_deltas
        if isinstance(delta, dict) and isinstance(delta.get("delta_id"), str)
    )
    fixture["world_condition_registry"] = _dedupe_scalars(world_condition_refs)

    reserved_protocol_ids = collect_protocol_ids(scene_one_trace)
    fixture["reserved_protocol_ids"] = reserved_protocol_ids
    fixture["campaign_handoff"] = {
        "handoff_version": "two_scene_continuity_v0.1",
        "source_trace_id": scene_one_trace.get("trace_id"),
        "source_run_id": scene_one_trace.get("run_id"),
        "source_scene_id": source_scene_id,
        "source_packet_id": packet.get("packet_id"),
        "source_packet_sha256": packet_sha256,
        "source_runtime_state_sha256": runtime_state_sha256,
        "transferred_event_refs": [
            event.get("event_id") for event in prior_events
        ],
        "transferred_state_delta_refs": [
            delta.get("delta_id")
            for delta in prior_state_deltas
            if isinstance(delta, dict)
        ],
        "transferred_memory_delta_refs_by_owner": {
            owner_id: [
                delta.get("delta_id") for delta in memory_by_owner.get(owner_id, [])
            ]
            for owner_id in sorted(target_characters)
        },
        "transferred_pressure_refs": [
            _pressure_ref(record) for record in inherited_pressure
        ],
        "reserved_protocol_ids": reserved_protocol_ids,
    }
    return fixture


def collect_protocol_ids(trace: dict[str, Any]) -> list[str]:
    """Collect model-claimed and Kernel-generated scene identities."""

    runtime_state = trace.get("runtime_state", {})
    used_identities = runtime_state.get("used_protocol_ids", [])
    identities = (
        list(used_identities) if isinstance(used_identities, list) else []
    )
    packet_id = trace.get("scene_packet", {}).get("packet_id")
    if isinstance(packet_id, str):
        identities.append(packet_id)
    identities.extend(
        delta.get("delta_id")
        for delta in trace.get("memory_handoff", {}).get(
            "derived_memory_deltas", []
        )
        if isinstance(delta, dict) and isinstance(delta.get("delta_id"), str)
    )
    return _dedupe_scalars(
        identity for identity in identities if isinstance(identity, str)
    )


def evaluate_continuity_study(
    scene_one_fixture: dict[str, Any],
    scene_two_fixture: dict[str, Any],
    scene_one_trace: dict[str, Any],
    scene_two_trace: dict[str, Any],
    *,
    scene_elapsed_seconds: dict[str, float] | None = None,
    max_rounds: int = MAX_STUDY_ROUNDS,
) -> dict[str, Any]:
    """Evaluate execution, continuity, and information-isolation evidence."""

    _validate_round_cap(max_rounds)
    elapsed = scene_elapsed_seconds or {}
    packet_one_hash = content_hash(scene_one_trace.get("scene_packet"))
    packet_two_hash = content_hash(scene_two_trace.get("scene_packet"))
    handoff = scene_two_fixture.get("campaign_handoff", {})

    scene_one_ids = set(collect_protocol_ids(scene_one_trace))
    scene_two_ids = set(collect_protocol_ids(scene_two_trace))
    replayed_ids = sorted(scene_one_ids & scene_two_ids)

    checks: list[dict[str, Any]] = []

    def check(check_id: str, passed: bool, evidence: Any) -> None:
        checks.append(
            {
                "check_id": check_id,
                "status": "pass" if passed else "fail",
                "evidence": evidence,
            }
        )

    for label, trace in (
        ("scene_one", scene_one_trace),
        ("scene_two", scene_two_trace),
    ):
        committed = (
            trace.get("final_decision") == "allowed"
            and trace.get("runtime_status") == "finished"
            and trace.get("transaction", {}).get("status") == "committed"
            and trace.get("scene_packet", {}).get("commit_status") == "committed"
        )
        check(
            f"{label}_committed",
            committed,
            {
                "final_decision": trace.get("final_decision"),
                "runtime_status": trace.get("runtime_status"),
                "transaction": trace.get("transaction", {}).get("status"),
                "packet": trace.get("scene_packet", {}).get("commit_status"),
            },
        )
        check(
            f"{label}_within_world_tick_cap",
            len(trace.get("world_ticks", [])) <= max_rounds,
            {
                "observed": len(trace.get("world_ticks", [])),
                "cap": max_rounds,
            },
        )
        check(
            f"{label}_within_llm_call_cap",
            len(trace.get("agent_runs", [])) <= max_rounds,
            {
                "observed": len(trace.get("agent_runs", [])),
                "cap": max_rounds,
            },
        )

    check(
        "scene_packet_hash_bound_to_followup",
        handoff.get("source_packet_sha256") == packet_one_hash
        and scene_two_fixture.get("world_state_ledger", {})
        .get("campaign_handoff", {})
        .get("source_packet_sha256")
        == packet_one_hash,
        {
            "expected": packet_one_hash,
            "observed_top_level": handoff.get("source_packet_sha256"),
            "observed_world_handoff": scene_two_fixture.get(
                "world_state_ledger", {}
            )
            .get("campaign_handoff", {})
            .get("source_packet_sha256"),
        },
    )
    check(
        "cross_scene_protocol_id_non_replay",
        not replayed_ids
        and set(scene_two_fixture.get("reserved_protocol_ids", []))
        == scene_one_ids,
        {
            "replayed_ids": replayed_ids,
            "expected_reserved_ids": sorted(scene_one_ids),
            "observed_reserved_ids": sorted(
                scene_two_fixture.get("reserved_protocol_ids", [])
            ),
        },
    )

    world_contexts = [
        run.get("projected_context", {})
        for run in scene_two_trace.get("agent_runs", [])
        if run.get("agent_name") == "world"
    ]
    world_handoff_visible = any(
        context.get("world_state_ledger", {})
        .get("campaign_handoff", {})
        .get("source_packet_sha256")
        == packet_one_hash
        for context in world_contexts
    )
    check(
        "scene_two_world_received_committed_handoff",
        world_handoff_visible,
        {
            "world_context_count": len(world_contexts),
            "source_packet_sha256": packet_one_hash,
        },
    )

    expected_memory_by_owner = handoff.get(
        "transferred_memory_delta_refs_by_owner", {}
    )
    character_contexts_by_owner: dict[str, list[dict[str, Any]]] = defaultdict(
        list
    )
    for run in scene_two_trace.get("agent_runs", []):
        if run.get("agent_name") != "character":
            continue
        owner_id = run.get("agent_instance_id")
        context = run.get("projected_context")
        if isinstance(owner_id, str) and isinstance(context, dict):
            character_contexts_by_owner[owner_id].append(context)

    all_expected_memory_ids = {
        memory_id
        for values in expected_memory_by_owner.values()
        if isinstance(values, list)
        for memory_id in values
        if isinstance(memory_id, str)
    }
    for owner_id in sorted(scene_two_fixture.get("characters", {})):
        contexts = character_contexts_by_owner.get(owner_id, [])
        delivered_ids = {
            item.get("delta_id")
            for context in contexts
            for item in context.get("private_memory_query", [])
            if isinstance(item, dict) and isinstance(item.get("delta_id"), str)
        }
        owner_expected = set(expected_memory_by_owner.get(owner_id, []))
        other_expected = all_expected_memory_ids - owner_expected
        authorized_records = [
            item
            for item in scene_two_fixture.get("characters", {})
            .get(owner_id, {})
            .get("private_memory", [])
            if isinstance(item, dict)
        ]
        authorized_hashes = {content_hash(item) for item in authorized_records}
        delivered_items = [
            item
            for context in contexts
            for item in context.get("private_memory_query", [])
            if isinstance(item, dict)
        ]
        unauthorized_memory_refs = sorted(
            {
                str(item.get("delta_id") or content_hash(item))
                for item in delivered_items
                if content_hash(item) not in authorized_hashes
            }
        )
        expected_records = {
            item.get("delta_id"): item
            for item in scene_two_fixture.get("characters", {})
            .get(owner_id, {})
            .get("private_memory", [])
            if isinstance(item, dict) and item.get("delta_id") in owner_expected
        }
        delivered_records: dict[str, set[str]] = defaultdict(set)
        for context in contexts:
            for item in context.get("private_memory_query", []):
                if (
                    isinstance(item, dict)
                    and isinstance(item.get("delta_id"), str)
                    and item.get("delta_id") in owner_expected
                ):
                    delivered_records[item["delta_id"]].add(content_hash(item))
        content_mismatch_ids = sorted(
            memory_id
            for memory_id in owner_expected
            if memory_id not in expected_records
            or delivered_records.get(memory_id)
            != {content_hash(expected_records[memory_id])}
        )
        check(
            f"{owner_id}_received_owner_memory_only",
            bool(contexts)
            and owner_expected <= delivered_ids
            and not (delivered_ids & other_expected)
            and not content_mismatch_ids
            and not unauthorized_memory_refs,
            {
                "character_context_count": len(contexts),
                "expected_owner_memory_ids": sorted(owner_expected),
                "delivered_handoff_memory_ids": sorted(
                    delivered_ids & all_expected_memory_ids
                ),
                "foreign_handoff_memory_ids": sorted(delivered_ids & other_expected),
                "content_mismatch_ids": content_mismatch_ids,
                "unauthorized_memory_refs": unauthorized_memory_refs,
            },
        )

    inherited_pressure = scene_one_trace.get("runtime_state", {}).get(
        "pressure_ledger", []
    )
    check(
        "pressure_ledger_transferred_exactly",
        content_hash(scene_two_fixture.get("pressure_history", []))
        == content_hash(inherited_pressure),
        {
            "source_sha256": content_hash(inherited_pressure),
            "followup_sha256": content_hash(
                scene_two_fixture.get("pressure_history", [])
            ),
            "source_count": len(inherited_pressure),
            "followup_count": len(scene_two_fixture.get("pressure_history", [])),
        },
    )

    source_event_history = [
        _world_event_handoff_view(event)
        for event in scene_one_trace.get("scene_packet", {}).get(
            "resolved_events", []
        )
        if isinstance(event, dict)
    ]
    source_state_history = deepcopy(
        scene_one_trace.get("scene_packet", {}).get("state_deltas", [])
    )
    world_handoff = scene_two_fixture.get("world_state_ledger", {}).get(
        "campaign_handoff", {}
    )
    event_refs = {
        event.get("event_id")
        for event in source_event_history
    }
    transferred_event_refs = set(handoff.get("transferred_event_refs", []))
    check(
        "committed_event_history_transferred",
        event_refs == transferred_event_refs
        and content_hash(world_handoff.get("committed_event_history", []))
        == content_hash(source_event_history)
        and content_hash(world_handoff.get("world_state_delta_history", []))
        == content_hash(source_state_history),
        {
            "source_event_refs": sorted(event_refs),
            "transferred_event_refs": sorted(transferred_event_refs),
            "source_event_history_sha256": content_hash(source_event_history),
            "followup_event_history_sha256": content_hash(
                world_handoff.get("committed_event_history", [])
            ),
            "source_state_delta_history_sha256": content_hash(
                source_state_history
            ),
            "followup_state_delta_history_sha256": content_hash(
                world_handoff.get("world_state_delta_history", [])
            ),
        },
    )

    chain_payload = {
        "scene_one_packet_sha256": packet_one_hash,
        "scene_two_fixture_sha256": content_hash(scene_two_fixture),
        "scene_two_packet_sha256": packet_two_hash,
    }
    study = {
        "study_type": "two_scene_continuity",
        "study_version": "v0.3",
        "max_rounds_per_scene": max_rounds,
        "round_definition": {
            "world_tick_cap": max_rounds,
            "llm_call_cap": max_rounds,
        },
        "scene_one": _scene_metrics(
            scene_one_trace, elapsed.get("scene_one")
        ),
        "scene_two": _scene_metrics(
            scene_two_trace, elapsed.get("scene_two")
        ),
        "state_chain": {
            **chain_payload,
            "campaign_chain_sha256": content_hash(chain_payload),
        },
        "continuity_checks": checks,
        "continuity_verdict": (
            "pass"
            if checks and all(item["status"] == "pass" for item in checks)
            else "fail"
        ),
        "combined": _combined_metrics(
            scene_one_trace,
            scene_two_trace,
            elapsed,
        ),
        "artifact_paths": {
            "scene_one_trace": scene_one_trace.get("artifacts", {}).get(
                "trace_json"
            ),
            "scene_one_report": scene_one_trace.get("artifacts", {}).get(
                "report_md"
            ),
            "scene_two_trace": scene_two_trace.get("artifacts", {}).get(
                "trace_json"
            ),
            "scene_two_report": scene_two_trace.get("artifacts", {}).get(
                "report_md"
            ),
        },
    }
    return study


def render_study_report(study: dict[str, Any]) -> str:
    """Render a concise local Markdown index for the raw study artifacts."""

    lines = [
        "# Two-Scene Continuity Study",
        "",
        f"- Verdict: `{study.get('continuity_verdict')}`",
        f"- Per-scene World tick cap: `{study.get('max_rounds_per_scene')}`",
        f"- Per-scene LLM call cap: `{study.get('max_rounds_per_scene')}`",
        f"- Campaign chain SHA-256: `{study.get('state_chain', {}).get('campaign_chain_sha256')}`",
        "",
        "## Scene Metrics",
        "",
        "| Scene | Decision | Transaction | World ticks | LLM calls | Input tokens | Output tokens | Total tokens | Elapsed seconds |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key in ("scene_one", "scene_two"):
        scene = study.get(key, {})
        tokens = scene.get("token_usage", {})
        lines.append(
            "| {scene} | `{decision}` | `{transaction}` | {ticks} | {calls} | "
            "{input_tokens} | {output_tokens} | {total_tokens} | {elapsed} |".format(
                scene=key,
                decision=scene.get("final_decision"),
                transaction=scene.get("transaction_status"),
                ticks=scene.get("world_ticks"),
                calls=scene.get("llm_calls"),
                input_tokens=tokens.get("input_tokens"),
                output_tokens=tokens.get("output_tokens"),
                total_tokens=tokens.get("total_tokens"),
                elapsed=scene.get("elapsed_seconds"),
            )
        )

    lines.extend(["", "## Continuity Checks", ""])
    for item in study.get("continuity_checks", []):
        lines.append(
            f"- `{item.get('status')}` `{item.get('check_id')}`: "
            f"`{content_hash(item.get('evidence'))}`"
        )

    lines.extend(["", "## Agent Calls", ""])
    for key in ("scene_one", "scene_two"):
        lines.append(f"### {key}")
        lines.append("")
        lines.append(
            "| Call | Agent | Instance | Stage | Input | Output | Total | Seconds |"
        )
        lines.append("| ---: | --- | --- | --- | ---: | ---: | ---: | ---: |")
        for call in study.get(key, {}).get("agent_calls", []):
            lines.append(
                "| {call_index} | {agent_name} | {agent_instance_id} | "
                "{protocol_stage} | {input_tokens} | {output_tokens} | "
                "{total_tokens} | {elapsed_seconds} |".format(**call)
            )
        lines.append("")

    lines.extend(["## Full Trace Reports", ""])
    for label, path_key in (
        ("Scene 1", "scene_one_report"),
        ("Scene 2", "scene_two_report"),
    ):
        lines.append(f"- {label}: `{study.get('artifact_paths', {}).get(path_key)}`")
    lines.append("")
    return "\n".join(lines)


def _require_committed_scene(trace: dict[str, Any]) -> None:
    if trace.get("final_decision") != "allowed":
        raise ValueError("Scene 1 was not allowed; no campaign handoff may be built.")
    if trace.get("runtime_status") != "finished":
        raise ValueError("Scene 1 did not finish; no campaign handoff may be built.")
    if trace.get("transaction", {}).get("status") != "committed":
        raise ValueError("Scene 1 transaction was not committed.")
    if trace.get("scene_packet", {}).get("commit_status") != "committed":
        raise ValueError("Scene 1 ScenePacket was not committed.")


def _require_trace_matches_fixture(
    fixture: dict[str, Any], trace: dict[str, Any]
) -> None:
    fixture_trace_id = fixture.get("trace_id")
    if (
        not isinstance(fixture_trace_id, str)
        or trace.get("trace_id") != fixture_trace_id
    ):
        raise ValueError("Scene 1 trace does not match the supplied fixture trace_id.")
    fixture_scene_id = fixture.get("scene_id")
    packet = trace.get("scene_packet")
    if (
        not isinstance(fixture_scene_id, str)
        or not isinstance(packet, dict)
        or packet.get("scene_id") != fixture_scene_id
    ):
        raise ValueError("Scene 1 trace does not match the supplied fixture scene_id.")
    fixture_sha256 = content_hash(fixture)
    if trace.get("fixture_sha256") != fixture_sha256:
        raise ValueError(
            "Scene 1 trace does not match the supplied fixture content hash."
        )


def _validate_round_cap(max_rounds: int) -> None:
    if (
        not isinstance(max_rounds, int)
        or isinstance(max_rounds, bool)
        or not 1 <= max_rounds <= MAX_STUDY_ROUNDS
    ):
        raise ValueError(
            f"max_rounds must be an integer between 1 and {MAX_STUDY_ROUNDS}."
        )


def _world_event_handoff_view(event: dict[str, Any]) -> dict[str, Any]:
    allowed_fields = (
        "message_type",
        "scene_id",
        "event_id",
        "source_input_type",
        "source_input_ref",
        "event_kind",
        "actors",
        "outcome",
        "public_surface",
        "visibility",
        "spoken_line_records",
        "causal_basis",
        "commit_status",
    )
    return {
        field: deepcopy(event[field])
        for field in allowed_fields
        if field in event
    }


def _dedupe_records(
    records: list[Any], identity_field: str
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            continue
        identity = record.get(identity_field)
        if isinstance(identity, str):
            if identity in seen:
                continue
            seen.add(identity)
        output.append(deepcopy(record))
    return output


def _merge_records_strict(
    records: list[Any],
    identity_field: str,
    *,
    record_kind: str,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    seen: dict[str, str] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        identity = record.get(identity_field)
        if not isinstance(identity, str):
            output.append(deepcopy(record))
            continue
        record_sha256 = content_hash(record)
        prior_sha256 = seen.get(identity)
        if prior_sha256 is not None:
            if prior_sha256 != record_sha256:
                raise ValueError(
                    f"Conflicting {record_kind} records reuse {identity_field} "
                    f"{identity}."
                )
            continue
        seen[identity] = record_sha256
        output.append(deepcopy(record))
    return output


def _dedupe_scalars(values: Any) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str) or not value or value in seen:
            continue
        seen.add(value)
        output.append(value)
    return output


def _pressure_ref(record: Any) -> str | None:
    if not isinstance(record, dict):
        return None
    pulse_id = record.get("pulse_id")
    if isinstance(pulse_id, str):
        return pulse_id
    original = record.get("original_plot_pulse")
    if isinstance(original, dict) and isinstance(original.get("pulse_id"), str):
        return original["pulse_id"]
    return None


def _scene_metrics(
    trace: dict[str, Any], measured_elapsed_seconds: float | None
) -> dict[str, Any]:
    totals = trace.get("token_usage", {}).get("totals", {})
    agent_calls = []
    for index, run in enumerate(trace.get("agent_runs", [])):
        usage = run.get("token_usage")
        if not isinstance(usage, dict):
            usage = {}
        agent_calls.append(
            {
                "call_index": run.get("call_index", index),
                "agent_name": run.get("agent_name"),
                "agent_instance_id": run.get("agent_instance_id"),
                "protocol_stage": run.get("protocol_stage"),
                "input_tokens": usage.get("input_tokens", 0),
                "output_tokens": usage.get("output_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "token_source": usage.get("source"),
                "token_count_is_estimated": usage.get("is_estimated"),
                "elapsed_seconds": run.get("elapsed_seconds"),
            }
        )
    elapsed_seconds = _effective_elapsed_seconds(
        trace,
        measured_elapsed_seconds,
    )
    return {
        "trace_id": trace.get("trace_id"),
        "run_id": trace.get("run_id"),
        "final_decision": trace.get("final_decision"),
        "runtime_status": trace.get("runtime_status"),
        "transaction_status": trace.get("transaction", {}).get("status"),
        "scene_packet_status": trace.get("scene_packet", {}).get(
            "commit_status"
        ),
        "world_ticks": len(trace.get("world_ticks", [])),
        "llm_calls": len(trace.get("agent_runs", [])),
        "repair_attempts": len(trace.get("repair_attempts", [])),
        "authority_reviews": len(trace.get("authority_reviews", [])),
        "committed_events": len(
            trace.get("runtime_state", {}).get("committed_world_events", [])
        ),
        "memory_deltas": len(
            trace.get("memory_handoff", {}).get("derived_memory_deltas", [])
        ),
        "token_usage": {
            "input_tokens": totals.get("input_tokens", 0),
            "output_tokens": totals.get("output_tokens", 0),
            "total_tokens": totals.get("total_tokens", 0),
            "exact_agent_count": totals.get("exact_agent_count", 0),
            "estimated_agent_count": totals.get("estimated_agent_count", 0),
            "sources": totals.get("sources", []),
        },
        "elapsed_seconds": elapsed_seconds,
        "agent_calls": agent_calls,
        "narration": [
            segment.get("prose")
            for segment in trace.get("published_narration_segments", [])
            if isinstance(segment, dict) and isinstance(segment.get("prose"), str)
        ],
    }


def _combined_metrics(
    scene_one_trace: dict[str, Any],
    scene_two_trace: dict[str, Any],
    elapsed: dict[str, float],
) -> dict[str, Any]:
    traces = (scene_one_trace, scene_two_trace)
    totals = [
        trace.get("token_usage", {}).get("totals", {}) for trace in traces
    ]
    by_agent: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "calls": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
            "elapsed_seconds": 0.0,
        }
    )
    for trace in traces:
        for run in trace.get("agent_runs", []):
            usage = run.get("token_usage")
            if not isinstance(usage, dict):
                usage = {}
            agent_name = str(run.get("agent_name", "unknown"))
            bucket = by_agent[agent_name]
            bucket["calls"] += 1
            bucket["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
            bucket["output_tokens"] += int(usage.get("output_tokens", 0) or 0)
            bucket["total_tokens"] += int(usage.get("total_tokens", 0) or 0)
            bucket["elapsed_seconds"] += float(
                run.get("elapsed_seconds", 0.0) or 0.0
            )
    for bucket in by_agent.values():
        bucket["elapsed_seconds"] = round(bucket["elapsed_seconds"], 6)
    scene_elapsed_seconds = [
        _effective_elapsed_seconds(scene_one_trace, elapsed.get("scene_one")),
        _effective_elapsed_seconds(scene_two_trace, elapsed.get("scene_two")),
    ]
    return {
        "llm_calls": sum(len(trace.get("agent_runs", [])) for trace in traces),
        "world_ticks": sum(len(trace.get("world_ticks", [])) for trace in traces),
        "input_tokens": sum(int(total.get("input_tokens", 0) or 0) for total in totals),
        "output_tokens": sum(
            int(total.get("output_tokens", 0) or 0) for total in totals
        ),
        "total_tokens": sum(int(total.get("total_tokens", 0) or 0) for total in totals),
        "elapsed_seconds": round(sum(scene_elapsed_seconds), 6),
        "by_agent": dict(sorted(by_agent.items())),
    }


def _effective_elapsed_seconds(
    trace: dict[str, Any],
    override: float | None,
) -> float:
    if (
        isinstance(override, (int, float))
        and not isinstance(override, bool)
        and override >= 0
    ):
        return round(float(override), 6)
    trace_elapsed = trace.get("elapsed_seconds")
    if (
        isinstance(trace_elapsed, (int, float))
        and not isinstance(trace_elapsed, bool)
        and trace_elapsed >= 0
    ):
        return round(float(trace_elapsed), 6)
    return round(
        sum(
            float(run.get("elapsed_seconds", 0.0) or 0.0)
            for run in trace.get("agent_runs", [])
            if isinstance(run, dict)
        ),
        6,
    )
