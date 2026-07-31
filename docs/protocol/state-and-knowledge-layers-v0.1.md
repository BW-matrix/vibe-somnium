# State and Knowledge Layers v0.1

This document defines the general storage and knowledge-separation model. The executable visibility, public-scope, and retrieval profile is specified in [world-driven-runtime-v0.1](world-driven-runtime-v0.1.md).

This document defines the storage and visibility model behind the protocol.

The main correction introduced here is simple:

- something can be true in the world
- without being public
- without being known by every character

Because of that, `public ledger` is too coarse as a primary term.

This spec separates world truth, public knowledge, private memory, and canon.

## Core Distinction

The system must distinguish at least these two questions:

1. What is objectively true right now?
2. Who is allowed to know it?

If those are collapsed into one shared ledger, the system drifts back toward hidden omniscience.

## Layer Overview

| Layer | Meaning | Typical contents | Visibility |
| --- | --- | --- | --- |
| `world_state_ledger` | objective committed reality | locations, injuries, stolen objects, hidden actions, changed resources | system-restricted |
| `public_event_ledger` | events that have become publicly knowable | public speeches, discovered crimes, witnessed fights, announced policies | shared/public |
| `private_memory` | agent-specific knowledge, belief, and recollection | secrets, partial observations, mistaken inferences, personal history | self only unless explicitly exposed |
| `public_canon` | stable world rules and publicly established setting facts | geography, institutions, public history, openly known role facts | shared/public |
| `latent_canon` | already true but not yet publicly revealed canon | hidden lineage, sealed history, secret institutions, unrevealed rule exceptions | restricted |

## Layer Roles

### `world_state_ledger`

This is the closest thing to the system's objective reality log.

It stores:

- what has actually happened
- what has physically changed
- where people and important objects are
- what hidden actions succeeded or failed
- what consequences are already real even if nobody has noticed yet

It should not be universally readable by character agents.

### `public_event_ledger`

This is not "everything that happened."

It is only:

- what has become publicly observable
- what has been publicly declared
- what has been discovered or widely learned
- what a normal scene participant is allowed to treat as shared reality

This is the layer that should usually replace the old coarse phrase `public ledger`.

### `private_memory`

Each character should maintain its own memory layer.

This includes:

- direct observations
- suspicions
- incomplete or distorted recollections
- secrets
- personal interpretation of prior scenes

`private_memory` is not always reliable, and it should not be collapsed into world truth.

### `public_canon`

This is the stable public setting base.

It answers questions like:

- what kind of world this is
- what institutions exist
- what public history is accepted
- which role facts are already established openly

It should be durable and slow-changing compared with scene events.

### `latent_canon`

This is canon that already exists at the system level but is not yet public.

It is useful for:

- future reveals
- secret world structures
- backstory that should constrain the story before readers know it
- hidden truths that must stay consistent across scenes

## Access Matrix

| Layer | Character Agent | World Agent | Plot Agent | Narrator Agent | Canon Steward | Orchestrator |
| --- | --- | --- | --- | --- | --- | --- |
| `world_state_ledger` | no direct access | full access | limited summaries only | no direct access | access when canon review needs it | metadata-level access as needed |
| `public_event_ledger` | read access | full access | read access | committed summaries only | read access | read access |
| `private_memory` | own memory only | no raw access; only transformed proposals and authorized deltas | no raw access | limited POV-scoped access only when authorized | no routine access | no routine literary access |
| `public_canon` | read access | read access | read access | limited render-relevant access | full access | policy-summary access |
| `latent_canon` | no direct access | limited resolution-relevant access | limited structure-relevant access | no direct access | full access | no routine access |

Important runtime rule:

- this access matrix defines maximum legal access
- actual prompt/context delivery must go through `AgentContextPacket` and field-level projection
- full ledger access should not be simulated by placing ledger summaries into every agent context

For context assembly, see [agent-context-packet-and-field-visibility-v0.1](agent-context-packet-and-field-visibility-v0.1.md).

## Write Responsibility

| Layer | Primary writer | Secondary writer | Notes |
| --- | --- | --- | --- |
| `world_state_ledger` | `World Agent` | `Orchestrator` may package references, not invent facts | truth first enters the system here |
| `public_event_ledger` | `World Agent` | `Orchestrator` may publish committed event summaries | only after visibility conditions are met |
| `private_memory` | owning `Character Agent` | `World Agent` may inject observation deltas | each agent keeps its own local record |
| `public_canon` | `Canon Steward` | none by default | used for stable public setting facts |
| `latent_canon` | `Canon Steward` | none by default | revealed later, not improvised by scene convenience |

## Promotion Rules

The most important transitions are:

### 1. From action to world truth

When a hidden or visible action is resolved, the result goes into `world_state_ledger`.

This answers:

- Did it happen?
- Did it fail?
- What changed?

### 2. From world truth to private knowledge

If a character saw, heard, inferred, or plausibly noticed something, the relevant part becomes a `private_memory` delta.

Different characters may receive:

- different fragments
- different certainty levels
- different interpretations

### 3. From world truth to public knowledge

Only when an event becomes broadly knowable should it enter `public_event_ledger`.

Typical triggers:

- public speech
- witnessed confrontation
- discovered evidence
- public announcement
- consequence too large to remain hidden
- explicit information release

### 4. From latent canon to public canon

When a hidden canon fact is legitimately revealed and stabilized, it may move from `latent_canon` to `public_canon`.

This should be explicit, not accidental narrator leakage.

## Example

A hidden theft happens at night:

- Wei steals the ledger
- Lin hears hurried footsteps
- the archive door is scratched
- nobody publicly discovers the loss until morning

The layers should update like this:

### `world_state_ledger`

- ledger removed from archive cabinet
- archive lock damaged
- Wei now possesses the ledger

### `private_memory: Wei`

- I took the ledger
- I damaged the lock
- I believe no one saw me

### `private_memory: Lin`

- heard hurried footsteps near archive
- uncertain whether the sound came from Wei

### `public_event_ledger`

Only after discovery:

- archive break-in discovered
- ledger officially reported missing

## Protocol Consequences

This model implies several rules:

1. `Narrator Agent` should not narrate from `world_state_ledger` unless the scene packet or POV authority allows it.
2. `Plot Agent` may use high-level structure summaries, but not raw hidden truth as a free omniscient planning stream.
3. `Character Agent` should reason from `private_memory`, `public_event_ledger`, visible observations, and `public_canon`.
4. `World Agent` is the main bridge between objective change and distributed knowledge.
5. `Runtime Kernel` should deliver projected views, not complete system objects, when assembling agent contexts; `Orchestrator` is the legacy umbrella term.

## Executable Public Scope Registry

Public visibility is scoped social access, not global omniscience. Executable v0.2 requires:

- `scene_public` with `scope_ref` equal to the current scene id and explicit registered participants
- `local_public`, `institution_public`, `city_public`, or `realm_public` with a registered scope instance, matching scope type, and explicit members
- an exact `publication_id` in the character's encounter refs before a public event enters `CharacterContextPacket`
- valid membership in the event's scope at the time of projection

Two institutions with the same scope type do not share membership. An event can remain queryable in `public_event_ledger` without being copied into every owner's `private_memory`.

## Executable Character Memory Retrieval

The current `CharacterContextPacket` retrieves only owner memory. Its configured policy:

1. filters to allowed `memory_status` values, normally `active` and `contested`
2. excludes `superseded` and `withdrawn` records by default
3. ranks declared salience, falling back to certainty, then preserves recency by list position
4. applies a hard item cap
5. records selected refs and every exclusion reason in `memory_retrieval_record`
6. performs no model-authored compression

## Terminology Recommendation

Going forward, prefer these terms:

- `world_state_ledger`
- `public_event_ledger`
- `private_memory`
- `public_canon`
- `latent_canon`

Avoid using plain `public ledger` unless the context clearly means the public event layer.

## Current Follow-Ups

1. persist public-scope membership and encounter history across scenes
2. complete the canon-vs-state classification checklist
3. extend memory retrieval with contradiction and long-form retention policies without hiding source lineage
4. test multi-scene propagation and expiry under real providers
