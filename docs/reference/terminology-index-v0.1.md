# Terminology Index v0.1

This document is the first canonical vocabulary index for `a2a-literary-agents`.

Its purpose is to keep the project's term family stable as the protocol grows.

## Why This Exists

As the protocol expands, term drift becomes a real risk:

- one idea may collect multiple names
- the same word may be used at different abstraction levels
- an informal shortcut may start replacing a more precise term

This index exists to reduce that drift.

## Scope

This is not a full ontology yet.

It is:

- a canonical naming directory
- a quick-reference glossary
- a place to mark preferred terms and discouraged aliases

## Naming Principles

1. Prefer one canonical term per concept.
2. Keep protocol-layer terms stable once published.
3. Prefer precise storage-layer names over coarse narrative shorthand.
4. Mark ambiguous aliases as discouraged instead of silently letting them spread.
5. Let future schemas inherit vocabulary from this index.

## Term Families

- project identity
- agent roles
- message and packet types
- interaction and pacing units
- state and knowledge layers
- canon and authority layers
- visibility and routing terms
- runtime control and checkpoint terms

## Canonical Terms

| Term | Family | Meaning | Preferred usage | Discouraged alias or note | Primary source |
| --- | --- | --- | --- | --- | --- |
| `a2a-literary-agents` | project identity | repository and project name | use for repo, searchability, public reference | do not replace with the codename in formal references | `README.md` |
| `vibe-somnium / 织梦` | project identity | working title / codename | use as codename, internal identity, aesthetic label | not ideal as the main searchable repo name | `README.md` |
| `Character Agent` | agent role | owns will, motive, subjective choice | use for role authority and private cognition discussions | avoid shortening to just `character` when authority matters | `agent-constraint-matrix-v0.1.md` |
| `World Agent` | agent role | controls simulation progression, requests character decisions, and adjudicates committed world change | use for world ticks, causality, resolution, and state transition | simulation control does not grant character will, plot destiny, or prose authority | `world-driven-runtime-v0.1.md` |
| `Plot Agent` | agent role | injects bounded pressure and structural escalation through `PlotPulse` | use for pressure, not fate completion | avoid implying direct control over characters or world facts | `world-driven-runtime-v0.1.md` |
| `Narrator Agent` | agent role | renders committed projected material into prose | use for expression and voice layers after `NarrationCheckpoint` | avoid giving it fact-writing or state access authority | `world-driven-runtime-v0.1.md` |
| `Canon Steward` | agent role | governs canon review and canon mutation approval | use for canon law and reveal governance | avoid lowercase role naming in new normative text | `communication-permission-matrix-v0.1.md` |
| `Router Agent` | agent role | binds a valid `CharacterDecisionRequest` to its declared Character Agent owner | use only for recipient routing and `RoutePlan` creation | must not build context, suggest action, or decide consequence | `world-driven-runtime-v0.1.md` |
| `Authority Judge` | agent role | reviews semantic authority, visibility, factual status, and overreach without creating content | use for `AuthorityReview` over proposals, plot pulses, and prose | do not use it as a rewriting or fallback author | `world-driven-runtime-v0.1.md` |
| `Runtime Kernel` | runtime infrastructure | deterministic program for transport, schema, projection, storage, checkpointing, and trace | use for non-semantic runtime mechanics | not an agent, author, semantic judge, or replacement for World | `world-driven-runtime-v0.1.md` |
| `orchestrator` | legacy coordination role | older umbrella term for routing, validation, scheduling, and protocol guarding | preserve when discussing earlier specs | in World-driven runtime use `Runtime Kernel`, `Router Agent`, or `Authority Judge` for the precise responsibility | `world-driven-runtime-v0.1.md` |
| `World-driven runtime` | runtime architecture | execution model in which World advances simulation while domain authority remains distributed | use for the new tick-based control architecture | does not mean World is a master author | `world-driven-runtime-v0.1.md` |
| `Intent` | message type | a character's declared intention | use for character-side intention before consequence | avoid using it as a synonym for inner raw thought | `communication-permission-matrix-v0.1.md` |
| `ActionProposal` | message type | generic earlier term for a proposed action submitted for resolution | use in earlier protocol discussions | prefer `EventProposal` for World-driven runtime objects; never a guarantee of outcome | `communication-permission-matrix-v0.1.md` |
| `Observation` | message type | what becomes perceptible to an agent or scene participant | use for delivered sensory or situational input | avoid using for inferred global truth | `communication-permission-matrix-v0.1.md` |
| `Resolution` | message type | a world-side adjudicated result with auditable basis | use for consequence, success/failure, and visibility outcomes | should remain world-owned and source-backed | `resolution-state-delta-commit-pipeline-v0.1.md` |
| `StateDelta` | message type | the state change committed after resolution | use for changes to world or knowledge-bearing state | not the same as narration or publication | `resolution-state-delta-commit-pipeline-v0.1.md` |
| `VisibilityResult` | message type | world-side record of what became visible, reportable, or inferable to a scope | use before deriving memory or publication eligibility | not the same as objective state change | `resolution-state-delta-commit-pipeline-v0.1.md` |
| `WorldTickResult` | runtime message | authoritative output of one World-controlled simulation tick | use for consumed inputs, optional adjudication, counters, and the single next directive | not a prose beat or unrestricted author command | `world-driven-runtime-v0.1.md` |
| `WorldDirective` | runtime message | `next_directive` inside `WorldTickResult` | use for `request_character_decision`, `continue_world`, or `finish_scene` | current object has no standalone message type or validator | `world-driven-runtime-v0.1.md` |
| `CharacterDecisionRequest` | runtime message | neutral World request for one character owner to make one bounded decision | use whenever simulation progression requires meaningful character will | must not contain a preferred answer or guaranteed consequence | `world-driven-runtime-v0.1.md` |
| `RoutePlan` | routing record | Router-owned binding from a decision request to its declared character agent and projection policy | use before Kernel context construction | not a place for story summary, memory retrieval, or action advice | `world-driven-runtime-v0.1.md` |
| `EventProposal` | message type | parameterized character-owned attempted action submitted for semantic review and world adjudication | use as the World-driven character response type | desired effects are not committed outcomes | `world-driven-runtime-v0.1.md` |
| `AuthorityReview` | authority record | immutable semantic review of one decision request, proposal, adjudication, Plot pulse or disposition, or narration subject | bind exact subject hash, critical reviewed fields, authority basis, run nonce, and review-context hash | Judge findings and Judge-controlled ids must not enter creative contexts | `world-driven-runtime-v0.1.md` |
| `ApprovedEventProposal` | approval envelope | Kernel-created wrapper around the exact Judge-approved `EventProposal` | use as the only character proposal input accepted by the next World tick | not a corrected, summarized, or rewritten proposal | `world-driven-runtime-v0.1.md` |
| `WorldAdjudication` | runtime resolution | World-owned consequence decision over one approved proposal, registered scheduled event, or approved Plot pulse | use for rule-backed outcome, committed events, state deltas, visibility, candidates, and explicit Plot translation | accepts only exact registered, source-hashed, unconsumed inputs | `world-driven-runtime-v0.1.md` |
| `CommittedWorldEvent` | committed record | World-authored event nested in a validated adjudication and appended by Kernel | use as checkpoint, projection, and ledger input | commitment does not make the event public knowledge or canon | `world-driven-runtime-v0.1.md` |
| `PlotPulse` | checkpoint message | bounded Plot proposal for future structural pressure emitted at a deterministic checkpoint | use for Judge-reviewed pressure that may be presented to a later World tick | never a fact; requires explicit World disposition | `world-driven-runtime-v0.1.md` |
| `PlotPulseDisposition` | runtime resolution | World-owned accept, downgrade, defer, or reject decision over one approved pending Plot pulse | use before scene completion to state whether and how pressure enters world causality | Kernel cannot synthesize the disposition | `world-driven-runtime-v0.1.md` |
| `ExistingWorldConditionRef` | world binding | registered ref to an objective condition that already exists before Plot pressure is considered | use when accepted or downgraded pressure needs no new adjudicated event | not permission for Plot or Kernel to invent a condition | `world-driven-runtime-v0.1.md` |
| `PressureLedger` | runtime ledger | scene-local record of approved Plot pulses and cumulative pressure cost | use for stacking and intensity validation | not a world-fact ledger | `world-driven-runtime-v0.1.md` |
| `OptionTopologyCheck` | pressure validation | deterministic check that meaningful alternatives, refusal, and a non-Plot-compliant path remain | use before approving cumulative pressure | a natural-language non-forcing clause alone is insufficient | `world-driven-runtime-v0.1.md` |
| `NarrationCheckpoint` | checkpoint packet | Kernel-generated committed-only boundary for one narration pass | use for event views, source refs, POV contract, and narration bounds | current nested object has no `message_type` or standalone validator | `world-driven-runtime-v0.1.md` |
| `NarrationDraft` | output type | conceptual label for narrator prose awaiting post-narration authority review | use in architecture discussion | current executable payload is `prose`, then a Kernel-built narration subject | `world-driven-runtime-v0.1.md` |
| `CheckpointPolicy` | runtime policy | Kernel-read Plot and Narration intervals over transaction-accepted event count | use for `plot_every_committed_beats` and `narrate_every_committed_beats` | current profile has no cross-scene persistence fields | `world-driven-runtime-v0.1.md` |
| `committed beat` | pacing and runtime unit | one event appended to current `committed_world_events` | use as the deterministic checkpoint counter input | every current committed event counts; there is no countability field | `world-driven-runtime-v0.1.md` |
| `private_intent` | proposal field | current executable field for bounded owner-private motivation inside `EventProposal` | use only in system-restricted proposal and Judge/World contexts | not raw chain-of-thought and not character-public surface | `world-driven-runtime-v0.1.md` |
| `resolver_intent` | future hardening term | proposed narrower typed replacement for free-text `private_intent` | use only when discussing non-normative future schema | not a current executable field | `world-driven-runtime-v0.1.md` |
| `semantic authority review` | authority process | Judge evaluation of whether an object's meaning stays inside its owner's authority | use after Kernel structural checks | not schema validation and not content rewriting | `world-driven-runtime-v0.1.md` |
| `request_sha256` | integrity field | Kernel hash of the complete `CharacterDecisionRequest` | use to prove Router preserved the exact request | does not replace semantic request review | `world-driven-runtime-v0.1.md` |
| `subject_sha256` | integrity field | Kernel hash of the exact object presented to `Authority Judge` | use to bind review to proposal, Plot pulse, or narration subject | not a semantic correctness proof | `world-driven-runtime-v0.1.md` |
| `proposal_sha256` | integrity field | Kernel hash of the immutable approved `EventProposal` | use in approval wrapper and next World adjudication | does not hash the resulting World event | `world-driven-runtime-v0.1.md` |
| `run_nonce` | replay-binding field | cryptographically random identity for one runtime execution | bind every Authority review to the current run | must never be inferred from fixture story data | `world-driven-runtime-v0.1.md` |
| `review_context_sha256` | audit-binding field | hash of the exact projected audit context supplied to Authority Judge | prove that a review applies to this context as well as this subject | subject hash alone is insufficient | `world-driven-runtime-v0.1.md` |
| `Pressure` | message type | structural or dramatic pressure introduced by plot logic | use for pressure, deadlines, or tension sources | not a fact by itself | `scene-pressure-packet-and-plot-budget-v0.1.md` |
| `CanonMutationRequest` | message type | formal request for canon review | use when a proposed fact would alter, reveal, or extend canon | not the same as ordinary scene resolution | `canon-mutation-review-checklist-v0.1.md` |
| `CanonDecision` | message type | steward-issued review outcome on a canon request | use for approval, rejection, or deferment of canon mutation | should always leave a traceable decision record | `canon-mutation-review-checklist-v0.1.md` |
| `CanonDelta` | canon record | the recorded change produced by an approved canon decision | use for change-log entries that update canon layers | not a scene-state delta | `canon-mutation-review-checklist-v0.1.md` |
| `CanonReviewContext` | context packet | canon-relevant projected context for `Canon Steward` | use when reviewing mutation or reveal requests | should exclude irrelevant private cognition | `agent-context-packet-and-field-visibility-v0.1.md` |
| `publication_threshold` | publication policy | the threshold test that decides whether an event enters `public_event_ledger` | use for public-knowledge promotion rules | do not confuse with world truth or canon mutation | `event-publication-thresholds-v0.1.md` |
| `publication_mode` | publication field | the path by which an event became public | use for witness, declaration, discovery, or release-based promotion | not the same as scope | `event-publication-thresholds-v0.1.md` |
| `PublicationCandidate` | publication candidate | committed scene material that may qualify for public event publication | use before threshold approval | not yet a `public_event_delta` | `resolution-state-delta-commit-pipeline-v0.1.md` |
| `public_event_delta` | publication record | a concrete entry promoted into `public_event_ledger` | use for published event summaries with explicit scope | stronger than private memory, weaker than canon | `event-publication-thresholds-v0.1.md` |
| `DialogueWindow` | interaction unit | the default bounded unit for spoken interaction | use as the standard dialogue coordination unit | prefer this over single-line turn language | `dialogue-window-schema-v0.1.md` |
| `ScenePacket` | packet type | atomically published system-level packet for downstream projection, rendering, and memory | use after successful scene completion and deterministic sealing | complete packet is not default narrator input | `scene-packet-schema-v0.1.md` |
| `ScenePacketView` | context packet | per-agent projected slice of a `ScenePacket` | use when an agent may see only part of committed material | not a new truth layer | `agent-context-packet-and-field-visibility-v0.1.md` |
| `NarratorInputPacket` | context packet | projected legal factual input for `Narrator Agent` | use as the prose grounding source | not raw `ScenePacket` or raw world state | `agent-context-packet-and-field-visibility-v0.1.md` |
| `AgentContextPacket` | context packet | general per-agent context envelope for one protocol step | use for runtime prompt/context assembly | should package and redact, not author | `agent-context-packet-and-field-visibility-v0.1.md` |
| `CharacterContextPacket` | context packet | owner-specific context for a `Character Agent` to form intent or dialogue | use for visible facts, own memory, public events, and public canon | excludes other private memory and raw world state | `agent-context-packet-and-field-visibility-v0.1.md` |
| `CharacterRepairContextPacket` | context packet | origin-only retry context containing the original legal Character view, that Character's rejected proposal, and code-only Judge `required_repairs` | use for bounded `EventProposal` repair by the same Character Agent | excludes Judge ids, global audit context, findings, other memory, and hidden world state | `world-driven-runtime-v0.1.md` |
| `WorldRepairContextPacket` | context packet | origin-only retry context containing the original legal World view, rejected tick, and allowlisted deterministic violation codes | use only for bounded structural World repair | must not contain a replacement outcome or free-form story advice | `world-driven-runtime-v0.1.md` |
| `NarrationRepairContextPacket` | context packet | origin-only retry context containing the original legal narration view, rejected prose, and code-only Judge repairs | use for bounded Narrator correction | excludes global audit context, candidates, and replacement prose | `world-driven-runtime-v0.1.md` |
| `OutputSyntaxRepairContextPacket` | context packet | origin-only packet containing one agent's rejected raw output, parser diagnostic, original stage, and context hash | permit exactly one syntax-only JSON retransmission under a new projection contract and dispatch seal | cannot authorize semantic changes, Kernel punctuation repair, or a second retry | `world-driven-runtime-v0.1.md` |
| `SyntaxRepairConservationValidator` | deterministic validation gate | lexical proof that repaired JSON preserves ordered string and literal tokens while changing only a bounded punctuation allowlist | run before schema validation or Authority after an `OutputSyntaxRepairContextPacket` response | if conservation cannot be proved, quarantine instead of asking an agent to judge equivalence | `world-driven-runtime-v0.1.md` |
| `PlotContextSummary` | context packet | structural view used by `Plot Agent` to propose pressure | use for pressure planning with limited summaries | must not expose raw hidden truth | `agent-context-packet-and-field-visibility-v0.1.md` |
| `packet-to-memory handoff` | protocol transition | the lawful derivation step from committed `ScenePacket` into owner-specific `MemoryDelta` output | use for discussing packet-to-memory derivation rules | do not confuse with narration or public publication | `scene-packet-to-memory-handoff-v0.1.md` |
| `ScenePressurePacket` | packet type | bounded scene-level pressure bundle from plot logic | use for scene or beat pressure inputs with scope, duration, and non-forcing clause | keep distinct from committed events | `scene-pressure-packet-and-plot-budget-v0.1.md` |
| `SceneDraft` | output type | narrator-side scene draft material | use for prose drafts, not canon facts | should remain downstream of committed packets | `agent-constraint-matrix-v0.1.md` |
| `FieldProjection` | projection audit record | one destination field's exact source path, source-value hash, mapping mode, and deterministic projection operation | use inside every executable `ProjectionManifest` | must match the separate Kernel-held source anchor | `agent-context-packet-and-field-visibility-v0.1.md` |
| `LeafProjection` | projection audit record | exact delivered leaf path, value hash, stable-id-derived source tokens/path, source hash, and deterministic operation | use to prove recursively complete provenance before a model call, including original indices after list filtering | top-level field provenance or compacted projected indices do not replace it | `world-driven-runtime-v0.1.md` |
| `source_tokens` | projection integrity field | path tokens relative to a Kernel-held source anchor | bind a delivered leaf to its original stable-id-matched source item and raw list index | never derive a filtered source index from the projected index alone | `agent-context-packet-and-field-visibility-v0.1.md` |
| `direct observation` | memory acquisition boundary | perception authorized by explicit committed-event `observer_refs` | permit automatic observation `MemoryDelta` only for named legal observers | public-scope membership alone is not observation | `scene-packet-to-memory-handoff-v0.1.md` |
| `ProjectionContract` | projection security object | Kernel-held external policy, recipient, context, and source anchors for one projection | validate a manifest without trusting its self-description | raw source snapshots are ephemeral Kernel data and are not copied into the manifest or public sample | `agent-context-packet-and-field-visibility-v0.1.md` |
| `ProjectionManifest` | projection audit record | complete provenance record for one model-facing projected context | use to audit included/excluded families, top-level fields, and every recursively delivered leaf | not a free-form explanation or story summary | `world-driven-runtime-v0.1.md` |
| `ValidatedProjection` | dispatch permit | immutable binding over canonical projected context, stage, exact role and instance, manifest id, and contract id | the only legal input to World-driven model dispatch | prevents validation-for-A and delivery-to-B substitution | `world-driven-runtime-v0.1.md` |
| `NormalizationRecord` | interface audit record | warning-level record of one explicitly recoverable non-security value normalization | preserve field path, policy, and before/after values while retaining raw model output | never use for identity, visibility, authority, source, target, or canon repair | `world-driven-runtime-v0.1.md` |
| `security-critical field` | validation policy | field that carries identity, authority, visibility, target, canon, or interiority permission | use for fields that must not be silently guessed | not a normal recoverable schema typo | `agent-context-packet-and-field-visibility-v0.1.md` |
| `owner_projection` | handoff filter | the owner-specific legal slice of a committed packet used for memory derivation | use for handoff-time filtering before writing `MemoryDelta` | not a new truth layer | `scene-packet-to-memory-handoff-v0.1.md` |
| `pov_contract` | packet field | packet-level authority boundary for viewpoint and interiority | use to define what narration may know or claim | do not treat it as a mere style hint | `scene-packet-schema-v0.1.md` |
| `authorized_interiority` | packet field | explicitly permitted inner material included in a `ScenePacket` | use as the legal route for packet-level inner access | absence should be treated as absence of permission | `scene-packet-schema-v0.1.md` |
| `InteriorityGrant` | proposal field | Character-owned authorization to expose one exact owner field under a bounded access mode and scope | use before World can copy interiority into a committed event | World, Plot, Narrator, and Kernel cannot invent the grant | `world-driven-runtime-v0.1.md` |
| `visibility_deltas` | packet field | newly visible or inferable consequences carried by a packet | use to separate event truth from distributed knowledge | keep distinct from `state_deltas` | `scene-packet-schema-v0.1.md` |
| `canon_reveal_candidates` | packet field | committed material that may expose `latent_canon` but still needs governance | use before steward approval | not approved public canon | `scene-packet-schema-v0.1.md` |
| `canon_effects_committed` | packet field | approved canon reveal or mutation effects attached to committed packet material | use only after steward decision or explicit no-review-needed outcome | not pending reveal material | `scene-packet-schema-v0.1.md` |
| `narration_bounds` | packet field | packet-level limits on compression and factual claims | use to constrain downstream prose rendering | do not let narrator exceed these bounds | `scene-packet-schema-v0.1.md` |
| `non_forcing_clause` | pressure field | statement of how meaningful character agency remains open under pressure | use in every `ScenePressurePacket` | absence should block or quarantine pressure | `scene-pressure-packet-and-plot-budget-v0.1.md` |
| `pressure_budget` | pressure policy | policy for limiting pressure intensity, stacking, novelty, relief, and agency risk | use to prevent Plot Agent railroading | not a story outcome | `scene-pressure-packet-and-plot-budget-v0.1.md` |
| `adjudication_basis` | resolution field | audit summary for a world-side consequence decision | use to explain decision basis without chain-of-thought | not hidden authorial reasoning | `resolution-state-delta-commit-pipeline-v0.1.md` |
| `NarrationClaimMap` | narration grounding record | unit-by-unit mapping from prose spans to legal checkpoint sources, certainty, and scope | use before Authority approval of narration | prose fluency is not grounding evidence | `world-driven-runtime-v0.1.md` |
| `NarrationClaimUnit` | narration grounding record | deterministic punctuation/newline, offset-, and hash-bound segment covering all non-whitespace prose | use as the exact coverage key for `NarrationClaimMap` | complete span coverage is not atomic semantic proposition parsing | `world-driven-runtime-v0.1.md` |
| `skipped_narration_checkpoint` | runtime trace record | checkpoint skipped because no newly accepted event is visible under the POV contract | use instead of asking Narrator to guess from an empty view | not a narration failure | `world-driven-runtime-v0.1.md` |
| `MemoryDelta` | memory unit | owner-scoped update unit for `private_memory`, bound in v0.2 to a source packet, source event, and acquisition mode | use for owner-specific memory entries derived from committed scenes or legal recollection paths | not objective world truth | `memory-delta-format-v0.1.md` |
| `delta_kind` | memory field | distinguishes what kind of memory update a delta carries | use to separate observation, suspicion, recollection, and revision | do not collapse all memory into generic content text | `memory-delta-format-v0.1.md` |
| `acquisition_mode` | memory field | records how the owner came to hold a memory | use for sensory, reported, inferred, or self-acted acquisition paths | keep distinct from certainty | `memory-delta-format-v0.1.md` |
| `memory_status` | memory field | records the current standing of a memory entry | use for active, superseded, withdrawn, or contested states | preserve revision lineage instead of silently deleting history | `memory-delta-format-v0.1.md` |
| `supersedes` | memory field | points to earlier deltas revised by a later delta | use to trace memory revision lineage | not a delete operation | `memory-delta-format-v0.1.md` |
| `MemoryRetrievalRecord` | projection audit record | selected owner-memory refs plus excluded refs and reasons under one retrieval policy | use inside `CharacterContextPacket` | not a model-written memory summary | `world-driven-runtime-v0.1.md` |
| `dramatic window` | pacing unit | bounded dramatic move larger than one utterance and smaller than a whole scene | use as the default interaction cadence | avoid defaulting to line-by-line turn simulation | `communication-permission-matrix-v0.1.md` |
| `world_state_ledger` | state layer | objective committed reality log | use for what is true in the world regardless of who knows it | do not flatten into public knowledge | `state-and-knowledge-layers-v0.1.md` |
| `public_event_ledger` | knowledge layer | events that have become publicly knowable | use for shared event history | prefer this over the coarse phrase `public ledger` | `state-and-knowledge-layers-v0.1.md` |
| `PublicScopeRegistry` | visibility registry | concrete scene, place, institution, city, or realm scope instances with type and membership | use to evaluate scoped public access | a generic public-scope label is not membership | `world-driven-runtime-v0.1.md` |
| `scope_ref` | visibility field | concrete identity of the scene or public-scope instance governing access | use with every committed visibility or public event record | never omit or substitute a generic scope name | `world-driven-runtime-v0.1.md` |
| `private_memory` | knowledge layer | agent-specific memory, belief, and recollection | use for local knowledge and misinterpretation | not always reliable and not equal to world truth | `state-and-knowledge-layers-v0.1.md` |
| `public_canon` | canon layer | stable public setting facts and openly established world rules | use for shared setting reference | keep distinct from scene events | `state-and-knowledge-layers-v0.1.md` |
| `latent_canon` | canon layer | already true canon that is not yet public | use for hidden truths and future reveals | do not leak through narrator convenience | `state-and-knowledge-layers-v0.1.md` |
| `reveal_path` | reveal governance | the lawful exposure route by which hidden canon becomes eligible for promotion | use for committed evidence, declaration, or institutional exposure paths | not every exposure is a promotion | `latent-to-public-canon-reveal-rules-v0.1.md` |
| `exposure_scope` | reveal field | the scope at which a hidden canon fact has been legally exposed | use to distinguish institutional, local, or wider exposure | do not confuse with universal public canon | `latent-to-public-canon-reveal-rules-v0.1.md` |
| `public canon promotion` | reveal outcome | the explicit governance step that moves a hidden fact into `public_canon` | use for approved latent-to-public transitions | do not infer it automatically from narration or public event publication | `latent-to-public-canon-reveal-rules-v0.1.md` |
| `canon_origin` | canon axis | provenance of a canon entry | use `preauthored`, `emergent`, `clarified`, or `promoted` independently from visibility | do not encode visibility in origin | `canon-mutation-review-checklist-v0.1.md` |
| `canon_visibility` | canon axis | lawful exposure class of a canon entry | use `public`, `latent`, or `scoped` independently from origin | not a stability judgment | `canon-mutation-review-checklist-v0.1.md` |
| `canon_stability` | canon axis | resistance of a canon entry to later mutation | use `immutable`, `stable`, `provisional`, or `contested` | not a visibility layer | `canon-mutation-review-checklist-v0.1.md` |
| `Immutable Canon` | canon layer | non-routine foundational rules and anchors | use for hard-setting constraints | avoid casual mutation | `communication-permission-matrix-v0.1.md` |
| `private_self` | visibility layer | sender-only raw cognition scope | use for hidden motive and raw inner state | never expose by default | `communication-permission-matrix-v0.1.md` |
| `private_target` | visibility layer | sender-and-target-only message scope | use for directed but non-public communication | keep distinct from self-only cognition | `communication-permission-matrix-v0.1.md` |
| `scene_public` | visibility layer | visible to legitimate scene participants | use for shared scene-level visibility | not equivalent to global public knowledge | `communication-permission-matrix-v0.1.md` |
| `system_restricted` | visibility layer | reserved for routing, validation, or canon review layers | use for infrastructure-only visibility | do not narrativize it | `communication-permission-matrix-v0.1.md` |
| `event bus` | routing layer | the validation and message-routing path | use for soft schema validation discussions | not an agent in the story world | `communication-permission-matrix-v0.1.md` |
| `soft validation, hard permission` | design principle | recover from malformed communication but block authority leakage | use as a global protocol slogan | one of the project's canonical design principles | `README.md` |
| `Candidate Read Policy` | governance policy | rule that pending publication and canon-reveal candidates remain system-restricted | use to exclude candidates from Character, Plot, and Narrator contexts | candidate status is not publication, canon, or narration permission | `world-driven-runtime-v0.1.md` |
| `SceneTransaction` | runtime transaction | all-or-nothing working state for one World-driven scene | use to distinguish provisional acceptance from outward publication | `CommittedWorldEvent` inside working state is not yet externally published | `world-driven-runtime-v0.1.md` |
| `SealingRecord` | packet audit record | deterministic record of source refs, included/excluded refs, collection hashes, packet hash, and assembly policy | use for committed or quarantined `ScenePacket` audit | quarantined adjudications are excluded refs, never published source refs | `world-driven-runtime-v0.1.md` |
| `PublicExportSeal` | export audit record | a new ScenePacket payload seal computed after private run identifiers are removed from a verified real trace | use with `seal_scope = sanitized_public_export` in public evidence | never reuse the private payload hash after redaction | `world-driven-runtime-v0.1.md` |
| `Protocol ID` | runtime identity | syntax-bounded identifier matching `^[A-Za-z][A-Za-z0-9_.:-]{0,127}$` | use for run-local tick, request, route, proposal, adjudication, event, candidate, pulse, and review identities | non-string, malformed, overlong, or replayed ids fail closed | `world-driven-runtime-v0.1.md` |
| `quarantined_runtime_state` | audit record | rejected transaction-local state preserved after rollback | use for debugging and audit only | must not feed Character, Plot, Narrator, public ledger, or memory | `world-driven-runtime-v0.1.md` |
| `working_narration_segments` | transaction-local output | Authority-approved prose held inside the current scene transaction | use before final scene commit | approval alone does not make it player-visible | `world-driven-runtime-v0.1.md` |
| `published_narration_segments` | runtime output | Authority-approved working prose released only after scene-atomic commit | use for player-visible narration | not populated by provisional approval alone | `world-driven-runtime-v0.1.md` |
| `quarantined_narration_segments` | audit record | approved or attempted working prose retained after scene rollback | use for debugging only | must never be shown as committed story output | `world-driven-runtime-v0.1.md` |
| `origin-only repair` | repair policy | bounded retry sent only to the same role through its original legal view plus allowlisted repair data | use for current World, Character, and Narrator retry paths; field paths must resolve inside the reviewed subject | not permission to expose global Judge context or replacement content | `agent-context-packet-and-field-visibility-v0.1.md` |
| `total_output_token_budget` | runtime budget | trace-wide cap over returned model output tokens | use for pre-call reservation and post-response transition blocking | does not cap input or aggregate provider-billed tokens | `world-driven-runtime-v0.1.md` |

## Discouraged or Ambiguous Terms

| Term | Status | Use instead | Reason |
| --- | --- | --- | --- |
| `public ledger` | discouraged | `public_event_ledger` or `world_state_ledger` | too coarse and collapses truth with publicity |
| `world` | context-dependent | `World Agent` when referring to the agent role | too ambiguous in protocol discussions |
| `character` | context-dependent | `Character Agent` when authority matters | can refer either to the fictional person or the system role |
| `Emergent Canon` | deprecated compound label | `canon_origin = emergent` plus explicit `canon_visibility` and `canon_stability` | sounds like a third storage or visibility layer |

## How To Extend This Index

Add a term when at least one of these becomes true:

- the term appears in more than one protocol file
- the term carries authority or storage semantics
- the term will likely be inherited by future schemas
- the term can be confused with a nearby concept

When adding a term:

1. choose one canonical spelling
2. assign it to a term family
3. define its meaning in one sentence
4. note any discouraged aliases
5. point to the source file where it is first or best defined

## Near-Term Follow-Ups

1. add a term status field such as `draft`, `stable`, `discouraged`
2. split the index into subfiles if the vocabulary family grows large
3. add explicit stability labels when terms move from conceptual to executable profiles
4. keep future trace fixture terms aligned here before implementation begins
