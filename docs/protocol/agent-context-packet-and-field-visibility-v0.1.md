# AgentContextPacket and Field Visibility v0.1

This document defines the first runtime context assembly contract for `a2a-literary-agents`.

The access matrices define what each agent is allowed to know in principle. This spec defines what each agent actually receives during a protocol step.

Its central rule is simple:

- complete protocol objects are system objects
- agents receive projected views
- visibility labels are not security by themselves unless context assembly enforces them

Runtime status:

- this document remains the general projection law
- [world-driven-runtime-v0.1](world-driven-runtime-v0.1.md) is the normative executable v0.2 profile
- the executable profile splits the earlier `Orchestrator` umbrella into `Runtime Kernel`, `Router Agent`, and `Authority Judge`

## Purpose

`AgentContextPacket` exists to solve five protocol problems:

1. prevent hidden omniscience from returning through prompt construction
2. define per-agent projected views of `ScenePacket`, `DialogueWindow`, memory, canon, and public events
3. distinguish recoverable schema fields from security-critical authority fields
4. make `Narrator Agent` consume `NarratorInputPacket`, not raw system state
5. give `Runtime Kernel` a mechanical assembly contract instead of editorial content power

Without this layer, the protocol may say that an agent cannot know a fact while still accidentally placing that fact inside the agent's prompt context.

## Design Constraints

Context assembly should satisfy these constraints:

1. no agent receives a complete system object by default
2. each projected field must have an explicit source and permission basis
3. hidden facts, hidden cognition, and pending canon may not leak through summaries
4. security-critical fields are never silently invented unless the route context has one unique legal value
5. context compression must cite source refs and must not create new facts

## Core Objects

| Object | Meaning | Owner | Notes |
| --- | --- | --- | --- |
| `AgentContextPacket` | the general per-agent context envelope assembled for one protocol step | `Runtime Kernel` | not literary content |
| `ScenePacketView` | a projected slice of a committed `ScenePacket` | `Runtime Kernel` | recipient-specific |
| `NarratorInputPacket` | the only legal factual input for narration | `Runtime Kernel` | derived from transaction-accepted, POV-visible material; publication remains atomic |
| `CharacterContextPacket` | the context a `Character Agent` may use to form intent or dialogue | `Runtime Kernel` | owner-specific memory plus visible world |
| `PlotContextSummary` | the structural view a `Plot Agent` may use to propose pressure | `Runtime Kernel` | no raw hidden truth |
| `CanonReviewContext` | the canon-relevant context for `Canon Steward` | `Runtime Kernel` | may include restricted canon refs |
| `FieldProjection` | a field-level allowlist mapping from source object to recipient view | protocol policy | prevents object-level leakage |
| `ProjectionContract` | Kernel-held source and policy anchors for one projected context | `Runtime Kernel` | external trust root; never supplied by the manifest or recipient |
| `ProjectionManifest` | audit record for one projected context | `Runtime Kernel` | must match the separate contract, exact recipient, and delivered context |
| `ValidatedProjection` | immutable dispatch permit produced only after projection validation | `Runtime Kernel` | seals context, protocol stage, role, instance id, manifest id, and contract id |

## AgentContextPacket Shape

Suggested payload fields:

| Field | Required | Type | Meaning |
| --- | --- | --- | --- |
| `context_id` | yes | string | stable id for this context packet |
| `scene_id` | yes | string | parent scene identity |
| `window_id` | recommended | string | active dramatic window if applicable |
| `recipient_agent_id` | yes | string | exact receiving agent instance |
| `recipient_role` | yes | string | `character_agent`, `world_agent`, `plot_agent`, `narrator_agent`, `canon_steward`, or `orchestrator` |
| `protocol_step` | yes | string | why this context is being assembled |
| `visible_inputs` | yes | object | projected observations, events, packets, memory, canon, or pressure |
| `source_refs` | yes | array | all source object ids used to build the context |
| `projection_policy` | yes | string | policy name or version used for field redaction |
| `redaction_notes` | recommended | array | what was removed and why |
| `validation_warnings` | optional | array | non-fatal assembly issues |
| `forbidden_sources` | recommended | array | source families this packet explicitly did not include |
| `based_on` | recommended | array | route, packet, policy, and matrix refs |

Important rule:

- `AgentContextPacket` is an infrastructure object, not a new story fact
- it may package, filter, and cite, but it may not invent or editorialize

## Context Assembly Flow

Recommended flow:

1. identify the recipient role and active protocol step
2. collect candidate source objects by route table
3. apply role-level allowlist
4. apply field-level projection
5. remove unresolved, pending, unauthorized, or out-of-scope material
6. attach source refs and redaction notes
7. validate security-critical fields
8. deliver only the projected context

Important rule:

- validation happens before delivery, not after the receiving agent has already seen the material

## Security-Critical Fields

Some fields are ordinary schema fields. Others carry authority, privacy, or routing power.

| Field family | Examples | Missing-field behavior |
| --- | --- | --- |
| identity | `sender`, `recipient_agent_id`, `recipient_role`, `owner_agent_id` | quarantine unless route context has one unique legal value |
| authority | `message_type`, `writer_role`, `authority_basis`, `mutation_kind`, `outcome_type` | quarantine or require repair |
| visibility | `visibility`, `observer_scope`, `exposure_scope`, `scope_limit`, `knowledge_ceiling` | quarantine or require explicit repair |
| target | `target`, `target_id`, `addressee_ids`, `affected_options` | infer only if mechanically unique; otherwise repair |
| canon reference | `canon_ref`, `latent_ref`, `target_layer`, `canon_delta_ref` | defer or quarantine |
| interiority | `authorized_interiority.subject_id`, `access_mode`, `scope_limit` | reject as unusable if incomplete |

Recoverable fields include `message_id`, `scene_id`, `window_id`, `based_on`, and optional lineage metadata.

Important rule:

- soft validation may repair coordination
- it must not repair privacy or authority by guessing

## Field Projection: DialogueWindow

`DialogueWindow` is not one shareable object. It mixes private tactic, surface speech proposal, resolver input, and audit material.

| Field | Resolver view | Target visible view | Narrator candidate view | Audit-only view |
| --- | --- | --- | --- | --- |
| `window_kind` | allow | allow if visible in behavior | allow after resolution | allow |
| `speaker_id` | allow | allow | allow after resolution | allow |
| `addressee_ids` | allow | allow for included targets | allow after resolution | allow |
| `local_goal` | allow | no by default | no direct read | allow |
| `stance.emotional_tone` | allow | only if externally legible | only if committed or authorized | allow |
| `stance.tactical_posture` | allow | no by default | no direct read | allow |
| `disclosure_policy.must_not_reveal` | allow | no | no | allow |
| `disclosure_policy.may_imply` | allow | no direct read | no direct read | allow |
| `disclosure_policy.can_lie` | allow | no | no | allow |
| `disclosure_policy.preferred_mask` | allow | only as visible performance if resolved | only if committed as visible behavior | allow |
| `speech_acts.intent` | allow | no direct read | no direct read | allow |
| `speech_acts.proposition` | allow | visible if spoken or implied in committed event | allow only after commitment | allow |
| `speech_acts.candidate_lines` | allow as non-authoritative | visible only if chosen or paraphrased in committed surface | candidate reference only, never fact by itself | allow |
| `speech_acts.expected_effect` | allow | no | no | allow |
| `fallback_if_blocked` | allow | no | no direct read | allow |
| `exit_condition` | allow | no direct read | no direct read | allow |

Important rule:

- `Narrator Agent` does not render from raw `DialogueWindow`
- it may only use dialogue material after `World Agent` resolution and a transaction-safe narration projection; no prose becomes public until final `ScenePacket` sealing

## Field Projection: ScenePacket

The complete `ScenePacket` is a system object. Recipient views are narrower.

| View | Recipient | May contain | Must exclude |
| --- | --- | --- | --- |
| `ScenePacketView` | any eligible agent | fields legal for that role and step | unauthorized interiority, pending canon, hidden state not visible to recipient |
| `NarratorInputPacket` | `Narrator Agent` | committed events, authorized interiority, narration bounds, approved public/canon material | raw hidden state, rejected branches, raw DialogueWindow, unapproved candidates |
| `CharacterContextPacket` | one `Character Agent` | visible scene facts, owner memory query results, encountered public events, public canon | other private memory, raw world ledger, hidden canon |
| `PlotContextSummary` | `Plot Agent` | structure progress, public events, relationship trends, limited non-spoiling summaries | raw cognition, exact hidden world facts, future outcomes |
| `CanonReviewContext` | `Canon Steward` | canon refs, mutation request, committed evidence, reveal basis | irrelevant private cognition, prose drafts |

Important rule:

- a visibility label inside a packet is evidence for projection
- it is not permission to send the whole packet

## Agent Context Matrix

| Recipient | Default context contents | Explicit exclusions |
| --- | --- | --- |
| `Character Agent` | owner `private_memory` query result, visible observations, encountered public events, public canon, public pressure | raw `world_state_ledger`, other agents' private memory, latent canon, full `ScenePacket` |
| `World Agent` | submitted proposals, relevant world state, public canon, limited latent canon if resolution-relevant, canon decisions | raw inner monologue not transformed into action, plot destiny directives |
| `Plot Agent` | structure summary, public event trends, relationship map summaries, pressure budget state | raw hidden truth, exact private cognition, direct outcome authority |
| `Narrator Agent` | `NarratorInputPacket`, approved style guide, narration bounds | raw proposals, hidden world ledger, pending reveal candidates, unauthorized interiority |
| `Canon Steward` | canon refs, review request, committed reveal evidence, affected canon history | scene prose drafts unless canon-relevant, irrelevant private memory |
| `Orchestrator` | route metadata, validation policy, projection policy, source refs | literary content rewriting authority |

In the executable World-driven profile, the legacy `Orchestrator` row is decomposed as follows:

| Executable component | Receives | May do | Must not do |
| --- | --- | --- | --- |
| `Runtime Kernel` | system objects, schemas, registries, projection policy | deterministic projection, validation, transaction, sealing, and trace | make semantic or literary judgments |
| `Router Agent` | one approved `CharacterDecisionRequest` routing view | bind the request to its declared owner and projection policy | summarize story state, retrieve memory, or suggest a choice |
| `Authority Judge` | a subject-specific audit context | review authority, grounding, visibility, and overreach | rewrite the subject or create replacement story content |

## Context Compression Policy

Compression is allowed when a context would be too large, but compression is not free narration.

Allowed compression:

- short factual summaries of already legal material
- role-specific lists of relevant refs
- salience-ranked memory query results
- public event summaries within legal scope

Forbidden compression:

- replacing hidden facts with suggestive summaries that reveal them
- merging suspicion into fact
- turning unresolved candidate material into committed reality
- narrativizing route decisions as story meaning

Any non-mechanical summary should include:

- `source_refs`
- `compression_policy`
- `omitted_categories`

The current executable profile does not permit free-form model compression in `CharacterContextPacket`, `PlotContextSummary`, or `NarratorInputPacket`. If a later profile permits such compression, it must introduce a separately reviewed compression subject rather than silently extending Kernel authority.

## Executable Projection Manifest

Every model-facing context in the World-driven profile has a Kernel-side `ProjectionManifest` sidecar and a separate Kernel-held `ProjectionContract`. The manifest is recorded in the private trace and validated before delivery; neither object is included inside the recipient prompt or public sample. The contract, not the manifest, supplies the trusted policy id, exact `{role, instance_id}` recipient, source paths, source hashes, mapping modes, and immutable source snapshots used during validation. A manifest cannot establish its own authority by changing a source label and recomputing its hashes.

The manifest records:

- `manifest_id`
- policy id, `projection_type`, and exact `{role, instance_id}` recipient
- contract id and contract hash
- SHA-256 of the complete delivered context
- included and excluded source families
- one `FieldProjection` for every top-level projected field
- one leaf-projection record for every recursively delivered terminal value, including empty containers

Each `FieldProjection` records:

- destination field
- SHA-256 of the delivered field value
- exact source path
- SHA-256 of the source value before projection
- deterministic projection operation
- mapping mode: external `source_projection` or registered `kernel_policy_derivation`

Each leaf record additionally carries the exact JSON-style destination path, `source_tokens` relative to its contract anchor, and hashes the delivered leaf. Filtered arrays resolve a stable object id such as `event_id`, `publication_id`, or `memory_id` before recording the original source index; compacted projected indices are never reused as source indices. Duplicate stable identities are rejected before projection, and identity-bearing lists never fall back to structural equality when identity resolution is missing or ambiguous.

Before delivery, Kernel independently supplies the expected stage policy and exact recipient, verifies the external contract, complete field and leaf coverage, source-anchor hashes, source paths, source tokens, mapping modes, projection operations, duplicate or unknown paths, and every delivered value hash. Unanchored story fields quarantine the projection. Success creates a sealed `ValidatedProjection`; model dispatch accepts that permit rather than separate mutable `role`, `instance_id`, and `projected_context` arguments. The final context hash or top-level-only provenance is not sufficient.

## Origin-Only Repair Projections

Repair is another projection boundary, not permission to resend a global audit dump.

| Repair packet | Recipient | Legal contents | Explicit exclusions |
| --- | --- | --- | --- |
| `WorldRepairContextPacket` | original `World Agent` instance | original legal World context, rejected tick, deterministic allowlisted violation codes, fixed constraints | Judge prose, Character-private data absent from the original context, new story suggestions |
| `CharacterRepairContextPacket` | original `Character Agent` owner | original legal Character context, that Character's rejected proposal, code-only Judge repair objects | Judge ids, global audit context, other memory, hidden state, free-text Judge findings |
| `NarrationRepairContextPacket` | original `Narrator Agent` instance | original legal narration view, rejected prose, code-only Judge repair objects | Judge ids, hidden facts, candidate material, global audit context, replacement prose |

Repair count is fixture-bounded. A Judge-provided `field_path` must resolve inside the reviewed subject; paths into `source_context` or `global_audit_context` are blocked rather than forwarded. A repaired object must pass the complete original schema, deterministic validation, projection validation, and any required Authority review; failed content never enters working state merely because a retry exists.

## Runtime Visibility and Retrieval Rules

The executable profile applies these additional rules before delivery:

1. `scene_public` requires `scope_ref` equal to the current `scene_id` and an explicit scene participant registry.
2. `private_self` requires one observer equal to the event's primary actor and a matching owner `scope_ref`.
3. `scene_pair` requires exactly two unique current scene participants and includes every event actor.
4. `local_public`, `institution_public`, `city_public`, and `realm_public` require a registered scope instance with matching type and membership.
5. Membership makes a scoped public record legally queryable; it does not make the member a direct observer.
6. A newly committed event enters direct-observation memory only for explicit `observer_refs`; public-scope observers must also belong to the cited scope instance.
7. A public ledger record enters a Character context only when the character has an explicit encounter ref and valid scope membership.
8. Character memory retrieval filters by allowed status, ranks by declared salience with certainty fallback, applies the configured item cap, and records every excluded ref and reason.
9. Superseded or withdrawn memory is excluded unless a later policy explicitly authorizes historical retrieval.
10. `PublicationCandidate` and `CanonRevealCandidate` are system-restricted and absent from Character, Plot, and Narrator contexts.

## Review and Replay Binding

Projection is necessary but not sufficient for authority safety. Every `AuthorityReview` in the executable profile is also bound to:

- exact `subject_id`, `subject_type`, and `subject_sha256`
- non-empty `reviewed_fields` covering every critical field for that subject type
- non-empty `authority_basis`
- exact random `run_nonce`
- exact `review_context_sha256`

Missing or mismatched bindings quarantine the subject. The Kernel does not infer them from prose or route convenience.

## Hard Boundaries

Context assembly may:

- project fields
- redact illegal material
- attach warnings and source refs
- produce per-agent context packets

Context assembly may not:

- invent facts
- choose literary emphasis as if it were an author
- launder hidden state into summaries
- make pending canon usable as public truth
- repair missing security-critical fields by creative inference

## Example

```json
{
  "context_id": "ctx_char_lin_018_06",
  "scene_id": "scene_018",
  "window_id": "win_018_06",
  "recipient_agent_id": "char_lin",
  "recipient_role": "character_agent",
  "protocol_step": "prepare_dialogue_window",
  "visible_inputs": {
    "observations": [
      "Wei asked about the records room in a way Lin could perceive as unusually careful."
    ],
    "private_memory_query": [
      "Lin remembers hearing hurried footsteps near the archive."
    ],
    "public_events": [],
    "public_canon": [
      "Archive ledgers are normally sealed after dusk."
    ],
    "pressure": [
      "The inspection deadline is approaching."
    ]
  },
  "source_refs": ["sp_018_02:view:char_lin", "md_lin_201", "pc_archive_rule_03", "spp_018_01:view:public"],
  "projection_policy": "field_visibility_v0.1",
  "redaction_notes": [
    "Wei's disclosure_policy and hidden goal were excluded.",
    "Raw world_state_ledger entries were not included."
  ],
  "forbidden_sources": ["raw_world_state_ledger", "latent_canon", "other_private_memory"],
  "based_on": ["agent-constraint-matrix-v0.1", "communication-permission-matrix-v0.1"]
}
```

## Relationship to Adjacent Specs

This document should be read together with:

- `communication-permission-matrix-v0.1.md`
- `agent-constraint-matrix-v0.1.md`
- `dialogue-window-schema-v0.1.md`
- `scene-packet-schema-v0.1.md`
- `scene-packet-to-memory-handoff-v0.1.md`

Current executable status:

1. the World-driven runtime emits and validates top-level plus recursively complete leaf provenance for every model-facing context
2. adversarial fixtures cover hidden-state leakage, candidate leakage, public-scope confusion, replay, and projection laundering
3. bounded origin-only World, Character, and Narrator repair projections are executable; Plot has no repair projection
4. remaining work is broader long-form retrieval, canon-governance execution, and stronger semantic assurance beyond one Judge call
