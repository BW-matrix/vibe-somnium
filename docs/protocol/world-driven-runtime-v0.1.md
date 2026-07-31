# World-Driven Runtime Protocol v0.2 (Stable v0.1 Document Path)

This document is the normative executable profile for the current World-driven runtime in `a2a-literary-agents`.

The stable file name is retained for existing links. The executable protocol described here is v0.2.

Its governing rule is:

> World controls simulation flow; each authority controls only its own domain.

`World Agent` advances simulation, requests character decisions, and adjudicates approved inputs. It does not own character will, Plot destiny, Narrator prose, canon promotion, or permission review.

## Implementation Status

This specification matches:

- `src/a2a_literary_agents/world_runtime.py`
- `src/a2a_literary_agents/world_projection.py`
- `src/a2a_literary_agents/runtime_validation.py`
- `src/a2a_literary_agents/visibility.py`
- `scripts/export_public_trace.py`
- `fixtures/traces/world_driven_archive_exchange.json`
- `fixtures/traces/world_driven_scheduled_bell.json`
- `docs/runner/world-driven-real-sample-v0.2.md`

Statements labeled **current invariant** are enforced by code and covered by tests. Statements under **Current Limits** are explicit non-guarantees.

## Authority Model

| Component | Owns | Must not do |
| --- | --- | --- |
| `World Agent` | simulation ticks, bounded consequence, state transition, visibility result, explicit Plot translation | choose character intent, write prose, promote canon, invent owner interiority |
| `Character Agent` | one character's intent, attempted action, disclosure limits, optional owner interiority grant | commit outcome, write another mind, assert hidden world truth |
| `Plot Agent` | bounded pressure and option-topology analysis | create facts, force choices, declare outcomes or destiny |
| `Narrator Agent` | prose rendering from a projected narration checkpoint | invent facts, expand certainty or visibility, read candidates or raw ledgers |
| `Router Agent` | exact request-to-owner routing | summarize story state, redirect ownership, suggest action |
| `Authority Judge` | semantic authority, grounding, visibility, and overreach review | rewrite the subject, create replacement story content, mutate state |
| `Canon Steward` | canon mutation and reveal governance | decide ordinary scene consequence or rewrite prose |
| `Runtime Kernel` | deterministic projection, validation, scheduling, identity registry, transaction, sealing, trace | literary judgment, semantic repair, editorial selection |

`Authority Judge` has a broad audit view because it is a security role, not a creative role. Its output is audit-only and cannot itself become story fact.

## Core Runtime Invariants

1. Complete ledgers and protocol objects are system objects; model-agents receive projected contexts.
2. Every Authority approval is bound to the exact subject, audit context, and run nonce.
3. Character choice is requested, never synthesized by World or Router.
4. World may adjudicate only an approved `EventProposal`, an unconsumed registered scheduled event, or an approved pending `PlotPulse`.
5. Plot pressure becomes a world condition only through an explicit World disposition or adjudication.
6. Narrator sees committed, POV-visible event views only.
7. A blocked scene publishes no runtime state, ScenePacket facts, or memory handoff.
8. Candidate publication or canon material remains system-restricted and absent from Character, Plot, and Narrator contexts.
9. Run-local protocol identities are syntax-bounded, at most 128 characters, and single-use.
10. Missing or malformed authority, identity, visibility, source-binding, and enum fields fail closed; validator input errors become quarantine evidence rather than runtime exceptions.
11. Every delivered projected field and leaf is bound to a separate Kernel-held `ProjectionContract`; the `ProjectionManifest` cannot self-authorize its recipient, source, policy, or mapping mode.
12. Repair returns only to the originating role through a bounded, projected repair context; invalid work never enters working state before repair.
13. Fixture `runtime_mode` is explicit: only `world_driven` and `legacy_window_v0.1` are routable; missing or unknown values never fall back.
14. Every nested request, proposal, pulse, adjudication, event, and packet remains bound to the current `scene_id`; a valid id from another scene is still invalid here.
15. A Character-authored proposal keeps its actor as `CommittedWorldEvent.actors[0]`; speech proposals must commit exactly one source-bound spoken-line record.
16. Public-scope membership grants query eligibility, not direct observation. Only explicit `observer_refs` can produce automatic direct-observation memory.
17. Filtered projected arrays bind leaf provenance to stable source identities and original source indices, never to their compacted projected indices.
18. Projection success creates a sealed `ValidatedProjection` that binds protocol stage, exact `{role, instance_id}`, context bytes, manifest id, and contract id; model dispatch cannot substitute independent recipient or context arguments.
19. Duplicate projection-source identities are blocked before projection, and `trace_id` path containment is proven before any output directory is created.

## Control Loop

```text
player request
  -> WorldControlContext
  -> World Agent: WorldTickResult
  -> deterministic WorldTick validation
  -> Authority Judge for any WorldAdjudication
  -> provisional working-state commit
  -> Authority Judge for CharacterDecisionRequest
  -> Router Agent: RoutePlan
  -> Runtime Kernel: owner-specific CharacterContextPacket
  -> Character Agent: EventProposal
  -> Authority Judge: AuthorityReview
  -> Runtime Kernel: immutable ApprovedEventProposal
  -> next World tick
  -> periodic PlotPulse and NarrationCheckpoint
  -> explicit World disposition for pending Plot pressure
  -> atomic scene commit or rollback
```

The working state is visible only inside the current scene transaction. It becomes published runtime state only after `finish_scene` and all required checks succeed.

Eligible World structural failures, Character proposal review failures, and Narrator review failures may each take a fixture-bounded origin-only semantic repair path. Security-critical failures and all failures outside the explicit allowlists quarantine immediately. Every role may use one separately sealed syntax-only JSON retransmission; Plot has no content or authority repair loop.

## Runtime State

The Kernel maintains these current transaction-local collections:

| State key | Meaning |
| --- | --- |
| `committed_world_events` | provisionally accepted events inside the scene transaction |
| `world_state_delta_ledger` | provisionally accepted objective state changes |
| `visibility_result_ledger` | visibility records exactly bound to committed events |
| `publication_candidates` | pending publication candidates; never public ledger entries by themselves |
| `canon_reveal_candidates` | pending reveal candidates; never canon deltas by themselves |
| `pressure_ledger` | approved Plot pulses used for stacking and cumulative intensity checks |
| `option_topology` | registered meaningful options used by Plot validation |
| `consumed_scheduled_world_event_refs` | registered schedule inputs already used in this transaction |
| `used_protocol_ids` | run-local replay registry for identity-bearing objects |
| `last_plot_event_index` | last committed event index examined by Plot checkpointing |
| `last_narrated_event_index` | last committed event index examined under the POV contract |

The word `committed` inside a `CommittedWorldEvent` means accepted into the working transaction. External publication occurs only when the scene transaction commits.

## WorldTickResult

Each World call returns exactly one `world_tick_result` with:

- `message_type = WorldTickResult`
- `scene_id`
- unique `tick_id`
- exact `tick_index`
- `consumed_input_refs`
- `adjudication` or `null`
- `plot_pulse_disposition` or `null`
- one `next_directive`
- `checkpoint_state`
- non-empty `authority_basis`
- `visibility = system_restricted`
- `based_on`

Allowed directives are:

- `request_character_decision`
- `continue_world`
- `finish_scene`

A request directive contains a strict `CharacterDecisionRequest`; undeclared fields are blocked.

## CharacterDecisionRequest and RoutePlan

`CharacterDecisionRequest` must include:

- exact `scene_id`, `source_tick_id`, and unique `request_id`
- one registered `target_character_id`
- a neutral `agency_question`
- `visible_trigger_refs` legal for that target
- a response contract with allowed action types
- `visibility = system_restricted`
- an authority basis

The request is Authority-reviewed before routing.

`RoutePlan` must preserve the request hash and route to the same target. Router cannot redirect a request or build the Character context. The Kernel performs context projection after routing.

## CharacterContextPacket

The Character projection may contain:

- the approved decision request
- owner-visible observations
- visibility-filtered committed event surfaces
- the owner's retrieved `private_memory` records
- encountered public events for scopes the owner belongs to
- `public_canon`
- a memory retrieval audit record

It excludes:

- raw `world_state_ledger`
- other owners' memory
- latent canon
- candidate publication or reveal material
- Plot structure plans
- event actors, observer lists, and visibility limits not needed by the owner

Memory retrieval currently filters by status, ranks by salience then recency, applies a bounded item cap, and performs no story summarization.

## EventProposal and InteriorityGrant

`EventProposal` is a Character-owned attempted action, not an outcome. It includes:

- identity and request binding
- `action_type`
- `intent_summary`
- `public_surface`
- owner-private `private_intent`
- requested `desired_effect`
- `disclosure_limits`
- explicit `interiority_grant`
- restricted visibility and source refs

`interiority_grant` is either the exact all-`none` sentinel or:

```json
{
  "grant_status": "authorized",
  "source_field": "intent_summary | private_intent",
  "access_mode": "intent | self_reported_state",
  "scope_limit": "one_beat"
}
```

World may omit authorized interiority. If it includes an interiority record, it must exactly copy the granted owner field, preserve the proposal id and field name, and include a source hash. World-authored summaries of a character's mind are blocked. Scheduled events and Plot inputs cannot authorize character interiority.

## AuthorityReview

Every Authority review includes:

- unique `review_id`
- exact `subject_type`, `subject_ref`, and `subject_sha256`
- exact `run_nonce`
- exact `review_context_sha256`
- `verdict`
- `findings`
- origin-safe `required_repairs`
- non-empty `authority_basis`
- explicit `reviewed_fields`
- `visibility = system_restricted`

The Kernel also projects an Authority-only, sorted `forbidden_protocol_ids` list containing every run-local protocol id already claimed before the review. The list is included in `review_context_sha256`; it is never projected to Character, Narrator, Plot, Router, or World agents. The Judge must return a new `review_id` absent from that list. A missing, duplicated, or replayed id quarantines the review, and the Kernel never repairs or renames security-critical identifiers.

`allow` and `warning` require complete coverage of all critical fields for that subject type. Empty review coverage cannot approve.

Current bounded repair paths are:

- `WorldRepairContextPacket` for a narrow deterministic allowlist of structural causal-binding failures
- `CharacterRepairContextPacket` for Judge-requested `EventProposal` repairs
- `NarrationRepairContextPacket` for Judge-requested prose repairs
- `OutputSyntaxRepairContextPacket` for one syntax-only JSON retransmission by the exact originating agent

Character and Narrator repair instructions are code-only objects containing `repair_code` and `field_path`; free-text hidden facts are blocked from returning to the origin. `field_path` must resolve to an existing field inside the reviewed subject and may not point into `source_context` or `global_audit_context`, preventing the path string itself from becoming an audit-data laundering channel. Character and Narrator receive their own rejected output but do not receive Judge-generated `review_id`, findings, or global audit material. Approved wrappers expose only a Kernel-derived authority binding hash, never a Judge-controlled identifier. World repair receives only its original legal context, rejected output, deterministic violation codes, and fixed repair constraints. No rejected subject enters working state before repair succeeds.

JSON syntax repair is separate from semantic repair. The Kernel projects only the originating agent address, original stage and context hash, parser diagnostic, and that same agent's rejected raw output. The repair has its own `ProjectionContract`, `ProjectionManifest`, sealed `ValidatedProjection`, call count, and token usage. It may correct syntax only and is limited to one attempt. Before any repaired object reaches normal schema validation or Authority, the deterministic `SyntaxRepairConservationValidator` requires one strict JSON object equal to the provider's parsed object, identical ordered string and literal tokens, and at most four allowlisted structural edits: missing commas, trailing-comma removal, or terminal closing brackets. An unprovable change, any key/scalar/order drift, another structural edit, or a second parse failure quarantines the stage. The Kernel never inserts punctuation or rewrites model content itself. Plot therefore has no content or authority repair loop even though it shares this universal syntax-only retransmission path.

Narration review additionally requires a non-empty `claim_map`. The Kernel first segments all non-whitespace prose at terminal punctuation and newlines into exact offset- and hash-bound `NarrationClaimUnit` records. Judge coverage must match those units; every unit cites committed checkpoint event refs and declares type, certainty, visibility scope, and grounding status. Judge cannot approve missing, `unsupported`, or `overclaim` entries. This guarantees complete textual coverage, not atomic semantic clause parsing; Judge must still assess every assertion inside a multi-claim sentence.

## WorldAdjudication

World may adjudicate only one approved input at a time. The current object includes:

- unique `adjudication_id`
- exact `input_type`, `input_ref`, and `input_sha256`
- `outcome_type` and factual `outcome_summary`
- non-empty `applicable_rules` and `constraint_basis`
- audit-only `adjudication_basis`
- typed `uncertainty_model`
- constrained `failed_alternatives`
- exactly one `CommittedWorldEvent`
- typed `StateDelta` records
- visibility results
- optional system-restricted candidates

`uncertainty_model.mode` is `deterministic`, `bounded_judgment`, or `seeded_random`. Non-deterministic adjudication must record at least one non-selected alternative and the constraints that rejected it. A seeded model requires a stable seed ref.

The committed event must:

- preserve the approved input type and ref
- cite both the input and adjudication in `causal_basis`
- use registered actors and observers
- preserve the approved Character proposal actor as `actors[0]`
- separate `outcome` from `public_surface`
- contain a concrete visibility `scope_ref`
- omit `narrative_surface`
- use only grant-bound `authorized_interiority`
- record dialogue as `paraphrased` semantic content or `exact_committed` text

For a Character `speech` proposal, omitting `spoken_line_records` is a hard source-binding failure. The one legal record preserves the proposal id, speaker id, source field, source hash, and either exact text or exact Character-owned semantic content. World cannot erase the record and replace it with an invented confession or paraphrase.

Each `VisibilityResult` must exactly preserve its source event's scope, scope instance, observers, and limits. Each `StateDelta` must target `world_state_ledger` and cite a committed event from the same adjudication.

Natural-language adjudication remains a semantic trust boundary: deterministic validation proves structure and bindings; Authority Judge evaluates causal relevance and overreach.

## Scheduled World Events

World may advance without a Character proposal only through a registered, unconsumed scheduled event. The projected schedule includes an exact source hash. World must preserve that id and hash, and the Kernel records consumption to prevent replay.

The scheduled event fixture demonstrates autonomous World progression without character puppeteering.

## PlotPulse and PressureLedger

Plot receives only:

- public structural goal
- explicitly public relationship summary
- allowlisted public event views
- public committed event surfaces
- approved pressure history
- registered option topology

It does not receive private cognition, raw world state, latent canon, or candidates.

`PlotPulse` must declare pressure kind, scope, duration, affected options, a non-forcing clause, world-fact dependencies, forbidden outcomes, budget cost, and option topology. The executable enums are:

- `pressure_kind`: `deadline`, `resource_scarcity`, `social_exposure`, `institutional_constraint`, `relationship_strain`, `moral_dilemma`, `environmental_pressure`, `information_asymmetry`, or `escalation_signal`
- `scope`: `beat`, `scene`, `sequence`, `subscene`, `location`, `relationship`, `institution`, or `timeline`
- `duration`: `one_window`, `next_beat`, `next_two_beats`, `scene`, `chapter`, `scheduled`, or `until_condition`

Unknown values are hard-blocked rather than treated as creative synonyms. The exact allowlists are included in the projected Plot output schema.

Current deterministic checks require:

- at least two meaningful options after pressure
- a refusal path
- a world-legal non-Plot-compliant path
- no convergence on one outcome
- exact same-kind stacking count
- scene-level cumulative intensity at or below 6
- relief when agency risk is high

An approved pulse is not a fact. World must explicitly accept, downgrade, defer, or reject it. Accepted or downgraded pressure must bind to a committed world condition. Deferred or rejected pressure must claim no condition and cannot carry a `WorldAdjudication` derived from that pulse. A simultaneous Character proposal may still be adjudicated independently. The disposition itself is Authority-reviewed.

An accepted or downgraded pulse may cite an already registered world-condition ref without creating a new event. If it creates a new objective condition, World must produce a source-bound adjudication and exactly one committed event; Kernel cannot turn pressure acknowledgement into a `StateDelta`.

The only current recoverable Plot normalization maps `budget_cost.intensity = moderate` to `medium`. The raw model output remains in the trace, and a `NormalizationRecord` preserves field path, before/after values, policy, and warning. No identity, visibility, authority, target, source, or canon field is normalized this way.

Kernel may not synthesize a final disposition. If a Plot checkpoint creates pressure after World requested scene finish, the runtime performs another World tick and Judge review before finishing.

## NarrationCheckpoint

Narrator receives a projected checkpoint, not the full ScenePacket. It contains:

- POV-visible committed event views
- observable surfaces
- sanitized scope and scope instance
- owner-granted focal interiority only
- committed spoken-line records
- safe style and certainty bounds
- source event refs

It excludes raw state, actors when not needed, observer lists, visibility limits, private memory, proposals, Authority findings, Plot pulses, candidates, and secret-bearing `must_not_claim` text.

If no newly committed event is visible under the POV contract, the Kernel records `skipped_narration_checkpoints` and does not call Narrator.

Narrator returns prose only. Deterministic forbidden-pattern checks run before Authority claim-map review. Approved prose first enters `working_narration_segments`; only successful scene commit copies it to `published_narration_segments`. A late failure leaves it only in `quarantined_narration_segments` for audit.

## ProjectionManifest

Each delivered model context has a Kernel-side sidecar manifest plus a separate Kernel-held contract. The contract is the trust root and contains the stage-selected policy id, exact `{role, instance_id}` recipient, source anchors, mapping modes, and Kernel-only source snapshots. The manifest contains:

- policy id, exact recipient, and projection type
- contract id and contract hash
- full context hash
- one `FieldProjection` per top-level field
- one `LeafProjection` for every recursively delivered scalar, empty container, or terminal value
- projected value hash
- source path
- source tokens relative to the contract anchor
- source value hash
- projection operation
- `source_projection` or registered `kernel_policy_derivation` mapping mode
- included and excluded refs
- redaction and compression policies
- forbidden downstream use

The sidecar is audit evidence and is never delivered inside the recipient prompt. The private trace stores manifest and contract metadata but not duplicated raw source snapshots; public samples exclude both. Before every model call, Kernel independently supplies the expected policy and recipient, verifies exact field and leaf coverage, contract source hashes, source paths, source tokens, mapping modes, projection operations, duplicate or unknown paths, and every delivered value hash. A manifest that relabels `fixture.public_canon` as `fixture.latent_canon`, even with internally consistent hashes, is blocked by the external contract. For a filtered list, stable object identity locates the original source item before the leaf path is resolved; projected index zero may therefore bind to source index one. Missing or duplicate identity never falls back to structural equality.

Successful validation emits an immutable `ValidatedProjection` containing canonical context JSON and the exact dispatch address. `_call_agent` consumes this permit rather than separately supplied role, instance, stage, or mutable context values, closing validation-to-dispatch substitution. A final context hash or top-level-only manifest is not considered sufficient provenance.

## Visibility and Public Scope

Visibility is fail-closed.

- `scene_public` requires `scope_ref == scene_id` and an explicit participant registry.
- `private_self` requires exactly one observer equal to `actors[0]`, and `scope_ref` must name that owner.
- `scene_pair` requires exactly two unique current scene participants and must include every event actor.
- `local_public`, `institution_public`, `city_public`, and `realm_public` require a concrete `scope_ref` registered with matching scope type and members.
- public-scope membership permits scoped ledger lookup but never implies presence, perception, or memory.
- direct `observer_refs` represent direct observation and must themselves be valid members of the cited public-scope instance.
- unknown actors or observers are blocked.
- event views expose only sanitized scope metadata downstream.

An encountered public event requires both an explicit encounter ref and legal membership in that publication's concrete scope. A newly committed public-scope event creates automatic observation memory only for explicit `observer_refs`; other members may later receive a `received_report` memory through a separate encounter path. `public` is not global omniscience.

## Candidate Read Policy

`PublicationCandidate` and `CanonRevealCandidate` are pending system objects. They require:

- stable candidate id
- committed source event ref
- `status = pending | deferred`
- `visibility = system_restricted`
- source binding
- positive expiry in ticks

Candidates may be read by World only while creating the adjudication and by Authority for audit. They are retained in the system ScenePacket for later governance. Character, Plot, and Narrator projections exclude them.

Candidate status never means publication, canon promotion, or narration permission.

The current runtime validates a positive `expires_after_ticks` value but does not yet advance candidate age or expire deferred candidates across persistent scenes.

## Scene Transaction and Sealing

The scene uses `scene_atomic` transaction semantics.

On success:

- working state becomes published runtime state
- ScenePacket is `committed`
- visibility-derived memory handoff is created
- Authority-approved working narration becomes published narration

On any block, exhausted repair, model error, budget block, or tick limit:

- working state is retained only as `quarantined_runtime_state` for audit
- published runtime state rolls back to the initial scene state
- ScenePacket is `quarantined` with no resolved events from the failed transaction
- quarantined adjudication ids move to `SealingRecord.excluded_refs` and never appear as packet source refs
- memory handoff is empty
- any approved-but-unpublished working prose is retained only as quarantined narration

The `SealingRecord` includes source adjudication refs, included and excluded refs, source collection hashes, and a hash of the packet payload before the sealing record is attached. Assembly order is mechanical accepted-runtime order; Kernel cannot summarize, omit, or select for literary effect. Each derived `MemoryDelta` names its source packet and explicit acquisition mode.

## Run-Local Replay Protection

Every claimed protocol identity must match `^[A-Za-z][A-Za-z0-9_.:-]{0,127}$`. Non-string, overlong, malformed, missing, and repeated identities are blocked. The single-use registry includes:

- tick ids
- request ids
- route ids
- proposal ids
- adjudication ids
- event and delta ids
- visibility result ids
- candidate ids
- Plot pulse ids
- Authority review ids

Authority outputs also echo the random run nonce and review-context hash, preventing an approval from another run or audit context from being reused unchanged. Judge-controlled `review_id` remains audit-only; downstream agents receive a Kernel-derived binding over fixed approval fields instead.

## Provider Isolation

The Codex CLI backend launches one ephemeral headless process per model-agent call. It uses a dedicated `CODEX_HOME` and operator-designated isolated work directory, disables shell and web tools, ignores repository rules and user configuration, and supplies only projected protocol context through stdin. Operators should keep that work directory empty; v0.2 creates it but does not erase pre-existing contents. Codex remains a harnessed agent backend rather than a bare model endpoint, so built-in provider instructions still contribute input-token overhead.

The child environment is reconstructed from an operating-system allowlist and does not inherit arbitrary parent API keys, GitHub tokens, A2A secrets, or application variables. Codex login state is read only from the dedicated ignored home. Project reasoning effort `max` maps to the current CLI value `xhigh`; unknown values fail before invocation.

## Token and Call Budgets

Call count is enforced before each model invocation. State transition is blocked when returned usage exceeds configured per-agent or trace output limits.

Backend distinction:

- OpenAI-compatible mode sends a provider-side output token field.
- Codex CLI mode has no equivalent hard output-token flag in the current integration. Its limit is prompt guidance plus post-response precommit validation. Timeout and call count remain hard process controls.
- Mock mode uses deterministic estimated usage and post-response precommit validation.

Reports record this enforcement mode explicitly. Codex CLI token limits must not be described as guaranteed cost caps. `total_output_token_budget` governs returned output only; input and aggregate provider-billed tokens are telemetry and have no hard trace-wide cap in v0.2. A provider record is marked exact only when all supplied counts are non-negative and, when all three are present, `total_tokens == input_tokens + output_tokens`; inconsistent telemetry falls back to local estimates.

Current default per-agent output budgets are 12,000 for Plot and Router, 16,000 for Character, Narrator, and Canon Steward, and 24,000 for World, Authority, and Judge. The trace-wide output budget is 300,000. Provider output usage may include hidden reasoning tokens, so validation uses returned provider telemetry when available rather than visible JSON length.

## Allowed Fixture Call Order

The archive exchange has a 19-call base path. Each successful Character repair inserts one origin-only Character retry and one Authority re-review before the base path resumes:

| Call | Stage |
| --- | --- |
| 0 | World tick requests Wei |
| 1 | Judge reviews Wei request |
| 2 | Router routes Wei |
| 3 | Wei Character proposes |
| 4 | Judge reviews Wei proposal |
| 5 | World adjudicates Wei and requests Lin |
| 6 | Judge reviews Wei adjudication |
| 7 | Judge reviews Lin request |
| 8 | Router routes Lin |
| 9 | Lin Character proposes |
| 10 | Judge reviews Lin proposal |
| 11 | World adjudicates Lin and requests finish |
| 12 | Judge reviews Lin adjudication |
| 13 | Plot proposes checkpoint pressure |
| 14 | Judge reviews Plot pulse |
| 15 | Narrator renders committed visible events |
| 16 | Judge reviews narration claim map |
| 17 | World explicitly defers the pending pulse |
| 18 | Judge reviews the Plot disposition |

The current verified real-provider sample completed the 19-call base path without repair and with one audited recoverable Plot-intensity normalization. Origin-only semantic and syntax repair remain executable and regression-tested; rejected material reaches neither working state nor World merely because a retry path exists.

The exact executable order is documented in `../runner/world-driven-mvp-v0.2.md`.

## Failure Statuses

| Status | Meaning |
| --- | --- |
| `quarantined_world_tick` | World schema, visibility, source, identity, or input rule failed |
| `quarantined_world_adjudication` | adjudication Judge did not approve |
| `quarantined_plot_pulse_disposition` | World Plot translation disposition was not approved |
| `quarantined_decision_request` | Character request Judge did not approve |
| `quarantined_character_decision` | Router, Character proposal, repair, or proposal review failed |
| `quarantined_checkpoint` | Plot or narration checkpoint failed |
| `quarantined_final_narration` | forced final narration failed |
| `max_world_ticks_exceeded` | World did not finish within the bounded tick limit |

All non-finished outcomes roll back the scene transaction.

## Current Limits

- Runtime state is scene-local. A bounded study helper can materialize a second fixture from one committed scene, but there is no persistent campaign database.
- World, Character, and Narrator have bounded origin-only repair paths; Plot and Canon Steward do not.
- Candidate governance is recorded but Canon Steward and publication promotion are not yet executed inside the World-driven loop.
- Candidate expiry values are validated but not aged by a persistent clock.
- Memory handoff currently derives observation records from visible committed surfaces; it is not a long-lived contradiction or decay engine.
- Natural-language causal relevance and prose entailment still depend on Authority Judge quality.
- Narration claim units guarantee full text-span coverage but are sentence/newline segments rather than a deterministic semantic proposition parser.
- One Character decision is active at a time.
- Codex CLI starts a separate headless process per agent call and is slower than a direct API backend.
- The runtime is an authority-safety MVP, not evidence of literary quality or autonomous long-run coherence.

## Verification

The current suite contains 107 passing tests and 16 subtests. It covers the allowed two-character trace, scheduled World progression, pre-write path containment, successful origin-bound JSON syntax repair, deterministic semantic-drift rejection, and second-failure quarantine, external projection-contract and exact-recipient binding, filtered-list source-index provenance, duplicate projection-source ids, dual pending proposal-plus-Plot consumption, cross-scene request and Plot rejection, committed two-scene handoff, full source-fixture hash binding, exact owner-memory allowlisting, conflicting-memory-id rejection, model/runtime plus Kernel packet/memory identity reservation, Character actor and single-spoken-line binding, hard failure for speech from a non-speech proposal, request and proposal ownership, Authority coverage and run binding, protocol-id syntax and replay, atomic rollback, candidate leakage, direct-observer versus public-membership isolation, interiority forgery, executable Plot enums, derived stacking-count normalization and cumulative pressure, rejected-pulse adjudication, Narrator overclaim, World-only public export, complete projection-evidence export gating, public-export sealing, elapsed-call telemetry, and token consistency and transition blocks.

One sanitized real Codex run, including every parsed model-agent output and exact provider token record, is published at `../runner/world-driven-real-sample-v0.2.md`. The exporter accepts only successful committed Codex CLI traces with exact provider usage, one uniquely bound and internally consistent projection manifest and contract per call, complete recursively delivered leaf coverage and hashes, contract-bound leaf source paths and operations, manifest/contract policy parity, no unanchored field or blocking validation, and a valid private ScenePacket seal. It removes private run identifiers and creates a separately verifiable `sanitized_public_export` seal. This release gate establishes retained-trace consistency; it is not an external digital signature.

Run:

```powershell
python -m pytest -q
```

## Related Specifications

- `agent-context-packet-and-field-visibility-v0.1.md`
- `resolution-state-delta-commit-pipeline-v0.1.md`
- `scene-pressure-packet-and-plot-budget-v0.1.md`
- `scene-packet-schema-v0.1.md`
- `scene-packet-to-memory-handoff-v0.1.md`
- `state-and-knowledge-layers-v0.1.md`
- `communication-permission-matrix-v0.1.md`
- `agent-constraint-matrix-v0.1.md`
