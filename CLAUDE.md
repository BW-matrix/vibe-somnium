# CLAUDE.md - a2a-literary-agents / vibe-somnium / 织梦

This file is onboarding context for Claude or any reviewer joining the project.

## Project Identity

| Key | Value |
| --- | --- |
| Repository | `a2a-literary-agents` |
| Codename | `vibe-somnium / 织梦` |
| Author | Bowen Qi |
| License | Code: Apache-2.0; docs/protocol text: CC BY 4.0 |
| Stage | MVP runtime prototype + protocol hardening |

The core claim: AI writing fails when authorial power collapses into one prompt-following model. This project splits authority across bounded agents and records every context projection, decision, and validation step.

## Agent Roles

| Agent | Owns | Must Not Do |
| --- | --- | --- |
| `Plot Agent` | pressure, tension, stakes | decide destiny, puppet characters, declare facts |
| `Character Agent` | intent, motive, local choice | decide objective outcome, write others' minds |
| `World Agent` | simulation flow, decision requests, consequence, state transition | choose character will, write prose, promote canon |
| `Router Agent` | bind a valid World request to one Character Agent | invent context, action, consequence, or prose |
| `Narrator Agent` | prose rendering from committed inputs | invent facts, leak hidden truth, broaden visibility |
| `Canon Steward` | canon mutation review | decide scene outcome or rewrite prose |
| `Authority Judge` | semantic authority-overreach review | create story material or rewrite reviewed objects |
| `Runtime Kernel` | deterministic projection, transport, schema checks, sealing, trace | semantic judgment or creative selection |

## Primary World-Driven Flow

```text
player/request
  -> WorldTickResult / CharacterDecisionRequest
  -> AuthorityReview of the request
  -> Router RoutePlan
  -> projected CharacterContextPacket
  -> Character EventProposal
  -> AuthorityReview
  -> immutable ApprovedEventProposal
  -> next World tick adjudication / CommittedWorldEvent
  -> AuthorityReview of WorldAdjudication
  -> periodic PlotPulse and NarrationCheckpoint
  -> Authority-reviewed player-facing prose
  -> World-owned, Authority-reviewed PlotPulseDisposition
  -> scene-atomic commit or rollback
```

Every creative model-agent receives only projected context. Full system objects are not normal prompt inputs. Judge receives an audit context, but it is not part of literary creation and cannot repair by rewriting content.
The legacy single-window v0.1 flow remains executable for regression coverage.

Runtime hardening currently includes Kernel-held projection contracts, exact role-and-instance recipient binding, sealed validated-dispatch permits, field- and leaf-complete manifests with stable-id-derived original source indices, pre-write trace-path containment, duplicate source-id rejection, one origin-bound JSON retransmission guarded by deterministic syntax/content conservation before fail-closed quarantine, cross-scene guards, syntax-bounded single-use protocol ids, bounded origin-only World/Character/Narrator semantic repairs, strict Character actor/speech/interiority ownership, separate public membership/encounter/direct-observer memory paths, executable Plot enums, audited recoverable normalization, full projection-evidence public export gating, explicit published-versus-quarantined narration under scene-atomic commit, and a committed two-scene handoff with full source-fixture hash binding, exact owner-memory allowlisting, conflicting-memory-id rejection, and reservation of both model/runtime and Kernel packet/memory identities. Judge-controlled ids never enter creative contexts. Plot has no content or authority repair loop. The full suite currently passes 107 tests and 16 subtests.

## Runtime Backends

The MVP runner supports:

- `mock`: deterministic fixture outputs
- `codex-cli`: isolated headless `codex exec` calls
- `real`: OpenAI-compatible chat completions
- `auto`: API when configured, otherwise mock

`codex-cli` mode uses an isolated `CODEX_HOME`, defaulting to `.local/codex-cli-home`. `.local/` is ignored and must never be committed because it may contain login state.

The child process receives an explicit environment allowlist rather than the parent environment, disables shell and web tools, ignores user rules/configuration, and maps the project setting `max` to the Codex CLI's accepted `xhigh` reasoning value. Unknown reasoning values fail closed.

## Current Runnable Commands

```powershell
python -m pytest -q
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_archive_exchange.json --llm-mode mock
python scripts/run_trace.py run --fixture fixtures/traces/allowed_archive_probe.json --llm-mode mock
python scripts/run_trace.py run --fixture fixtures/traces/adversarial_narrator_leak.json --llm-mode mock
python scripts/run_trace.py run --fixture fixtures/traces/adversarial_plot_railroading.json --llm-mode mock
python scripts/run_two_scene_study.py --scene-one fixtures/traces/world_driven_archive_exchange.json --scene-two-template fixtures/traces/world_driven_dawn_inspection_followup.json --out .local/two-scene-study --llm-mode codex-cli --max-rounds 100
```

Codex CLI real backend:

```powershell
$env:A2A_CODEX_HOME = Join-Path $PWD ".local\codex-cli-home"
$env:A2A_CODEX_WORKDIR = Join-Path $PWD ".local\codex-cli-workdir"
$env:A2A_LLM_MODEL="gpt-5.5"
$env:A2A_CODEX_REASONING_EFFORT="max"
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_archive_exchange.json --llm-mode codex-cli --out .local/real-runs
```

## What To Preserve

- `soft validation, hard permission`
- `private cognition, public consequence`
- `plot provides pressure, not destiny`
- `narrator cannot invent facts`
- `complete objects are system objects; agents receive projected views`
- `judge reviews authority; judge does not author`

## Important Files

- `src/a2a_literary_agents/runner.py`: single-window protocol runner
- `src/a2a_literary_agents/world_runtime.py`: primary World-driven state machine
- `src/a2a_literary_agents/campaign_study.py`: committed cross-scene materialization, continuity checks, hashes, and study metrics
- `src/a2a_literary_agents/world_projection.py`: per-role context construction for World-driven execution
- `src/a2a_literary_agents/runtime_validation.py`: deterministic identity, route, hash, and authority-envelope guards
- `src/a2a_literary_agents/visibility.py`: fail-closed event and public-scope membership checks
- `src/a2a_literary_agents/projection.py`: projected context construction
- `src/a2a_literary_agents/interface.py`: schema alias normalization before validation and sealing
- `src/a2a_literary_agents/llm.py`: mock, OpenAI-compatible, and Codex CLI providers
- `src/a2a_literary_agents/validation.py`: deterministic validators and Judge verdict handling
- `fixtures/traces/`: allowed and adversarial trace fixtures
- `docs/runner/mvp-runner-v0.1.md`: runner documentation
- `docs/runner/world-driven-mvp-v0.2.md`: primary runtime operations
- `docs/runner/world-driven-real-sample-v0.2.md`: sanitized 19-call real-provider evidence with exact usage, no agent repair, and one audited recoverable intensity normalization
- `docs/research/two-scene-continuity-study-v0.3.md`: two-scene continuity, failure, token, and latency evidence
- `scripts/run_two_scene_study.py`: bounded two-scene real-run harness with optional Scene 1 reuse
- `scripts/export_public_trace.py`: accepts only successful exact-usage Codex traces with complete per-call field/leaf evidence, contract-bound leaf paths and policy parity, and no blocking validation; it verifies the private packet seal, strips private trace material, and re-seals the public payload
- `docs/protocol/`: protocol specs
- `docs/reference/terminology-index-v0.1.md`: canonical terminology

## Current Limits

- World-driven execution is currently bounded to one scene and does not persist a campaign ledger between runs.
- Eligible World structural failures, Character proposal review failures, and Narrator review failures support one bounded origin-only semantic repair by default. Every role may receive one separately sealed syntax-only JSON retransmission; Plot has no content or authority repair loop.
- Security-critical failures, unapproved repair codes, exhausted repairs, and all hard blocks quarantine the path.
- World requests, adjudications, Plot pulses, Narrator prose, and Plot dispositions receive Authority review bound to the run and audit context.
- Scene failure rolls back published state and memory while retaining a quarantined audit snapshot.
- Publication and canon candidates are isolated but are not yet promoted inside this runtime.
- Candidate expiry values are validated but are not yet aged across persistent scene time.
- Interface normalization applies to the legacy runner; World-driven schemas fail closed.
- Codex CLI mode is slower than direct API mode.
- Codex CLI remains a harnessed agent backend, so built-in provider instructions add input-token overhead even when tools and user rules are disabled.
- Token usage is recorded per agent. Direct API and Codex CLI JSON events are exact only when supplied counts are non-negative and supplied totals equal input plus output; otherwise the runner records local estimates.
- Codex CLI output budgets are not provider-side hard caps; they are prompt guidance plus post-response precommit checks.
- The trace-wide configured budget covers output tokens only. Input and aggregate billed tokens are recorded but not hard-capped in v0.2.

## Reviewer Guidance

When reviewing this project, focus on:

- whether projected context prevents hidden omniscience
- whether World consequence is auditable
- whether Plot pressure preserves meaningful choice
- whether Narrator prose is grounded in `NarratorInputPacket`
- whether Judge detects semantic overreach without becoming a hidden author
- whether projection source lineage prevents summary laundering
- whether any late failure can still publish scene state or memory
- whether candidate and public-scope data can cross recipient boundaries
- whether `.local/` and auth material remain untracked
