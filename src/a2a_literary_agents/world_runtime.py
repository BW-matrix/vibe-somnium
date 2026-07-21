"""World-driven multi-agent runtime.

World controls simulation ticks. The Runtime Kernel only routes projected
contexts, validates interfaces, records audit evidence, and persists results.
"""

from __future__ import annotations

import hashlib
import json
import os
import secrets
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .config import RunnerConfig
from .json_util import load_json_file, stable_json, write_json_file
from .llm import AgentProvider, build_provider
from .path_safety import is_safe_path_id, resolve_run_directory
from .prompts import build_prompt
from .report import write_report
from .runtime_validation import (
    build_narration_claim_units,
    has_block,
    is_protocol_id,
    is_review_approved,
    review_requires_repair,
    validate_authority_review,
    validate_decision_request_grounding,
    validate_event_proposal,
    validate_plot_pulse,
    validate_route_plan,
    validate_syntax_repair_conservation,
    validate_world_fixture,
    validate_world_tick,
)
from .token_usage import summarize_token_usage
from .validation import validate_narration
from .visibility import event_directly_observed_by
from .world_projection import (
    authority_review_context,
    character_decision_context,
    character_repair_context,
    narration_checkpoint_context,
    narration_repair_context,
    output_syntax_repair_context,
    plot_pulse_context,
    router_context,
    validate_projection_manifest,
    world_control_context,
    world_repair_context,
)


WORLD_ORIGIN_REPAIRABLE_CODES = {
    "adjudication_input_not_consumed",
    "approved_proposal_not_consumed",
    "incomplete_causal_binding",
    "invalid_alternative_outcome",
    "invalid_collection_item",
    "missing_committed_event",
    "scene_observer_not_participant",
    "visibility_binding_mismatch",
    "unbound_state_delta",
    "unknown_actor",
    "unknown_observer",
}

MAX_OUTPUT_SYNTAX_REPAIR_ATTEMPTS = 1


@dataclass(frozen=True)
class ValidatedProjection:
    """A sealed context whose validation and dispatch recipient are inseparable."""

    role: str
    instance_id: str
    stage: str
    canonical_context_json: str
    context_sha256: str
    manifest_id: str
    contract_id: str


def run_world_trace(fixture_path: str, out_dir: str, config: RunnerConfig) -> dict[str, Any]:
    fixture = load_json_file(fixture_path)
    created_at = datetime.now(timezone.utc).isoformat()
    run_id = _run_id(created_at)
    run_nonce = secrets.token_hex(16)
    trace_id = fixture.get("trace_id") if isinstance(fixture.get("trace_id"), str) else "invalid_fixture"
    fixture_violations = validate_world_fixture(fixture)
    safe_trace_id = trace_id if is_safe_path_id(trace_id) else "quarantined_fixture"
    run_dir = resolve_run_directory(out_dir, safe_trace_id, run_id)
    os.makedirs(run_dir, exist_ok=True)
    provider = build_provider(config)

    checkpoint_policy = _checkpoint_policy(fixture)
    runtime_state: dict[str, Any] = {
        "tick_index": 0,
        "committed_world_events": [],
        "world_state_delta_ledger": [],
        "visibility_result_ledger": [],
        "publication_candidates": [],
        "canon_reveal_candidates": [],
        "consumed_scheduled_world_event_refs": [],
        "pressure_ledger": deepcopy(fixture.get("pressure_history", [])),
        "option_topology": deepcopy(fixture.get("option_topology", {})),
        "checkpoint_policy": checkpoint_policy,
        "last_plot_event_index": 0,
        "last_narrated_event_index": 0,
        "used_protocol_ids": [],
    }
    initial_runtime_state = deepcopy(runtime_state)
    trace = _new_trace(
        fixture, fixture_path, config, created_at, run_id, run_nonce, checkpoint_policy
    )
    _record_validation(trace, "world_fixture", fixture_violations)
    if has_block(fixture_violations):
        trace["runtime_status"] = "quarantined_world_fixture"
    pending_approved_proposal: dict[str, Any] | None = None
    pending_plot_pulse: dict[str, Any] | None = None
    raw_max_world_ticks = fixture.get("max_world_ticks", 8)
    max_world_ticks = raw_max_world_ticks if isinstance(raw_max_world_ticks, int) and not isinstance(raw_max_world_ticks, bool) else 0
    finished = False

    while not has_block(fixture_violations) and runtime_state["tick_index"] < max_world_ticks:
        tick_index = runtime_state["tick_index"]
        world_ctx, world_manifest, world_contract = world_control_context(
            fixture,
            runtime_state,
            pending_approved_proposal,
            pending_plot_pulse,
        )
        world_projection = _record_projection(
            trace,
            world_ctx,
            world_manifest,
            world_contract,
            f"world_tick_{tick_index}",
            expected_projection_type="WorldControlContext",
            expected_role="world",
            expected_instance_id="world_controller",
        )
        if world_projection is None:
            trace["runtime_status"] = "quarantined_projection"
            break
        world_call_context = json.loads(world_projection.canonical_context_json)
        world_tick: dict[str, Any] | None = None
        violations: list[dict[str, Any]] = []
        max_world_repairs = fixture.get("max_world_repair_attempts", 1)
        for attempt_index in range(max_world_repairs + 1):
            world_stage = (
                f"world_tick_{tick_index}"
                if attempt_index == 0
                else f"world_repair_tick_{tick_index}_{attempt_index}"
            )
            world_output = _call_agent(
                provider,
                projection=world_projection,
                fixture=fixture,
                trace=trace,
                config=config,
            )
            world_tick = _payload(world_output, "world_tick_result")
            violations = validate_world_tick(
                world_tick,
                expected_tick_index=tick_index,
                pending_approved_proposal=pending_approved_proposal,
                pending_plot_pulse=pending_plot_pulse,
                existing_world_condition_refs=_world_condition_refs(fixture, runtime_state),
                scheduled_world_event_hashes=_scheduled_world_event_hashes(fixture, runtime_state),
                expected_scene_id=fixture["scene_id"],
                character_ids=set(fixture.get("characters", {})),
                public_scope_registry=fixture.get("public_scope_registry", {}),
                scene_participant_ids=fixture.get("scene_participant_ids"),
            )
            if (
                world_tick
                and world_tick.get("next_directive", {}).get("directive_type")
                == "request_character_decision"
            ):
                grounding_state = runtime_state
                current_adjudication = world_tick.get("adjudication")
                if isinstance(current_adjudication, dict):
                    grounding_state = deepcopy(runtime_state)
                    grounding_state["committed_world_events"] = [
                        *runtime_state.get("committed_world_events", []),
                        *current_adjudication.get("committed_events", []),
                    ]
                violations.extend(
                    validate_decision_request_grounding(
                        world_tick["next_directive"].get("decision_request"),
                        fixture,
                        grounding_state,
                    )
                )
            if not has_block(violations) and world_tick:
                violations.extend(
                    _claim_protocol_ids(
                        runtime_state,
                        _world_tick_protocol_ids(world_tick),
                        "world_tick",
                    )
                )
            if not has_block(violations):
                _record_validation(trace, world_stage, violations)
                break
            if (
                world_tick
                and attempt_index < max_world_repairs
                and _world_origin_repairable(violations)
            ):
                _record_validation(
                    trace,
                    f"{world_stage}_rejected",
                    _as_repair_required(violations),
                )
                repair_ctx, repair_manifest, repair_contract = world_repair_context(
                    world_ctx,
                    world_tick,
                    violations,
                    attempt_index + 1,
                )
                repair_projection = _record_projection(
                    trace,
                    repair_ctx,
                    repair_manifest,
                    repair_contract,
                    f"world_repair_tick_{tick_index}_{attempt_index + 1}",
                    expected_projection_type="WorldRepairContextPacket",
                    expected_role="world",
                    expected_instance_id="world_controller",
                )
                if repair_projection is None:
                    trace["runtime_status"] = "quarantined_projection"
                    break
                trace["repair_attempts"].append(
                    {
                        "origin_agent_id": "world_controller",
                        "request_id": f"world_tick_{tick_index}",
                        "rejected_subject_ref": world_tick.get("tick_id"),
                        "authority_review_ref": None,
                        "attempt_index": attempt_index + 1,
                        "repair_codes": [item.get("code") for item in violations],
                    }
                )
                world_projection = repair_projection
                world_call_context = json.loads(
                    world_projection.canonical_context_json
                )
                continue
            _record_validation(trace, world_stage, violations)
            trace["runtime_status"] = "quarantined_world_tick"
            break
        if trace.get("runtime_status") in {
            "quarantined_projection",
            "quarantined_world_tick",
        }:
            break

        assert world_tick is not None
        trace["world_ticks"].append(deepcopy(world_tick))
        adjudication = world_tick.get("adjudication")
        adjudication_review: dict[str, Any] | None = None
        if isinstance(adjudication, dict) and adjudication:
            adjudication_review = _run_authority_review(
                fixture,
                runtime_state,
                provider,
                trace,
                config,
                subject_type="world_adjudication",
                subject=adjudication,
                subject_ref=adjudication["adjudication_id"],
                source_context=world_call_context,
                stage=f"authority_world_adjudication_{adjudication['adjudication_id']}",
            )
            if not is_review_approved(adjudication_review):
                trace["runtime_status"] = "quarantined_world_adjudication"
                break
        disposition = world_tick.get("plot_pulse_disposition")
        if pending_plot_pulse is not None and isinstance(disposition, dict):
            disposition_review = _run_authority_review(
                fixture,
                runtime_state,
                provider,
                trace,
                config,
                subject_type="plot_pulse_disposition",
                subject=disposition,
                subject_ref=disposition["pulse_id"],
                source_context=world_call_context,
                stage=f"authority_plot_disposition_{disposition['pulse_id']}",
            )
            if not is_review_approved(disposition_review):
                trace["runtime_status"] = "quarantined_plot_pulse_disposition"
                break
        if isinstance(adjudication, dict) and adjudication:
            _commit_adjudication(runtime_state, trace, adjudication)
            if adjudication.get("input_type") == "event_proposal":
                pending_approved_proposal = None
            elif adjudication.get("input_type") == "scheduled_world_event":
                runtime_state["consumed_scheduled_world_event_refs"].append(
                    adjudication["input_ref"]
                )
        if pending_plot_pulse is not None:
            trace["plot_pulse_dispositions"].append(
                deepcopy(world_tick["plot_pulse_disposition"])
            )
            if world_tick["plot_pulse_disposition"].get("decision") == "deferred":
                trace["deferred_plot_pulses"].append(
                    deepcopy(pending_plot_pulse)
                )
            trace["consumed_plot_pulses"].append(deepcopy(pending_plot_pulse))
            pending_plot_pulse = None

        checkpoint_result = _run_due_checkpoints(
            fixture,
            runtime_state,
            provider,
            trace,
            config,
        )
        if checkpoint_result.get("approved_plot_pulse"):
            pending_plot_pulse = checkpoint_result["approved_plot_pulse"]
        if checkpoint_result.get("blocked"):
            trace["runtime_status"] = "quarantined_checkpoint"
            break

        directive = world_tick["next_directive"]
        directive_type = directive["directive_type"]
        if directive_type == "request_character_decision":
            decision_request = directive["decision_request"]
            request_review = _run_authority_review(
                fixture,
                runtime_state,
                provider,
                trace,
                config,
                subject_type="character_decision_request",
                subject=decision_request,
                subject_ref=decision_request["request_id"],
                source_context=world_call_context,
                stage=f"authority_decision_request_{decision_request['request_id']}",
            )
            if not is_review_approved(request_review):
                trace["runtime_status"] = "quarantined_decision_request"
                break
            approved = _run_character_decision(
                fixture,
                runtime_state,
                provider,
                trace,
                config,
                decision_request,
            )
            if approved is None:
                trace["runtime_status"] = "quarantined_character_decision"
                break
            pending_approved_proposal = approved
        elif directive_type == "finish_scene":
            if pending_plot_pulse is not None:
                # Plot pressure is an approved input, not a Kernel-authored result.
                # Give World another tick so it can explicitly accept, downgrade,
                # defer, or reject it under Authority review.
                runtime_state["tick_index"] += 1
                continue
            final_checkpoint = _run_due_checkpoints(
                fixture,
                runtime_state,
                provider,
                trace,
                config,
                force_narration=True,
            )
            if final_checkpoint.get("approved_plot_pulse"):
                pending_plot_pulse = final_checkpoint["approved_plot_pulse"]
                runtime_state["tick_index"] += 1
                continue
            if final_checkpoint.get("blocked"):
                trace["runtime_status"] = "quarantined_final_narration"
                break
            trace["runtime_status"] = "finished"
            finished = True
            break

        runtime_state["tick_index"] += 1

    if not finished and trace.get("runtime_status") is None:
        _record_validation(
            trace,
            "runtime_kernel",
            [
                {
                    "severity": "block",
                    "kind": "runtime_limit",
                    "code": "max_world_ticks_exceeded",
                    "message": f"World did not finish within {max_world_ticks} ticks.",
                }
            ],
        )
        trace["runtime_status"] = "max_world_ticks_exceeded"

    transaction_committed = finished and not _trace_has_block(trace)
    working_narration = trace.pop("working_narration_segments", [])
    if transaction_committed:
        published_state = runtime_state
        trace["transaction"] = {
            "status": "committed",
            "policy": "scene_atomic",
            "committed_event_refs": [
                event.get("event_id")
                for event in runtime_state.get("committed_world_events", [])
            ],
        }
        trace["narration_segments"] = deepcopy(working_narration)
        trace["published_narration_segments"] = deepcopy(working_narration)
        trace["quarantined_narration_segments"] = []
    else:
        trace["quarantined_runtime_state"] = deepcopy(runtime_state)
        published_state = initial_runtime_state
        trace["transaction"] = {
            "status": "rolled_back",
            "policy": "scene_atomic",
            "quarantined_event_refs": [
                event.get("event_id")
                for event in runtime_state.get("committed_world_events", [])
            ],
        }
        trace["narration_segments"] = []
        trace["published_narration_segments"] = []
        trace["quarantined_narration_segments"] = deepcopy(working_narration)
    trace["runtime_state"] = deepcopy(published_state)
    trace["scene_packet"] = _seal_world_scene_packet(fixture, published_state, trace)
    trace["memory_handoff"] = (
        _derive_memory_handoff(
            fixture,
            published_state,
            trace["scene_packet"]["packet_id"],
        )
        if transaction_committed
        else {"owner_projections": [], "derived_memory_deltas": []}
    )
    return _finish_trace(trace, run_dir)


def _run_character_decision(
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
    provider: AgentProvider,
    trace: dict[str, Any],
    config: RunnerConfig,
    decision_request: dict[str, Any],
) -> dict[str, Any] | None:
    request_id = decision_request["request_id"]
    router_ctx, router_manifest, router_contract = router_context(fixture, decision_request)
    router_projection = _record_projection(
        trace,
        router_ctx,
        router_manifest,
        router_contract,
        f"route_{request_id}",
        expected_projection_type="RouterContextPacket",
        expected_role="router",
        expected_instance_id="character_router",
    )
    if router_projection is None:
        return None
    router_output = _call_agent(
        provider,
        projection=router_projection,
        fixture=fixture,
        trace=trace,
        config=config,
    )
    route_plan = _payload(router_output, "route_plan")
    route_violations = validate_route_plan(
        route_plan,
        decision_request,
        set(fixture.get("characters", {})),
        router_ctx["decision_request_sha256"],
    )
    if not has_block(route_violations) and route_plan:
        route_violations.extend(
            _claim_protocol_ids(
                runtime_state,
                [route_plan.get("route_id")],
                "route_plan",
            )
        )
    _record_validation(trace, f"route_{request_id}", route_violations)
    if has_block(route_violations):
        return None
    assert route_plan is not None
    trace["route_plans"].append(deepcopy(route_plan))

    character_ctx, character_manifest, character_contract = character_decision_context(
        fixture,
        runtime_state,
        decision_request,
        route_plan,
    )
    character_id = route_plan["recipient_agent_id"]
    character_projection = _record_projection(
        trace,
        character_ctx,
        character_manifest,
        character_contract,
        f"character_decision_{request_id}",
        expected_projection_type="WorldDrivenCharacterContextPacket",
        expected_role="character",
        expected_instance_id=character_id,
    )
    if character_projection is None:
        return None
    max_repairs = fixture.get("max_character_repair_attempts", 1)
    proposal_context = json.loads(character_projection.canonical_context_json)
    proposal_projection = character_projection
    proposal: dict[str, Any] | None = None
    review: dict[str, Any] | None = None
    for attempt_index in range(max_repairs + 1):
        character_output = _call_agent(
            provider,
            projection=proposal_projection,
            fixture=fixture,
            trace=trace,
            config=config,
        )
        proposal = _payload(character_output, "event_proposal")
        proposal_violations = validate_event_proposal(proposal, decision_request, route_plan)
        if not has_block(proposal_violations) and proposal:
            proposal_violations.extend(
                _claim_protocol_ids(
                    runtime_state,
                    [proposal.get("proposal_id")],
                    "event_proposal",
                )
            )
        _record_validation(trace, f"event_proposal_{request_id}_attempt_{attempt_index}", proposal_violations)
        if has_block(proposal_violations):
            return None
        assert proposal is not None
        trace["event_proposals"].append(deepcopy(proposal))

        review = _run_authority_review(
            fixture,
            runtime_state,
            provider,
            trace,
            config,
            subject_type="event_proposal",
            subject=proposal,
            subject_ref=proposal["proposal_id"],
            source_context=proposal_context,
            stage=f"authority_event_proposal_{proposal['proposal_id']}",
        )
        if is_review_approved(review):
            break
        if review_requires_repair(review) and attempt_index < max_repairs:
            repair_ctx, repair_manifest, repair_contract = character_repair_context(
                character_ctx,
                proposal,
                review,
                attempt_index + 1,
            )
            repair_projection = _record_projection(
                trace,
                repair_ctx,
                repair_manifest,
                repair_contract,
                f"character_repair_{request_id}_{attempt_index + 1}",
                expected_projection_type="CharacterRepairContextPacket",
                expected_role="character",
                expected_instance_id=character_id,
            )
            if repair_projection is None:
                return None
            trace["repair_attempts"].append(
                {
                    "origin_agent_id": character_id,
                    "request_id": request_id,
                    "rejected_subject_ref": review["subject_ref"],
                    "authority_review_ref": review["review_id"],
                    "attempt_index": attempt_index + 1,
                }
            )
            proposal_projection = repair_projection
            proposal_context = json.loads(
                proposal_projection.canonical_context_json
            )
            continue
        if review_requires_repair(review):
            _record_validation(
                trace,
                f"repair_limit_{request_id}",
                [
                    {
                        "severity": "block",
                        "kind": "authority_repair",
                        "code": "character_repair_limit_exceeded",
                        "message": f"Character repair limit {max_repairs} exhausted for {request_id}.",
                    }
                ],
            )
        return None

    if proposal is None or review is None or not is_review_approved(review):
        return None

    approved = {
        "approval_id": f"approved_{proposal['proposal_id']}",
        "proposal_id": proposal["proposal_id"],
        "authority_binding_sha256": _authority_binding(review),
        "proposal_sha256": _content_hash(proposal),
        "original_proposal": deepcopy(proposal),
        "approval_semantics": "Judge approves the immutable original proposal and does not rewrite it.",
    }
    trace["approved_event_proposals"].append(deepcopy(approved))
    return approved


def _run_due_checkpoints(
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
    provider: AgentProvider,
    trace: dict[str, Any],
    config: RunnerConfig,
    *,
    force_narration: bool = False,
) -> dict[str, Any]:
    result: dict[str, Any] = {"blocked": False, "approved_plot_pulse": None}
    event_count = len(runtime_state["committed_world_events"])
    policy = runtime_state["checkpoint_policy"]

    plot_due = _checkpoint_due(
        event_count,
        runtime_state["last_plot_event_index"],
        policy["plot_every_committed_beats"],
    )
    if plot_due:
        plot_ctx, plot_manifest, plot_contract = plot_pulse_context(fixture, runtime_state)
        plot_projection = _record_projection(
            trace,
            plot_ctx,
            plot_manifest,
            plot_contract,
            f"plot_checkpoint_{event_count}",
            expected_projection_type="PlotPulseContext",
            expected_role="plot",
            expected_instance_id="plot_checkpoint",
        )
        if plot_projection is None:
            result["blocked"] = True
            return result
        plot_output = _call_agent(
            provider,
            projection=plot_projection,
            fixture=fixture,
            trace=trace,
            config=config,
        )
        pulse = _payload(plot_output, "plot_pulse")
        pulse, normalization_records = _normalize_plot_pulse(pulse)
        trace["normalization_records"].extend(normalization_records)
        pulse_violations = validate_plot_pulse(
            pulse,
            runtime_state.get("pressure_ledger", []),
            runtime_state.get("option_topology", {}),
            fixture["scene_id"],
        )
        pulse_violations = [
            *[
                {
                    "severity": "warning",
                    "kind": "recoverable_normalization",
                    "code": record["code"],
                    "message": record["message"],
                }
                for record in normalization_records
            ],
            *pulse_violations,
        ]
        if not has_block(pulse_violations) and pulse:
            pulse_violations.extend(
                _claim_protocol_ids(
                    runtime_state,
                    [pulse.get("pulse_id")],
                    "plot_pulse",
                )
            )
        _record_validation(trace, f"plot_pulse_{event_count}", pulse_violations)
        if has_block(pulse_violations):
            result["blocked"] = True
            return result
        assert pulse is not None
        trace["plot_pulses"].append(deepcopy(pulse))
        review = _run_authority_review(
            fixture,
            runtime_state,
            provider,
            trace,
            config,
            subject_type="plot_pulse",
            subject=pulse,
            subject_ref=pulse["pulse_id"],
            source_context=plot_ctx,
            stage=f"authority_plot_pulse_{pulse['pulse_id']}",
        )
        if not is_review_approved(review):
            result["blocked"] = True
            return result
        approved_pulse = {
            "approval_id": f"approved_{pulse['pulse_id']}",
            "pulse_id": pulse["pulse_id"],
            "authority_binding_sha256": _authority_binding(review),
            "pulse_sha256": _content_hash(pulse),
            "original_plot_pulse": deepcopy(pulse),
        }
        result["approved_plot_pulse"] = approved_pulse
        runtime_state["pressure_ledger"].append(deepcopy(approved_pulse))
        runtime_state["last_plot_event_index"] = event_count

    narration_due = force_narration and event_count > runtime_state["last_narrated_event_index"]
    narration_due = narration_due or _checkpoint_due(
        event_count,
        runtime_state["last_narrated_event_index"],
        policy["narrate_every_committed_beats"],
    )
    if narration_due:
        narrator_ctx, narrator_manifest, narrator_contract = narration_checkpoint_context(fixture, runtime_state)
        checkpoint = narrator_ctx["narration_checkpoint"]
        narrator_projection = _record_projection(
            trace,
            narrator_ctx,
            narrator_manifest,
            narrator_contract,
            f"narration_{checkpoint['checkpoint_id']}",
            expected_projection_type="NarrationCheckpoint",
            expected_role="narrator",
            expected_instance_id="narrator_checkpoint",
        )
        if narrator_projection is None:
            result["blocked"] = True
            return result
        if not checkpoint["source_event_refs"]:
            trace["skipped_narration_checkpoints"].append(
                {
                    "checkpoint_id": checkpoint["checkpoint_id"],
                    "reason": "no_events_visible_under_pov_contract",
                    "examined_event_count": event_count
                    - runtime_state["last_narrated_event_index"],
                    "projection_manifest": narrator_manifest,
                }
            )
            runtime_state["last_narrated_event_index"] = event_count
            return result
        max_repairs = fixture.get("max_narrator_repair_attempts", 1)
        narration_context = json.loads(narrator_projection.canonical_context_json)
        narration_projection = narrator_projection
        narration_subject: dict[str, Any] | None = None
        review: dict[str, Any] | None = None
        for attempt_index in range(max_repairs + 1):
            narration_stage = (
                f"narration_{checkpoint['checkpoint_id']}"
                if attempt_index == 0
                else f"narration_repair_{checkpoint['checkpoint_id']}_{attempt_index}"
            )
            narrator_output = _call_agent(
                provider,
                projection=narration_projection,
                fixture=fixture,
                trace=trace,
                config=config,
            )
            narration_violations = validate_narration(
                narrator_output,
                narration_context,
                fixture.get("narration_bounds", {}),
            )
            _record_validation(trace, narration_stage, narration_violations)
            if has_block(narration_violations):
                result["blocked"] = True
                return result
            narration_subject = {
                "source_checkpoint_id": checkpoint["checkpoint_id"],
                "source_event_refs": checkpoint["source_event_refs"],
                "prose": (narrator_output or {}).get("prose", ""),
            }
            narration_subject["claim_units"] = build_narration_claim_units(
                narration_subject["prose"], checkpoint["checkpoint_id"]
            )
            review = _run_authority_review(
                fixture,
                runtime_state,
                provider,
                trace,
                config,
                subject_type="narration",
                subject=narration_subject,
                subject_ref=checkpoint["checkpoint_id"],
                source_context=narration_context,
                stage=f"authority_{narration_stage}",
            )
            if is_review_approved(review):
                break
            if review_requires_repair(review) and attempt_index < max_repairs:
                repair_ctx, repair_manifest, repair_contract = narration_repair_context(
                    narrator_ctx,
                    narration_subject,
                    review,
                    attempt_index + 1,
                )
                repair_projection = _record_projection(
                    trace,
                    repair_ctx,
                    repair_manifest,
                    repair_contract,
                    f"narration_repair_{checkpoint['checkpoint_id']}_{attempt_index + 1}",
                    expected_projection_type="NarrationRepairContextPacket",
                    expected_role="narrator",
                    expected_instance_id="narrator_checkpoint",
                )
                if repair_projection is None:
                    result["blocked"] = True
                    return result
                trace["repair_attempts"].append(
                    {
                        "origin_agent_id": "narrator_checkpoint",
                        "request_id": checkpoint["checkpoint_id"],
                        "rejected_subject_ref": review["subject_ref"],
                        "authority_review_ref": review["review_id"],
                        "attempt_index": attempt_index + 1,
                    }
                )
                narration_projection = repair_projection
                narration_context = json.loads(
                    narration_projection.canonical_context_json
                )
                continue
            if review_requires_repair(review):
                _record_validation(
                    trace,
                    f"narration_repair_limit_{checkpoint['checkpoint_id']}",
                    [
                        {
                            "severity": "block",
                            "kind": "authority_repair",
                            "code": "narration_repair_limit_exceeded",
                            "message": (
                                f"Narration repair limit {max_repairs} exhausted for "
                                f"{checkpoint['checkpoint_id']}."
                            ),
                        }
                    ],
                )
            result["blocked"] = True
            return result
        if narration_subject is None or not is_review_approved(review):
            result["blocked"] = True
            return result
        trace["working_narration_segments"].append(narration_subject)
        runtime_state["last_narrated_event_index"] = event_count
    return result


def _run_authority_review(
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
    provider: AgentProvider,
    trace: dict[str, Any],
    config: RunnerConfig,
    *,
    subject_type: str,
    subject: dict[str, Any],
    subject_ref: str,
    source_context: dict[str, Any],
    stage: str,
) -> dict[str, Any] | None:
    review_ctx, review_manifest, review_contract = authority_review_context(
        fixture,
        runtime_state,
        subject_type,
        subject,
        source_context,
        trace["run_nonce"],
    )
    review_projection = _record_projection(
        trace,
        review_ctx,
        review_manifest,
        review_contract,
        stage,
        expected_projection_type="AuthorityReviewContext",
        expected_role="authority",
        expected_instance_id="authority_judge",
    )
    if review_projection is None:
        return None
    review_context = json.loads(review_projection.canonical_context_json)
    output = _call_agent(
        provider,
        projection=review_projection,
        fixture=fixture,
        trace=trace,
        config=config,
    )
    review = _payload(output, "authority_review")
    violations = validate_authority_review(
        review,
        subject_type=subject_type,
        subject_ref=subject_ref,
        subject_sha256=_content_hash(subject),
        subject=subject,
        expected_run_nonce=trace["run_nonce"],
        expected_review_context_sha256=review_context["review_context_sha256"],
        review_context=review_context,
    )
    if not has_block(violations) and review:
        violations.extend(
            _claim_protocol_ids(
                runtime_state,
                [review.get("review_id")],
                "authority_review",
            )
        )
    _record_validation(trace, stage, violations)
    if review:
        trace["authority_reviews"].append(deepcopy(review))
    if has_block(violations):
        return None
    return review


def _commit_adjudication(
    runtime_state: dict[str, Any], trace: dict[str, Any], adjudication: dict[str, Any]
) -> None:
    trace["world_adjudications"].append(deepcopy(adjudication))
    runtime_state["committed_world_events"].extend(deepcopy(adjudication.get("committed_events", [])))
    runtime_state["world_state_delta_ledger"].extend(deepcopy(adjudication.get("state_deltas", [])))
    runtime_state["visibility_result_ledger"].extend(deepcopy(adjudication.get("visibility_results", [])))
    runtime_state["publication_candidates"].extend(deepcopy(adjudication.get("publication_candidates", [])))
    runtime_state["canon_reveal_candidates"].extend(deepcopy(adjudication.get("canon_reveal_candidates", [])))


def _call_agent(
    provider: AgentProvider,
    *,
    projection: ValidatedProjection,
    fixture: dict[str, Any],
    trace: dict[str, Any],
    config: RunnerConfig,
    _syntax_repair_attempt: int = 0,
) -> dict[str, Any] | None:
    try:
        projected_context = json.loads(projection.canonical_context_json)
    except (TypeError, json.JSONDecodeError):
        projected_context = None
    if (
        not isinstance(projected_context, dict)
        or _content_hash(projected_context) != projection.context_sha256
    ):
        _record_validation(
            trace,
            "projection_dispatch",
            [
                {
                    "severity": "block",
                    "kind": "projection_dispatch",
                    "code": "validated_projection_seal_mismatch",
                    "message": "Validated projection changed before dispatch; provider was not called.",
                }
            ],
        )
        return None

    role = projection.role
    instance_id = projection.instance_id
    stage = projection.stage
    if len(trace["agent_runs"]) >= config.max_llm_calls_per_trace:
        _record_validation(
            trace,
            "runtime_budget",
            [
                {
                    "severity": "block",
                    "kind": "runtime_budget",
                    "code": "max_llm_calls_exceeded",
                    "message": f"Call budget {config.max_llm_calls_per_trace} exhausted before {stage}.",
                }
            ],
        )
        return None
    output_tokens_used = sum(
        int(item.get("output_tokens", 0))
        for item in trace["token_usage"]["agents"]
        if isinstance(item.get("output_tokens", 0), int)
    )
    call_output_cap = config.max_tokens_for(role)
    output_budget_remaining = config.total_output_token_budget - output_tokens_used
    if output_budget_remaining < call_output_cap:
        _record_validation(
            trace,
            "runtime_budget",
            [
                {
                    "severity": "block",
                    "kind": "runtime_budget",
                    "code": "total_output_token_budget_exceeded",
                    "message": (
                        f"Only {output_budget_remaining} output tokens remain before {stage}, "
                        f"below the reserved per-call cap {call_output_cap}."
                    ),
                }
            ],
        )
        return None

    prompt = build_prompt(role, projected_context)
    completion = provider.complete(
        role,
        prompt,
        fixture,
        runtime_bindings={
            "RUN_NONCE": trace["run_nonce"],
            "REVIEW_CONTEXT_SHA256": projected_context.get(
                "review_context_sha256", ""
            ),
        },
    )
    record = {
        "call_index": len(trace["agent_runs"]),
        "agent_name": role,
        "agent_instance_id": instance_id,
        "protocol_stage": stage,
        "projection_manifest_id": projection.manifest_id,
        "projection_contract_id": projection.contract_id,
        "mode": completion.mode,
        "projected_context": projected_context,
        "prompt": completion.prompt,
        "raw_output": completion.raw_output,
        "parsed_output": completion.parsed_output,
        "error": completion.error,
        "token_usage": completion.token_usage,
    }
    trace["agent_runs"].append(record)
    budget_violation = False
    if completion.token_usage:
        usage = deepcopy(completion.token_usage)
        usage["agent_instance_id"] = instance_id
        usage["protocol_stage"] = stage
        trace["token_usage"]["agents"].append(usage)
        if int(usage.get("output_tokens", 0)) > call_output_cap:
            budget_violation = True
            _record_validation(
                trace,
                "runtime_budget",
                [
                    {
                        "severity": "block",
                        "kind": "runtime_budget",
                        "code": "per_agent_output_token_budget_exceeded",
                        "message": f"{stage} exceeded its configured output limit {call_output_cap}; no state transition is allowed.",
                    }
                ],
            )
        if sum(
            int(item.get("output_tokens", 0))
            for item in trace["token_usage"]["agents"]
            if isinstance(item.get("output_tokens", 0), int)
        ) > config.total_output_token_budget:
            budget_violation = True
            _record_validation(
                trace,
                "runtime_budget",
                [
                    {
                        "severity": "block",
                        "kind": "runtime_budget",
                        "code": "total_output_token_budget_exceeded",
                        "message": "Agent output crossed the configured trace output-token budget.",
                    }
                ],
            )
    if budget_violation:
        return None
    if completion.error:
        if (
            completion.error.startswith("json_decode_error:")
            and completion.raw_output
            and _syntax_repair_attempt < MAX_OUTPUT_SYNTAX_REPAIR_ATTEMPTS
        ):
            next_attempt = _syntax_repair_attempt + 1
            _record_validation(
                trace,
                f"{stage}_rejected",
                [
                    {
                        "severity": "repair_required",
                        "kind": "agent_call",
                        "code": "invalid_json_syntax",
                        "message": (
                            "Origin agent output was not valid JSON; one syntax-only "
                            "retry is permitted before quarantine."
                        ),
                    }
                ],
            )
            repair_ctx, repair_manifest, repair_contract = (
                output_syntax_repair_context(
                    role=role,
                    instance_id=instance_id,
                    original_stage=stage,
                    original_context_sha256=projection.context_sha256,
                    invalid_raw_output=completion.raw_output,
                    parser_error=completion.error,
                    attempt_index=next_attempt,
                )
            )
            repair_stage = f"{stage}_json_syntax_repair_{next_attempt}"
            repair_projection = _record_projection(
                trace,
                repair_ctx,
                repair_manifest,
                repair_contract,
                repair_stage,
                expected_projection_type="OutputSyntaxRepairContextPacket",
                expected_role=role,
                expected_instance_id=instance_id,
            )
            if repair_projection is None:
                return None
            trace["repair_attempts"].append(
                {
                    "repair_kind": "json_syntax",
                    "origin_agent_id": instance_id,
                    "request_id": stage,
                    "rejected_subject_ref": stage,
                    "authority_review_ref": None,
                    "attempt_index": next_attempt,
                    "repair_codes": ["invalid_json_syntax"],
                    "original_call_index": record["call_index"],
                }
            )
            return _call_agent(
                provider,
                projection=repair_projection,
                fixture=fixture,
                trace=trace,
                config=config,
                _syntax_repair_attempt=next_attempt,
            )
        _record_validation(
            trace,
            stage,
            [
                {
                    "severity": "block",
                    "kind": "agent_call",
                    "code": "agent_completion_error",
                    "message": completion.error,
                }
            ],
        )
        return None
    if projected_context.get("context_type") == "OutputSyntaxRepairContextPacket":
        conservation_violations = validate_syntax_repair_conservation(
            projected_context.get("invalid_raw_output"),
            completion.raw_output,
            completion.parsed_output,
        )
        _record_validation(
            trace,
            f"{stage}_conservation",
            conservation_violations,
        )
        if has_block(conservation_violations):
            return None
    return completion.parsed_output


def _payload(output: dict[str, Any] | None, key: str) -> dict[str, Any] | None:
    if not isinstance(output, dict):
        return None
    value = output.get(key)
    return value if isinstance(value, dict) else None


def _record_validation(
    trace: dict[str, Any], key: str, violations: list[dict[str, Any]]
) -> None:
    if key in trace["validation"]:
        trace["validation"][key].extend(violations)
    else:
        trace["validation"][key] = violations


def _world_origin_repairable(violations: list[dict[str, Any]]) -> bool:
    blocking_codes = {
        str(item.get("code"))
        for item in violations
        if item.get("severity") == "block"
    }
    return bool(blocking_codes) and blocking_codes <= WORLD_ORIGIN_REPAIRABLE_CODES


def _normalize_plot_pulse(
    pulse: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    if not isinstance(pulse, dict):
        return pulse, []
    normalized = deepcopy(pulse)
    budget = normalized.get("budget_cost")
    if not isinstance(budget, dict) or budget.get("intensity") != "moderate":
        return normalized, []
    budget["intensity"] = "medium"
    return normalized, [
        {
            "code": "normalized_plot_intensity",
            "message": "Normalized recoverable PlotPulse intensity synonym moderate -> medium.",
            "field_path": "plot_pulse.budget_cost.intensity",
            "before": "moderate",
            "after": "medium",
            "policy": "recoverable_schema_value_normalization_v0.1",
        }
    ]


def _as_repair_required(
    violations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    repaired = deepcopy(violations)
    for item in repaired:
        if item.get("severity") == "block":
            item["severity"] = "repair_required"
    return repaired


def _record_projection(
    trace: dict[str, Any],
    context: dict[str, Any],
    manifest: dict[str, Any],
    contract: dict[str, Any],
    stage: str,
    *,
    expected_projection_type: str,
    expected_role: str,
    expected_instance_id: str,
) -> ValidatedProjection | None:
    expected_recipient = {
        "role": expected_role,
        "instance_id": expected_instance_id,
    }
    violations = validate_projection_manifest(
        context,
        manifest,
        contract,
        expected_projection_type=expected_projection_type,
        expected_recipient=expected_recipient,
    )
    _record_validation(trace, f"projection_{stage}", violations)
    trace["projection_manifests"].append(manifest)
    contract_record = deepcopy(contract)
    for anchor in contract_record.get("field_anchors", {}).values():
        if isinstance(anchor, dict):
            anchor.pop("_source_value", None)
    trace["projection_contracts"].append(contract_record)
    if has_block(violations):
        return None
    canonical_context_json = stable_json(context)
    return ValidatedProjection(
        role=expected_role,
        instance_id=expected_instance_id,
        stage=stage,
        canonical_context_json=canonical_context_json,
        context_sha256=_content_hash(context),
        manifest_id=str(manifest["manifest_id"]),
        contract_id=str(contract["contract_id"]),
    )


def _checkpoint_policy(fixture: dict[str, Any]) -> dict[str, int]:
    raw = fixture.get("checkpoint_policy", {})
    if not isinstance(raw, dict):
        raw = {}
    plot_interval = raw.get("plot_every_committed_beats", 2)
    narration_interval = raw.get("narrate_every_committed_beats", 2)
    return {
        "plot_every_committed_beats": max(0, plot_interval) if isinstance(plot_interval, int) and not isinstance(plot_interval, bool) else 0,
        "narrate_every_committed_beats": max(0, narration_interval) if isinstance(narration_interval, int) and not isinstance(narration_interval, bool) else 0,
    }


def _checkpoint_due(current: int, previous: int, interval: int) -> bool:
    return interval > 0 and current > previous and current - previous >= interval


def _content_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def _authority_binding(review: dict[str, Any]) -> str:
    """Bind approval without forwarding Judge-controlled identifiers or prose."""

    return _content_hash(
        {
            "subject_type": review.get("subject_type"),
            "subject_ref": review.get("subject_ref"),
            "subject_sha256": review.get("subject_sha256"),
            "verdict": review.get("verdict"),
            "run_nonce": review.get("run_nonce"),
            "review_context_sha256": review.get("review_context_sha256"),
        }
    )


def _world_condition_refs(
    fixture: dict[str, Any], runtime_state: dict[str, Any]
) -> set[str]:
    refs = set(str(ref) for ref in fixture.get("world_condition_registry", []))
    refs.update(
        str(event["publication_id"])
        for event in fixture.get("public_event_ledger", [])
        if isinstance(event, dict) and event.get("publication_id")
    )
    refs.update(
        str(event["event_id"])
        for event in runtime_state.get("committed_world_events", [])
        if isinstance(event, dict) and event.get("event_id")
    )
    refs.update(
        str(delta["delta_id"])
        for delta in runtime_state.get("world_state_delta_ledger", [])
        if isinstance(delta, dict) and delta.get("delta_id")
    )
    return refs


def _world_tick_protocol_ids(world_tick: dict[str, Any]) -> list[str | None]:
    identifiers: list[str | None] = [world_tick.get("tick_id")]
    directive = world_tick.get("next_directive")
    if isinstance(directive, dict):
        request = directive.get("decision_request")
        if isinstance(request, dict):
            identifiers.append(request.get("request_id"))
    adjudication = world_tick.get("adjudication")
    if isinstance(adjudication, dict):
        identifiers.append(adjudication.get("adjudication_id"))
        collection_keys = {
            "committed_events": "event_id",
            "state_deltas": "delta_id",
            "visibility_results": "visibility_result_id",
            "publication_candidates": "publication_candidate_id",
            "canon_reveal_candidates": "canon_reveal_candidate_id",
        }
        for collection_name, identifier_key in collection_keys.items():
            for item in adjudication.get(collection_name, []):
                if isinstance(item, dict):
                    identifiers.append(item.get(identifier_key))
    return identifiers


def _claim_protocol_ids(
    runtime_state: dict[str, Any],
    identifiers: list[Any],
    kind: str,
) -> list[dict[str, Any]]:
    invalid_positions = [
        index for index, identifier in enumerate(identifiers) if not is_protocol_id(identifier)
    ]
    if invalid_positions:
        return [
            {
                "severity": "block",
                "kind": kind,
                "code": "invalid_protocol_id",
                "message": (
                    "Every claimed protocol identity must match "
                    "^[A-Za-z][A-Za-z0-9_.:-]{0,127}$; invalid positions: "
                    + ", ".join(str(index) for index in invalid_positions)
                ),
            }
        ]
    normalized = list(identifiers)
    seen_in_object: set[str] = set()
    repeated_in_object: set[str] = set()
    for identifier in normalized:
        if identifier in seen_in_object:
            repeated_in_object.add(identifier)
        seen_in_object.add(identifier)
    used = set(runtime_state.get("used_protocol_ids", []))
    replayed = sorted(repeated_in_object | (set(normalized) & used))
    if replayed:
        return [
            {
                "severity": "block",
                "kind": kind,
                "code": "protocol_id_replay",
                "message": "Run-local protocol identities may be used only once: "
                + ", ".join(replayed),
            }
        ]
    runtime_state.setdefault("used_protocol_ids", []).extend(normalized)
    return []


def _scheduled_world_event_hashes(
    fixture: dict[str, Any], runtime_state: dict[str, Any]
) -> dict[str, str]:
    consumed = set(runtime_state.get("consumed_scheduled_world_event_refs", []))
    return {
        str(record["schedule_id"]): _content_hash(record)
        for record in fixture.get("scheduled_world_events", [])
        if isinstance(record, dict)
        and record.get("schedule_id")
        and record["schedule_id"] not in consumed
    }


def _seal_world_scene_packet(
    fixture: dict[str, Any], runtime_state: dict[str, Any], trace: dict[str, Any]
) -> dict[str, Any]:
    packet_payload = {
        "packet_id": f"sp_{fixture['trace_id']}_{trace['run_id']}",
        "scene_id": fixture["scene_id"],
        "packet_scope": "world_driven_scene",
        "commit_status": (
            "committed"
            if trace.get("runtime_status") == "finished" and not _trace_has_block(trace)
            else "quarantined"
        ),
        "resolved_events": deepcopy(runtime_state["committed_world_events"]),
        "state_deltas": deepcopy(runtime_state["world_state_delta_ledger"]),
        "visibility_deltas": deepcopy(runtime_state["visibility_result_ledger"]),
        "publication_candidates": deepcopy(runtime_state["publication_candidates"]),
        "canon_reveal_candidates": deepcopy(runtime_state["canon_reveal_candidates"]),
        "pov_contract": deepcopy(fixture.get("pov_contract", {})),
        "narration_bounds": deepcopy(fixture.get("narration_bounds", {})),
    }
    source_collections = {
        "resolved_events": packet_payload["resolved_events"],
        "state_deltas": packet_payload["state_deltas"],
        "visibility_deltas": packet_payload["visibility_deltas"],
        "publication_candidates": packet_payload["publication_candidates"],
        "canon_reveal_candidates": packet_payload["canon_reveal_candidates"],
    }
    committed_transaction = trace.get("transaction", {}).get("status") == "committed"
    adjudication_refs = [
        item.get("adjudication_id") for item in trace["world_adjudications"]
    ]
    packet_payload["sealing_record"] = {
        "sealed_by": "runtime_kernel",
        "assembly_policy_version": "mechanical_scene_sealing_v0.2",
        "assembly_rule": "append validated adjudication collections in accepted runtime order; no summarization, omission, or literary selection",
        "source_adjudication_refs": adjudication_refs if committed_transaction else [],
        "included_refs": {
            "resolved_events": [
                item.get("event_id") for item in packet_payload["resolved_events"]
            ],
            "state_deltas": [
                item.get("delta_id") for item in packet_payload["state_deltas"]
            ],
            "visibility_deltas": [
                item.get("visibility_result_id")
                for item in packet_payload["visibility_deltas"]
            ],
            "publication_candidates": [
                item.get("publication_candidate_id")
                for item in packet_payload["publication_candidates"]
            ],
            "canon_reveal_candidates": [
                item.get("canon_reveal_candidate_id")
                for item in packet_payload["canon_reveal_candidates"]
            ],
        },
        "excluded_refs": [] if committed_transaction else adjudication_refs,
        "source_collection_sha256": {
            name: _content_hash(collection)
            for name, collection in source_collections.items()
        },
        "sealed_payload_sha256": _content_hash(packet_payload),
        "consumed_scheduled_world_event_refs": deepcopy(
            runtime_state.get("consumed_scheduled_world_event_refs", [])
        ),
        "candidate_policy": "candidates remain system-restricted and are absent from character, plot, and narration contexts",
    }
    return packet_payload


def _derive_memory_handoff(
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
    source_packet_id: str,
) -> dict[str, Any]:
    owner_projections: list[dict[str, Any]] = []
    memory_deltas: list[dict[str, Any]] = []
    for owner_id in fixture.get("characters", {}):
        visible_events = []
        for event in runtime_state["committed_world_events"]:
            if event_directly_observed_by(event, owner_id, fixture):
                visible_events.append(event.get("event_id"))
                memory_deltas.append(
                    {
                        "delta_id": f"md_{owner_id}_{event.get('event_id')}",
                        "owner_agent_id": owner_id,
                        "writer_role": "world_agent",
                        "source_packet_id": source_packet_id,
                        "source_event_id": event.get("event_id"),
                        "delta_kind": "observation",
                        "acquisition_mode": "direct_observation",
                        "content": event.get("public_surface") or event.get("outcome"),
                        "certainty": "medium",
                        "memory_status": "active",
                        "based_on": [event.get("event_id")],
                    }
                )
        owner_projections.append({"owner_agent_id": owner_id, "visible_event_refs": visible_events})
    return {"owner_projections": owner_projections, "derived_memory_deltas": memory_deltas}


def _new_trace(
    fixture: dict[str, Any],
    fixture_path: str,
    config: RunnerConfig,
    created_at: str,
    run_id: str,
    run_nonce: str,
    checkpoint_policy: dict[str, int],
) -> dict[str, Any]:
    return {
        "trace_id": fixture.get("trace_id", "invalid_fixture"),
        "run_id": run_id,
        "run_nonce": run_nonce,
        "runtime_mode": "world_driven",
        "runtime_status": None,
        "fixture_path": fixture_path,
        "created_at": created_at,
        "llm_mode": config.llm_mode,
        "model": config.model,
        "checkpoint_policy": checkpoint_policy,
        "agent_runs": [],
        "projection_manifests": [],
        "projection_contracts": [],
        "validation": {},
        "world_ticks": [],
        "route_plans": [],
        "event_proposals": [],
        "approved_event_proposals": [],
        "authority_reviews": [],
        "repair_attempts": [],
        "world_adjudications": [],
        "plot_pulses": [],
        "plot_pulse_dispositions": [],
        "consumed_plot_pulses": [],
        "deferred_plot_pulses": [],
        "working_narration_segments": [],
        "narration_segments": [],
        "published_narration_segments": [],
        "quarantined_narration_segments": [],
        "skipped_narration_checkpoints": [],
        "normalization_records": [],
        "token_usage": {
            "budget": {
                "max_llm_calls_per_trace": config.max_llm_calls_per_trace,
                "total_output_token_budget": config.total_output_token_budget,
                "per_agent_max_output_tokens": config.per_agent_max_output_tokens,
                "enforcement": {
                    "call_count": "hard_pre_call",
                    "state_transition": "hard_precommit",
                    "openai_compatible_output_tokens": "provider_request_cap",
                    "codex_cli_output_tokens": "soft_prompt_budget_plus_post_response_precommit_block",
                    "wall_time": "subprocess_or_http_timeout",
                },
            },
            "agents": [],
            "totals": {},
        },
        "artifacts": {},
    }


def _finish_trace(trace: dict[str, Any], run_dir: str) -> dict[str, Any]:
    blocked = _trace_has_block(trace)
    trace["final_decision"] = "blocked" if blocked or trace.get("runtime_status") != "finished" else "allowed"
    summarize_token_usage(trace)
    trace_path = os.path.join(run_dir, "trace.json")
    report_path = os.path.join(run_dir, "report.md")
    trace["artifacts"] = {"trace_json": trace_path, "report_md": report_path}
    write_json_file(trace_path, trace)
    write_report(report_path, trace)
    return trace


def _trace_has_block(trace: dict[str, Any]) -> bool:
    return any(
        item.get("severity") == "block"
        for violations in trace.get("validation", {}).values()
        for item in violations
    )


def _run_id(created_at: str) -> str:
    return created_at.replace("-", "").replace(":", "").replace("+", "Z").replace(".", "_")
