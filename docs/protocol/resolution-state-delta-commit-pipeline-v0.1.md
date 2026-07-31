# Resolution, StateDelta, and ScenePacket Commit Pipeline v0.1

This document defines the first auditable pipeline from character proposal to committed scene packet.

The goal is to prevent `World Agent` from becoming a hidden author. The world may decide consequence, but consequence must be traceable to submitted intent, current state, canon, constraints, uncertainty policy, and visible effects.

Runtime status:

- this document defines the general consequence and commit law
- [world-driven-runtime-v0.1](world-driven-runtime-v0.1.md) is the normative executable v0.2 profile
- the executable profile uses `WorldAdjudication`, `AuthorityReview`, an atomic scene transaction, and a deterministic `SealingRecord`

## Purpose

The commit pipeline exists to solve five protocol problems:

1. define how `World Agent` adjudicates `Intent`, `ActionProposal`, and `DialogueWindow`
2. make `Resolution` and `StateDelta` concrete enough to audit
3. distinguish committed consequence from publication candidates and canon reveal candidates
4. constrain `Orchestrator` assembly so packet sealing does not become editorial power
5. give `Narrator Agent` and memory handoff a stable committed source

Without this pipeline, the system may stop narrator-level invention while still allowing world-level consequence invention.

## Design Constraints

The pipeline should satisfy these constraints:

1. every outcome must cite input refs and applicable rules
2. every state change must be represented as a `StateDelta`
3. every visibility result must distinguish "happened" from "known"
4. publication and canon reveal are two-phase operations
5. packet assembly must be mechanical, source-backed, and sealed

## Pipeline Overview

Recommended flow:

1. `World Agent` advances the scene and emits a neutral `CharacterDecisionRequest` when owner choice is required
2. `Authority Judge` reviews the request before `Router Agent` binds it to the declared owner
3. `Character Agent` submits an `EventProposal` from an owner-specific `CharacterContextPacket`
4. `Authority Judge` reviews the exact proposal and `Runtime Kernel` creates an immutable `ApprovedEventProposal`
5. `World Agent` emits a source-bound `WorldAdjudication`
6. `Authority Judge` reviews the complete adjudication before the Kernel applies its events, deltas, visibility records, or candidates to transaction-local working state
7. publication thresholds and canon governance remain separate follow-up decisions
8. `Runtime Kernel` projects narration checkpoints and seals the final `ScenePacket` mechanically
9. the scene transaction either publishes all accepted state and memory handoff together or rolls back all of it

Important rule:

- consequence commits before narration
- publication and canon promotion require explicit gates after consequence
- transaction-local acceptance is provisional until the scene finishes successfully

## Resolution Shape

Suggested `Resolution` fields:

| Field | Required | Type | Meaning |
| --- | --- | --- | --- |
| `resolution_id` | yes | string | stable id for the adjudication |
| `scene_id` | yes | string | parent scene |
| `window_id` | recommended | string | dramatic window being resolved |
| `input_refs` | yes | array | proposals, pressure packets, observations, or prior state refs being adjudicated |
| `actor_refs` | yes | array | acting characters or entities |
| `applicable_rules` | yes | array | canon, world rules, social rules, physical constraints, or scene constraints |
| `constraint_basis` | yes | array | facts or limits that materially shaped the outcome |
| `uncertainty_model` | recommended | object | deterministic, probabilistic, hybrid, or author-defined adjudication mode |
| `outcome_type` | yes | string | `success`, `failure`, `partial_success`, `misfire`, `blocked`, `delayed`, or `contested` |
| `outcome_summary` | yes | string | concise factual consequence |
| `failed_alternatives` | optional | array | attempted branches that did not become true |
| `visibility_result_refs` | recommended | array | visibility records produced by this resolution |
| `state_delta_refs` | recommended | array | committed state deltas produced by this resolution |
| `publication_candidate_refs` | optional | array | possible public event candidates |
| `canon_reveal_candidate_refs` | optional | array | possible reveal candidates |
| `adjudication_basis` | yes | string | audit summary without chain-of-thought |
| `based_on` | recommended | array | policy, matrix, packet, canon, and ledger refs |

Important rule:

- `adjudication_basis` should explain the basis of the decision
- it should not expose chain-of-thought or hidden authorial reasoning

## Outcome Types

| Outcome type | Meaning | Commit behavior |
| --- | --- | --- |
| `success` | attempted action achieves its intended direct effect | may produce direct state deltas |
| `failure` | attempted action does not achieve the intended effect | may still produce side-effect deltas |
| `partial_success` | some effect occurs, but not the full intended effect | commit only the achieved portion |
| `misfire` | attempt produces an unintended consequence | commit the unintended consequence if rule-backed |
| `blocked` | attempt is prevented before meaningful effect | may commit visibility or pressure effects only |
| `delayed` | consequence is scheduled but not complete yet | create pending or future-triggered state refs |
| `contested` | outcome is socially or perceptually disputed | commit objective state separately from public interpretation |

## StateDelta Shape

Suggested `StateDelta` fields:

| Field | Required | Type | Meaning |
| --- | --- | --- | --- |
| `delta_id` | yes | string | stable id for this state change |
| `source_resolution_id` | yes | string | resolution that produced it |
| `target_layer` | yes | string | usually `world_state_ledger`; sometimes route metadata or public/canon candidate refs |
| `target_kind` | yes | string | character, object, location, relation, resource, institution, schedule, or condition |
| `target_id` | yes | string | entity being changed |
| `change_kind` | yes | string | create, update, move, remove, reveal_marker, schedule, damage, transfer, relation_shift |
| `before_ref` | optional | string | previous state ref when available |
| `after_summary` | yes | string | committed state after the change |
| `persistence` | recommended | string | momentary, scene, chapter, persistent, scheduled |
| `visibility_basis` | recommended | array | who could perceive or infer this change |
| `based_on` | recommended | array | input, rule, and resolution refs |

Important rule:

- `StateDelta` records objective change
- it does not decide who knows the change unless paired with visibility records

## VisibilityResult Shape

Suggested `VisibilityResult` fields:

| Field | Required | Meaning |
| --- | --- | --- |
| `visibility_result_id` | yes | stable id |
| `source_resolution_id` | yes | resolution source |
| `observer_scope` | yes | self, pair, scene group, local public, institution public, or restricted subset |
| `observer_refs` | recommended | specific agents or groups if known |
| `visible_content` | yes | what became visible, reportable, or inferable |
| `certainty` | recommended | low, medium, high |
| `exposure_mode` | recommended | saw, heard, was_told, inferred, discovered, declared |
| `limits` | recommended | what this visibility result does not prove |

Important rule:

- visibility may produce memory eligibility
- it does not automatically produce public event publication

## Two-Phase Publication and Reveal Semantics

`ResolvedScenePacket` may carry candidates, not final promotions.

| Candidate type | Meaning | Finalizing authority |
| --- | --- | --- |
| `PublicationCandidate` | committed scene material may qualify for `public_event_ledger` | publication threshold policy and `World Agent` |
| `CanonRevealCandidate` | committed scene material may expose `latent_canon` | `Canon Steward` |
| `CanonMutationRequest` | current scene may require new or clarified canon | `Canon Steward` |

Field naming rule:

- use `publication_candidates` before threshold approval
- use `public_event_deltas` only after publication is approved
- use `canon_reveal_candidates` before canon review
- use `canon_effects_committed` or `CanonDelta` only after steward decision

## ScenePacket Assembly and Sealing

`Runtime Kernel` may assemble and seal packets. It may not author content.

| Packet field | Allowed writer/source | Assembly rule |
| --- | --- | --- |
| `resolved_events` | accepted `CommittedWorldEvent` records from `World Agent` | exact ordered copy; no Kernel-authored summary |
| `state_deltas` | committed `StateDelta` refs | include refs and summaries, not hidden unfiltered ledger dumps |
| `visibility_deltas` | `VisibilityResult` records | include scope and limits |
| `publication_candidates` | resolution-backed candidate records | mark as candidates until threshold approval |
| `public_event_deltas` | approved publication records only | include only after publication decision |
| `authorized_interiority` | POV contract or character-authorized material | include only with explicit authority basis |
| `canon_reveal_candidates` | resolution-backed reveal markers | mark as candidates until steward approval |
| `canon_effects_committed` | `CanonDecision` or `CanonDelta` | include only after steward decision |
| `narration_bounds` | policy plus resolution constraints | assemble from hard limits and POV contract |
| `based_on` | all source refs | mandatory for sealing |

Seal conditions:

1. all included events have `Resolution` refs
2. all state changes have accepted `StateDelta` refs
3. all visibility claims cite `VisibilityResult` refs
4. all publication and reveal material is clearly marked as candidate or approved
5. no unresolved proposal is represented as fact
6. no summary lacks source refs
7. every accepted adjudication has an allow/warning `AuthorityReview` bound to the exact subject hash, review-context hash, and run nonce
8. every run-local identity is unique and every consumable proposal, scheduled event, or Plot pulse is consumed at most once

The executable `SealingRecord` additionally includes:

- source adjudication refs
- included refs grouped by source collection
- SHA-256 for every source collection
- SHA-256 of the packet payload before the sealing record is attached
- the deterministic assembly policy identifier

Kernel assembly follows accepted-runtime order. It may not omit, reorder, compress, or select material for literary effect. The executable `ProjectionManifest` separately proves recursively complete leaf provenance for every model-facing view; sealing provenance does not replace projection provenance.

On rollback, `source_adjudication_refs` contains no quarantined adjudication. Rejected or late-failing refs are preserved separately as `excluded_refs` with deterministic reasons, so an audit record cannot imply that blocked material contributed to the sealed packet.

A public trace is a separately sealed artifact, not the private packet with fields silently deleted. Export first verifies the successful real-provider trace and its exact usage records, recursively removes private run identifiers and audit-only material, recomputes every affected source-collection hash, and then writes a new packet hash with `seal_scope = sanitized_public_export`. The private seal is retained only as a verified provenance fact, never reused as the public seal.

## Narrator Input Projection

In a post-commit renderer, `Narrator Agent` receives a `NarratorInputPacket`, not the full system packet. Executable v0.2 performs narration before outward scene publication, so it projects the equivalent transaction-local `NarrationCheckpoint` from accepted working events. The resulting prose remains unpublished working material until the whole scene seals successfully.

It may include:

- committed resolved events
- committed state deltas that are legal to render
- approved or legally bounded visibility changes
- authorized interiority
- narration bounds
- approved public or canon material

It must exclude:

- raw `world_state_ledger`
- rejected alternatives
- unresolved candidate lines
- pending `PublicationCandidate`
- pending `CanonRevealCandidate`
- raw latent canon

A late narration or Authority failure therefore cannot invalidate already published prose: no prose has been published yet. It is retained only as quarantined audit material after rollback.

## Hard Boundaries

`World Agent` may:

- adjudicate consequence
- commit state deltas under current rules
- mark visibility results
- generate candidates for publication or reveal

`World Agent` may not:

- choose outcomes purely for drama
- write character inner truth
- promote canon without steward review
- treat plot pressure as destiny
- publish hidden facts without threshold support

`Orchestrator` may:

- package refs
- validate commit readiness
- seal packets
- project legal views

`Orchestrator` may not:

- omit source-backed material for literary preference
- add prose emphasis as fact
- upgrade candidates into approved deltas
- rewrite resolutions

In the executable profile these mechanical permissions belong to `Runtime Kernel`; semantic permission review belongs to `Authority Judge`, and owner routing belongs to `Router Agent`. The legacy `Orchestrator` label does not denote a model-agent in that profile.

## Atomic Scene Transaction

`CommittedWorldEvent` means accepted into transaction-local working state, not yet externally published. The runtime publishes world events, state deltas, visibility results, candidates, `ScenePacket`, and memory handoff only after `finish_scene` and all required checks succeed.

Any late block, invalid Plot disposition, narration overclaim, budget failure, or sealing failure causes:

- `transaction_status = rolled_back`
- no published runtime state
- no resolved event in the outward `ScenePacket`
- no derived `MemoryDelta`
- preservation of the rejected working state only under `quarantined_runtime_state` for audit

This is an all-or-nothing scene transaction, not a best-effort append log.

## World Adjudication Inputs

The executable runtime permits World adjudication only over one of these registered inputs:

- an exact, unconsumed `ApprovedEventProposal`
- an exact, unconsumed scheduled world event
- an exact, approved, pending `PlotPulse`

Every adjudication includes an uncertainty model and failed alternatives. Non-deterministic outcome types require concrete failed alternatives; `partial_success`, `delayed`, and `contested` are not free dramatic convenience buttons.

For an approved pending `PlotPulse`, World has two legal branches:

1. cite an already registered `existing_world_condition_ref` and emit no adjudication or state delta
2. create a new objective condition through one source-bound adjudication and exactly one committed event, with every state delta bound to that event

Acknowledging pressure is never sufficient basis for a state delta.

An approved Character proposal and an approved Plot pulse may be pending in the same World tick. In that case the proposal remains the sole adjudication input, the pulse receives its independent `PlotPulseDisposition`, and `consumed_input_refs` must contain both exact ids. The projected output contract must expose both obligations; choosing the proposal with an `if/elif` schema branch and silently omitting the pulse is a blocking protocol contradiction.

## Bounded World Repair

The executable profile permits one fixture-bounded return to the same World instance only when every blocking code belongs to a narrow deterministic origin-repair allowlist, such as missing input consumption, incomplete causal binding, invalid alternative shape, unknown registered actor/observer, or unbound state delta.

`WorldRepairContextPacket` contains the original legal World view, the rejected output, deterministic code/path violations, and fixed constraints. It contains no replacement outcome and no free-form Judge recommendation. Identity, visibility authority, replay, source-hash, or non-allowlisted failures quarantine immediately. The rejected adjudication never enters working state.

## Example

```json
{
  "resolution": {
    "resolution_id": "res_411",
    "scene_id": "scene_018",
    "window_id": "win_018_05",
    "input_refs": ["dw_018_05", "spp_018_01", "wsl_archive_state_07"],
    "actor_refs": ["char_wei", "char_lin"],
    "applicable_rules": ["public_canon:archive_access_rule", "pressure_budget:inspection_deadline"],
    "constraint_basis": [
      "Wei knows the ledger is missing but does not confess.",
      "Lin has prior suspicion but no proof."
    ],
    "uncertainty_model": {
      "mode": "hybrid",
      "notes": "social read resolved by prior memory and visible dialogue pressure"
    },
    "outcome_type": "partial_success",
    "outcome_summary": "Wei's probe makes Lin more suspicious, but Lin does not obtain proof.",
    "failed_alternatives": [
      "Lin does not extract a confession.",
      "Wei does not fully hide his unusual concern."
    ],
    "visibility_result_refs": ["vr_411"],
    "state_delta_refs": ["sd_118"],
    "publication_candidate_refs": [],
    "canon_reveal_candidate_refs": [],
    "adjudication_basis": "The result follows from Wei's cautious probing, Lin's existing suspicion, and the absence of public evidence.",
    "based_on": ["dialogue-window-schema-v0.1", "state-and-knowledge-layers-v0.1"]
  }
}
```

## Relationship to Adjacent Specs

This document should be read together with:

- `scene-packet-schema-v0.1.md`
- `event-publication-thresholds-v0.1.md`
- `latent-to-public-canon-reveal-rules-v0.1.md`
- `canon-mutation-review-checklist-v0.1.md`
- `agent-context-packet-and-field-visibility-v0.1.md`

Current executable status:

1. adversarial fixtures cover hidden theft, false/public-scope confusion, candidate leakage, World overreach, replay, and late rollback
2. narration is checked with a source-bound claim map before scene commit
3. remaining work includes richer rule registries, multi-scene persistence, and live canon/publication governance
