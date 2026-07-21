"""Deterministic guardrails for World-driven protocol interfaces.

These validators enforce shape, identity, ownership, and routing invariants.
Semantic literary judgment remains the Authority Judge Agent's responsibility.
"""

from __future__ import annotations

import hashlib
import json
import re
from difflib import SequenceMatcher
from functools import wraps
from typing import Any

from .path_safety import is_safe_path_id

from .json_util import stable_json
from .visibility import legal_character_trigger_refs


AUTHORITY_VERDICTS = {"allow", "warning", "repair_required", "block"}
WORLD_DIRECTIVES = {"request_character_decision", "continue_world", "finish_scene"}
PLOT_PULSE_DISPOSITIONS = {"accepted", "downgraded", "deferred", "rejected"}
WORLD_OUTCOME_TYPES = {"success", "failure", "partial_success", "blocked", "delayed", "contested"}
SPOKEN_LINE_STATUSES = {"paraphrased", "exact_committed"}
WORLD_EVENT_VISIBILITY_SCOPES = {
    "private_self",
    "private_target",
    "scene_pair",
    "restricted_subset",
    "scene_public",
    "local_public",
    "institution_public",
    "city_public",
    "realm_public",
    "system_restricted",
}
DIRECT_OBSERVER_SCOPES = {
    "private_self",
    "private_target",
    "scene_pair",
    "restricted_subset",
}
PUBLIC_VISIBILITY_SCOPES = {
    "scene_public",
    "local_public",
    "institution_public",
    "city_public",
    "realm_public",
}
AUTHORIZED_INTERIORITY_FIELDS = {
    "subject_id",
    "access_mode",
    "content",
    "authority_basis",
    "scope_limit",
    "source_proposal_id",
    "source_field",
    "source_sha256",
}

MAX_SYNTAX_REPAIR_STRUCTURAL_EDITS = 4


def validate_syntax_repair_conservation(
    original_raw_output: Any,
    repaired_raw_output: Any,
    parsed_output: Any,
) -> list[dict[str, Any]]:
    """Prove that a JSON retry changed syntax, not protocol content."""

    if not isinstance(original_raw_output, str) or not isinstance(
        repaired_raw_output, str
    ):
        return [
            _syntax_repair_block(
                "syntax_repair_missing_raw_output",
                "Syntax repair requires both original and repaired raw strings.",
            )
        ]
    try:
        strict_parsed = json.loads(repaired_raw_output.strip())
    except (TypeError, json.JSONDecodeError) as exc:
        return [
            _syntax_repair_block(
                "syntax_repair_not_strict_json",
                f"Syntax repair must return one strict JSON object: {exc}",
            )
        ]
    if not isinstance(strict_parsed, dict):
        return [
            _syntax_repair_block(
                "syntax_repair_root_not_object",
                "Syntax repair must return a JSON object at the root.",
            )
        ]
    if strict_parsed != parsed_output:
        return [
            _syntax_repair_block(
                "syntax_repair_parser_binding_mismatch",
                "Strictly reparsed JSON does not equal the provider parsed output.",
            )
        ]

    try:
        original_compact = _compact_json_outside_strings(original_raw_output)
        repaired_compact = _compact_json_outside_strings(repaired_raw_output)
        original_tokens = _json_semantic_tokens(original_raw_output.strip())
        repaired_tokens = _json_semantic_tokens(repaired_raw_output.strip())
    except ValueError as exc:
        return [
            _syntax_repair_block(
                "syntax_repair_conservation_unprovable",
                f"Runtime cannot prove syntax-only conservation: {exc}",
            )
        ]

    if original_tokens != repaired_tokens:
        return [
            _syntax_repair_block(
                "syntax_repair_semantic_drift",
                "Keys, scalar values, or their order changed during syntax repair.",
            )
        ]

    edit_count = 0
    matcher = SequenceMatcher(
        None,
        original_compact,
        repaired_compact,
        autojunk=False,
    )
    for tag, original_start, original_end, repaired_start, repaired_end in matcher.get_opcodes():
        if tag == "equal":
            continue
        original_segment = original_compact[original_start:original_end]
        repaired_segment = repaired_compact[repaired_start:repaired_end]
        edit_count += max(len(original_segment), len(repaired_segment))
        if tag == "insert" and _allowed_syntax_insertion(
            repaired_segment,
            original_start,
            original_compact,
            repaired_end,
            repaired_compact,
        ):
            continue
        if tag == "delete" and _allowed_syntax_deletion(
            original_segment,
            original_start,
            original_end,
            original_compact,
            repaired_start,
            repaired_compact,
        ):
            continue
        return [
            _syntax_repair_block(
                "syntax_repair_forbidden_structural_edit",
                "Repair changed syntax outside the narrow comma or terminal-closure allowlist.",
            )
        ]
    if edit_count == 0:
        return [
            _syntax_repair_block(
                "syntax_repair_made_no_change",
                "A rejected JSON response cannot be accepted without a syntax change.",
            )
        ]
    if edit_count > MAX_SYNTAX_REPAIR_STRUCTURAL_EDITS:
        return [
            _syntax_repair_block(
                "syntax_repair_edit_budget_exceeded",
                f"Syntax repair used {edit_count} structural edits; maximum is {MAX_SYNTAX_REPAIR_STRUCTURAL_EDITS}.",
            )
        ]
    return []


def _compact_json_outside_strings(text: str) -> str:
    compact: list[str] = []
    in_string = False
    escaped = False
    for char in text.strip():
        if in_string:
            compact.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            compact.append(char)
        elif not char.isspace():
            compact.append(char)
    if in_string:
        raise ValueError("original or repaired output has an unterminated string")
    return "".join(compact)


def _json_semantic_tokens(text: str) -> list[tuple[str, Any]]:
    tokens: list[tuple[str, Any]] = []
    index = 0
    structural = set("{}[]:,")
    literal_pattern = re.compile(
        r"(?:-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?|true|false|null)"
    )
    while index < len(text):
        char = text[index]
        if char.isspace():
            index += 1
            continue
        if char in structural:
            index += 1
            continue
        if char == '"':
            end = index + 1
            escaped = False
            while end < len(text):
                current = text[end]
                if escaped:
                    escaped = False
                elif current == "\\":
                    escaped = True
                elif current == '"':
                    break
                end += 1
            if end >= len(text):
                raise ValueError("unterminated JSON string token")
            raw_string = text[index : end + 1]
            try:
                decoded = json.loads(raw_string)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON string token: {exc}") from exc
            tokens.append(("string", decoded))
            index = end + 1
            continue
        match = literal_pattern.match(text, index)
        if not match:
            raise ValueError(f"unknown token at character {index}")
        raw_literal = match.group(0)
        next_index = match.end()
        if (
            next_index < len(text)
            and text[next_index] not in structural
            and not text[next_index].isspace()
            and text[next_index] != '"'
        ):
            raise ValueError(f"ambiguous literal boundary at character {next_index}")
        tokens.append(("literal", raw_literal))
        index = next_index
    return tokens


def _allowed_syntax_insertion(
    segment: str,
    original_index: int,
    original: str,
    repaired_end: int,
    repaired: str,
) -> bool:
    if segment and set(segment) == {","}:
        return True
    return (
        segment
        and set(segment).issubset({"}", "]"})
        and original_index == len(original)
        and repaired_end == len(repaired)
    )


def _allowed_syntax_deletion(
    segment: str,
    original_start: int,
    original_end: int,
    original: str,
    repaired_index: int,
    repaired: str,
) -> bool:
    if segment and set(segment) == {","}:
        return original_end < len(original) and original[original_end] in "}]"
    return (
        segment
        and set(segment).issubset({"}", "]"})
        and original_end == len(original)
        and repaired_index == len(repaired)
    )


def _syntax_repair_block(code: str, message: str) -> dict[str, Any]:
    return {
        "severity": "block",
        "kind": "output_syntax_repair",
        "code": code,
        "message": message,
    }


SPOKEN_LINE_COMMON_FIELDS = {
    "status",
    "speaker_id",
    "source_proposal_id",
    "source_field",
    "source_sha256",
}
RESPONSE_CONTRACT_FIELDS = {"output_type", "allowed_action_types"}
ALLOWED_ACTION_TYPES = {"speech", "physical", "cognitive_commitment", "refusal", "wait"}
PLOT_PRESSURE_KINDS = {
    "deadline",
    "resource_scarcity",
    "social_exposure",
    "institutional_constraint",
    "relationship_strain",
    "moral_dilemma",
    "environmental_pressure",
    "information_asymmetry",
    "escalation_signal",
}
PLOT_SCOPES = {
    "beat",
    "scene",
    "sequence",
    "subscene",
    "location",
    "relationship",
    "institution",
    "timeline",
}
PLOT_DURATIONS = {
    "one_window",
    "next_beat",
    "next_two_beats",
    "scene",
    "chapter",
    "scheduled",
    "until_condition",
}
DECISION_REQUEST_FIELDS = {
    "message_type",
    "scene_id",
    "request_id",
    "source_tick_id",
    "target_character_id",
    "agency_question",
    "visible_trigger_refs",
    "response_contract",
    "visibility",
    "authority_basis",
}
WORLD_TICK_FIELDS = {
    "message_type", "scene_id", "tick_id", "tick_index", "consumed_input_refs",
    "adjudication", "plot_pulse_disposition", "next_directive", "checkpoint_state",
    "authority_basis", "visibility", "based_on",
}
WORLD_ADJUDICATION_FIELDS = {
    "adjudication_id", "input_type", "input_ref", "input_sha256", "outcome_type",
    "outcome_summary", "applicable_rules", "constraint_basis", "adjudication_basis",
    "uncertainty_model", "failed_alternatives",
    "committed_events", "state_deltas", "visibility_results", "publication_candidates",
    "canon_reveal_candidates",
}
COMMITTED_EVENT_FIELDS = {
    "message_type", "scene_id", "event_id", "source_input_type", "source_input_ref",
    "event_kind", "actors", "outcome", "public_surface", "visibility",
    "authorized_interiority", "spoken_line_records", "causal_basis", "commit_status",
}
ROUTE_PLAN_FIELDS = {
    "message_type", "route_id", "request_id", "request_sha256", "recipient_agent_id",
    "projection_profile", "reason", "visibility", "authority_basis", "based_on",
}
EVENT_PROPOSAL_FIELDS = {
    "message_type", "scene_id", "proposal_id", "request_id", "actor_id", "action_type",
    "intent_summary", "public_surface", "private_intent", "desired_effect",
    "disclosure_limits", "interiority_grant", "visibility_request", "visibility", "authority_basis", "based_on",
}
AUTHORITY_REVIEW_FIELDS = {
    "message_type", "review_id", "subject_type", "subject_ref", "subject_sha256", "verdict",
    "findings", "required_repairs", "authority_basis", "reviewed_fields", "visibility", "claim_map",
    "run_nonce", "review_context_sha256",
}
AUTHORITY_REQUIRED_REVIEW_FIELDS = {
    "character_decision_request": {
        "target_character_id", "agency_question", "visible_trigger_refs",
        "response_contract", "visibility", "authority_basis",
    },
    "event_proposal": {
        "actor_id", "action_type", "intent_summary", "public_surface",
        "private_intent", "desired_effect", "disclosure_limits",
        "interiority_grant", "visibility_request", "based_on",
    },
    "world_adjudication": {
        "input_type", "input_ref", "input_sha256", "outcome_type",
        "outcome_summary", "applicable_rules", "constraint_basis",
        "adjudication_basis", "uncertainty_model", "failed_alternatives",
        "committed_events", "state_deltas",
        "visibility_results", "publication_candidates", "canon_reveal_candidates",
    },
    "plot_pulse": {
        "pressure_kind", "scope", "duration", "affected_options",
        "non_forcing_clause", "world_fact_dependency", "forbidden_outcomes",
        "budget_cost", "option_topology_check", "based_on",
    },
    "plot_pulse_disposition": {
        "pulse_id", "pulse_sha256", "decision", "translation_summary",
        "world_condition_refs",
    },
    "narration": {"source_checkpoint_id", "source_event_refs", "prose", "claim_units"},
}
PLOT_PULSE_FIELDS = {
    "message_type", "scene_id", "pulse_id", "pressure_kind", "scope", "duration",
    "affected_options", "non_forcing_clause", "world_fact_dependency", "forbidden_outcomes",
    "visibility", "budget_cost", "option_topology_check", "authority_basis", "based_on",
}
STATE_DELTA_FIELDS = {
    "delta_id", "target_layer", "target_id", "change_kind", "after_summary", "based_on",
}
VISIBILITY_RESULT_FIELDS = {
    "visibility_result_id", "source_event_id", "scope", "scope_ref", "observer_refs", "limits",
}
PUBLICATION_CANDIDATE_FIELDS = {
    "publication_candidate_id", "source_event_ref", "proposed_scope", "scope_ref",
    "candidate_summary", "status", "visibility", "based_on", "expires_after_ticks",
}
CANON_REVEAL_CANDIDATE_FIELDS = {
    "canon_reveal_candidate_id", "source_event_ref", "canon_ref", "exposure_summary",
    "status", "visibility", "based_on", "expires_after_ticks",
}
ORIGIN_SAFE_REPAIR_CODES = {
    "remove_unsupported_fact",
    "remove_other_mind_claim",
    "reduce_certainty",
    "remove_outcome_declaration",
    "restore_visibility_scope",
    "preserve_owner_identity",
    "schema_only",
}

PROTOCOL_ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")


def _fail_closed_validator(kind: str):
    """Convert unexpected validator input failures into quarantine evidence."""

    def decorator(function):
        @wraps(function)
        def wrapped(*args, **kwargs) -> list[dict[str, Any]]:
            try:
                return function(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 - validators must never fail open
                return [
                    _block(
                        kind,
                        "validator_input_error",
                        "Validator rejected malformed input without executing the path "
                        f"({type(exc).__name__}).",
                    )
                ]

        return wrapped

    return decorator


def is_protocol_id(value: Any) -> bool:
    return isinstance(value, str) and bool(PROTOCOL_ID_PATTERN.fullmatch(value))


def _is_enum(value: Any, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


@_fail_closed_validator("world_fixture")
def validate_world_fixture(fixture: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Validate security-critical fixture configuration before any model call."""

    violations: list[dict[str, Any]] = []
    if not isinstance(fixture, dict):
        return [_block("world_fixture", "invalid_fixture", "World-driven fixture must be an object.")]
    if fixture.get("runtime_mode") != "world_driven":
        violations.append(_block("world_fixture", "invalid_runtime_mode", "World runtime accepts only runtime_mode=world_driven."))
    for field in ["trace_id", "scene_id"]:
        if not is_protocol_id(fixture.get(field)):
            violations.append(
                _block(
                    "world_fixture",
                    "invalid_fixture_identity",
                    f"Fixture `{field}` must be a protocol id of at most 128 characters.",
                )
            )
    if not is_safe_path_id(fixture.get("trace_id")):
        violations.append(
            _block(
                "world_fixture",
                "invalid_trace_path_id",
                "Fixture `trace_id` must also be one safe, portable filesystem segment.",
            )
        )
    if not isinstance(fixture.get("user_request"), str) or not fixture["user_request"].strip():
        violations.append(
            _block(
                "world_fixture",
                "missing_user_request",
                "World-driven fixture requires a non-empty user_request before context projection.",
            )
        )
    characters = fixture.get("characters")
    if not isinstance(characters, dict) or not characters:
        violations.append(_block("world_fixture", "invalid_character_registry", "World-driven fixture requires a non-empty character registry."))
        characters = {}
    else:
        for character_id, character in characters.items():
            if not is_protocol_id(character_id):
                violations.append(_block("world_fixture", "invalid_character_id", "Character registry keys must be protocol ids."))
            if not isinstance(character, dict):
                violations.append(_block("world_fixture", "invalid_character_record", f"Character `{character_id}` must be an object."))
                continue
            private_memory = character.get("private_memory", [])
            if not isinstance(private_memory, list) or not all(
                isinstance(item, dict) for item in private_memory
            ):
                violations.append(_block("world_fixture", "invalid_private_memory", f"Character `{character_id}` private_memory must be a list of objects."))
            else:
                _reject_duplicate_collection_ids(
                    private_memory,
                    "delta_id",
                    f"characters.{character_id}.private_memory",
                    violations,
                )
    participants = fixture.get("scene_participant_ids")
    if not isinstance(participants, list) or not participants or not all(is_protocol_id(item) for item in participants):
        violations.append(_block("world_fixture", "invalid_scene_participant_registry", "scene_participant_ids must be a non-empty list of character ids."))
    else:
        if len(participants) != len(set(participants)):
            violations.append(_block("world_fixture", "duplicate_scene_participant", "scene_participant_ids must be unique."))
        unknown = sorted(item for item in participants if item not in characters)
        if unknown:
            violations.append(_block("world_fixture", "unknown_scene_participant", "Scene participant registry names unknown characters: " + ", ".join(unknown)))
    pov_contract = fixture.get("pov_contract")
    if not isinstance(pov_contract, dict):
        violations.append(_block("world_fixture", "invalid_pov_contract", "pov_contract must be an object."))
    else:
        focal_agent_id = pov_contract.get("focal_agent_id")
        if not isinstance(focal_agent_id, str) or focal_agent_id not in characters:
            violations.append(_block("world_fixture", "invalid_focal_agent", "pov_contract.focal_agent_id must name one registered Character Agent."))
    public_scope_registry = fixture.get("public_scope_registry", {})
    if not isinstance(public_scope_registry, dict):
        violations.append(_block("world_fixture", "invalid_public_scope_registry", "public_scope_registry must be an object."))
    else:
        for scope_ref, entry in public_scope_registry.items():
            if not isinstance(scope_ref, str) or not scope_ref or not isinstance(entry, dict):
                violations.append(_block("world_fixture", "invalid_public_scope_entry", "Each public scope entry requires a non-empty string key and object value."))
                continue
            scope_type = entry.get("scope_type")
            members = entry.get("members")
            if not _is_enum(scope_type, PUBLIC_VISIBILITY_SCOPES):
                violations.append(_block("world_fixture", "invalid_public_scope_type", f"Public scope `{scope_ref}` has an invalid scope_type."))
            if not isinstance(members, list) or not all(
                isinstance(item, str) and item in characters for item in members
            ):
                violations.append(_block("world_fixture", "invalid_public_scope_members", f"Public scope `{scope_ref}` members must be registered Character ids."))
    if not isinstance(fixture.get("narration_bounds", {}), dict):
        violations.append(_block("world_fixture", "invalid_narration_bounds", "narration_bounds must be an object."))
    else:
        for field in ["must_preserve", "must_not_claim", "forbidden_claim_patterns"]:
            value = fixture.get("narration_bounds", {}).get(field, [])
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                violations.append(_block("world_fixture", "invalid_narration_bound", f"narration_bounds.{field} must be a list of strings."))
    checkpoint_policy = fixture.get("checkpoint_policy", {})
    if not isinstance(checkpoint_policy, dict):
        violations.append(_block("world_fixture", "invalid_checkpoint_policy", "checkpoint_policy must be an object."))
    else:
        for field in ["plot_every_committed_beats", "narrate_every_committed_beats"]:
            value = checkpoint_policy.get(field, 2)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                violations.append(_block("world_fixture", "invalid_checkpoint_interval", f"checkpoint_policy.{field} must be a non-negative integer."))
    max_world_ticks = fixture.get("max_world_ticks", 8)
    if not isinstance(max_world_ticks, int) or isinstance(max_world_ticks, bool) or max_world_ticks < 1:
        violations.append(_block("world_fixture", "invalid_max_world_ticks", "max_world_ticks must be a positive integer."))
    for field in [
        "max_character_repair_attempts",
        "max_narrator_repair_attempts",
        "max_world_repair_attempts",
    ]:
        value = fixture.get(field, 1)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            violations.append(
                _block(
                    "world_fixture",
                    "invalid_repair_limit",
                    f"{field} must be a non-negative integer.",
                )
            )
    for field in ["public_canon", "public_event_ledger", "pressure_history", "scheduled_world_events", "world_condition_registry"]:
        value = fixture.get(field, [])
        if not isinstance(value, list):
            violations.append(_block("world_fixture", "invalid_fixture_collection", f"{field} must be a list."))
    for field in [
        "world_state_ledger",
        "visible_observations",
        "encountered_public_event_refs",
        "public_relationship_summary",
        "option_topology",
    ]:
        value = fixture.get(field, {})
        if not isinstance(value, dict):
            violations.append(_block("world_fixture", "invalid_fixture_mapping", f"{field} must be an object."))

    public_events = fixture.get("public_event_ledger", [])
    if isinstance(public_events, list):
        _reject_duplicate_collection_ids(
            public_events,
            "publication_id",
            "public_event_ledger",
            violations,
        )
        for index, event in enumerate(public_events):
            if not isinstance(event, dict):
                violations.append(_block("world_fixture", "invalid_public_event", f"public_event_ledger[{index}] must be an object."))
                continue
            for field in ["publication_id", "effective_scope", "scope_ref", "public_summary"]:
                if not isinstance(event.get(field), str) or not event.get(field):
                    violations.append(_block("world_fixture", "invalid_public_event", f"public_event_ledger[{index}].{field} must be a non-empty string."))
            if not is_protocol_id(event.get("publication_id")):
                violations.append(_block("world_fixture", "invalid_public_event_id", f"public_event_ledger[{index}].publication_id must be a protocol id."))

    pressure_history = fixture.get("pressure_history", [])
    if isinstance(pressure_history, list) and not all(
        isinstance(item, dict) for item in pressure_history
    ):
        violations.append(_block("world_fixture", "invalid_pressure_history", "pressure_history must contain only objects."))

    scheduled_events = fixture.get("scheduled_world_events", [])
    if isinstance(scheduled_events, list):
        _reject_duplicate_collection_ids(
            scheduled_events,
            "schedule_id",
            "scheduled_world_events",
            violations,
        )
        for index, record in enumerate(scheduled_events):
            if not isinstance(record, dict) or not is_protocol_id(record.get("schedule_id")):
                violations.append(_block("world_fixture", "invalid_scheduled_world_event", f"scheduled_world_events[{index}] requires a protocol-id schedule_id."))

    condition_registry = fixture.get("world_condition_registry", [])
    if isinstance(condition_registry, list) and not all(
        is_protocol_id(item) for item in condition_registry
    ):
        violations.append(_block("world_fixture", "invalid_world_condition_registry", "world_condition_registry must contain only protocol ids."))
    elif isinstance(condition_registry, list) and len(condition_registry) != len(
        set(condition_registry)
    ):
        violations.append(_block("world_fixture", "duplicate_world_condition_id", "world_condition_registry ids must be unique."))

    observations = fixture.get("visible_observations", {})
    if isinstance(observations, dict):
        for character_id, records in observations.items():
            if character_id not in characters or not isinstance(records, list):
                violations.append(_block("world_fixture", "invalid_visible_observations", "visible_observations keys must be registered Characters with list values."))
                continue
            _reject_duplicate_collection_ids(
                records,
                "observation_id",
                f"visible_observations.{character_id}",
                violations,
            )
            for index, record in enumerate(records):
                if not isinstance(record, dict) or not isinstance(record.get("observation_id"), str):
                    violations.append(_block("world_fixture", "invalid_visible_observation", f"visible_observations.{character_id}[{index}] requires an observation_id."))

    encountered = fixture.get("encountered_public_event_refs", {})
    if isinstance(encountered, dict):
        for character_id, refs in encountered.items():
            if character_id not in characters or not isinstance(refs, list) or not all(
                isinstance(ref, str) for ref in refs
            ):
                violations.append(_block("world_fixture", "invalid_encounter_registry", "encountered_public_event_refs must map registered Characters to string lists."))

    option_topology = fixture.get("option_topology", {})
    if isinstance(option_topology, dict):
        for character_id, options in option_topology.items():
            if character_id not in characters or not isinstance(options, list) or not all(
                isinstance(option, str) for option in options
            ):
                violations.append(_block("world_fixture", "invalid_option_topology", "option_topology must map registered Characters to string option lists."))

    memory_policy = fixture.get("character_memory_retrieval_policy", {})
    if not isinstance(memory_policy, dict):
        violations.append(_block("world_fixture", "invalid_memory_retrieval_policy", "character_memory_retrieval_policy must be an object."))
    else:
        max_items = memory_policy.get("max_items", 16)
        statuses = memory_policy.get("allowed_statuses", ["active", "contested"])
        if not isinstance(max_items, int) or isinstance(max_items, bool) or max_items < 0:
            violations.append(_block("world_fixture", "invalid_memory_retrieval_limit", "character_memory_retrieval_policy.max_items must be a non-negative integer."))
        if not isinstance(statuses, list) or not all(isinstance(item, str) for item in statuses):
            violations.append(_block("world_fixture", "invalid_memory_statuses", "character_memory_retrieval_policy.allowed_statuses must be a string list."))

    mock_outputs = fixture.get("mock_agent_outputs", {})
    if not isinstance(mock_outputs, dict):
        violations.append(_block("world_fixture", "invalid_mock_outputs", "mock_agent_outputs must be an object when present."))
    return violations


def _reject_duplicate_collection_ids(
    collection: list[Any],
    id_field: str,
    collection_name: str,
    violations: list[dict[str, Any]],
) -> None:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in collection:
        if not isinstance(item, dict):
            continue
        identity = item.get(id_field)
        if not isinstance(identity, str) or not identity:
            continue
        if identity in seen:
            duplicates.add(identity)
        seen.add(identity)
    if duplicates:
        violations.append(
            _block(
                "world_fixture",
                "duplicate_projection_source_id",
                f"{collection_name}.{id_field} values must be unique: "
                + ", ".join(sorted(duplicates)),
            )
        )


def build_narration_claim_units(prose: str, checkpoint_id: str) -> list[dict[str, Any]]:
    """Split all non-whitespace prose into exact, hash-bound review units."""

    if not isinstance(prose, str) or not prose.strip():
        return []
    terminal_chars = {".", "!", "?", "。", "！", "？"}
    trailing_closers = {'"', "'", "”", "’", ")", "]", "}"}
    raw_spans: list[tuple[int, int]] = []
    start = 0
    index = 0
    while index < len(prose):
        char = prose[index]
        if char in terminal_chars:
            end = index + 1
            while end < len(prose) and prose[end] in trailing_closers:
                end += 1
            raw_spans.append((start, end))
            start = end
            index = end
            continue
        if char == "\n":
            raw_spans.append((start, index))
            start = index + 1
        index += 1
    raw_spans.append((start, len(prose)))

    units: list[dict[str, Any]] = []
    for raw_start, raw_end in raw_spans:
        chunk = prose[raw_start:raw_end]
        if not chunk.strip():
            continue
        leading = len(chunk) - len(chunk.lstrip())
        trailing = len(chunk) - len(chunk.rstrip())
        unit_start = raw_start + leading
        unit_end = raw_end - trailing
        claim_text = prose[unit_start:unit_end]
        claim_index = len(units)
        units.append(
            {
                "claim_id": f"{checkpoint_id}:claim:{claim_index}",
                "start": unit_start,
                "end": unit_end,
                "claim_text": claim_text,
                "claim_sha256": hashlib.sha256(stable_json(claim_text).encode("utf-8")).hexdigest(),
            }
        )
    return units


@_fail_closed_validator("world_tick_schema")
def validate_world_tick(
    result: dict[str, Any] | None,
    *,
    expected_tick_index: int,
    pending_approved_proposal: dict[str, Any] | None,
    pending_plot_pulse: dict[str, Any] | None = None,
    existing_world_condition_refs: set[str] | None = None,
    scheduled_world_event_hashes: dict[str, str] | None = None,
    expected_scene_id: str | None = None,
    character_ids: set[str] | None = None,
    public_scope_registry: dict[str, Any] | None = None,
    scene_participant_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    if not result:
        return [_block("world_tick_schema", "missing_world_tick", "World Agent did not return WorldTickResult.")]

    _require_security_fields(
        result,
        [
            "message_type",
            "scene_id",
            "tick_id",
            "tick_index",
            "consumed_input_refs",
            "next_directive",
            "checkpoint_state",
            "authority_basis",
            "visibility",
            "based_on",
        ],
        "world_tick_schema",
        violations,
    )
    if "adjudication" not in result:
        violations.append(_block("world_tick_schema", "missing_security_critical_field", "Missing security-critical field `adjudication`; object is quarantined, not inferred."))
    if "plot_pulse_disposition" not in result:
        violations.append(_block("world_tick_schema", "missing_security_critical_field", "Missing security-critical field `plot_pulse_disposition`; object is quarantined, not inferred."))
    if result.get("message_type") != "WorldTickResult":
        violations.append(_block("world_tick_schema", "invalid_message_type", "message_type must be WorldTickResult."))
    _reject_unexpected_fields(result, WORLD_TICK_FIELDS, "world_tick_schema", violations)
    if expected_scene_id and result.get("scene_id") != expected_scene_id:
        violations.append(_block("world_tick_schema", "scene_id_mismatch", "WorldTickResult references the wrong scene."))
    if result.get("visibility") != "system_restricted":
        violations.append(_block("world_tick_schema", "unsafe_visibility", "WorldTickResult must remain system_restricted."))
    consumed_input_refs = result.get("consumed_input_refs")
    if not isinstance(consumed_input_refs, list) or not all(
        is_protocol_id(item) for item in consumed_input_refs
    ):
        violations.append(_block("world_tick_schema", "invalid_consumed_input_refs", "consumed_input_refs must be a list."))
        consumed_input_refs = []
    for field in ["authority_basis", "based_on"]:
        if not isinstance(result.get(field), list):
            violations.append(_block("world_tick_schema", "invalid_list_field", f"WorldTickResult `{field}` must be a list."))
    if result.get("tick_index") != expected_tick_index:
        violations.append(
            _block(
                "world_tick_integrity",
                "tick_index_mismatch",
                f"Expected tick_index {expected_tick_index}, got {result.get('tick_index')!r}.",
            )
        )

    adjudication = result.get("adjudication")
    expected_input_type: str | None = None
    expected_input_ref: str | None = None
    expected_input_sha256: str | None = None
    if pending_approved_proposal:
        proposal = pending_approved_proposal.get("original_proposal", {})
        expected_input_type = "event_proposal"
        expected_input_ref = proposal.get("proposal_id")
        expected_input_sha256 = pending_approved_proposal.get("proposal_sha256")
        if not isinstance(adjudication, dict):
            violations.append(
                _block(
                    "world_adjudication",
                    "approved_proposal_not_adjudicated",
                    "World must adjudicate the pending ApprovedEventProposal before advancing.",
                )
            )
        else:
            violations.extend(
                validate_world_adjudication(
                    adjudication,
                    expected_input_type,
                    expected_input_ref,
                    expected_input_sha256,
                    expected_scene_id,
                    character_ids,
                    public_scope_registry,
                    proposal,
                    scene_participant_ids,
                )
            )
        if expected_input_ref not in consumed_input_refs:
            violations.append(
                _block(
                    "world_tick_integrity",
                    "approved_proposal_not_consumed",
                    "World must list the pending proposal id in consumed_input_refs.",
                )
            )
    elif isinstance(adjudication, dict) and adjudication:
        input_type = adjudication.get("input_type")
        input_ref = adjudication.get("input_ref")
        if input_type == "scheduled_world_event":
            expected_input_type = input_type
            expected_input_ref = input_ref if isinstance(input_ref, str) else None
            expected_input_sha256 = (scheduled_world_event_hashes or {}).get(str(input_ref))
            if expected_input_sha256 is None:
                violations.append(_block("world_adjudication", "unregistered_scheduled_world_event", "World may advance only a registered, unconsumed scheduled world event."))
        elif input_type == "plot_pulse" and pending_plot_pulse:
            expected_input_type = input_type
            expected_input_ref = pending_plot_pulse.get("pulse_id")
            expected_input_sha256 = pending_plot_pulse.get("pulse_sha256")
        else:
            violations.append(_block("world_adjudication", "adjudication_without_approved_input", "World adjudication requires an approved Character proposal, a registered scheduled event, or the pending approved PlotPulse."))
        if expected_input_type and expected_input_ref and expected_input_sha256:
            violations.extend(
                validate_world_adjudication(
                    adjudication,
                    expected_input_type,
                    expected_input_ref,
                    expected_input_sha256,
                    expected_scene_id,
                    character_ids,
                    public_scope_registry,
                    None,
                    scene_participant_ids,
                )
            )
            if expected_input_ref not in consumed_input_refs:
                violations.append(_block("world_tick_integrity", "adjudication_input_not_consumed", "World must list the adjudicated input in consumed_input_refs."))
    elif adjudication not in (None, {}):
        violations.append(_block("world_adjudication", "invalid_adjudication", "adjudication must be an object or null."))

    if pending_plot_pulse:
        pulse_id = pending_plot_pulse.get("pulse_id")
        if pulse_id not in consumed_input_refs:
            violations.append(
                _block(
                    "world_tick_integrity",
                    "approved_plot_pulse_not_consumed",
                    "World must list the pending PlotPulse id in consumed_input_refs.",
                )
            )
        disposition = result.get("plot_pulse_disposition")
        if not isinstance(disposition, dict):
            violations.append(_block("plot_pulse_disposition", "missing_plot_pulse_disposition", "World must explicitly accept, downgrade, defer, or reject a pending PlotPulse."))
        else:
            _require_security_fields(
                disposition,
                ["pulse_id", "pulse_sha256", "decision", "translation_summary", "world_condition_refs"],
                "plot_pulse_disposition",
                violations,
            )
            if disposition.get("pulse_id") != pulse_id or disposition.get("pulse_sha256") != pending_plot_pulse.get("pulse_sha256"):
                violations.append(_block("plot_pulse_disposition", "plot_pulse_integrity_mismatch", "PlotPulse disposition must preserve the approved pulse id and hash."))
            if not _is_enum(disposition.get("decision"), PLOT_PULSE_DISPOSITIONS):
                violations.append(_block("plot_pulse_disposition", "invalid_plot_pulse_disposition", "PlotPulse disposition decision is invalid."))
            condition_refs = disposition.get("world_condition_refs")
            if not isinstance(condition_refs, list) or not all(isinstance(ref, str) for ref in condition_refs):
                violations.append(_block("plot_pulse_disposition", "invalid_world_condition_refs", "world_condition_refs must be a list."))
            else:
                grounded_refs = set(existing_world_condition_refs or set())
                if isinstance(adjudication, dict):
                    grounded_refs.update(
                        str(item["event_id"])
                        for item in adjudication.get("committed_events", [])
                        if isinstance(item, dict) and item.get("event_id")
                    )
                    grounded_refs.update(
                        str(item["delta_id"])
                        for item in adjudication.get("state_deltas", [])
                        if isinstance(item, dict) and item.get("delta_id")
                    )
                decision = disposition.get("decision")
                if _is_enum(decision, {"accepted", "downgraded"}) and not condition_refs:
                    violations.append(_block("plot_pulse_disposition", "missing_world_condition_ref", "Accepted or downgraded pressure must bind to at least one committed world condition."))
                illegal_refs = sorted(ref for ref in condition_refs if ref not in grounded_refs)
                if illegal_refs:
                    violations.append(_block("plot_pulse_disposition", "ungrounded_world_condition_ref", "PlotPulse disposition cites uncommitted world conditions: " + ", ".join(illegal_refs)))
                if _is_enum(decision, {"deferred", "rejected"}) and condition_refs:
                    violations.append(_block("plot_pulse_disposition", "inactive_disposition_has_world_condition", "Deferred or rejected pressure may not claim translated world conditions."))
                if (
                    _is_enum(decision, {"deferred", "rejected"})
                    and isinstance(adjudication, dict)
                    and adjudication.get("input_type") == "plot_pulse"
                ):
                    violations.append(
                        _block(
                            "plot_pulse_disposition",
                            "inactive_disposition_has_adjudication",
                            "Deferred or rejected Plot pressure may not commit an adjudication derived from that pulse.",
                        )
                    )
    elif result.get("plot_pulse_disposition") not in (None, {}):
        violations.append(_block("plot_pulse_disposition", "disposition_without_pending_pulse", "World may not dispose a PlotPulse when none is pending."))

    directive = result.get("next_directive")
    if not isinstance(directive, dict):
        violations.append(_block("world_directive", "missing_directive", "next_directive must be an object."))
        return violations
    directive_type = directive.get("directive_type")
    _reject_unexpected_fields(
        directive,
        {"directive_type", "reason", "decision_request"},
        "world_directive",
        violations,
    )
    if not _is_enum(directive_type, WORLD_DIRECTIVES):
        violations.append(_block("world_directive", "invalid_directive_type", f"Invalid directive_type: {directive_type!r}."))
    if directive_type == "request_character_decision":
        violations.extend(
            validate_decision_request(
                directive.get("decision_request"),
                result.get("tick_id"),
                expected_scene_id,
            )
        )
    elif directive.get("decision_request") not in (None, {}):
        violations.append(
            _block(
                "world_directive",
                "unexpected_decision_request",
                "decision_request is legal only for request_character_decision.",
            )
        )
    return violations


@_fail_closed_validator("world_adjudication")
def validate_world_adjudication(
    adjudication: dict[str, Any],
    expected_input_type: str | None,
    expected_input_ref: str | None,
    expected_input_sha256: str | None,
    expected_scene_id: str | None = None,
    character_ids: set[str] | None = None,
    public_scope_registry: dict[str, Any] | None = None,
    expected_input_object: dict[str, Any] | None = None,
    scene_participant_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    _require_security_fields(
        adjudication,
        [
            "adjudication_id",
            "input_type",
            "input_ref",
            "input_sha256",
            "outcome_type",
            "outcome_summary",
            "applicable_rules",
            "constraint_basis",
            "adjudication_basis",
            "uncertainty_model",
            "failed_alternatives",
            "committed_events",
            "state_deltas",
            "visibility_results",
            "publication_candidates",
            "canon_reveal_candidates",
        ],
        "world_adjudication",
        violations,
    )
    _reject_unexpected_fields(
        adjudication,
        WORLD_ADJUDICATION_FIELDS,
        "world_adjudication",
        violations,
    )
    if adjudication.get("input_type") != expected_input_type:
        violations.append(
            _block(
                "world_adjudication",
                "input_type_mismatch",
                "World adjudication uses the wrong approved input type.",
            )
        )
    if adjudication.get("input_ref") != expected_input_ref:
        violations.append(
            _block(
                "world_adjudication",
                "input_ref_mismatch",
                "World adjudication references the wrong approved input.",
            )
        )
    if expected_input_sha256 and adjudication.get("input_sha256") != expected_input_sha256:
        violations.append(
            _block(
                "world_adjudication",
                "input_hash_mismatch",
                "World adjudication did not preserve the approved input hash.",
            )
        )
    if not _is_enum(adjudication.get("outcome_type"), WORLD_OUTCOME_TYPES):
        violations.append(_block("world_adjudication", "invalid_outcome_type", "WorldAdjudication outcome_type is invalid."))
    for field in ["applicable_rules", "constraint_basis"]:
        if not isinstance(adjudication.get(field), list) or not adjudication.get(field):
            violations.append(_block("world_adjudication", "invalid_list_field", f"WorldAdjudication `{field}` must be a non-empty list."))
    uncertainty_model = adjudication.get("uncertainty_model")
    if not isinstance(uncertainty_model, dict):
        violations.append(_block("world_adjudication", "invalid_uncertainty_model", "WorldAdjudication uncertainty_model must be an object."))
    else:
        _require_security_fields(
            uncertainty_model,
            ["mode", "evidence_refs", "uncertainty_sources"],
            "uncertainty_model",
            violations,
        )
        _reject_unexpected_fields(
            uncertainty_model,
            {"mode", "evidence_refs", "uncertainty_sources", "seed_ref"},
            "uncertainty_model",
            violations,
        )
        if not _is_enum(
            uncertainty_model.get("mode"),
            {"deterministic", "bounded_judgment", "seeded_random"},
        ):
            violations.append(_block("world_adjudication", "invalid_uncertainty_mode", "uncertainty_model.mode is invalid."))
        for field in ["evidence_refs", "uncertainty_sources"]:
            if not isinstance(uncertainty_model.get(field), list):
                violations.append(_block("world_adjudication", "invalid_uncertainty_field", f"uncertainty_model.{field} must be a list."))
        if uncertainty_model.get("mode") == "seeded_random" and not uncertainty_model.get("seed_ref"):
            violations.append(_block("world_adjudication", "missing_seed_ref", "seeded_random adjudication requires a stable seed_ref."))
    failed_alternatives = adjudication.get("failed_alternatives")
    if not isinstance(failed_alternatives, list):
        violations.append(_block("world_adjudication", "invalid_failed_alternatives", "failed_alternatives must be a list."))
    else:
        for index, alternative in enumerate(failed_alternatives):
            if not isinstance(alternative, dict):
                violations.append(_block("world_adjudication", "invalid_failed_alternative", f"failed_alternatives[{index}] must be an object."))
                continue
            _require_security_fields(
                alternative,
                ["outcome_type", "rejected_by"],
                f"failed_alternatives[{index}]",
                violations,
            )
            _reject_unexpected_fields(
                alternative,
                {"outcome_type", "rejected_by"},
                f"failed_alternatives[{index}]",
                violations,
            )
            if not _is_enum(alternative.get("outcome_type"), WORLD_OUTCOME_TYPES):
                violations.append(_block("world_adjudication", "invalid_alternative_outcome", f"failed_alternatives[{index}] uses an invalid outcome_type."))
            if alternative.get("outcome_type") == adjudication.get("outcome_type"):
                violations.append(_block("world_adjudication", "duplicate_selected_outcome", f"failed_alternatives[{index}] repeats the selected outcome."))
            if not isinstance(alternative.get("rejected_by"), list) or not alternative.get("rejected_by"):
                violations.append(_block("world_adjudication", "ungrounded_failed_alternative", f"failed_alternatives[{index}].rejected_by must cite constraints."))
        if (
            isinstance(uncertainty_model, dict)
            and uncertainty_model.get("mode") != "deterministic"
            and not failed_alternatives
        ):
            violations.append(_block("world_adjudication", "missing_failed_alternative", "Non-deterministic adjudication must show at least one constrained alternative."))
    events = adjudication.get("committed_events", [])
    if not isinstance(events, list) or not events:
        violations.append(_block("world_adjudication", "missing_committed_event", "Adjudication must commit at least one event."))
    elif len(events) != 1:
        violations.append(
            _block(
                "world_adjudication",
                "multiple_events_per_adjudication",
                "Executable v0.2 permits exactly one CommittedWorldEvent per adjudication so checkpoint counting cannot skip thresholds.",
            )
        )
    else:
        for index, event in enumerate(events):
            if not isinstance(event, dict):
                violations.append(_block("committed_event", "invalid_event", f"committed_events[{index}] must be an object."))
                continue
            _require_security_fields(
                event,
                [
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
                    "authorized_interiority",
                    "spoken_line_records",
                    "causal_basis",
                    "commit_status",
                ],
                f"committed_event[{index}]",
                violations,
            )
            _reject_unexpected_fields(
                event,
                COMMITTED_EVENT_FIELDS,
                f"committed_event[{index}]",
                violations,
            )
            if event.get("message_type") != "CommittedWorldEvent" or event.get("commit_status") != "committed":
                violations.append(_block("committed_event", "invalid_commit_envelope", f"committed_events[{index}] has an invalid message_type or commit_status."))
            if expected_scene_id and event.get("scene_id") != expected_scene_id:
                violations.append(_block("committed_event", "scene_id_mismatch", f"committed_events[{index}] references the wrong scene."))
            if event.get("source_input_type") != expected_input_type or event.get("source_input_ref") != expected_input_ref:
                violations.append(_block("committed_event", "source_input_mismatch", f"committed_events[{index}] references the wrong adjudication input."))
            if "narrative_surface" in event:
                violations.append(_block("committed_event", "world_prose_smuggling", f"committed_events[{index}] may not contain narrative_surface; Narrator owns prose."))
            actors = event.get("actors")
            if not isinstance(actors, list) or not all(
                isinstance(actor, str) for actor in actors
            ):
                violations.append(_block("committed_event", "invalid_actors", f"committed_events[{index}].actors must be a list."))
            elif character_ids is not None:
                unknown_actors = sorted(
                    actor for actor in actors if actor not in character_ids
                )
                if unknown_actors:
                    violations.append(_block("committed_event", "unknown_actor", f"committed_events[{index}] names unregistered actors: " + ", ".join(unknown_actors)))
            if (
                expected_input_type == "event_proposal"
                and isinstance(expected_input_object, dict)
                and (
                    not isinstance(actors, list)
                    or not actors
                    or actors[0] != expected_input_object.get("actor_id")
                )
            ):
                violations.append(
                    _block(
                        "committed_event",
                        "source_actor_mismatch",
                        f"committed_events[{index}].actors[0] must preserve the approved EventProposal actor_id.",
                    )
                )
            if not isinstance(event.get("causal_basis"), list):
                violations.append(_block("committed_event", "invalid_causal_basis", f"committed_events[{index}].causal_basis must be a list."))
            else:
                required_causal_refs = {
                    str(expected_input_ref),
                    str(adjudication.get("adjudication_id")),
                }
                missing_causal_refs = sorted(
                    required_causal_refs - set(str(ref) for ref in event["causal_basis"])
                )
                if missing_causal_refs:
                    violations.append(_block("committed_event", "incomplete_causal_binding", f"committed_events[{index}] omits required causal refs: " + ", ".join(missing_causal_refs)))
            visibility = event.get("visibility")
            if not isinstance(visibility, dict):
                violations.append(_block("committed_event", "invalid_visibility", f"committed_events[{index}].visibility must be an object."))
            else:
                _require_security_fields(
                    visibility,
                    ["scope", "scope_ref", "observer_refs", "limits"],
                    f"committed_event[{index}].visibility",
                    violations,
                )
                observers = visibility.get("observer_refs")
                if not isinstance(observers, list) or not all(
                    isinstance(observer, str) for observer in observers
                ):
                    violations.append(_block("committed_event", "invalid_observer_refs", f"committed_events[{index}].visibility.observer_refs must be a list."))
                else:
                    if character_ids is not None:
                        unknown_observers = sorted(
                            observer
                            for observer in observers
                            if observer not in character_ids
                        )
                        if unknown_observers:
                            violations.append(_block("committed_event", "unknown_observer", f"committed_events[{index}] names unregistered observers: " + ", ".join(unknown_observers)))
                    scope = visibility.get("scope")
                    scope_ref = visibility.get("scope_ref")
                    if not _is_enum(scope, WORLD_EVENT_VISIBILITY_SCOPES):
                        violations.append(_block("committed_event", "invalid_visibility_scope", f"committed_events[{index}] uses an undeclared visibility scope."))
                    if not isinstance(scope_ref, str) or not scope_ref:
                        violations.append(_block("committed_event", "invalid_visibility_scope_ref", f"committed_events[{index}] requires a non-empty string scope_ref."))
                    if _is_enum(scope, DIRECT_OBSERVER_SCOPES) and not observers:
                        violations.append(_block("committed_event", "missing_direct_observers", f"committed_events[{index}] direct visibility requires explicit observers."))
                    if scope == "private_self":
                        primary_actor = actors[0] if isinstance(actors, list) and actors else None
                        if (
                            not isinstance(primary_actor, str)
                            or observers != [primary_actor]
                            or scope_ref != primary_actor
                        ):
                            violations.append(_block("committed_event", "private_self_owner_mismatch", f"committed_events[{index}] private_self visibility must bind exactly to actors[0]."))
                    if scope == "scene_pair":
                        participants = scene_participant_ids
                        if (
                            not isinstance(participants, list)
                            or len(observers) != 2
                            or len(set(observers)) != 2
                            or any(observer not in participants for observer in observers)
                            or (
                                isinstance(actors, list)
                                and any(actor not in observers for actor in actors)
                            )
                        ):
                            violations.append(_block("committed_event", "invalid_scene_pair", f"committed_events[{index}] scene_pair visibility requires exactly two current scene participants and must include every actor."))
                    if scope == "system_restricted" and observers:
                        violations.append(_block("committed_event", "restricted_event_has_character_observers", f"committed_events[{index}] system_restricted visibility cannot name Character observers."))
                    if scope == "scene_public" and scope_ref != expected_scene_id:
                        violations.append(_block("committed_event", "scene_scope_ref_mismatch", f"committed_events[{index}] scene_public visibility must bind to the current scene id."))
                    if scope == "scene_public":
                        participants = scene_participant_ids
                        if not isinstance(participants, list) or not participants:
                            violations.append(_block("committed_event", "missing_scene_participant_registry", f"committed_events[{index}] scene_public visibility requires an explicit participant registry."))
                        elif any(observer not in participants for observer in observers):
                            violations.append(_block("committed_event", "scene_observer_not_participant", f"committed_events[{index}] names an observer outside the scene participant registry."))
                    if _is_enum(scope, {"local_public", "institution_public", "city_public", "realm_public"}):
                        registry = public_scope_registry or {}
                        entry = registry.get(scope_ref) if isinstance(registry, dict) else None
                        if not isinstance(entry, dict) or entry.get("scope_type") != scope:
                            violations.append(_block("committed_event", "unregistered_public_scope", f"committed_events[{index}] cites an unregistered or mismatched public scope instance."))
                        else:
                            members = entry.get("members")
                            if not isinstance(members, list) or any(
                                observer not in members for observer in observers
                            ):
                                violations.append(
                                    _block(
                                        "committed_event",
                                        "public_observer_not_scope_member",
                                        f"committed_events[{index}] public-scope observers must be registered scope members.",
                                    )
                                )
            interiority = event.get("authorized_interiority")
            if not isinstance(interiority, list):
                violations.append(_block("committed_event", "invalid_authorized_interiority", f"committed_events[{index}].authorized_interiority must be a list."))
            else:
                for inner_index, item in enumerate(interiority):
                    if not isinstance(item, dict):
                        violations.append(_block("committed_event", "invalid_authorized_interiority", f"authorized_interiority[{inner_index}] must be an object."))
                        continue
                    _require_security_fields(
                        item,
                        list(AUTHORIZED_INTERIORITY_FIELDS),
                        f"authorized_interiority[{inner_index}]",
                        violations,
                    )
                    _reject_unexpected_fields(
                        item,
                        AUTHORIZED_INTERIORITY_FIELDS,
                        f"authorized_interiority[{inner_index}]",
                        violations,
                    )
                    if isinstance(event.get("actors"), list) and item.get("subject_id") not in event["actors"]:
                        violations.append(_block("committed_event", "interiority_subject_not_actor", f"authorized_interiority[{inner_index}] names a non-actor subject."))
                violations.extend(
                    _validate_interiority_binding(
                        interiority,
                        expected_input_type,
                        expected_input_object,
                    )
                )
            spoken_lines = event.get("spoken_line_records")
            if not isinstance(spoken_lines, list):
                violations.append(_block("committed_event", "invalid_spoken_line_records", f"committed_events[{index}].spoken_line_records must be a list."))
            else:
                for line_index, line in enumerate(spoken_lines):
                    if not isinstance(line, dict):
                        violations.append(_block("committed_event", "invalid_spoken_line_record", f"spoken_line_records[{line_index}] must be an object."))
                        continue
                    _require_security_fields(
                        line,
                        list(SPOKEN_LINE_COMMON_FIELDS),
                        f"spoken_line_records[{line_index}]",
                        violations,
                    )
                    if not _is_enum(line.get("status"), SPOKEN_LINE_STATUSES):
                        violations.append(_block("committed_event", "invalid_spoken_line_status", f"spoken_line_records[{line_index}] is not committed dialogue."))
                    if isinstance(event.get("actors"), list) and line.get("speaker_id") not in event["actors"]:
                        violations.append(_block("committed_event", "spoken_line_speaker_not_actor", f"spoken_line_records[{line_index}] names a non-actor speaker."))
                    if line.get("status") == "paraphrased" and not line.get("semantic_content"):
                        violations.append(_block("committed_event", "missing_spoken_semantics", f"spoken_line_records[{line_index}] requires semantic_content."))
                    if line.get("status") == "exact_committed" and not line.get("text"):
                        violations.append(_block("committed_event", "missing_exact_spoken_text", f"spoken_line_records[{line_index}] requires exact text."))
                    allowed_line_fields = set(SPOKEN_LINE_COMMON_FIELDS)
                    allowed_line_fields.add("semantic_content" if line.get("status") == "paraphrased" else "text")
                    _reject_unexpected_fields(
                        line,
                        allowed_line_fields,
                        f"spoken_line_records[{line_index}]",
                        violations,
                    )
                violations.extend(
                    _validate_spoken_line_binding(
                        spoken_lines,
                        expected_input_type,
                        expected_input_object,
                    )
                )
    for field in [
        "state_deltas",
        "visibility_results",
        "publication_candidates",
        "canon_reveal_candidates",
    ]:
        collection = adjudication.get(field)
        if not isinstance(collection, list):
            violations.append(
                _block(
                    "world_adjudication",
                    "invalid_collection_type",
                    f"WorldAdjudication `{field}` must be a list.",
                )
            )
        elif not all(isinstance(item, dict) for item in collection):
            violations.append(
                _block(
                    "world_adjudication",
                    "invalid_collection_item",
                    f"Every item in WorldAdjudication `{field}` must be an object.",
                )
                )
    visibility_results = adjudication.get("visibility_results")
    if isinstance(events, list) and isinstance(visibility_results, list):
        event_by_id = {
            event.get("event_id"): event
            for event in events
            if isinstance(event, dict) and event.get("event_id")
        }
        for index, result in enumerate(visibility_results):
            if not isinstance(result, dict):
                continue
            _require_security_fields(
                result,
                [
                    "visibility_result_id",
                    "source_event_id",
                    "scope",
                    "scope_ref",
                    "observer_refs",
                    "limits",
                ],
                f"visibility_results[{index}]",
                violations,
            )
            _reject_unexpected_fields(
                result,
                VISIBILITY_RESULT_FIELDS,
                f"visibility_results[{index}]",
                violations,
            )
            source_event = event_by_id.get(result.get("source_event_id"))
            if not isinstance(source_event, dict):
                violations.append(_block("visibility_result", "unknown_source_event", f"visibility_results[{index}] does not bind to a committed event in this adjudication."))
                continue
            expected_visibility = source_event.get("visibility")
            projected_result = {
                field: result.get(field)
                for field in ["scope", "scope_ref", "observer_refs", "limits"]
            }
            if projected_result != expected_visibility:
                violations.append(_block("visibility_result", "visibility_binding_mismatch", f"visibility_results[{index}] must exactly preserve its committed event visibility."))
    if isinstance(events, list):
        event_ids = {
            str(event.get("event_id"))
            for event in events
            if isinstance(event, dict) and event.get("event_id")
        }
        state_deltas = adjudication.get("state_deltas")
        if isinstance(state_deltas, list):
            for index, delta in enumerate(state_deltas):
                if not isinstance(delta, dict):
                    continue
                _require_security_fields(
                    delta,
                    list(STATE_DELTA_FIELDS),
                    f"state_deltas[{index}]",
                    violations,
                )
                _reject_unexpected_fields(
                    delta,
                    STATE_DELTA_FIELDS,
                    f"state_deltas[{index}]",
                    violations,
                )
                if delta.get("target_layer") != "world_state_ledger":
                    violations.append(_block("state_delta", "illegal_target_layer", "World StateDelta may target only world_state_ledger."))
                based_on = delta.get("based_on")
                if not isinstance(based_on, list) or not event_ids.intersection(
                    str(ref) for ref in based_on
                ):
                    violations.append(_block("state_delta", "unbound_state_delta", f"state_deltas[{index}] must cite a committed event from this adjudication."))
        violations.extend(
            _validate_candidate_collection(
                adjudication.get("publication_candidates"),
                "publication_candidate",
                PUBLICATION_CANDIDATE_FIELDS,
                "publication_candidate_id",
                event_ids,
            )
        )
        violations.extend(
            _validate_candidate_collection(
                adjudication.get("canon_reveal_candidates"),
                "canon_reveal_candidate",
                CANON_REVEAL_CANDIDATE_FIELDS,
                "canon_reveal_candidate_id",
                event_ids,
            )
        )
    return violations


def _validate_candidate_collection(
    candidates: Any,
    kind: str,
    allowed_fields: set[str],
    identifier_field: str,
    event_ids: set[str],
) -> list[dict[str, Any]]:
    if not isinstance(candidates, list):
        return []
    violations: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        if not isinstance(candidate, dict):
            continue
        _require_security_fields(
            candidate,
            list(allowed_fields),
            f"{kind}[{index}]",
            violations,
        )
        _reject_unexpected_fields(
            candidate,
            allowed_fields,
            f"{kind}[{index}]",
            violations,
        )
        if candidate.get("source_event_ref") not in event_ids:
            violations.append(_block(kind, "candidate_source_mismatch", f"{kind}[{index}] must cite a committed event from this adjudication."))
        if not _is_enum(candidate.get("status"), {"pending", "deferred"}):
            violations.append(_block(kind, "invalid_candidate_status", f"{kind}[{index}] cannot claim approval or commitment."))
        if candidate.get("visibility") != "system_restricted":
            violations.append(_block(kind, "unsafe_candidate_visibility", f"{kind}[{index}] must remain system_restricted."))
        based_on = candidate.get("based_on")
        if not isinstance(based_on, list) or candidate.get("source_event_ref") not in based_on:
            violations.append(_block(kind, "unbound_candidate", f"{kind}[{index}].based_on must cite its source event."))
        expiry = candidate.get("expires_after_ticks")
        if not isinstance(expiry, int) or expiry < 1:
            violations.append(_block(kind, "invalid_candidate_expiry", f"{kind}[{index}] requires a positive expires_after_ticks value."))
        if not isinstance(candidate.get(identifier_field), str):
            violations.append(_block(kind, "invalid_candidate_id", f"{kind}[{index}] requires a stable id."))
    return violations


@_fail_closed_validator("character_decision_request")
def validate_decision_request(
    request: dict[str, Any] | None,
    source_tick_id: str | None,
    expected_scene_id: str | None = None,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    if not isinstance(request, dict):
        return [_block("decision_request", "missing_decision_request", "World directive requires CharacterDecisionRequest.")]
    _require_security_fields(
        request,
        [
            "message_type",
            "scene_id",
            "request_id",
            "source_tick_id",
            "target_character_id",
            "agency_question",
            "visible_trigger_refs",
            "response_contract",
            "visibility",
            "authority_basis",
        ],
        "decision_request",
        violations,
    )
    if request.get("message_type") != "CharacterDecisionRequest":
        violations.append(_block("decision_request", "invalid_message_type", "message_type must be CharacterDecisionRequest."))
    if request.get("source_tick_id") != source_tick_id:
        violations.append(_block("decision_request", "source_tick_mismatch", "CharacterDecisionRequest must reference its World tick."))
    if expected_scene_id and request.get("scene_id") != expected_scene_id:
        violations.append(_block("decision_request", "scene_id_mismatch", "CharacterDecisionRequest must remain in the current scene."))
    if request.get("visibility") != "system_restricted":
        violations.append(_block("decision_request", "unsafe_visibility", "CharacterDecisionRequest visibility must be system_restricted."))
    response_contract = request.get("response_contract")
    if not isinstance(response_contract, dict):
        violations.append(_block("decision_request", "invalid_response_contract", "response_contract must be an object."))
    else:
        _require_security_fields(
            response_contract,
            list(RESPONSE_CONTRACT_FIELDS),
            "decision_request.response_contract",
            violations,
        )
        _reject_unexpected_fields(
            response_contract,
            RESPONSE_CONTRACT_FIELDS,
            "decision_request.response_contract",
            violations,
        )
        if response_contract.get("output_type") != "EventProposal":
            violations.append(_block("decision_request", "invalid_response_output_type", "response_contract.output_type must be EventProposal."))
        allowed_action_types = response_contract.get("allowed_action_types")
        if (
            not isinstance(allowed_action_types, list)
            or not allowed_action_types
            or not all(isinstance(item, str) and item in ALLOWED_ACTION_TYPES for item in allowed_action_types)
        ):
            violations.append(_block("decision_request", "invalid_allowed_action_types", "response_contract.allowed_action_types must be a non-empty allowlist of executable action types."))
    if not isinstance(request.get("visible_trigger_refs"), list):
        violations.append(_block("decision_request", "invalid_visible_trigger_refs", "visible_trigger_refs must be a list."))
    if not isinstance(request.get("authority_basis"), list) or not request.get("authority_basis"):
        violations.append(_block("decision_request", "invalid_authority_basis", "authority_basis must be a non-empty list."))
    unexpected_fields = sorted(set(request) - DECISION_REQUEST_FIELDS)
    if unexpected_fields:
        violations.append(
            _block(
                "decision_request",
                "undeclared_decision_request_field",
                "CharacterDecisionRequest contains fields outside the strict projection contract: "
                + ", ".join(unexpected_fields),
            )
        )
    return violations


@_fail_closed_validator("character_decision_request")
def validate_decision_request_grounding(
    request: dict[str, Any] | None,
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
) -> list[dict[str, Any]]:
    if not isinstance(request, dict):
        return []
    target = request.get("target_character_id")
    refs = request.get("visible_trigger_refs")
    if not isinstance(target, str) or not isinstance(refs, list):
        return [
            _block(
                "decision_request_visibility",
                "invalid_visible_trigger_refs",
                "Decision request target and visible_trigger_refs must be structurally valid before grounding checks.",
            )
        ]
    legal_refs = legal_character_trigger_refs(fixture, runtime_state, target)
    illegal_refs = sorted(str(ref) for ref in refs if str(ref) not in legal_refs)
    if illegal_refs:
        return [
            _block(
                "decision_request_visibility",
                "illegal_visible_trigger_ref",
                "CharacterDecisionRequest cites refs not visible to its target: "
                + ", ".join(illegal_refs),
            )
        ]
    return []


@_fail_closed_validator("route_plan")
def validate_route_plan(
    plan: dict[str, Any] | None,
    request: dict[str, Any],
    character_ids: set[str],
    expected_request_sha256: str | None = None,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    if not isinstance(plan, dict):
        return [_block("route_plan", "missing_route_plan", "Router Agent did not return RoutePlan.")]
    _require_security_fields(
        plan,
        [
            "message_type",
            "route_id",
            "request_id",
            "request_sha256",
            "recipient_agent_id",
            "projection_profile",
            "reason",
            "visibility",
            "authority_basis",
            "based_on",
        ],
        "route_plan",
        violations,
    )
    _reject_unexpected_fields(plan, ROUTE_PLAN_FIELDS, "route_plan", violations)
    if plan.get("message_type") != "RoutePlan":
        violations.append(_block("route_plan", "invalid_message_type", "message_type must be RoutePlan."))
    if plan.get("request_id") != request.get("request_id"):
        violations.append(_block("route_plan", "request_id_mismatch", "RoutePlan references the wrong decision request."))
    if plan.get("recipient_agent_id") != request.get("target_character_id"):
        violations.append(_block("route_plan", "recipient_mismatch", "Router may not redirect a World request to another character."))
    if plan.get("recipient_agent_id") not in character_ids:
        violations.append(_block("route_plan", "unknown_character", "RoutePlan recipient is not in the character registry."))
    if plan.get("visibility") != "system_restricted":
        violations.append(_block("route_plan", "unsafe_visibility", "RoutePlan visibility must be system_restricted."))
    if expected_request_sha256 and plan.get("request_sha256") != expected_request_sha256:
        violations.append(_block("route_plan", "request_hash_mismatch", "Router must preserve the exact decision request hash."))
    return violations


@_fail_closed_validator("event_proposal")
def validate_event_proposal(
    proposal: dict[str, Any] | None,
    request: dict[str, Any],
    route_plan: dict[str, Any],
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    if not isinstance(proposal, dict):
        return [_block("event_proposal", "missing_event_proposal", "Character Agent did not return EventProposal.")]
    _require_security_fields(
        proposal,
        [
            "message_type",
            "scene_id",
            "proposal_id",
            "request_id",
            "actor_id",
            "action_type",
            "intent_summary",
            "public_surface",
            "private_intent",
            "desired_effect",
            "disclosure_limits",
            "interiority_grant",
            "visibility_request",
            "visibility",
            "authority_basis",
            "based_on",
        ],
        "event_proposal",
        violations,
    )
    _reject_unexpected_fields(proposal, EVENT_PROPOSAL_FIELDS, "event_proposal", violations)
    if proposal.get("message_type") != "EventProposal":
        violations.append(_block("event_proposal", "invalid_message_type", "message_type must be EventProposal."))
    if proposal.get("request_id") != request.get("request_id"):
        violations.append(_block("event_proposal", "request_id_mismatch", "EventProposal references the wrong CharacterDecisionRequest."))
    if proposal.get("scene_id") != request.get("scene_id"):
        violations.append(_block("event_proposal", "scene_id_mismatch", "EventProposal references the wrong scene."))
    if proposal.get("actor_id") != route_plan.get("recipient_agent_id"):
        violations.append(_block("event_proposal", "actor_identity_mismatch", "Character Agent may propose only for its own actor id."))
    if proposal.get("visibility_request") != "system_restricted":
        violations.append(_block("event_proposal", "unsafe_visibility", "Raw EventProposal must remain system_restricted."))
    if proposal.get("visibility") != "system_restricted":
        violations.append(_block("event_proposal", "unsafe_envelope_visibility", "EventProposal envelope must remain system_restricted."))
    response_contract = request.get("response_contract")
    allowed_action_types = response_contract.get("allowed_action_types") if isinstance(response_contract, dict) else None
    if isinstance(allowed_action_types, list) and proposal.get("action_type") not in allowed_action_types:
        violations.append(_block("event_proposal", "action_type_not_allowed", "EventProposal action_type is outside the CharacterDecisionRequest response contract."))
    for field in ["disclosure_limits", "authority_basis", "based_on"]:
        if not isinstance(proposal.get(field), list):
            violations.append(_block("event_proposal", "invalid_list_field", f"EventProposal `{field}` must be a list."))
    grant = proposal.get("interiority_grant")
    if not isinstance(grant, dict):
        violations.append(_block("event_proposal", "invalid_interiority_grant", "interiority_grant must be an explicit object."))
    else:
        grant_fields = {"grant_status", "source_field", "access_mode", "scope_limit"}
        _require_security_fields(
            grant,
            list(grant_fields),
            "interiority_grant",
            violations,
        )
        _reject_unexpected_fields(grant, grant_fields, "interiority_grant", violations)
        status = grant.get("grant_status")
        if status == "none":
            if grant != {
                "grant_status": "none",
                "source_field": "none",
                "access_mode": "none",
                "scope_limit": "none",
            }:
                violations.append(_block("event_proposal", "invalid_no_interiority_grant", "A none grant must use only none sentinel values."))
        elif status == "authorized":
            if not _is_enum(grant.get("source_field"), {"intent_summary", "private_intent"}):
                violations.append(_block("event_proposal", "invalid_interiority_source", "Authorized interiority may cite only an owner-authored intent field."))
            if not _is_enum(grant.get("access_mode"), {"intent", "self_reported_state"}):
                violations.append(_block("event_proposal", "invalid_interiority_access", "Authorized interiority access_mode is invalid."))
            if grant.get("scope_limit") != "one_beat":
                violations.append(_block("event_proposal", "unbounded_interiority_grant", "Executable v0.2 permits only one_beat interiority grants."))
        else:
            violations.append(_block("event_proposal", "invalid_interiority_grant_status", "interiority_grant.grant_status is invalid."))
    return violations


def _validate_interiority_binding(
    interiority: list[dict[str, Any]],
    expected_input_type: str | None,
    expected_input_object: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if expected_input_type != "event_proposal" or not isinstance(expected_input_object, dict):
        if interiority:
            return [_block("committed_event", "unauthorized_interiority_source", "Only an approved Character EventProposal can authorize interiority.")]
        return []
    grant = expected_input_object.get("interiority_grant")
    if not isinstance(grant, dict) or grant.get("grant_status") != "authorized":
        if interiority:
            return [_block("committed_event", "interiority_without_owner_grant", "World may not author interiority without the Character owner's explicit grant.")]
        return []
    if len(interiority) > 1:
        return [_block("committed_event", "interiority_grant_overuse", "One EventProposal may authorize at most one interiority item.")]
    if not interiority:
        return []
    item = interiority[0]
    source_field = grant.get("source_field")
    source_content = expected_input_object.get(source_field)
    expected_hash = hashlib.sha256(stable_json(source_content).encode("utf-8")).hexdigest()
    expected = {
        "subject_id": expected_input_object.get("actor_id"),
        "access_mode": grant.get("access_mode"),
        "content": source_content,
        "scope_limit": grant.get("scope_limit"),
        "source_proposal_id": expected_input_object.get("proposal_id"),
        "source_field": source_field,
        "source_sha256": expected_hash,
    }
    mismatches = sorted(
        field for field, value in expected.items() if item.get(field) != value
    )
    if mismatches:
        return [_block("committed_event", "interiority_binding_mismatch", "World interiority does not exactly preserve the owner grant: " + ", ".join(mismatches))]
    if not isinstance(item.get("authority_basis"), list) or expected_input_object.get("proposal_id") not in item["authority_basis"]:
        return [_block("committed_event", "invalid_interiority_authority_basis", "authorized_interiority.authority_basis must cite the granting EventProposal.")]
    return []


def _validate_spoken_line_binding(
    spoken_lines: list[dict[str, Any]],
    expected_input_type: str | None,
    expected_input_object: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not spoken_lines:
        if (
            expected_input_type == "event_proposal"
            and isinstance(expected_input_object, dict)
            and expected_input_object.get("action_type") == "speech"
        ):
            return [
                _block(
                    "committed_event",
                    "missing_source_bound_spoken_line",
                    "A speech EventProposal must commit one source-bound spoken_line_record.",
                )
            ]
        return []
    if expected_input_type != "event_proposal" or not isinstance(expected_input_object, dict):
        return [_block("committed_event", "unauthorized_spoken_line_source", "Only an approved Character EventProposal can authorize committed speech.")]
    if expected_input_object.get("action_type") != "speech":
        return [_block("committed_event", "speech_not_proposed", "World may not commit speech for a non-speech EventProposal.")]
    if len(spoken_lines) > 1:
        return [_block("committed_event", "spoken_line_overproduction", "Executable v0.2 permits at most one committed speech record per EventProposal.")]

    line = spoken_lines[0]
    source_content = expected_input_object.get("public_surface")
    expected_hash = hashlib.sha256(stable_json(source_content).encode("utf-8")).hexdigest()
    expected = {
        "speaker_id": expected_input_object.get("actor_id"),
        "source_proposal_id": expected_input_object.get("proposal_id"),
        "source_field": "public_surface",
        "source_sha256": expected_hash,
    }
    mismatches = sorted(field for field, value in expected.items() if line.get(field) != value)
    if mismatches:
        return [_block("committed_event", "spoken_line_binding_mismatch", "World speech does not preserve the Character proposal binding: " + ", ".join(mismatches))]
    if line.get("status") == "paraphrased" and line.get("semantic_content") != source_content:
        return [_block("committed_event", "spoken_semantics_mismatch", "Paraphrased committed speech must copy the Character-owned public_surface semantics exactly.")]
    if line.get("status") == "exact_committed" and line.get("text") != source_content:
        return [_block("committed_event", "exact_spoken_text_mismatch", "Exact committed speech must copy the Character-owned public_surface text exactly.")]
    return []


@_fail_closed_validator("authority_review")
def validate_authority_review(
    review: dict[str, Any] | None,
    *,
    subject_type: str,
    subject_ref: str | None,
    subject_sha256: str | None = None,
    subject: dict[str, Any] | None = None,
    expected_run_nonce: str | None = None,
    expected_review_context_sha256: str | None = None,
    review_context: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    if not isinstance(review, dict):
        return [_block("authority_review", "missing_authority_review", "Authority Judge did not return AuthorityReview.")]
    _require_security_fields(
        review,
        [
            "message_type",
            "review_id",
            "subject_type",
            "subject_ref",
            "subject_sha256",
            "verdict",
            "findings",
            "required_repairs",
            "authority_basis",
            "reviewed_fields",
            "visibility",
            "run_nonce",
            "review_context_sha256",
        ],
        "authority_review",
        violations,
    )
    _reject_unexpected_fields(review, AUTHORITY_REVIEW_FIELDS, "authority_review", violations)
    if review.get("message_type") != "AuthorityReview":
        violations.append(_block("authority_review", "invalid_message_type", "message_type must be AuthorityReview."))
    if review.get("subject_type") != subject_type or review.get("subject_ref") != subject_ref:
        violations.append(_block("authority_review", "subject_mismatch", "AuthorityReview references the wrong subject."))
    if subject_sha256 and review.get("subject_sha256") != subject_sha256:
        violations.append(_block("authority_review", "subject_hash_mismatch", "AuthorityReview did not preserve the reviewed subject hash."))
    if expected_run_nonce and review.get("run_nonce") != expected_run_nonce:
        violations.append(_block("authority_review", "run_nonce_mismatch", "AuthorityReview is not bound to this runtime execution."))
    if (
        expected_review_context_sha256
        and review.get("review_context_sha256") != expected_review_context_sha256
    ):
        violations.append(_block("authority_review", "review_context_hash_mismatch", "AuthorityReview is not bound to the exact audit context supplied to Judge."))
    if not _is_enum(review.get("verdict"), AUTHORITY_VERDICTS):
        violations.append(_block("authority_review", "invalid_verdict", "AuthorityReview verdict is invalid."))
    if "rewritten_subject" in review or "replacement_content" in review:
        violations.append(_block("authority_review", "judge_rewrite_attempt", "Authority Judge may not return rewritten literary content."))
    if review.get("visibility") != "system_restricted":
        violations.append(_block("authority_review", "unsafe_visibility", "AuthorityReview must remain system_restricted."))
    for field in ["findings", "required_repairs", "authority_basis", "reviewed_fields"]:
        if field in review and not isinstance(review.get(field), list):
            violations.append(_block("authority_review", "invalid_list_field", f"AuthorityReview `{field}` must be a list."))
    authority_basis = review.get("authority_basis")
    if not isinstance(authority_basis, list) or not authority_basis or not all(
        isinstance(item, str) and item.strip() for item in authority_basis
    ):
        violations.append(_block("authority_review", "missing_authority_basis", "AuthorityReview must cite at least one non-empty authority or grounding basis."))
    reviewed_fields = review.get("reviewed_fields")
    if not isinstance(reviewed_fields, list) or not reviewed_fields or not all(
        isinstance(item, str) and item.strip() for item in reviewed_fields
    ):
        violations.append(_block("authority_review", "missing_review_coverage", "AuthorityReview must name the subject fields it actually checked."))
    else:
        unknown_fields = sorted(
            field
            for field in set(reviewed_fields)
            if not _reviewed_field_path_exists(
                subject or {}, review_context or {}, field
            )
        )
        if unknown_fields:
            violations.append(_block("authority_review", "unknown_reviewed_field", "AuthorityReview claims fields absent from the reviewed subject: " + ", ".join(unknown_fields)))
        if _is_enum(review.get("verdict"), {"allow", "warning"}):
            required_fields = AUTHORITY_REQUIRED_REVIEW_FIELDS.get(subject_type, set())
            covered_subject_fields = _covered_subject_top_level_fields(
                subject or {}, reviewed_fields
            )
            missing_fields = sorted(required_fields - covered_subject_fields)
            if missing_fields:
                violations.append(_block("authority_review", "incomplete_review_coverage", "AuthorityReview cannot approve before checking all critical fields: " + ", ".join(missing_fields)))
    if review.get("verdict") == "repair_required" and isinstance(review.get("required_repairs"), list):
        if not review["required_repairs"]:
            violations.append(_block("authority_review", "missing_repair_instruction", "repair_required must provide at least one origin-safe repair code."))
        for index, repair in enumerate(review["required_repairs"]):
            if not isinstance(repair, dict):
                violations.append(
                    _block(
                        "authority_review",
                        "unsafe_repair_instruction",
                        f"required_repairs[{index}] must be a code-only object, not free text.",
                    )
                )
                continue
            if set(repair) != {"repair_code", "field_path"}:
                violations.append(
                    _block(
                        "authority_review",
                        "unsafe_repair_instruction",
                        f"required_repairs[{index}] may contain only repair_code and field_path.",
                    )
                )
            if not _is_enum(repair.get("repair_code"), ORIGIN_SAFE_REPAIR_CODES):
                violations.append(
                    _block(
                        "authority_review",
                        "unknown_repair_code",
                        f"required_repairs[{index}] uses an unapproved origin-safe repair code.",
                    )
                )
            field_path = repair.get("field_path")
            if not isinstance(field_path, str) or not field_path:
                violations.append(_block("authority_review", "invalid_repair_field_path", f"required_repairs[{index}].field_path must be a non-empty string."))
            else:
                normalized_path = (
                    field_path[len("subject.") :]
                    if field_path.startswith("subject.")
                    else field_path
                )
                if not _subject_field_path_exists(subject or {}, normalized_path):
                    violations.append(
                        _block(
                            "authority_review",
                            "repair_field_outside_subject",
                            f"required_repairs[{index}].field_path must resolve inside the reviewed subject.",
                        )
                    )
    elif review.get("required_repairs") not in (None, []):
        violations.append(_block("authority_review", "unexpected_repair_instruction", "required_repairs must be empty unless verdict is repair_required."))
    if subject_type == "narration":
        claim_map = review.get("claim_map")
        prose = (subject or {}).get("prose", "")
        checkpoint_id = str((subject or {}).get("source_checkpoint_id", "unknown"))
        expected_units = build_narration_claim_units(prose, checkpoint_id)
        supplied_units = (subject or {}).get("claim_units")
        if supplied_units != expected_units:
            violations.append(_block("narration_claim_map", "claim_unit_integrity_mismatch", "Narration subject claim_units must be the exact deterministic segmentation of prose."))
        if not isinstance(claim_map, list) or not claim_map:
            violations.append(_block("narration_claim_map", "missing_claim_map", "Narration review requires a non-empty claim_map."))
        else:
            allowed_source_refs = set((subject or {}).get("source_event_refs", []))
            claim_fields = {
                "claim_id", "claim_sha256", "claim_text", "claim_type", "source_refs", "certainty",
                "visibility_scope", "grounding_status",
            }
            expected_by_id = {unit["claim_id"]: unit for unit in expected_units}
            supplied_ids = [
                claim.get("claim_id")
                for claim in claim_map
                if isinstance(claim, dict)
            ]
            if len(supplied_ids) != len(set(supplied_ids)):
                violations.append(_block("narration_claim_map", "duplicate_claim_id", "Narration claim_map contains duplicate claim ids."))
            missing_claim_ids = sorted(
                set(expected_by_id) - set(supplied_ids), key=str
            )
            unexpected_claim_ids = sorted(
                set(supplied_ids) - set(expected_by_id), key=str
            )
            if missing_claim_ids:
                violations.append(_block("narration_claim_map", "incomplete_prose_coverage", "Narration claim_map omits prose units: " + ", ".join(missing_claim_ids)))
            if unexpected_claim_ids:
                violations.append(_block("narration_claim_map", "unknown_claim_unit", "Narration claim_map invents unknown prose units: " + ", ".join(str(item) for item in unexpected_claim_ids)))
            for index, claim in enumerate(claim_map):
                if not isinstance(claim, dict):
                    violations.append(_block("narration_claim_map", "invalid_claim", f"claim_map[{index}] must be an object."))
                    continue
                _require_security_fields(
                    claim,
                    list(claim_fields),
                    f"claim_map[{index}]",
                    violations,
                )
                _reject_unexpected_fields(
                    claim,
                    claim_fields,
                    f"claim_map[{index}]",
                    violations,
                )
                expected_unit = expected_by_id.get(claim.get("claim_id"))
                if expected_unit and (
                    claim.get("claim_text") != expected_unit["claim_text"]
                    or claim.get("claim_sha256") != expected_unit["claim_sha256"]
                ):
                    violations.append(_block("narration_claim_map", "claim_text_binding_mismatch", f"claim_map[{index}] does not preserve the exact prose unit text and hash."))
                source_refs = claim.get("source_refs")
                if not isinstance(source_refs, list) or not source_refs:
                    violations.append(_block("narration_claim_map", "invalid_claim_source_refs", f"claim_map[{index}].source_refs must be a non-empty list."))
                else:
                    illegal_refs = sorted(str(ref) for ref in source_refs if ref not in allowed_source_refs)
                    if illegal_refs:
                        violations.append(_block("narration_claim_map", "claim_source_mismatch", f"claim_map[{index}] cites sources outside NarrationCheckpoint: " + ", ".join(illegal_refs)))
                if not _is_enum(claim.get("grounding_status"), {"supported", "unsupported", "overclaim"}):
                    violations.append(_block("narration_claim_map", "invalid_grounding_status", f"claim_map[{index}] has an invalid grounding_status."))
                elif claim.get("grounding_status") != "supported" and _is_enum(review.get("verdict"), {"allow", "warning"}):
                    violations.append(_block("narration_claim_map", "unsafe_narration_approval", "Judge may not approve narration containing unsupported or overclaimed claims."))
    elif review.get("claim_map") not in (None, []):
        violations.append(_block("authority_review", "unexpected_claim_map", "claim_map is legal only for narration review."))
    if review.get("verdict") == "warning":
        violations.append(_warning("authority_review", "authority_warning", "Authority Judge returned a warning."))
    if review.get("verdict") == "repair_required":
        violations.append(_repair("authority_review", "authority_repair_required", "Subject must be retried by its originating Agent before continuing."))
    if review.get("verdict") == "block":
        violations.append(_block("authority_review", "authority_block", "Authority Judge blocked the subject."))
    return violations


@_fail_closed_validator("plot_pulse")
def validate_plot_pulse(
    pulse: dict[str, Any] | None,
    pressure_ledger: list[dict[str, Any]] | None = None,
    option_topology: dict[str, Any] | None = None,
    expected_scene_id: str | None = None,
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    if not isinstance(pulse, dict):
        return [_block("plot_pulse", "missing_plot_pulse", "Plot Agent did not return PlotPulse.")]
    _require_security_fields(
        pulse,
        [
            "message_type",
            "scene_id",
            "pulse_id",
            "pressure_kind",
            "scope",
            "duration",
            "affected_options",
            "non_forcing_clause",
            "world_fact_dependency",
            "forbidden_outcomes",
            "visibility",
            "budget_cost",
            "option_topology_check",
            "authority_basis",
            "based_on",
        ],
        "plot_pulse",
        violations,
    )
    _reject_unexpected_fields(pulse, PLOT_PULSE_FIELDS, "plot_pulse", violations)
    if pulse.get("message_type") != "PlotPulse":
        violations.append(_block("plot_pulse", "invalid_message_type", "message_type must be PlotPulse."))
    if expected_scene_id and pulse.get("scene_id") != expected_scene_id:
        violations.append(_block("plot_pulse", "scene_id_mismatch", "PlotPulse must remain in the current scene."))
    if not _is_enum(pulse.get("pressure_kind"), PLOT_PRESSURE_KINDS):
        violations.append(_block("plot_pulse", "invalid_pressure_kind", "PlotPulse pressure_kind is outside the executable allowlist."))
    if not _is_enum(pulse.get("scope"), PLOT_SCOPES):
        violations.append(_block("plot_pulse", "invalid_pressure_scope", "PlotPulse scope is outside the executable allowlist."))
    if not _is_enum(pulse.get("duration"), PLOT_DURATIONS):
        violations.append(_block("plot_pulse", "invalid_pressure_duration", "PlotPulse duration is outside the executable allowlist."))
    if pulse.get("visibility") != "system_restricted":
        violations.append(_block("plot_pulse", "unsafe_visibility", "PlotPulse must remain system_restricted until World translation."))
    for field in ["affected_options", "world_fact_dependency", "forbidden_outcomes", "authority_basis", "based_on"]:
        if not isinstance(pulse.get(field), list):
            violations.append(_block("plot_pulse", "invalid_list_field", f"PlotPulse `{field}` must be a list."))
    budget = pulse.get("budget_cost")
    if not isinstance(budget, dict):
        violations.append(_block("plot_pulse", "invalid_budget_cost", "PlotPulse budget_cost must be an object."))
    elif budget.get("agency_risk") == "high" and not budget.get("relief_available"):
        violations.append(_block("plot_pulse", "agency_risk_without_relief", "High agency risk requires a relief path."))
    elif isinstance(budget, dict):
        _require_security_fields(
            budget,
            ["intensity", "novelty", "stacking_count", "relief_available", "agency_risk"],
            "plot_budget",
            violations,
        )
        previous_same_kind = sum(
            1
            for entry in pressure_ledger or []
            if isinstance(entry, dict)
            and isinstance(entry.get("original_plot_pulse"), dict)
            and entry["original_plot_pulse"].get("pressure_kind") == pulse.get("pressure_kind")
        )
        if budget.get("stacking_count") != previous_same_kind + 1:
            violations.append(_block("plot_budget", "stacking_count_mismatch", "PlotPulse stacking_count must equal prior same-kind pulses plus one."))
        intensity_weights = {"low": 1, "medium": 2, "high": 3}
        current_intensity = intensity_weights.get(str(budget.get("intensity")))
        if current_intensity is None:
            violations.append(_block("plot_budget", "invalid_intensity", "PlotPulse intensity must be low, medium, or high."))
        else:
            cumulative_intensity = current_intensity + sum(
                intensity_weights.get(
                    str(entry.get("original_plot_pulse", {}).get("budget_cost", {}).get("intensity")),
                    0,
                )
                for entry in pressure_ledger or []
                if isinstance(entry, dict)
            )
            if cumulative_intensity > 6:
                violations.append(_block("plot_budget", "cumulative_pressure_budget_exceeded", "Scene-level cumulative pressure intensity exceeds the executable MVP budget."))
    topology = pulse.get("option_topology_check")
    if not isinstance(topology, dict):
        violations.append(_block("plot_option_topology", "missing_option_topology_check", "PlotPulse requires an option_topology_check object."))
    else:
        _require_security_fields(
            topology,
            [
                "meaningful_option_count_before",
                "meaningful_option_count_after",
                "refusal_path_preserved",
                "non_plot_compliant_path_preserved",
                "converges_on_single_outcome",
            ],
            "plot_option_topology",
            violations,
        )
        before = topology.get("meaningful_option_count_before")
        after = topology.get("meaningful_option_count_after")
        if not isinstance(before, int) or not isinstance(after, int):
            violations.append(_block("plot_option_topology", "invalid_option_count", "Option topology counts must be integers."))
        elif after < 2:
            violations.append(_block("plot_option_topology", "fake_agency", "Pressure must leave at least two meaningful options."))
        if topology.get("refusal_path_preserved") is not True:
            violations.append(_block("plot_option_topology", "missing_refusal_path", "Pressure must preserve a refusal path."))
        if topology.get("non_plot_compliant_path_preserved") is not True:
            violations.append(_block("plot_option_topology", "missing_non_plot_path", "Pressure must preserve a world-legal non-plot-compliant path."))
        if topology.get("converges_on_single_outcome") is not False:
            violations.append(_block("plot_option_topology", "single_outcome_convergence", "Pressure may not converge all meaningful options on one outcome."))
        if option_topology and isinstance(before, int):
            registered_options = sum(
                len(options)
                for options in option_topology.values()
                if isinstance(options, list)
            )
            if before > registered_options:
                violations.append(_block("plot_option_topology", "option_count_exceeds_registry", "Plot claims more pre-pressure options than the registered option topology contains."))
    return violations


def is_review_approved(review: dict[str, Any] | None) -> bool:
    return isinstance(review, dict) and _is_enum(review.get("verdict"), {"allow", "warning"})


def review_requires_repair(review: dict[str, Any] | None) -> bool:
    return isinstance(review, dict) and review.get("verdict") == "repair_required"


def has_block(violations: list[dict[str, Any]]) -> bool:
    return any(item.get("severity") == "block" for item in violations)


def _require_security_fields(
    obj: dict[str, Any],
    fields: list[str],
    kind: str,
    violations: list[dict[str, Any]],
) -> None:
    for field in fields:
        if field not in obj or obj.get(field) is None or obj.get(field) == "":
            violations.append(
                _block(
                    kind,
                    "missing_security_critical_field",
                    f"Missing security-critical field `{field}`; object is quarantined, not inferred.",
                )
            )


def _reject_unexpected_fields(
    obj: dict[str, Any],
    allowed_fields: set[str],
    kind: str,
    violations: list[dict[str, Any]],
) -> None:
    unexpected = sorted(set(obj) - allowed_fields)
    if unexpected:
        violations.append(
            _block(
                kind,
                "undeclared_field",
                "Object contains fields outside its executable contract: " + ", ".join(unexpected),
            )
        )


def _subject_field_path_exists(subject: Any, path: str) -> bool:
    if not isinstance(path, str) or not path:
        return False
    tokens: list[str | int | None] = []
    matched_text = ""
    for match in re.finditer(r"([^.\[\]]+)|\[(\d*)\]", path):
        matched_text += match.group(0)
        if match.group(2) is not None:
            tokens.append(int(match.group(2)) if match.group(2) else None)
        else:
            tokens.append(match.group(1))
    if matched_text != path.replace(".", ""):
        return False
    current_values = [subject]
    for token in tokens:
        next_values: list[Any] = []
        for current in current_values:
            if isinstance(token, str) and isinstance(current, dict) and token in current:
                next_values.append(current[token])
            elif (
                isinstance(token, int)
                and isinstance(current, list)
                and 0 <= token < len(current)
            ):
                next_values.append(current[token])
            elif token is None and isinstance(current, list) and current:
                next_values.extend(current)
            else:
                return False
        current_values = next_values
    return bool(tokens) and bool(current_values)


def _reviewed_field_path_exists(
    subject: dict[str, Any], review_context: dict[str, Any], path: str
) -> bool:
    if _subject_field_path_exists(subject, path):
        return True
    if path.startswith("subject."):
        return _subject_field_path_exists(subject, path[len("subject.") :])
    if path.startswith(("source_context.", "global_audit_context.")):
        return _subject_field_path_exists(review_context, path)
    return False


def _covered_subject_top_level_fields(
    subject: dict[str, Any], reviewed_fields: list[str]
) -> set[str]:
    covered: set[str] = set()
    for path in reviewed_fields:
        normalized = path[len("subject.") :] if path.startswith("subject.") else path
        if not _subject_field_path_exists(subject, normalized):
            continue
        top_level = re.split(r"[.\[]", normalized, maxsplit=1)[0]
        if top_level:
            covered.add(top_level)
    return covered


def _block(kind: str, code: str, message: str) -> dict[str, Any]:
    return {"severity": "block", "kind": kind, "code": code, "message": message}


def _warning(kind: str, code: str, message: str) -> dict[str, Any]:
    return {"severity": "warning", "kind": kind, "code": code, "message": message}


def _repair(kind: str, code: str, message: str) -> dict[str, Any]:
    return {"severity": "repair_required", "kind": kind, "code": code, "message": message}
