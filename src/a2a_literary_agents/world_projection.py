"""Projected contexts for the World-driven runtime.

Full ledgers and protocol objects remain Runtime Kernel objects. Each model-agent
receives a purpose-built view plus an auditable projection manifest.
"""

from __future__ import annotations

import hashlib
from copy import deepcopy
from typing import Any

from .json_util import stable_json
from .runtime_validation import (
    AUTHORITY_REQUIRED_REVIEW_FIELDS,
    PLOT_DURATIONS,
    PLOT_PRESSURE_KINDS,
    PLOT_SCOPES,
)
from .visibility import (
    encountered_public_events,
    event_visible_to,
    legal_character_trigger_refs,
    public_event_views,
    projected_visibility,
    visible_event_views,
)


_STABLE_SOURCE_ID_FIELDS = (
    "event_id",
    "publication_id",
    "memory_id",
    "delta_id",
    "proposal_id",
    "request_id",
    "pulse_id",
    "adjudication_id",
    "route_id",
    "schedule_id",
    "visibility_result_id",
    "publication_candidate_id",
    "canon_reveal_candidate_id",
    "agent_id",
    "owner_agent_id",
    "character_id",
)


_KERNEL_POLICY_FIELDS = {
    "WorldControlContext": {
        "context_type",
        "authority_limits",
        "candidate_item_contracts",
        "candidate_policy",
        "directive_policy",
        "plot_pulse_translation_policy",
        "world_adjudication_contract",
        "required_output_shape",
    },
    "WorldRepairContextPacket": {"context_type"},
    "RouterContextPacket": {"context_type", "routing_limits", "required_output_shape"},
    "WorldDrivenCharacterContextPacket": {
        "context_type",
        "authority_limits",
        "forbidden_sources",
        "required_output_shape",
    },
    "AuthorityReviewContext": {
        "context_type",
        "review_scope",
        "judge_limits",
        "reviewed_fields_policy",
        "origin_safe_repair_contract",
        "required_output_shape",
    },
    "CharacterRepairContextPacket": {"context_type"},
    "PlotPulseContext": {"context_type", "authority_limits", "required_output_shape"},
    "NarrationCheckpoint": {"context_type", "forbidden_sources", "required_output_shape"},
    "NarrationRepairContextPacket": {"context_type"},
    "OutputSyntaxRepairContextPacket": {
        "context_type",
        "repair_rules",
        "visibility",
    },
}


def world_control_context(
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
    pending_approved_proposal: dict[str, Any] | None,
    pending_plot_pulse: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    scheduled_world_events = _scheduled_world_event_views(fixture, runtime_state)
    context = {
        "context_type": "WorldControlContext",
        "scene_id": fixture["scene_id"],
        "user_request": fixture["user_request"],
        "tick_index": runtime_state["tick_index"],
        "world_state_ledger": deepcopy(fixture.get("world_state_ledger", {})),
        "committed_world_events": deepcopy(runtime_state.get("committed_world_events", [])),
        "world_state_delta_ledger": deepcopy(runtime_state.get("world_state_delta_ledger", [])),
        "public_canon": deepcopy(fixture.get("public_canon", [])),
        "public_event_ledger": deepcopy(fixture.get("public_event_ledger", [])),
        "approved_event_proposal": deepcopy(pending_approved_proposal),
        "approved_plot_pulse": deepcopy(pending_plot_pulse),
        "scheduled_world_events": scheduled_world_events,
        "checkpoint_policy": deepcopy(runtime_state["checkpoint_policy"]),
        "character_registry": _character_registry(fixture),
        "scene_participant_ids": deepcopy(fixture.get("scene_participant_ids", [])),
        "legal_character_trigger_refs": {
            character_id: sorted(
                legal_character_trigger_refs(fixture, runtime_state, character_id)
            )
            for character_id in fixture.get("characters", {})
        },
        "existing_world_condition_refs": _existing_world_condition_refs(
            fixture, runtime_state
        ),
        "authority_limits": [
            "World controls simulation flow and adjudicates consequences.",
            "World cannot choose a character's intent or action.",
            "World cannot write player-facing prose or promote canon.",
            "Only an Authority-approved proposal may be adjudicated.",
            "CommittedWorldEvent.actors may contain only registered Character Agent ids; objective scheduled events with no Character initiator use an empty list.",
        ],
        "directive_policy": [
            "Request a Character decision only when completing user_request requires a new Character-owned choice.",
            "If the current adjudication fully satisfies user_request and no required choice remains, use finish_scene.",
            "Use continue_world only for a registered objective transition that can advance without Character will.",
            "For non-request directives, decision_request must be null.",
        ],
        "candidate_policy": [
            "publication_candidates and canon_reveal_candidates are either empty lists or strict objects matching candidate_item_contracts; strings are never legal.",
            "An ordinary scene_public event does not automatically require a PublicationCandidate.",
            "Candidate material remains system_restricted and cannot be used as approved public-event or canon state.",
        ],
        "plot_pulse_translation_policy": [
            "Deferred or rejected pressure uses adjudication=null and world_condition_refs=[].",
            "Accepted or downgraded pressure may use adjudication=null only when world_condition_refs cites existing_world_condition_refs and no new fact or state change is created.",
            "If pressure creates a new objective condition, adjudication must commit exactly one event and every StateDelta must cite that event.",
            "Never emit a StateDelta merely to record that pressure was acknowledged.",
        ],
        "candidate_item_contracts": {
            "PublicationCandidate": {
                "publication_candidate_id": "stable id",
                "source_event_ref": "one committed event_id from this adjudication",
                "proposed_scope": "scene_public | local_public | institution_public | city_public | realm_public",
                "scope_ref": "registered concrete scope id",
                "candidate_summary": "publicly knowable event summary, not objective hidden truth",
                "status": "pending",
                "visibility": "system_restricted",
                "based_on": ["the same source event_id"],
                "expires_after_ticks": "positive integer",
            },
            "CanonRevealCandidate": {
                "canon_reveal_candidate_id": "stable id",
                "source_event_ref": "one committed event_id from this adjudication",
                "canon_ref": "existing latent canon ref",
                "exposure_summary": "what was exposed without assuming promotion",
                "status": "pending",
                "visibility": "system_restricted",
                "based_on": ["the same source event_id"],
                "expires_after_ticks": "positive integer",
            },
        },
        "world_adjudication_contract": _world_adjudication_shape(
            fixture["scene_id"], pending_approved_proposal, pending_plot_pulse, scheduled_world_events
        ),
        "required_output_shape": _world_tick_shape(
            fixture["scene_id"], pending_approved_proposal, pending_plot_pulse, scheduled_world_events
        ),
    }
    manifest, contract = _manifest(
        context=context,
        projection_type="WorldControlContext",
        recipient={"role": "world", "instance_id": "world_controller"},
        included=[
            "world_state_ledger",
            "committed_world_events",
            "world_state_delta_ledger",
            "public_canon",
            "public_event_ledger",
            "approved_event_proposal",
            "approved_plot_pulse",
            "scheduled_world_events",
            "legal_character_trigger_refs",
            "existing_world_condition_refs",
        ],
        excluded=["raw_private_memory", "unapproved_event_proposal", "narrator_draft"],
        rule="World receives objective state and approved inputs, never raw character memory or rejected proposals.",
        provenance={
            "scene_id": _provenance(
                "fixture.scene_id",
                fixture.get("scene_id"),
                "exact_copy",
            ),
            "user_request": _provenance(
                "fixture.user_request",
                fixture.get("user_request"),
                "exact_copy_of_player_input",
            ),
            "tick_index": _provenance(
                "runtime_state.tick_index",
                runtime_state.get("tick_index"),
                "exact_copy",
            ),
            "world_state_ledger": _provenance(
                "fixture.world_state_ledger",
                fixture.get("world_state_ledger", {}),
                "exact_copy",
            ),
            "committed_world_events": _provenance(
                "runtime_state.committed_world_events",
                runtime_state.get("committed_world_events", []),
                "exact_copy_for_world_authority",
            ),
            "world_state_delta_ledger": _provenance(
                "runtime_state.world_state_delta_ledger",
                runtime_state.get("world_state_delta_ledger", []),
                "exact_copy_for_world_authority",
            ),
            "public_canon": _provenance(
                "fixture.public_canon",
                fixture.get("public_canon", []),
                "exact_copy",
            ),
            "public_event_ledger": _provenance(
                "fixture.public_event_ledger",
                fixture.get("public_event_ledger", []),
                "exact_copy_for_world_authority",
            ),
            "approved_event_proposal": _provenance(
                "runtime.pending_approved_proposal",
                pending_approved_proposal,
                "exact_copy_after_authority_approval",
            ),
            "approved_plot_pulse": _provenance(
                "runtime.pending_plot_pulse",
                pending_plot_pulse,
                "exact_copy_after_authority_approval",
            ),
            "scheduled_world_events": _provenance(
                "fixture.scheduled_world_events",
                fixture.get("scheduled_world_events", []),
                "filter_consumed_then_attach_source_hash",
            ),
            "checkpoint_policy": _provenance(
                "runtime_state.checkpoint_policy",
                runtime_state.get("checkpoint_policy", {}),
                "exact_copy",
            ),
            "character_registry": _provenance(
                "fixture.characters",
                fixture.get("characters", {}),
                "select_agent_id_and_status; redact_private_memory",
            ),
            "scene_participant_ids": _provenance(
                "fixture.scene_participant_ids",
                fixture.get("scene_participant_ids", []),
                "exact_copy",
            ),
            "legal_character_trigger_refs": _provenance(
                "fixture.visible_observations+fixture.public_event_ledger+runtime_state.committed_world_events",
                {
                    character_id: sorted(
                        legal_character_trigger_refs(
                            fixture, runtime_state, character_id
                        )
                    )
                    for character_id in fixture.get("characters", {})
                },
                "apply_visibility_and_encounter_policy; expose_refs_only",
            ),
            "existing_world_condition_refs": _provenance(
                "fixture.world_condition_registry+fixture.public_event_ledger+runtime_state.committed_world_events+runtime_state.world_state_delta_ledger",
                _existing_world_condition_refs(fixture, runtime_state),
                "collect_registered_condition_refs_without_summary_invention",
            ),
        },
    )
    return context, manifest, contract


def world_repair_context(
    original_context: dict[str, Any],
    rejected_world_tick: dict[str, Any],
    violations: list[dict[str, Any]],
    attempt_index: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    repair_constraints = [
        {
            "kind": item.get("kind"),
            "code": item.get("code"),
            "message": item.get("message"),
        }
        for item in violations
    ]
    context = deepcopy(original_context)
    context["context_type"] = "WorldRepairContextPacket"
    context["previous_world_tick"] = deepcopy(rejected_world_tick)
    context["repair_request"] = {
        "attempt_index": attempt_index,
        "repair_constraints": repair_constraints,
        "rules": [
            "Return a complete replacement WorldTickResult for the same tick_index.",
            "Correct only the listed deterministic identity or schema violations.",
            "Do not treat the failed attempt as a committed event or new story fact.",
            "Preserve Character ownership, visibility boundaries, and the approved input hash.",
        ],
    }
    repair_provenance = {
        field: _provenance(
            f"runtime.original_world_context.{field}",
            value,
            "exact_copy_of_original_validated_projection",
        )
        for field, value in original_context.items()
        if field != "context_type"
    }
    repair_provenance.update(
        {
            "previous_world_tick": _provenance(
                "runtime.rejected_world_tick",
                rejected_world_tick,
                "exact_copy_of_uncommitted_origin_output",
            ),
            "repair_request": _provenance(
                "runtime.world_tick_validation",
                repair_constraints,
                "select_kind_code_and_message_for_origin_only_retry",
            ),
        }
    )
    manifest, contract = _manifest(
        context=context,
        projection_type="WorldRepairContextPacket",
        recipient={"role": "world", "instance_id": "world_controller"},
        included=[
            "original_world_control_context",
            "previous_world_tick",
            "deterministic_repair_constraints",
        ],
        excluded=[
            "private_memory",
            "unapproved_event_proposals",
            "narrator_draft",
            "provider_secrets",
        ],
        rule="Only deterministic Runtime validation feedback returns to the originating World Agent; the rejected tick remains uncommitted.",
        provenance=repair_provenance,
    )
    return context, manifest, contract


def output_syntax_repair_context(
    *,
    role: str,
    instance_id: str,
    original_stage: str,
    original_context_sha256: str,
    invalid_raw_output: str,
    parser_error: str,
    attempt_index: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Project one syntax-only retry back to the exact originating agent."""

    recipient = {"role": role, "instance_id": instance_id}
    context = {
        "context_type": "OutputSyntaxRepairContextPacket",
        "origin_agent_address": deepcopy(recipient),
        "original_protocol_stage": original_stage,
        "original_context_sha256": original_context_sha256,
        "repair_attempt_index": attempt_index,
        "parser_error": parser_error,
        "invalid_raw_output": invalid_raw_output,
        "repair_rules": [
            "Return one valid JSON object and nothing else.",
            "Correct JSON syntax only; preserve every field, value, list item, and semantic claim.",
            "Do not add, remove, rename, summarize, or reinterpret content.",
            "The rejected output is uncommitted and cannot be treated as a new story fact.",
        ],
        "visibility": "system_restricted",
    }
    manifest, contract = _manifest(
        context=context,
        projection_type="OutputSyntaxRepairContextPacket",
        recipient=recipient,
        included=[
            "origin_agent_address",
            "original_protocol_stage",
            "original_context_sha256",
            "invalid_raw_output",
            "parser_error",
        ],
        excluded=[
            "full_original_projected_context",
            "other_agent_contexts",
            "provider_secrets",
            "unrelated_runtime_state",
        ],
        rule="Only the originating agent receives its own rejected raw output and parser diagnostic for one syntax-only retry.",
        provenance={
            "origin_agent_address": _provenance(
                "kernel.validated_projection.recipient",
                recipient,
                "exact_copy",
            ),
            "original_protocol_stage": _provenance(
                "kernel.validated_projection.stage",
                original_stage,
                "exact_copy",
            ),
            "original_context_sha256": _provenance(
                "kernel.validated_projection.context_sha256",
                original_context_sha256,
                "exact_copy",
            ),
            "repair_attempt_index": _provenance(
                "kernel.output_syntax_repair_counter",
                attempt_index,
                "exact_copy",
            ),
            "parser_error": _provenance(
                "provider.json_parser.error",
                parser_error,
                "exact_copy",
            ),
            "invalid_raw_output": _provenance(
                "provider.rejected_raw_output",
                invalid_raw_output,
                "exact_copy_to_origin_only",
            ),
        },
    )
    return context, manifest, contract


def router_context(
    fixture: dict[str, Any], decision_request: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context = {
        "context_type": "RouterContextPacket",
        "scene_id": fixture["scene_id"],
        "decision_request": deepcopy(decision_request),
        "decision_request_sha256": _content_hash(decision_request),
        "character_registry": _character_registry(fixture),
        "routing_limits": [
            "Route only; do not add intent, action, fact, consequence, or prose.",
            "The recipient must match decision_request.target_character_id.",
        ],
        "required_output_shape": {
            "route_plan": {
                "message_type": "RoutePlan",
                "route_id": "stable id",
                "request_id": "copied request id",
                "request_sha256": _content_hash(decision_request),
                "recipient_agent_id": "registered character id",
                "projection_profile": "character_private_owner_view",
                "reason": "routing basis only",
                "visibility": "system_restricted",
                "authority_basis": ["routing policy ref"],
                "based_on": ["request ref"],
            }
        },
    }
    manifest, contract = _manifest(
        context=context,
        projection_type="RouterContextPacket",
        recipient={"role": "router", "instance_id": "character_router"},
        included=["decision_request", "character_registry.ids"],
        excluded=["private_memory", "world_state_ledger", "latent_canon", "plot_plan"],
        rule="Router sees routable identities and the World request, not story-private context.",
        provenance={
            "scene_id": _provenance(
                "fixture.scene_id",
                fixture.get("scene_id"),
                "exact_copy",
            ),
            "decision_request": _provenance(
                "world_tick.next_directive.decision_request",
                decision_request,
                "exact_copy",
            ),
            "decision_request_sha256": _provenance(
                "world_tick.next_directive.decision_request",
                decision_request,
                "derive_sha256_from_exact_request",
            ),
            "character_registry": _provenance(
                "fixture.characters",
                fixture.get("characters", {}),
                "select_agent_id_and_status; redact_private_memory",
            ),
        },
    )
    return context, manifest, contract


def character_decision_context(
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
    decision_request: dict[str, Any],
    route_plan: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    character_id = route_plan["recipient_agent_id"]
    character = fixture["characters"][character_id]
    private_memory_query, memory_retrieval_record = _private_memory_query(
        character, fixture
    )
    context = {
        "context_type": "WorldDrivenCharacterContextPacket",
        "scene_id": fixture["scene_id"],
        "recipient_agent_id": character_id,
        "decision_request": deepcopy(decision_request),
        "visible_observations": deepcopy(fixture.get("visible_observations", {}).get(character_id, [])),
        "visible_committed_events": visible_event_views(
            runtime_state.get("committed_world_events", []), character_id, fixture
        ),
        "private_memory_query": private_memory_query,
        "memory_retrieval_record": memory_retrieval_record,
        "encountered_public_events": encountered_public_events(fixture, character_id),
        "public_canon": deepcopy(fixture.get("public_canon", [])),
        "authority_limits": [
            "Decide only this character's intent and attempted action.",
            "Do not declare objective success, another character's mind, or hidden world truth.",
            "desired_effect is a request, not a committed consequence.",
        ],
        "forbidden_sources": [
            "raw_world_state_ledger",
            "other_private_memory",
            "latent_canon",
            "full_committed_event",
            "plot_structure_plan",
        ],
        "required_output_shape": {
            "event_proposal": {
                "message_type": "EventProposal",
                "scene_id": fixture["scene_id"],
                "proposal_id": "stable id",
                "request_id": decision_request["request_id"],
                "actor_id": character_id,
                "action_type": "speech | physical | cognitive_commitment | refusal | wait",
                "intent_summary": "private owner intent",
                "public_surface": "what could become externally observable",
                "private_intent": "owner-private motivation",
                "desired_effect": "requested effect, never an outcome declaration",
                "disclosure_limits": [],
                "interiority_grant": {
                    "grant_status": "none | authorized",
                    "source_field": "none | intent_summary | private_intent",
                    "access_mode": "none | intent | self_reported_state",
                    "scope_limit": "none | one_beat",
                },
                "visibility_request": "system_restricted",
                "visibility": "system_restricted",
                "authority_basis": ["character ownership and request refs"],
                "based_on": [],
            }
        },
    }
    manifest, contract = _manifest(
        context=context,
        projection_type="WorldDrivenCharacterContextPacket",
        recipient={"role": "character", "instance_id": character_id},
        included=[
            "decision_request",
            "own_private_memory",
            "visible_observations",
            "visible_committed_events",
            "encountered_public_events",
            "public_canon",
            "memory_retrieval_record",
        ],
        excluded=["world_state_ledger", "other_private_memory", "latent_canon", "plot_structure_plan"],
        rule="Owner-only memory plus visibility-backed event surfaces.",
        provenance={
            "scene_id": _provenance(
                "fixture.scene_id",
                fixture.get("scene_id"),
                "exact_copy",
            ),
            "recipient_agent_id": _provenance(
                "validated_route_plan.recipient_agent_id",
                route_plan.get("recipient_agent_id"),
                "exact_copy_after_route_validation",
            ),
            "decision_request": _provenance(
                "world_tick.next_directive.decision_request",
                decision_request,
                "exact_copy_after_authority_review",
            ),
            "visible_observations": _provenance(
                f"fixture.visible_observations.{character_id}",
                fixture.get("visible_observations", {}).get(character_id, []),
                "owner_key_exact_copy",
            ),
            "visible_committed_events": _provenance(
                "runtime_state.committed_world_events",
                runtime_state.get("committed_world_events", []),
                "filter_event_visible_to; select_event_id_and_public_surface; redact_actors_observer_refs_and_limits",
            ),
            "private_memory_query": _provenance(
                f"fixture.characters.{character_id}.private_memory",
                character.get("private_memory", []),
                "filter_status; rank_salience_recency; cap_items; no_compression",
            ),
            "memory_retrieval_record": _provenance(
                f"fixture.characters.{character_id}.private_memory",
                character.get("private_memory", []),
                "derive_selection_audit_without_story_summary",
            ),
            "encountered_public_events": _provenance(
                "fixture.public_event_ledger",
                fixture.get("public_event_ledger", []),
                "filter_explicit_encounter_refs; apply_public_event_allowlist",
            ),
            "public_canon": _provenance(
                "fixture.public_canon",
                fixture.get("public_canon", []),
                "exact_copy",
            ),
        },
    )
    return context, manifest, contract


def authority_review_context(
    fixture: dict[str, Any],
    runtime_state: dict[str, Any],
    subject_type: str,
    subject: dict[str, Any],
    source_context: dict[str, Any],
    run_nonce: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    subject_ref = _subject_ref(subject_type, subject)
    subject_sha256 = _content_hash(subject)
    global_audit_context = {
        "world_state_ledger": deepcopy(fixture.get("world_state_ledger", {})),
        "public_canon": deepcopy(fixture.get("public_canon", [])),
        "public_event_ledger": deepcopy(fixture.get("public_event_ledger", [])),
        "committed_world_events": deepcopy(runtime_state.get("committed_world_events", [])),
        "character_memory_by_owner": {
            owner: deepcopy(data.get("private_memory", []))
            for owner, data in fixture.get("characters", {}).items()
        },
    }
    forbidden_protocol_ids = sorted(
        str(identity)
        for identity in runtime_state.get("used_protocol_ids", [])
        if isinstance(identity, str)
    )
    review_context_sha256 = _content_hash(
        {
            "run_nonce": run_nonce,
            "scene_id": fixture["scene_id"],
            "subject_type": subject_type,
            "subject_ref": subject_ref,
            "subject_sha256": subject_sha256,
            "source_context": source_context,
            "global_audit_context": global_audit_context,
            "forbidden_protocol_ids": forbidden_protocol_ids,
        }
    )
    context = {
        "context_type": "AuthorityReviewContext",
        "scene_id": fixture["scene_id"],
        "review_scope": "semantic_authority_and_grounding",
        "subject_type": subject_type,
        "subject_ref": subject_ref,
        "subject_sha256": subject_sha256,
        "run_nonce": run_nonce,
        "review_context_sha256": review_context_sha256,
        "forbidden_protocol_ids": forbidden_protocol_ids,
        "subject": deepcopy(subject),
        "source_context": deepcopy(source_context),
        "global_audit_context": global_audit_context,
        "judge_limits": [
            "Judge may allow, warn, require repair, or block.",
            "Judge must not rewrite the subject or create replacement literary content.",
            "Judge output is audit-only and is not a new story fact.",
            "For repair_required, required_repairs must contain code-only objects and no free-text secret-bearing explanation.",
        ],
        "reviewed_fields_policy": {
            "required_subject_fields": sorted(
                AUTHORITY_REQUIRED_REVIEW_FIELDS.get(subject_type, set())
            ),
            "allowed_path_forms": [
                "subject-relative path such as committed_events[0].visibility.scope",
                "subject-prefixed path such as subject.prose",
                "source_context-prefixed audit path",
                "global_audit_context-prefixed audit path",
            ],
            "coverage_rule": "Every required_subject_field must be named directly or through its subject-prefixed form before allow or warning.",
        },
        "origin_safe_repair_contract": {
            "allowed_repair_codes": [
                "remove_unsupported_fact",
                "remove_other_mind_claim",
                "reduce_certainty",
                "remove_outcome_declaration",
                "restore_visibility_scope",
                "preserve_owner_identity",
                "schema_only",
            ],
            "required_item_shape": {
                "repair_code": "one allowed code",
                "field_path": "subject field to repair",
            },
            "forbidden": "free-text repair instructions or hidden global facts",
        },
        "required_output_shape": {
            "authority_review": {
                "message_type": "AuthorityReview",
                "review_id": "new stable id not present in forbidden_protocol_ids",
                "subject_type": subject_type,
                "subject_ref": subject_ref,
                "subject_sha256": subject_sha256,
                "run_nonce": run_nonce,
                "review_context_sha256": review_context_sha256,
                "verdict": "allow | warning | repair_required | block",
                "findings": [],
                "required_repairs": [
                    {
                        "repair_code": "allowed code; only when repair_required",
                        "field_path": "subject field path",
                    }
                ],
                "authority_basis": [],
                "reviewed_fields": [],
                "visibility": "system_restricted",
                **(
                    {
                        "claim_map": [
                            {
                                "claim_id": "exact id from subject.claim_units",
                                "claim_sha256": "exact hash from subject.claim_units",
                                "claim_text": "exact text from subject.claim_units",
                                "claim_type": "event | visibility | causality | interiority | dialogue | canon",
                                "source_refs": ["committed event refs only"],
                                "certainty": "same or weaker than source",
                                "visibility_scope": "scope preserved from source",
                                "grounding_status": "supported | unsupported | overclaim",
                            }
                        ]
                    }
                    if subject_type == "narration"
                    else {}
                ),
            }
        },
    }
    manifest, contract = _manifest(
        context=context,
        projection_type="AuthorityReviewContext",
        recipient={"role": "authority", "instance_id": "authority_judge"},
        included=[
            "subject",
            "source_context",
            "global_audit_context",
            "forbidden_protocol_ids",
        ],
        excluded=["runtime_auth_tokens", "provider_secrets"],
        rule="Audit-only global view; output cannot mutate or author story material.",
        provenance={
            "scene_id": _provenance(
                "fixture.scene_id",
                fixture.get("scene_id"),
                "exact_copy",
            ),
            "subject_type": _provenance(
                "runtime.review_subject_type",
                subject_type,
                "exact_copy_from_kernel_stage",
            ),
            "subject_ref": _provenance(
                f"runtime.review_subject.{subject_type}",
                subject,
                "derive_subject_ref_from_registered_subject_type",
            ),
            "subject_sha256": _provenance(
                f"runtime.review_subject.{subject_type}",
                subject,
                "derive_sha256_from_exact_subject",
            ),
            "run_nonce": _provenance(
                "runtime.run_nonce",
                run_nonce,
                "exact_copy_from_kernel_run",
            ),
            "review_context_sha256": _provenance(
                "runtime.review_context_binding",
                {
                    "run_nonce": run_nonce,
                    "scene_id": fixture["scene_id"],
                    "subject_type": subject_type,
                    "subject_ref": subject_ref,
                    "subject_sha256": subject_sha256,
                    "source_context": source_context,
                    "global_audit_context": global_audit_context,
                    "forbidden_protocol_ids": forbidden_protocol_ids,
                },
                "derive_sha256_from_exact_review_context",
            ),
            "forbidden_protocol_ids": _provenance(
                "runtime_state.used_protocol_ids",
                runtime_state.get("used_protocol_ids", []),
                "sort_and_copy_for_authority_id_replay_prevention",
            ),
            "subject": _provenance(
                f"runtime.review_subject.{subject_type}", subject, "exact_copy"
            ),
            "source_context": _provenance(
                f"runtime.projected_context.{source_context.get('context_type', 'unknown')}",
                source_context,
                "exact_copy_for_audit",
            ),
            "global_audit_context": _provenance(
                "fixture_and_runtime.audit_sources",
                context["global_audit_context"],
                "assemble_full_audit_view; system_restricted",
            ),
        },
    )
    return context, manifest, contract


def character_repair_context(
    original_context: dict[str, Any],
    rejected_proposal: dict[str, Any],
    review: dict[str, Any],
    attempt_index: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context = deepcopy(original_context)
    context["context_type"] = "CharacterRepairContextPacket"
    context["previous_event_proposal"] = deepcopy(rejected_proposal)
    context["repair_request"] = {
        "subject_ref": review["subject_ref"],
        "attempt_index": attempt_index,
        "origin_safe_required_repairs": deepcopy(review.get("required_repairs", [])),
        "rules": [
            "Submit a new EventProposal with a new proposal_id.",
            "Preserve actor_id and request_id ownership.",
            "Do not infer hidden facts from the repair request.",
            "Repair instructions are constraints, not replacement literary content.",
        ],
    }
    repair_provenance = {
        field: _provenance(
            f"runtime.original_character_context.{field}",
            value,
            "exact_copy_of_original_validated_projection",
        )
        for field, value in original_context.items()
        if field != "context_type"
    }
    repair_provenance.update(
        {
            "previous_event_proposal": _provenance(
                "runtime.rejected_event_proposal",
                rejected_proposal,
                "exact_copy_of_uncommitted_origin_output",
            ),
            "repair_request": _provenance(
                "authority_review.required_repairs",
                review.get("required_repairs", []),
                "select_code_and_field_path_only; redact_findings_and_global_audit_context",
            ),
        }
    )
    manifest, contract = _manifest(
        context=context,
        projection_type="CharacterRepairContextPacket",
        recipient={
            "role": "character",
            "instance_id": str(original_context.get("recipient_agent_id")),
        },
        included=[
            "original_character_context",
            "previous_event_proposal",
            "origin_safe_required_repairs",
        ],
        excluded=["global_audit_context", "other_private_memory", "hidden_world_state", "authority_findings"],
        rule="Only Judge-declared origin-safe repair instructions return to the originating Character Agent.",
        provenance=repair_provenance,
    )
    return context, manifest, contract


def plot_pulse_context(
    fixture: dict[str, Any], runtime_state: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    public_events = [
        _public_event_surface(event)
        for event in runtime_state.get("committed_world_events", [])
        if _event_has_public_surface(event)
    ]
    context = {
        "context_type": "PlotPulseContext",
        "scene_id": fixture["scene_id"],
        "structure_goal": fixture.get("structure_goal"),
        "public_relationship_summary": deepcopy(
            fixture.get("public_relationship_summary", {})
        ),
        "public_canon": deepcopy(fixture.get("public_canon", [])),
        "public_event_ledger": public_event_views(fixture.get("public_event_ledger", [])),
        "committed_public_event_surfaces": public_events,
        "pressure_ledger": deepcopy(runtime_state.get("pressure_ledger", [])),
        "option_topology": deepcopy(runtime_state.get("option_topology", {})),
        "authority_limits": [
            "Create pressure, not facts, choices, outcomes, or destiny.",
            "A pulse requiring a new world fact must be translated by World before it exists.",
        ],
        "required_output_shape": {
            "plot_pulse": {
                "message_type": "PlotPulse",
                "scene_id": fixture["scene_id"],
                "pulse_id": "stable id",
                "pressure_kind": " | ".join(sorted(PLOT_PRESSURE_KINDS)),
                "scope": " | ".join(sorted(PLOT_SCOPES)),
                "duration": " | ".join(sorted(PLOT_DURATIONS)),
                "affected_options": [],
                "non_forcing_clause": "explicit refusal and alternative paths",
                "world_fact_dependency": [],
                "forbidden_outcomes": [],
                "visibility": "system_restricted",
                "budget_cost": {},
                "option_topology_check": {
                    "meaningful_option_count_before": "integer",
                    "meaningful_option_count_after": "integer >= 2",
                    "refusal_path_preserved": True,
                    "non_plot_compliant_path_preserved": True,
                    "converges_on_single_outcome": False,
                },
                "authority_basis": [],
                "based_on": [],
            }
        },
    }
    manifest, contract = _manifest(
        context=context,
        projection_type="PlotPulseContext",
        recipient={"role": "plot", "instance_id": "plot_checkpoint"},
        included=["structure_goal", "public_relationship_summary", "public_event_surfaces", "pressure_ledger", "option_topology"],
        excluded=["world_state_ledger", "private_memory", "latent_canon", "candidate_material"],
        rule="Plot sees structural and public summaries only.",
        provenance={
            "scene_id": _provenance(
                "fixture.scene_id",
                fixture.get("scene_id"),
                "exact_copy",
            ),
            "structure_goal": _provenance(
                "fixture.structure_goal",
                fixture.get("structure_goal"),
                "exact_copy_of_public_structural_goal",
            ),
            "public_relationship_summary": _provenance(
                "fixture.public_relationship_summary",
                fixture.get("public_relationship_summary", {}),
                "exact_copy_from_public_only_field; never_fallback_to_private_relationship_summary",
            ),
            "public_canon": _provenance(
                "fixture.public_canon",
                fixture.get("public_canon", []),
                "exact_copy",
            ),
            "public_event_ledger": _provenance(
                "fixture.public_event_ledger",
                fixture.get("public_event_ledger", []),
                "apply_public_event_allowlist; redact_internal_fields",
            ),
            "committed_public_event_surfaces": _provenance(
                "runtime_state.committed_world_events",
                runtime_state.get("committed_world_events", []),
                "filter_public_scope; select_event_id_and_public_surface; redact_private_fields",
            ),
            "pressure_ledger": _provenance(
                "runtime_state.pressure_ledger",
                runtime_state.get("pressure_ledger", []),
                "exact_copy_of_approved_pressure_records",
            ),
            "option_topology": _provenance(
                "runtime_state.option_topology",
                runtime_state.get("option_topology", {}),
                "exact_copy_of_registered_options",
            ),
        },
    )
    return context, manifest, contract


def narration_checkpoint_context(
    fixture: dict[str, Any], runtime_state: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    start = runtime_state.get("last_narrated_event_index", 0)
    source_events = runtime_state.get("committed_world_events", [])[start:]
    focal_agent_id = fixture.get("pov_contract", {}).get("focal_agent_id")
    if isinstance(focal_agent_id, str) and focal_agent_id in fixture.get("characters", {}):
        source_events = [
            event
            for event in source_events
            if event_visible_to(event, focal_agent_id, fixture)
        ]
    else:
        # Missing POV identity is security-critical. Fixture validation blocks
        # the run; this empty projection is defense in depth against direct use.
        source_events = []
    checkpoint = {
        "checkpoint_id": f"ncp_{fixture['trace_id']}_{runtime_state['tick_index']}",
        "scene_id": fixture["scene_id"],
        "event_views": [
            _narrator_event_view(event, focal_agent_id) for event in source_events
        ],
        "pov_contract": deepcopy(fixture.get("pov_contract", {})),
        "narration_bounds": _narrator_bounds_view(fixture.get("narration_bounds", {})),
        "source_event_refs": [event.get("event_id") for event in source_events],
    }
    context = {
        "context_type": "NarrationCheckpoint",
        "narration_checkpoint": checkpoint,
        "forbidden_sources": [
            "world_state_ledger",
            "private_memory",
            "event_proposals",
            "authority_findings",
            "plot_pulses",
            "candidate_material",
        ],
        "required_output_shape": {"prose": "grounded player-facing prose"},
    }
    manifest, contract = _manifest(
        context=context,
        projection_type="NarrationCheckpoint",
        recipient={"role": "narrator", "instance_id": "narrator_checkpoint"},
        included=["committed_event_views", "pov_contract", "narration_bounds"],
        excluded=["world_state_ledger", "private_memory", "event_proposals", "plot_pulses", "candidates"],
        rule="Narrator receives only committed, visibility-bounded event views.",
        provenance={
            "narration_checkpoint": _provenance(
                "runtime_state.committed_world_events+fixture.pov_contract+fixture.narration_bounds",
                {
                    "source_events": source_events,
                    "pov_contract": fixture.get("pov_contract", {}),
                    "narration_bounds": fixture.get("narration_bounds", {}),
                },
                "filter_focal_visibility; select_observable_surface; redact_actors_observer_refs_limits_and_secret_bounds; owner_filter_interiority",
            )
        },
    )
    return context, manifest, contract


def narration_repair_context(
    original_context: dict[str, Any],
    rejected_subject: dict[str, Any],
    review: dict[str, Any],
    attempt_index: int,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    context = deepcopy(original_context)
    context["context_type"] = "NarrationRepairContextPacket"
    context["previous_narration"] = {
        "source_checkpoint_id": rejected_subject.get("source_checkpoint_id"),
        "source_event_refs": deepcopy(rejected_subject.get("source_event_refs", [])),
        "prose": rejected_subject.get("prose", ""),
    }
    context["repair_request"] = {
        "subject_ref": review["subject_ref"],
        "attempt_index": attempt_index,
        "origin_safe_required_repairs": deepcopy(review.get("required_repairs", [])),
        "rules": [
            "Return a complete replacement prose string grounded in the same NarrationCheckpoint.",
            "Apply only the code-only origin_safe_required_repairs.",
            "Do not infer hidden facts from the existence of a repair request.",
            "Do not introduce a new event, mind claim, visibility scope, or causal claim.",
        ],
    }
    repair_provenance = {
        field: _provenance(
            f"runtime.original_narration_context.{field}",
            value,
            "exact_copy_of_original_validated_projection",
        )
        for field, value in original_context.items()
        if field not in {"context_type", "narration_checkpoint"}
    }
    repair_provenance.update(
        {
            "narration_checkpoint": _provenance(
                "runtime.original_narration_context.narration_checkpoint",
                original_context.get("narration_checkpoint", {}),
                "exact_copy_of_original_legal_view",
            ),
            "previous_narration": _provenance(
                "runtime.rejected_narration_subject",
                rejected_subject,
                "select_checkpoint_refs_and_prose; exclude_claim_map_and_audit_context",
            ),
            "repair_request": _provenance(
                "authority_review.required_repairs",
                review.get("required_repairs", []),
                "select_code_and_field_path_only; redact_findings_and_global_audit_context",
            ),
        }
    )
    manifest, contract = _manifest(
        context=context,
        projection_type="NarrationRepairContextPacket",
        recipient={"role": "narrator", "instance_id": "narrator_checkpoint"},
        included=[
            "original_narration_checkpoint",
            "previous_narration",
            "origin_safe_required_repairs",
        ],
        excluded=[
            "global_audit_context",
            "authority_findings",
            "world_state_ledger",
            "private_memory",
            "candidate_material",
        ],
        rule="Only the original legal Narrator view, rejected prose, and code-only repairs return to Narrator.",
        provenance=repair_provenance,
    )
    return context, manifest, contract


def _character_registry(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"agent_id": character_id, "status": data.get("status", "available")}
        for character_id, data in fixture.get("characters", {}).items()
    ]


def _existing_world_condition_refs(
    fixture: dict[str, Any], runtime_state: dict[str, Any]
) -> list[str]:
    refs = {str(ref) for ref in fixture.get("world_condition_registry", [])}
    refs.update(
        str(item["publication_id"])
        for item in fixture.get("public_event_ledger", [])
        if isinstance(item, dict) and item.get("publication_id")
    )
    refs.update(
        str(item["event_id"])
        for item in runtime_state.get("committed_world_events", [])
        if isinstance(item, dict) and item.get("event_id")
    )
    refs.update(
        str(item["delta_id"])
        for item in runtime_state.get("world_state_delta_ledger", [])
        if isinstance(item, dict) and item.get("delta_id")
    )
    return sorted(refs)


def _scheduled_world_event_views(
    fixture: dict[str, Any], runtime_state: dict[str, Any]
) -> list[dict[str, Any]]:
    consumed = set(runtime_state.get("consumed_scheduled_world_event_refs", []))
    views: list[dict[str, Any]] = []
    for record in fixture.get("scheduled_world_events", []):
        if not isinstance(record, dict) or not record.get("schedule_id"):
            continue
        if record["schedule_id"] in consumed:
            continue
        views.append(
            {
                "schedule_id": record["schedule_id"],
                "schedule_sha256": _content_hash(record),
                "record": deepcopy(record),
            }
        )
    return views


def _private_memory_query(
    character: dict[str, Any], fixture: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    raw_policy = fixture.get("character_memory_retrieval_policy", {})
    max_items = max(0, int(raw_policy.get("max_items", 16)))
    allowed_statuses = set(raw_policy.get("allowed_statuses", ["active", "contested"]))
    salience_rank = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    candidates: list[tuple[int, int, dict[str, Any]]] = []
    excluded_refs: list[dict[str, str]] = []

    for index, memory in enumerate(character.get("private_memory", [])):
        if not isinstance(memory, dict):
            excluded_refs.append({"memory_ref": f"index:{index}", "reason": "invalid_record"})
            continue
        status = str(memory.get("memory_status", "active"))
        memory_ref = str(memory.get("delta_id", f"index:{index}"))
        if status not in allowed_statuses:
            excluded_refs.append({"memory_ref": memory_ref, "reason": f"status:{status}"})
            continue
        salience = str(memory.get("salience", memory.get("certainty", "low")))
        candidates.append((salience_rank.get(salience, 0), index, memory))

    candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    selected = [deepcopy(item[2]) for item in candidates[:max_items]]
    for _, _, memory in candidates[max_items:]:
        excluded_refs.append(
            {
                "memory_ref": str(memory.get("delta_id", "unidentified")),
                "reason": "retrieval_limit",
            }
        )
    record = {
        "policy": {
            "max_items": max_items,
            "allowed_statuses": sorted(allowed_statuses),
            "ranking": "explicit salience, then certainty fallback, then later list position",
            "compression": "none; selected records are copied unchanged",
        },
        "selected_refs": [
            str(memory.get("delta_id", "unidentified")) for memory in selected
        ],
        "excluded_refs": excluded_refs,
    }
    return selected, record


def _narrator_event_view(
    event: dict[str, Any], focal_agent_id: str | None
) -> dict[str, Any]:
    interiority = event.get("authorized_interiority", [])
    if focal_agent_id:
        interiority = [
            item
            for item in interiority
            if isinstance(item, dict) and item.get("subject_id") == focal_agent_id
        ]
    return {
        "event_id": event.get("event_id"),
        "event_kind": event.get("event_kind"),
        # World supplies an observable fact surface, never pre-rendered prose.
        "observable_surface": event.get("public_surface"),
        "visibility": projected_visibility(event),
        "authorized_interiority": deepcopy(interiority),
        "spoken_line_records": deepcopy(event.get("spoken_line_records", [])),
    }


def _public_event_surface(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": event.get("event_id"),
        "public_surface": event.get("public_surface") or event.get("outcome"),
        "visibility": projected_visibility(event),
    }


def _narrator_bounds_view(bounds: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(bounds, dict):
        return {}
    safe_fields = {
        "tense",
        "voice",
        "style",
        "max_words",
        "pacing",
        "certainty_policy",
        "dialogue_policy",
    }
    return {
        field: deepcopy(bounds[field])
        for field in safe_fields
        if field in bounds
    }


def _event_has_public_surface(event: dict[str, Any]) -> bool:
    visibility = event.get("visibility", {})
    scope = visibility.get("scope") if isinstance(visibility, dict) else visibility
    return scope in {"scene_public", "local_public", "institution_public", "city_public", "realm_public"}


def _subject_ref(subject_type: str, subject: dict[str, Any]) -> str | None:
    keys = {
        "character_decision_request": "request_id",
        "event_proposal": "proposal_id",
        "world_adjudication": "adjudication_id",
        "plot_pulse": "pulse_id",
        "plot_pulse_disposition": "pulse_id",
        "narration": "checkpoint_id",
    }
    key = keys.get(subject_type)
    if subject_type == "narration":
        return subject.get("checkpoint_id") or subject.get("source_checkpoint_id")
    return subject.get(key) if key else None


def _world_tick_shape(
    scene_id: str,
    pending_approved_proposal: dict[str, Any] | None,
    pending_plot_pulse: dict[str, Any] | None,
    scheduled_world_events: list[dict[str, Any]],
) -> dict[str, Any]:
    has_adjudication_input = bool(
        pending_approved_proposal or pending_plot_pulse or scheduled_world_events
    )
    adjudication_shape = (
        _world_adjudication_shape(
            scene_id,
            pending_approved_proposal,
            pending_plot_pulse,
            scheduled_world_events,
        )
        if has_adjudication_input
        else None
    )
    consumed_input_refs: list[Any] = []
    if isinstance(adjudication_shape, dict):
        consumed_input_refs.append(adjudication_shape["input_ref"])
    if pending_plot_pulse:
        pulse_id = pending_plot_pulse.get("pulse_id")
        if pulse_id not in consumed_input_refs:
            consumed_input_refs.append(pulse_id)
    return {
        "world_tick_result": {
            "message_type": "WorldTickResult",
            "scene_id": "parent scene id",
            "tick_id": "stable id",
            "tick_index": "current integer tick",
            "consumed_input_refs": consumed_input_refs,
            "adjudication": adjudication_shape,
            "plot_pulse_disposition": (
                _plot_pulse_disposition_shape(pending_plot_pulse)
            ),
            "next_directive": {
                "directive_type": "request_character_decision | continue_world | finish_scene",
                "reason": "simulation-control basis",
                "decision_request": {
                    "message_type": "CharacterDecisionRequest",
                    "scene_id": scene_id,
                    "request_id": "stable id",
                    "source_tick_id": "must exactly equal this result's tick_id",
                    "target_character_id": "one registered character id",
                    "agency_question": "neutral question that does not prefer an answer",
                    "visible_trigger_refs": ["visibility-backed refs only"],
                    "response_contract": {
                        "output_type": "EventProposal",
                        "allowed_action_types": [
                            "speech",
                            "physical",
                            "cognitive_commitment",
                            "refusal",
                            "wait",
                        ],
                    },
                    "visibility": "system_restricted",
                    "authority_basis": ["why World may request, but not answer, this choice"],
                },
            },
            "checkpoint_state": {
                "committed_beats": "integer",
                "dialogue_turns": "integer",
            },
            "authority_basis": ["world simulation authority refs"],
            "visibility": "system_restricted",
            "based_on": [],
        }
    }


def _plot_pulse_disposition_shape(
    pending_plot_pulse: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if not pending_plot_pulse:
        return None
    return {
        "pulse_id": pending_plot_pulse.get("pulse_id"),
        "pulse_sha256": pending_plot_pulse.get("pulse_sha256"),
        "decision": "accepted | downgraded | deferred | rejected",
        "translation_summary": "how World will or will not translate this pressure",
        "world_condition_refs": [],
    }


def _world_adjudication_shape(
    scene_id: str,
    pending_approved_proposal: dict[str, Any] | None,
    pending_plot_pulse: dict[str, Any] | None,
    scheduled_world_events: list[dict[str, Any]],
) -> dict[str, Any]:
    proposal: dict[str, Any] = {}
    if pending_approved_proposal:
        proposal = pending_approved_proposal.get("original_proposal", {})
        input_type = "event_proposal"
        input_ref = proposal.get("proposal_id")
        input_sha256 = pending_approved_proposal.get("proposal_sha256")
    elif pending_plot_pulse:
        input_type = "plot_pulse"
        input_ref = pending_plot_pulse.get("pulse_id")
        input_sha256 = pending_plot_pulse.get("pulse_sha256")
    elif scheduled_world_events:
        input_type = "scheduled_world_event"
        input_ref = "one registered schedule_id"
        input_sha256 = "matching schedule_sha256"
    else:
        input_type = "no approved input"
        input_ref = "adjudication must be null"
        input_sha256 = "adjudication must be null"

    interiority_shape: list[dict[str, Any]] = []
    grant = proposal.get("interiority_grant")
    if isinstance(grant, dict) and grant.get("grant_status") == "authorized":
        source_field = grant.get("source_field")
        source_content = proposal.get(source_field)
        interiority_shape = [
            {
                "subject_id": proposal.get("actor_id"),
                "access_mode": grant.get("access_mode"),
                "content": source_content,
                "authority_basis": [proposal.get("proposal_id")],
                "scope_limit": grant.get("scope_limit"),
                "source_proposal_id": proposal.get("proposal_id"),
                "source_field": source_field,
                "source_sha256": _content_hash(source_content),
            }
        ]

    spoken_line_shape: list[dict[str, Any]] = []
    if proposal.get("action_type") == "speech":
        public_surface = proposal.get("public_surface")
        spoken_line_shape = [
            {
                "status": "paraphrased",
                "speaker_id": proposal.get("actor_id"),
                "semantic_content": public_surface,
                "source_proposal_id": proposal.get("proposal_id"),
                "source_field": "public_surface",
                "source_sha256": _content_hash(public_surface),
            }
        ]
    return {
        "adjudication_id": "stable id",
        "input_type": input_type,
        "input_ref": input_ref,
        "input_sha256": input_sha256,
        "outcome_type": "success | failure | partial_success | blocked | delayed | contested",
        "outcome_summary": "objective consequence without prose or private mind invention",
        "applicable_rules": [],
        "constraint_basis": [],
        "adjudication_basis": "auditable rule-and-constraint summary, not chain-of-thought",
        "uncertainty_model": {
            "mode": "deterministic | bounded_judgment | seeded_random",
            "evidence_refs": [],
            "uncertainty_sources": [],
        },
        "failed_alternatives": [
            {
                "outcome_type": "one of success | failure | partial_success | blocked | delayed | contested, excluding the selected outcome_type",
                "rejected_by": ["rule or constraint refs"],
            }
        ],
        "committed_events": [
            {
                "message_type": "CommittedWorldEvent",
                "scene_id": scene_id,
                "event_id": "stable id",
                "source_input_type": input_type,
                "source_input_ref": input_ref,
                "event_kind": "speech | physical | refusal | wait | mixed",
                "actors": [proposal.get("actor_id")] if proposal else [],
                "outcome": "objective committed result",
                "public_surface": "only the observable committed surface",
                "visibility": {
                    "scope": "scene_pair | scene_public | other declared executable scope",
                    "scope_ref": "concrete scene, institution, place, city, or realm scope id",
                    "observer_refs": [
                        "registered Character ids only; use scene_participant_ids for scene_public; never put a scope id here"
                    ],
                    "limits": "what observers still cannot know or infer as fact",
                },
                "authorized_interiority": interiority_shape,
                "spoken_line_records": spoken_line_shape,
                "causal_basis": [
                    input_ref,
                    "the exact adjudication_id generated for this object",
                ],
                "commit_status": "committed",
            }
        ],
        "state_deltas": [
            {
                "delta_id": "stable id",
                "target_layer": "world_state_ledger",
                "target_id": "state key or entity id",
                "change_kind": "objective transition kind",
                "after_summary": "objective post-change summary",
                "based_on": ["one committed event_id from this adjudication"],
            }
        ],
        "visibility_results": [
            {
                "visibility_result_id": "stable id",
                "source_event_id": "the committed event_id above",
                "scope": "exact committed event visibility.scope",
                "scope_ref": "exact committed event visibility.scope_ref",
                "observer_refs": [
                    "exact committed event Character observer ids; never a scope id"
                ],
                "limits": "exact committed event visibility limits",
            }
        ],
        "publication_candidates": [],
        "canon_reveal_candidates": [],
    }


def _manifest(
    *,
    context: dict[str, Any],
    projection_type: str,
    recipient: dict[str, str],
    included: list[str],
    excluded: list[str],
    rule: str,
    provenance: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    context_sha256 = _content_hash(context)
    provenance = provenance or {}
    field_projections = []
    leaf_projections = []
    for field in sorted(context):
        value_sha256 = _content_hash(context[field])
        source = provenance.get(field, {})
        if field in provenance:
            mapping_mode = "source_projection"
            default_source_path = f"source.{projection_type}.{field}"
            default_operation = "declared_source_projection"
        elif field in _KERNEL_POLICY_FIELDS.get(projection_type, set()):
            mapping_mode = "kernel_policy_derivation"
            default_source_path = f"kernel_policy.{projection_type}.{field}"
            default_operation = "registered_kernel_policy_derivation"
        else:
            mapping_mode = "unanchored"
            default_source_path = f"unanchored.{projection_type}.{field}"
            default_operation = "unanchored_projection_blocked"
        source_path = source.get("source_path", default_source_path)
        source_value = source.get("_source_value", context[field])
        source_value_sha256 = source.get(
            "source_value_sha256", _content_hash(source_value)
        )
        operation = source.get("projection_operation", default_operation)
        field_projections.append(
            {
                "projected_field": field,
                "value_sha256": value_sha256,
                "source_path": source_path,
                "source_value_sha256": source_value_sha256,
                "projection_operation": operation,
                "mapping_mode": mapping_mode,
            }
        )
        for relative_path, path_tokens, leaf_value in _leaf_values(context[field]):
            source_tokens, source_leaf, source_leaf_found = _source_binding_for_projected_leaf(
                context[field], source_value, path_tokens
            )
            source_relative_path = _relative_path_from_tokens(source_tokens)
            leaf_projections.append(
                {
                    "projected_path": f"$.{field}{relative_path}",
                    "value_sha256": _content_hash(leaf_value),
                    "source_path": f"{source_path}{source_relative_path}",
                    "source_tokens": source_tokens,
                    "source_value_sha256": _content_hash(source_leaf),
                    "projection_operation": (
                        operation
                        if source_leaf_found
                        else f"{operation}; derived_or_restructured_leaf"
                    ),
                }
            )
    compression_policy = (
        "mechanical field selection only; no literary or causal summary invention"
    )
    policy_id = f"{projection_type}.v0.1"
    contract_core = {
        "policy_id": policy_id,
        "projection_type": projection_type,
        "recipient": deepcopy(recipient),
        "context_sha256": context_sha256,
        "field_anchors": {
            record["projected_field"]: {
                "source_path": record["source_path"],
                "source_value_sha256": record["source_value_sha256"],
                "projection_operation": record["projection_operation"],
                "mapping_mode": record["mapping_mode"],
            }
            for record in field_projections
        },
        "included_refs": deepcopy(included),
        "excluded_refs": deepcopy(excluded),
        "redaction_rule": rule,
        "compression_policy": compression_policy,
        "forbidden_downstream_use": deepcopy(excluded),
    }
    contract = {
        "contract_id": f"pc_{_content_hash(contract_core)[:16]}",
        **contract_core,
    }
    for field, anchor in contract["field_anchors"].items():
        source = provenance.get(field, {})
        anchor["_source_value"] = deepcopy(
            source.get("_source_value", context[field])
        )
    manifest = {
        "manifest_id": f"pm_{_content_hash({'context_sha256': context_sha256, 'contract': _projection_contract_seal(contract)})[:16]}",
        "policy_id": policy_id,
        "projection_type": projection_type,
        "recipient": deepcopy(recipient),
        "context_sha256": context_sha256,
        "projection_contract_id": contract["contract_id"],
        "projection_contract_sha256": _content_hash(
            _projection_contract_seal(contract)
        ),
        "field_projections": field_projections,
        "leaf_projections": leaf_projections,
        "included_refs": included,
        "excluded_refs": excluded,
        "authority_basis": "runtime projection policy and recipient allowlist",
        "visibility_basis": "recipient-specific deterministic field selection",
        "redaction_rule": rule,
        "compression_policy": compression_policy,
        "forbidden_downstream_use": excluded,
    }
    return manifest, contract


def _provenance(
    source_path: str, source_value: Any, projection_operation: str
) -> dict[str, Any]:
    return {
        "source_path": source_path,
        "source_value_sha256": _content_hash(source_value),
        "projection_operation": projection_operation,
        "_source_value": deepcopy(source_value),
    }


def _projection_contract_seal(contract: dict[str, Any]) -> dict[str, Any]:
    """Return the auditable contract metadata without Kernel-only source values."""

    sealed = deepcopy(contract)
    anchors = sealed.get("field_anchors", {})
    if isinstance(anchors, dict):
        for anchor in anchors.values():
            if isinstance(anchor, dict):
                anchor.pop("_source_value", None)
    return sealed


def validate_projection_manifest(
    context: dict[str, Any],
    manifest: dict[str, Any],
    contract: dict[str, Any] | None = None,
    *,
    expected_projection_type: str | None = None,
    expected_recipient: dict[str, str] | None = None,
) -> list[dict[str, Any]]:
    """Verify a projection against Kernel-held identity and source anchors."""

    violations: list[dict[str, Any]] = []
    if not isinstance(context, dict) or not isinstance(manifest, dict):
        return [
            _projection_block(
                "invalid_projection_manifest",
                "Projection context and manifest must both be objects.",
            )
        ]
    if not isinstance(contract, dict):
        return [
            _projection_block(
                "missing_projection_contract",
                "Projection validation requires a Kernel-held contract outside the manifest.",
            )
        ]
    if not isinstance(expected_projection_type, str) or not expected_projection_type:
        violations.append(
            _projection_block(
                "missing_expected_projection_type",
                "Kernel must provide the expected projection type independently.",
            )
        )
    if (
        not isinstance(expected_recipient, dict)
        or set(expected_recipient) != {"role", "instance_id"}
        or not all(
            isinstance(expected_recipient.get(field), str)
            and bool(expected_recipient.get(field))
            for field in ["role", "instance_id"]
        )
    ):
        violations.append(
            _projection_block(
                "missing_expected_projection_recipient",
                "Kernel must provide the expected recipient independently.",
            )
        )

    expected_policy_id = (
        f"{expected_projection_type}.v0.1"
        if isinstance(expected_projection_type, str) and expected_projection_type
        else None
    )
    if contract.get("policy_id") != expected_policy_id:
        violations.append(_projection_block("projection_contract_policy_mismatch", "Projection contract is bound to the wrong stage policy."))
    if manifest.get("policy_id") != expected_policy_id:
        violations.append(_projection_block("projection_policy_id_mismatch", "ProjectionManifest declares the wrong stage policy."))
    if contract.get("projection_type") != expected_projection_type:
        violations.append(_projection_block("projection_contract_type_mismatch", "Projection contract is bound to the wrong projection type."))
    if contract.get("recipient") != expected_recipient:
        violations.append(_projection_block("projection_contract_recipient_mismatch", "Projection contract is bound to the wrong recipient."))
    if manifest.get("projection_type") != expected_projection_type:
        violations.append(_projection_block("projection_type_mismatch", "ProjectionManifest declares the wrong projection type."))
    if manifest.get("recipient") != expected_recipient:
        violations.append(_projection_block("projection_recipient_mismatch", "ProjectionManifest declares the wrong recipient."))
    if manifest.get("projection_contract_id") != contract.get("contract_id"):
        violations.append(_projection_block("projection_contract_id_mismatch", "ProjectionManifest cites the wrong Kernel contract."))
    contract_seal = _projection_contract_seal(contract)
    contract_identity_payload = deepcopy(contract_seal)
    contract_identity_payload.pop("contract_id", None)
    expected_contract_id = f"pc_{_content_hash(contract_identity_payload)[:16]}"
    if contract.get("contract_id") != expected_contract_id:
        violations.append(_projection_block("invalid_projection_contract_id", "Projection contract id is not derived from its external anchors and policy."))
    if manifest.get("projection_contract_sha256") != _content_hash(contract_seal):
        violations.append(_projection_block("projection_contract_hash_mismatch", "ProjectionManifest is not bound to the exact Kernel contract."))
    if contract.get("context_sha256") != _content_hash(context):
        violations.append(_projection_block("projection_contract_context_mismatch", "Projection contract is not bound to the delivered context."))
    if manifest.get("context_sha256") != _content_hash(context):
        violations.append(_projection_block("projection_context_hash_mismatch", "ProjectionManifest does not hash the exact delivered context."))
    expected_manifest_id = f"pm_{_content_hash({'context_sha256': _content_hash(context), 'contract': contract_seal})[:16]}"
    if manifest.get("manifest_id") != expected_manifest_id:
        violations.append(_projection_block("invalid_projection_manifest_id", "ProjectionManifest id is not bound to its context and Kernel contract."))

    for field in [
        "included_refs",
        "excluded_refs",
        "redaction_rule",
        "compression_policy",
        "forbidden_downstream_use",
    ]:
        if manifest.get(field) != contract.get(field):
            violations.append(
                _projection_block(
                    "projection_policy_mismatch",
                    f"ProjectionManifest `{field}` does not match the Kernel contract.",
                )
            )

    anchors = contract.get("field_anchors")
    if not isinstance(anchors, dict):
        return [
            *violations,
            _projection_block(
                "missing_projection_source_anchors",
                "Projection contract requires field_anchors from source objects.",
            ),
        ]

    field_records = manifest.get("field_projections")
    if not isinstance(field_records, list):
        return [
            *violations,
            _projection_block(
                "missing_field_provenance",
                "ProjectionManifest requires field_projections.",
            ),
        ]
    actual_fields: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(field_records):
        if not isinstance(record, dict):
            violations.append(_projection_block("invalid_field_provenance", f"field_projections[{index}] must be an object."))
            continue
        projected_field = record.get("projected_field")
        if not isinstance(projected_field, str) or not projected_field:
            violations.append(_projection_block("invalid_projected_field", f"field_projections[{index}] requires projected_field."))
            continue
        if projected_field in actual_fields:
            violations.append(_projection_block("duplicate_projected_field", f"ProjectionManifest repeats field {projected_field}."))
        actual_fields[projected_field] = record
        for field in ["value_sha256", "source_path", "source_value_sha256", "projection_operation", "mapping_mode"]:
            if not isinstance(record.get(field), str) or not record.get(field):
                violations.append(_projection_block("incomplete_field_provenance", f"{projected_field} lacks {field}."))
        anchor = anchors.get(projected_field)
        if not isinstance(anchor, dict):
            violations.append(_projection_block("missing_field_source_anchor", f"{projected_field} lacks an external source anchor."))
        else:
            if "_source_value" not in anchor:
                violations.append(_projection_block("missing_kernel_source_snapshot", f"{projected_field} source anchor lacks its Kernel-only snapshot."))
            elif anchor.get("source_value_sha256") != _content_hash(anchor["_source_value"]):
                violations.append(_projection_block("source_anchor_hash_mismatch", f"{projected_field} source anchor hash is invalid."))
            if anchor.get("mapping_mode") == "unanchored":
                violations.append(
                    _projection_block(
                        "unanchored_projected_field",
                        f"{projected_field} is neither source-anchored nor registered as Kernel policy.",
                    )
                )
            for field in ["source_path", "source_value_sha256", "projection_operation", "mapping_mode"]:
                if record.get(field) != anchor.get(field):
                    violations.append(
                        _projection_block(
                            "field_source_anchor_mismatch",
                            f"{projected_field} `{field}` does not match the Kernel source anchor.",
                        )
                    )
        if projected_field in context and record.get("value_sha256") != _content_hash(
            context[projected_field]
        ):
            violations.append(_projection_block("projected_field_hash_mismatch", f"ProjectionManifest hashes field {projected_field} incorrectly."))

    missing_fields = sorted(set(context) - set(actual_fields))
    unexpected_fields = sorted(set(actual_fields) - set(context))
    missing_anchors = sorted(set(context) - set(anchors))
    unexpected_anchors = sorted(set(anchors) - set(context))
    if missing_fields:
        violations.append(_projection_block("incomplete_field_coverage", "ProjectionManifest omits delivered fields: " + ", ".join(missing_fields)))
    if unexpected_fields:
        violations.append(_projection_block("unknown_projected_field", "ProjectionManifest names fields absent from context: " + ", ".join(unexpected_fields)))
    if missing_anchors:
        violations.append(_projection_block("incomplete_source_anchor_coverage", "Projection contract omits fields: " + ", ".join(missing_anchors)))
    if unexpected_anchors:
        violations.append(_projection_block("unknown_source_anchor", "Projection contract anchors fields absent from context: " + ", ".join(unexpected_anchors)))

    expected_leaves: dict[str, tuple[str, str, str, list[str | int]]] = {}
    for field in sorted(context):
        for relative_path, path_tokens, value in _leaf_values(context[field]):
            expected_leaves[f"$.{field}{relative_path}"] = (
                _content_hash(value),
                field,
                relative_path,
                path_tokens,
            )
    records = manifest.get("leaf_projections")
    if not isinstance(records, list):
        return [*violations, _projection_block("missing_leaf_provenance", "ProjectionManifest requires leaf_projections.")]
    actual: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            violations.append(_projection_block("invalid_leaf_provenance", f"leaf_projections[{index}] must be an object."))
            continue
        path = record.get("projected_path")
        if not isinstance(path, str) or not path:
            violations.append(_projection_block("invalid_projected_path", f"leaf_projections[{index}] requires projected_path."))
            continue
        if path in actual:
            violations.append(_projection_block("duplicate_projected_path", f"ProjectionManifest repeats {path}."))
        actual[path] = record
        for field in ["value_sha256", "source_path", "source_value_sha256", "projection_operation"]:
            if not isinstance(record.get(field), str) or not record.get(field):
                violations.append(_projection_block("incomplete_leaf_provenance", f"{path} lacks {field}."))
        source_tokens = record.get("source_tokens")
        if not isinstance(source_tokens, list) or not all(
            isinstance(token, (str, int)) and not isinstance(token, bool)
            for token in source_tokens
        ):
            violations.append(
                _projection_block(
                    "invalid_leaf_source_tokens",
                    f"{path} requires source_tokens relative to its audit source snapshot.",
                )
            )
    missing = sorted(set(expected_leaves) - set(actual))
    unexpected = sorted(set(actual) - set(expected_leaves))
    if missing:
        violations.append(_projection_block("incomplete_leaf_coverage", "ProjectionManifest omits delivered leaves: " + ", ".join(missing)))
    if unexpected:
        violations.append(_projection_block("unknown_projected_leaf", "ProjectionManifest names leaves absent from context: " + ", ".join(unexpected)))
    for path, (expected_hash, field, relative_path, path_tokens) in expected_leaves.items():
        record = actual.get(path)
        if record is None:
            continue
        if record.get("value_sha256") != expected_hash:
            violations.append(_projection_block("projected_leaf_hash_mismatch", f"ProjectionManifest hashes {path} incorrectly."))
        field_record = actual_fields.get(field)
        anchor = anchors.get(field)
        if (
            not field_record
            or not isinstance(anchor, dict)
            or "_source_value" not in anchor
        ):
            continue
        source_value = anchor["_source_value"]
        expected_source_tokens, source_leaf, source_leaf_found = (
            _source_binding_for_projected_leaf(
                context[field], source_value, path_tokens
            )
        )
        expected_source_path = (
            f"{field_record.get('source_path')}"
            f"{_relative_path_from_tokens(expected_source_tokens)}"
        )
        expected_source_hash = _content_hash(source_leaf)
        expected_operation = (
            field_record.get("projection_operation")
            if source_leaf_found
            else f"{field_record.get('projection_operation')}; derived_or_restructured_leaf"
        )
        if record.get("source_tokens") != expected_source_tokens:
            violations.append(_projection_block("leaf_source_tokens_mismatch", f"ProjectionManifest maps {path} to the wrong source tokens."))
        if record.get("source_path") != expected_source_path:
            violations.append(_projection_block("leaf_source_path_mismatch", f"ProjectionManifest maps {path} to the wrong source path."))
        if record.get("source_value_sha256") != expected_source_hash:
            violations.append(_projection_block("leaf_source_hash_mismatch", f"ProjectionManifest maps {path} to the wrong source hash."))
        if record.get("projection_operation") != expected_operation:
            violations.append(_projection_block("leaf_projection_operation_mismatch", f"ProjectionManifest maps {path} with the wrong operation."))
    return violations


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


def _value_at_tokens(value: Any, tokens: list[str | int]) -> tuple[Any, bool]:
    current = value
    for token in tokens:
        if isinstance(token, str) and isinstance(current, dict) and token in current:
            current = current[token]
            continue
        if isinstance(token, int) and isinstance(current, list) and 0 <= token < len(current):
            current = current[token]
            continue
        return None, False
    return current, True


def _source_binding_for_projected_leaf(
    projected_root: Any,
    source_root: Any,
    projected_tokens: list[str | int],
) -> tuple[list[str | int], Any, bool]:
    """Bind a projected leaf to its stable source object, not its new list index."""

    projected_current = projected_root
    source_current = source_root
    source_tokens: list[str | int] = []
    for token in projected_tokens:
        if isinstance(token, str):
            if not isinstance(projected_current, dict) or token not in projected_current:
                return source_tokens, source_current, False
            projected_next = projected_current[token]
            if not isinstance(source_current, dict) or token not in source_current:
                return source_tokens, source_current, False
            source_current = source_current[token]
            projected_current = projected_next
            source_tokens.append(token)
            continue

        if (
            not isinstance(token, int)
            or isinstance(token, bool)
            or not isinstance(projected_current, list)
            or token < 0
            or token >= len(projected_current)
        ):
            return source_tokens, source_current, False
        projected_item = projected_current[token]
        match = _matching_source_item(
            projected_current,
            source_current,
            token,
            projected_item,
        )
        if match is None:
            return source_tokens, source_current, False
        source_token, source_current = match
        projected_current = projected_item
        source_tokens.append(source_token)

    return source_tokens, source_current, True


def _matching_source_item(
    projected_list: list[Any],
    source_collection: Any,
    projected_index: int,
    projected_item: Any,
) -> tuple[str | int, Any] | None:
    if isinstance(source_collection, list):
        if projected_list == source_collection and projected_index < len(source_collection):
            return projected_index, source_collection[projected_index]

        identity = _stable_source_identity(projected_item)
        if identity is not None:
            identity_field, identity_value = identity
            matches = [
                (index, item)
                for index, item in enumerate(source_collection)
                if isinstance(item, dict)
                and item.get(identity_field) == identity_value
            ]
            if len(matches) == 1:
                return matches[0]
            # A declared stable identity that is missing or duplicated is an
            # authority failure; structural equality must not launder it.
            return None

        equality_matches = [
            (index, item)
            for index, item in enumerate(source_collection)
            if item == projected_item
        ]
        if len(equality_matches) == 1:
            return equality_matches[0]
        return None

    if isinstance(source_collection, dict):
        identity = _stable_source_identity(projected_item)
        if identity is None:
            return None
        _, identity_value = identity
        if identity_value in source_collection:
            return identity_value, source_collection[identity_value]
    return None


def _stable_source_identity(value: Any) -> tuple[str, str] | None:
    if not isinstance(value, dict):
        return None
    for field in _STABLE_SOURCE_ID_FIELDS:
        identity = value.get(field)
        if isinstance(identity, str) and identity:
            return field, identity
    return None


def _relative_path_from_tokens(tokens: list[str | int]) -> str:
    return "".join(
        f"[{token}]" if isinstance(token, int) else f".{token}"
        for token in tokens
    )


def _projection_block(code: str, message: str) -> dict[str, Any]:
    return {
        "severity": "block",
        "kind": "projection_manifest",
        "code": code,
        "message": message,
    }


def _content_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()
