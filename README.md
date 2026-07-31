# a2a-literary-agents

Working title / codename: `vibe-somnium / 织梦`

`a2a-literary-agents` is an experimental protocol and MVP runtime for literary multi-agent writing systems. The project explores whether fiction generation can become more stable when authorial power is split across bounded agents instead of concentrated inside one omniscient model prompt.

## Core Premise

Direct AI writing often collapses because the world changes with the latest prompt. Characters know too much, consequences bend toward convenience, and narration can quietly turn suspicion into fact.

This project treats that as an authority-boundary problem:

- `Plot Agent` provides pressure, not destiny.
- `Character Agent` decides intent, not outcome.
- `World Agent` controls simulation flow and consequence, not character will or prose.
- `Router Agent` routes a World decision request, but does not write context or action.
- `Narrator Agent` renders committed material, not hidden truth.
- `Canon Steward` reviews canon mutation, not scene outcome.
- `Authority Judge` reviews semantic authority overreach, but cannot rewrite story content.
- `Runtime Kernel` projects, validates, transports, seals, and records mechanically; it has no creative authority.

## Runtime Shape

The primary v0.2 runtime is a World-driven scene loop:

```text
player/request
  -> World Agent -> WorldTickResult / CharacterDecisionRequest
  -> Authority Judge -> request review
  -> Router Agent -> RoutePlan
  -> Runtime Kernel -> projected CharacterContextPacket
  -> Character Agent -> EventProposal
  -> Authority Judge -> AuthorityReview
  -> Runtime Kernel -> immutable ApprovedEventProposal
  -> next World tick -> WorldAdjudication / CommittedWorldEvent
  -> Authority Judge -> adjudication review
  -> repeat until deterministic checkpoint
  -> Plot Agent -> PlotPulse -> Authority Judge
  -> Narrator Agent -> grounded prose -> Authority Judge
  -> World Agent -> explicit PlotPulseDisposition -> Authority Judge
  -> scene-atomic commit or rollback
```

Every creative model-agent receives only a projected context. Complete protocol objects remain system objects.
The original single-window v0.1 runner remains available as a regression and compatibility path.

## Runnable MVP

The repository now includes a minimal Python runner:

- deterministic `mock` backend for fixtures and tests
- isolated `codex-cli` backend for headless local Codex execution
- OpenAI-compatible `real` backend for API-compatible providers
- a World-driven state machine with independent character-agent calls
- an explicit committed two-scene handoff that carries World history, owner-only memory, pressure, and reserved protocol ids without a persistent database
- hard identity, routing, visibility, source-reference, replay, and content-hash checks
- one origin-bound malformed-JSON retry guarded by deterministic syntax/content conservation, followed by fail-closed quarantine, plus syntax- and length-bounded protocol identities
- run-bound semantic Authority Judge gates for requests, proposals, World adjudication, Plot pressure, prose, and Plot disposition
- field- and leaf-complete `ProjectionManifest` provenance bound to a separate Kernel-held `ProjectionContract`, exact `{role, instance_id}` recipient, and stable-id-derived original source indices
- sealed `ValidatedProjection` dispatch permits so a context validated for one recipient cannot be sent to another model-agent
- pre-write safe-path checks for trace artifacts plus duplicate source-identity quarantine before projection
- Character-owned actor, speech, and interiority source binding across the World adjudication boundary
- executable Plot kind/scope/duration allowlists and cross-scene object rejection
- explicit separation of public-scope membership, encounter, direct observation, and private-memory writes
- bounded origin-only repair for eligible World, Character, and Narrator failures
- auditable normalization for explicitly recoverable non-security values
- scene-atomic rollback that prevents failed prose from publishing state or memory
- public trace export that verifies complete per-call field and leaf evidence, contract-bound source paths and policy parity, rejects blocking validation, verifies the private seal, and re-seals the sanitized payload
- an isolated Codex child environment that inherits no arbitrary parent secrets or user rules
- interface normalization for the legacy v0.1 runner
- trace reports that include projected inputs, raw agent outputs, token usage, validation results, Judge verdicts, sealed packets, and memory handoff

See [World-Driven Runtime v0.2](docs/protocol/world-driven-runtime-v0.1.md), the [World-Driven MVP Runner](docs/runner/world-driven-mvp-v0.2.md), and the [sanitized real Codex sample](docs/runner/world-driven-real-sample-v0.2.md). The legacy [MVP Trace Runner v0.1](docs/runner/mvp-runner-v0.1.md) remains a compatibility profile.

## Quick Start

Run deterministic tests:

```powershell
python -m pytest -q
```

Run the allowed fixture with mock outputs:

```powershell
python scripts/run_trace.py run --fixture fixtures/traces/allowed_archive_probe.json --llm-mode mock
```

Run the World-driven two-character fixture:

```powershell
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_archive_exchange.json --llm-mode mock
```

Run the bounded two-scene continuity study:

```powershell
python scripts/run_two_scene_study.py --scene-one fixtures/traces/world_driven_archive_exchange.json --scene-two-template fixtures/traces/world_driven_dawn_inspection_followup.json --out .local/two-scene-study --llm-mode codex-cli --max-rounds 100
```

Run with an isolated Codex CLI backend:

```powershell
$env:A2A_CODEX_HOME = Join-Path $PWD ".local\codex-cli-home"
$env:A2A_CODEX_WORKDIR = Join-Path $PWD ".local\codex-cli-workdir"
$env:A2A_LLM_MODEL="gpt-5.5"
$env:A2A_CODEX_REASONING_EFFORT="max"
$env:A2A_LLM_TIMEOUT_SECONDS="240"
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_archive_exchange.json --llm-mode codex-cli --out .local/real-runs
```

`.local/` is ignored and must not be committed. It may contain local Codex CLI login state.

## Current Fixtures

| Fixture | Expected | Purpose |
| --- | --- | --- |
| `world_driven_archive_exchange.json` | `allowed` | World requests separate Wei and Lin decisions; Router, Authority Judge, World adjudication, Plot checkpoint, and Narrator checkpoint all run |
| `world_driven_dawn_inspection_followup.json` | real-provider follow-up template | materialized only after a committed first scene; tests cross-scene state, owner memory, pressure, and protocol-id continuity; intentionally has no fabricated mock outputs |
| `world_driven_scheduled_bell.json` | `allowed` | World consumes a registered scheduled event without inventing a Character choice |
| `allowed_archive_probe.json` | `allowed` | legal pressure, legal character probing, scoped suspicion, legal narration, Judge allow |
| `adversarial_narrator_leak.json` | `blocked` | narrator turns suspicion into confirmed guilt; deterministic validator and Judge block it |
| `adversarial_plot_railroading.json` | `blocked` | Plot pressure puppets character choice and is blocked early |

## Verified Real Sample

One isolated `gpt-5.5` Codex CLI run of `world_driven_archive_exchange.json` completed the 19-call base path with a committed scene transaction. Provider telemetry reported 247,016 input tokens, 21,511 output tokens, and 268,527 total tokens, with 19 exact and no estimated call records. The run required no repair; Plot's recoverable `moderate` intensity synonym was transparently normalized to the executable `medium` enum and retained in the audit record.

The public sample preserves every model-agent's parsed output and per-call usage while excluding prompts, projected context payloads, raw provider JSONL, local paths, private run identifiers, and authentication state. Export requires a successful committed Codex CLI trace with exact provider usage, one uniquely bound manifest and contract per call, consistent recipient and context hashes, complete recursively delivered leaf coverage, contract-bound leaf source paths and operations, manifest/contract policy parity, no unanchored field or blocking validation, and a valid private ScenePacket seal. It then creates a separate `sanitized_public_export` seal. See [World-Driven Real Codex Sample v0.2](docs/runner/world-driven-real-sample-v0.2.md).

The invoked roles were World, Authority, Router, two independent Character instances, Plot, and Narrator. Canon Steward was not invoked because this fixture produced no executable canon-promotion step; the sample does not fabricate placeholder agent output.

## Two-Scene Continuity Study

A final isolated `gpt-5.5` hardening run completed two consecutive committed scenes under independent 100-World-tick and 100-model-call caps per scene. The accepted pair used 38 calls, 8 World ticks, 522,424 input tokens, 53,351 output tokens, and 575,775 total tokens in 1,624.597 runtime seconds. All 13 current checks passed, including full fixture/packet binding, exact owner-memory allowlisting, exact pressure transfer, complete 33-id reservation, and cross-scene non-replay.

The discovery campaign and final rerun consumed 1,447,739 tokens across 96 calls. Negative attempts exposed one Authority miss on a mixed Character action and one mechanically derivable Plot count error; independent review then found incomplete fixture, memory, and Kernel-id binding in the historical harness. Those gaps were fixed and the final pair rerun successfully. Its prose still contains a Lin pronoun inconsistency, demonstrating that protocol continuity is stronger than current literary-presentation continuity. See the [full study](docs/research/two-scene-continuity-study-v0.3.md) and the complete sanitized outputs for [Scene 1](docs/research/two-scene-continuity-scene-1-public-trace-v0.3.md) and [Scene 2](docs/research/two-scene-continuity-scene-2-public-trace-v0.3.md).

## Protocol Documents

- [communication-permission-matrix-v0.1](docs/protocol/communication-permission-matrix-v0.1.md)
- [world-driven-runtime-v0.1](docs/protocol/world-driven-runtime-v0.1.md)
- [agent-constraint-matrix-v0.1](docs/protocol/agent-constraint-matrix-v0.1.md)
- [agent-context-packet-and-field-visibility-v0.1](docs/protocol/agent-context-packet-and-field-visibility-v0.1.md)
- [scene-pressure-packet-and-plot-budget-v0.1](docs/protocol/scene-pressure-packet-and-plot-budget-v0.1.md)
- [dialogue-window-schema-v0.1](docs/protocol/dialogue-window-schema-v0.1.md)
- [resolution-state-delta-commit-pipeline-v0.1](docs/protocol/resolution-state-delta-commit-pipeline-v0.1.md)
- [scene-packet-schema-v0.1](docs/protocol/scene-packet-schema-v0.1.md)
- [scene-packet-to-memory-handoff-v0.1](docs/protocol/scene-packet-to-memory-handoff-v0.1.md)
- [memory-delta-format-v0.1](docs/protocol/memory-delta-format-v0.1.md)
- [state-and-knowledge-layers-v0.1](docs/protocol/state-and-knowledge-layers-v0.1.md)
- [event-publication-thresholds-v0.1](docs/protocol/event-publication-thresholds-v0.1.md)
- [latent-to-public-canon-reveal-rules-v0.1](docs/protocol/latent-to-public-canon-reveal-rules-v0.1.md)
- [canon-mutation-review-checklist-v0.1](docs/protocol/canon-mutation-review-checklist-v0.1.md)
- [terminology-index-v0.1](docs/reference/terminology-index-v0.1.md)

## Working Principles

- `soft validation, hard permission`
- `private cognition, public consequence`
- `plot provides pressure, not destiny`
- `narrator cannot invent facts`
- `complete objects are system objects; agents receive projected views`
- `judge reviews authority; judge does not author`
- `World controls simulation flow; each authority still controls only its own domain`

## Current Limits

- The World-driven runner now has a bounded two-scene materialization helper, but it is not a persistent story server or campaign database.
- Eligible World structural failures, Character `EventProposal` review failures, and Narrator review failures support one bounded origin-only semantic repair by default. Any agent may receive one separately sealed syntax-only JSON retransmission; Plot has no content or authority repair loop.
- Security-critical, authority, visibility, identity, replay, and unapproved repair failures quarantine the path; exhausted repair limits also quarantine it.
- Runtime Kernel validators enforce interfaces, provenance, and ownership; natural-language causal and prose coverage still depends on Authority Judge quality.
- Publication and canon candidates are isolated and recorded, but in-loop publication and Canon Steward promotion are not yet implemented.
- Candidate expiry values are validated but are not yet aged across persistent scene time.
- World-driven schemas are strict; interface alias normalization belongs to the legacy compatibility runner.
- Codex CLI mode is slower than direct API mode because each agent call is a separate headless process.
- Codex CLI is a harnessed agent backend rather than a bare model endpoint; even with tools and user rules disabled, built-in provider instructions contribute input-token overhead.
- Token usage is recorded per agent. Direct API and Codex CLI JSON events count as exact only when non-negative supplied totals are arithmetically consistent; otherwise the runner records local estimates.
- Codex CLI output limits are prompt guidance plus post-response precommit checks, not guaranteed provider-side cost caps.
- `A2A_TOTAL_OUTPUT_TOKEN_BUDGET` limits returned output only; input and aggregate billed tokens are telemetry rather than a provider-side hard cap in v0.2.

## License

This repository uses a mixed-license structure.

- Code and other non-documentation repository contents are licensed under Apache-2.0.
- Documentation and protocol text, including `README.md`, `CLAUDE.md`, and all files under `docs/`, are licensed under CC BY 4.0.
- Attribution and origin context are summarized in `NOTICE`.

See [LICENSE](LICENSE), [LICENSE-docs](LICENSE-docs), and [NOTICE](NOTICE).
