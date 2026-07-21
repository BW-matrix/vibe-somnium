# World-Driven MVP Runner v0.2

This document is the operational guide for the current World-driven MVP.

The normative authority and transaction contract is in `../protocol/world-driven-runtime-v0.1.md`.

## Runtime Selection

The public CLI calls `run_trace()`. Fixture metadata selects the path:

| Fixture condition | Runner |
| --- | --- |
| `runtime_mode = world_driven` | primary World-driven v0.2 runtime |
| `runtime_mode = legacy_window_v0.1` | legacy single-window compatibility runtime |
| missing or any other value | rejected before runtime selection; never falls back |

The legacy runner remains for regression fixtures. It is not the primary architecture.

## Requirements

- Python 3.11 or newer
- no third-party Python dependency for the core runner
- optional authenticated Codex CLI for `codex-cli` mode
- optional OpenAI-compatible endpoint for `real` mode

## Commands

Run all tests:

```powershell
python -m pytest -q
```

Run the allowed two-character fixture with deterministic mock outputs:

```powershell
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_archive_exchange.json --llm-mode mock
```

Run autonomous scheduled World progression:

```powershell
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_scheduled_bell.json --llm-mode mock
```

Choose a local artifact root:

```powershell
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_archive_exchange.json --llm-mode mock --out .local/verification-runs
```

The CLI prints:

```text
trace_id=<fixture trace id>
final_decision=allowed | blocked
token_total=<recorded total>
token_input=<recorded input>
token_output=<recorded output>
trace_json=<artifact path>
report_md=<artifact path>
```

Allowed exits use code `0`; blocked traces use code `2`.

## Backends

| Mode | Behavior |
| --- | --- |
| `mock` | consumes queued fixture outputs and records deterministic local token estimates |
| `codex-cli` | starts an isolated headless `codex exec` process for each model-agent call |
| `real` | calls an OpenAI-compatible chat-completions endpoint |
| `auto` | uses API mode when a key is configured, otherwise mock mode |

### Isolated Codex CLI

Recommended local configuration:

```powershell
$env:A2A_CODEX_HOME = Join-Path $PWD ".local\codex-cli-home"
$env:A2A_CODEX_WORKDIR = Join-Path $PWD ".local\codex-cli-workdir"
$env:A2A_CODEX_BINARY = Join-Path $PWD ".local\codex-cli\node_modules\@openai\codex-win32-x64\vendor\x86_64-pc-windows-msvc\bin\codex.exe"
$env:A2A_LLM_MODEL="gpt-5.5"
$env:A2A_CODEX_REASONING_EFFORT="max"
$env:A2A_LLM_TIMEOUT_SECONDS="240"
$env:A2A_MAX_LLM_CALLS_PER_TRACE="24"
$env:A2A_TOTAL_OUTPUT_TOKEN_BUDGET="300000"
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_archive_exchange.json --llm-mode codex-cli --out .local/real-runs
```

The runner uses:

- an isolated `CODEX_HOME`
- a dedicated ignored working directory that the operator should keep empty
- read-only sandbox
- no approvals
- ephemeral sessions
- ignored repository rules and user config
- explicit `model_reasoning_effort`; project `max` maps to the CLI's accepted `xhigh`
- a reconstructed OS-only child environment that does not inherit arbitrary parent secrets
- projected protocol context through stdin

`.local/` is ignored. Login state, OAuth material, local binaries, and real traces must never be committed.

The local npm package path above is Windows/x64-specific. If `codex` is already available on `PATH`, omit `A2A_CODEX_BINARY` or set it to `codex`; binary location and `CODEX_HOME` isolation are separate concerns.

Codex CLI output-token values are prompt guidance plus post-response transition limits. The current CLI integration has no provider-side hard output-token flag. Timeout and call count are hard process controls.

This backend is still the Codex agent harness, not a bare model endpoint. Disabling tools and user rules reduces capability and leakage surface but does not remove built-in provider instructions, which contribute to input-token cost and latency.

### OpenAI-Compatible Backend

Example:

```powershell
$env:A2A_LLM_BASE_URL="https://example.invalid/v1"
$env:A2A_LLM_API_KEY="local-secret"
$env:A2A_LLM_MODEL="provider-model"
$env:A2A_LLM_TOKEN_FIELD="max_tokens"
python scripts/run_trace.py run --fixture fixtures/traces/world_driven_archive_exchange.json --llm-mode real --out .local/real-runs
```

The configured token field is sent to the provider. Whether a non-OpenAI gateway accepts the field depends on that gateway.

## Allowed Archive Fixture

`world_driven_archive_exchange.json` demonstrates:

- independent Wei and Lin Character Agent calls
- Authority review of both World decision requests
- exact Router request-hash preservation
- Character-owned `EventProposal` objects
- explicit owner `interiority_grant`
- Authority review before World receives an approved proposal
- Authority review before World adjudication enters working state
- visibility-scoped private speech events
- Plot option-topology and pressure-budget review
- Narrator checkpoint projection and claim-map review
- explicit World deferral and Authority review of a pending Plot pulse
- scene-atomic commit and owner-specific memory handoff
- bounded origin-only repair when Authority rejects an unsupported proposal field

Deterministic mock base-path counts:

| Trace field | Expected |
| --- | --- |
| `agent_runs` | 19, plus 2 for each successful Character repair and re-review |
| `world_ticks` | 4 |
| `route_plans` | 2 |
| `event_proposals` | 2, plus each rejected repair source retained for audit |
| `approved_event_proposals` | 2 |
| `authority_reviews` | 9, plus one per repaired subject |
| `world_adjudications` | 2 |
| committed events | 2 |
| `plot_pulses` | 1 |
| `plot_pulse_dispositions` | 1 |
| `narration_segments` | 1 |
| `repair_attempts` | 0 on the base path; one syntax-only retransmission or fixture-bounded semantic repair when required |
| transaction status | `committed` |

## Exact 19-Call Base Order

| Index | Role / instance | Stage | Result |
| --- | --- | --- | --- |
| 0 | World / `world_controller` | `world_tick_0` | request Wei decision |
| 1 | Authority / `authority_judge` | `authority_decision_request_cdr_wei_001` | approve bounded request |
| 2 | Router / `character_router` | `route_cdr_wei_001` | route to Wei |
| 3 | Character / `char_wei` | `character_decision_cdr_wei_001` | propose Wei speech |
| 4 | Authority | `authority_event_proposal_prop_wei_001` | approve exact proposal |
| 5 | World | `world_tick_1` | adjudicate Wei and request Lin |
| 6 | Authority | `authority_world_adjudication_wadj_wei_001` | approve consequence |
| 7 | Authority | `authority_decision_request_cdr_lin_001` | approve Lin request |
| 8 | Router | `route_cdr_lin_001` | route to Lin |
| 9 | Character / `char_lin` | `character_decision_cdr_lin_001` | propose Lin reply and grant bounded focal intent |
| 10 | Authority | `authority_event_proposal_prop_lin_001` | approve exact proposal or request bounded repair |
| 11 | World | `world_tick_2` | adjudicate Lin and request finish |
| 12 | Authority | `authority_world_adjudication_wadj_lin_001` | approve consequence |
| 13 | Plot / `plot_checkpoint` | `plot_checkpoint_2` | propose deadline pressure |
| 14 | Authority | `authority_plot_pulse_pulse_archive_001` | approve non-forcing pulse |
| 15 | Narrator / `narrator_checkpoint` | `narration_ncp_world_driven_archive_exchange_2` | render two visible events |
| 16 | Authority | `authority_narration_ncp_world_driven_archive_exchange_2` | approve claim map |
| 17 | World | `world_tick_3` | explicitly defer unmaterialized pressure |
| 18 | Authority | `authority_plot_disposition_pulse_archive_001` | approve disposition |

This final World and Authority pair is intentional. Runtime Kernel cannot invent a disposition merely because the earlier World tick requested scene finish.

The current verified real sample completed the 19-call base path without repair and with one audited recoverable Plot-intensity normalization. Origin-only semantic and syntax repair remain executable and are covered by deterministic regression tests; a successful sample is not required to manufacture a repair merely to demonstrate the branch.

## Scheduled Bell Fixture

`world_driven_scheduled_bell.json` proves World can advance a registered objective schedule without asking Character to choose a non-choice.

Expected order:

1. World consumes the exact registered schedule id and hash.
2. Authority reviews the deterministic adjudication.
3. Narrator renders the focal-visible bell and opening doors.
4. Authority reviews the narration claims.

The schedule id is recorded as consumed, preventing replay inside the run.

## Projection Evidence

Every model call records one Kernel-side `ProjectionManifest` sidecar with:

- stage policy, projection type, and exact `{role, instance_id}` recipient
- external `ProjectionContract` id and hash
- full context hash
- field value hash
- complete recursively delivered leaf paths and hashes
- source path and source value hash
- source tokens that preserve original indices through filtered arrays
- projection operation
- source mapping mode
- included and excluded source families
- redaction and compression policy

The private report shows the exact projected context immediately before the model's raw output. Raw source snapshots remain inside the ephemeral Kernel contract and are not duplicated into the manifest, recipient prompt, private trace metadata, or public sample.
Kernel independently supplies the expected policy and recipient, validates complete field and leaf coverage, contract source hashes, source paths, stable-id-derived source tokens, mapping modes, projection operations, and delivered value hashes, then emits one sealed `ValidatedProjection` dispatch permit. Missing, duplicate, unknown, unanchored, or mismatched records quarantine projection before the provider is called.

Public export repeats the checks available from the retained trace: exact leaf coverage, delivered leaf hashes, source-token-derived paths under the contracted field anchor, contracted projection operations, and equality of the manifest's included/excluded refs, redaction rule, compression policy, and forbidden downstream uses with its contract. This is an internal-consistency and release gate, not a digital signature over an externally untrusted trace.

## Authority Evidence

Every `AuthorityReview` echoes:

- `subject_sha256`
- random run nonce
- `review_context_sha256`
- reviewed critical fields
- authority basis
- an Authority-only `forbidden_protocol_ids` list whose values cannot be reused as the current `review_id`

Mock fixture values use explicit `$RUN_NONCE` and `$REVIEW_CONTEXT_SHA256` placeholders. `MockAgentProvider` resolves only those explicit test placeholders. Real model-agents receive literal values in their projected context and must return them.

Judge-generated `review_id` remains audit-only. The forbidden-id list is sorted, Kernel-produced, and bound into the review-context hash; Character, Narrator, Plot, Router, and World contexts never receive either field. Reuse is a hard block rather than a normalization opportunity. Approved proposal and pulse wrappers carry only a Kernel-derived binding over fixed approval fields.

## Transaction Behavior

The runtime maintains working state until the entire scene succeeds.

Successful trace:

```json
{
  "transaction": {
    "status": "committed",
    "policy": "scene_atomic"
  }
}
```

Blocked trace:

- stores attempted state under `quarantined_runtime_state`
- publishes an initial/empty `runtime_state`
- seals a quarantined ScenePacket without failed scene events
- moves quarantined adjudication ids to `SealingRecord.excluded_refs` instead of source refs
- emits no memory deltas

This includes failures that occur after World consequence, such as a narration overclaim.

Authority-approved narration remains in `working_narration_segments` until final commit. Success publishes it; any late failure moves it only to `quarantined_narration_segments` and publishes no prose.

## Bounded Repair and Normalization

The executable profile supports fixture-bounded origin-only retry for:

- a narrow deterministic allowlist of World structural binding failures
- Character `EventProposal` when Judge returns code-only `repair_required`
- Narrator prose when Judge returns code-only `repair_required`
- any agent's invalid JSON through one separately sealed syntax-only retransmission

Semantic retries receive the original legal view plus only that same role's rejected subject and bounded repair codes. They receive no Judge `review_id`, findings, or global audit context. Syntax repair instead receives only the exact origin address, original stage and context hash, parser error, and the origin agent's own raw output. It has an independent projection contract and dispatch seal, consumes call and token budgets, and is limited to one attempt. A deterministic conservation validator then requires strict JSON, exact provider-parser equality, unchanged ordered key/scalar tokens, and only allowlisted comma or terminal-closure edits before the normal schema and Authority flow can resume. Plot has no content or authority repair loop. Security-critical fields, semantic repair drift, malformed enums or collections, invalid protocol ids, replay violations, unsafe repair text, and non-allowlisted World failures quarantine immediately.

The only current World-driven interface normalization is Plot intensity synonym `moderate -> medium`. It creates a warning and auditable before/after `NormalizationRecord`; the raw model output remains unchanged in the call trace. Security-critical fields are never normalized by this path.

## ScenePacket and Memory

On success, ScenePacket contains:

- resolved events
- state and visibility deltas
- pending candidates
- POV and system narration bounds
- a mechanical `SealingRecord`

The sealing record lists included/excluded refs and source hashes. Complete ScenePacket remains a system object; Narrator receives only a checkpoint projection.

Memory handoff is owner-specific. A character receives a delta only for an event that passes the same visibility and scope checks used by Character projection. Every executable delta records `source_packet_id`, `source_event_id`, and `acquisition_mode = direct_observation`.

## Artifacts

Each run writes:

```text
<out>/<trace_id>/<run_id>/trace.json
<out>/<trace_id>/<run_id>/report.md
```

`trace_id` is validated as one portable path segment before any directory is created. Kernel resolves both output root and candidate run directory and rejects any candidate outside that root; the World profile writes an invalid fixture only under a fixed `quarantined_fixture` segment, while the legacy profile raises before writing.

`trace.json` contains:

- every agent call and raw output
- exact projected contexts, manifests, and source-anchor contract metadata
- token records
- accepted protocol objects
- validation results
- transaction and quarantine state
- ScenePacket and memory handoff

`report.md` contains the same major evidence in a human-readable sequence, including every model-agent output.

## Token Telemetry

Each usage record includes:

- role, instance, and stage
- backend and model
- input, output, and total tokens
- provider-reported or local-estimated source
- configured output limit and remaining budget
- output budget enforcement mode

The aggregate report includes the configured trace output budget. This budget limits returned output only; input and aggregate provider-billed tokens are recorded but are not hard-capped in v0.2. Provider usage is exact only when supplied counts are non-negative and a supplied total equals input plus output; inconsistent records fall back to local estimates. Do not hard-code mock totals in documentation because context schemas change the serialized prompt size.

Default output budgets are 12,000 for Plot and Router, 16,000 for Character, Narrator, and Canon Steward, and 24,000 for World, Authority, and Judge. The trace-wide default is 300,000. Provider-reported output can include reasoning tokens beyond visible JSON text.

Enforcement summary:

| Backend | Output limit behavior |
| --- | --- |
| OpenAI-compatible | provider request cap plus precommit validation |
| Codex CLI | prompt guidance plus post-response precommit validation |
| mock | deterministic estimate plus post-response precommit validation |

## Verified Real Codex Run

The sanitized public artifact at [world-driven-real-sample-v0.2](world-driven-real-sample-v0.2.md) records one successful isolated `gpt-5.5` execution:

| Metric | Result |
| --- | ---: |
| model-agent calls | 19 |
| validated projection manifests | 19 |
| bounded repair attempts | 0 |
| audited normalizations | 1 |
| input tokens | 247,016 |
| output tokens | 21,511 |
| total tokens | 268,527 |
| estimated usage records | 0 |
| final decision | `allowed` |
| scene transaction | `committed` |

The artifact includes every parsed model-agent output and per-call usage. It excludes prompts, projected contexts, raw provider JSONL, local paths, private run identifiers, and authentication state. `scripts/export_public_trace.py` accepts only `codex-cli + allowed + finished + committed` traces with exact provider usage, one uniquely bound manifest and contract per call, matching recipient/context/contract seals, complete anchored field evidence, no blocking validation, and valid private packet collection hashes. It then attaches a separately verifiable `sanitized_public_export` seal after redaction.

## Tests

The World-driven tests cover:

- happy-path 19-call base trace and bounded repair insertion
- scheduled autonomous World event
- Router and Character ownership
- empty or incomplete Authority approval
- review hash, context, and nonce binding
- successful origin-bound malformed-JSON syntax repair plus second-failure quarantine without runtime exceptions
- deterministic syntax-repair semantic-drift rejection before Authority or state transition
- pre-write trace path containment and World quarantine versus legacy rejection
- external projection-contract, exact-recipient, and sealed dispatch binding
- duplicate source identities and self-consistent manifest forgery rejection
- simultaneous approved proposal and PlotPulse consumption
- run-local protocol id syntax, length, and replay
- World causal, state, visibility, and interiority binding
- Character source-actor and exactly-one speech-record binding
- cross-scene request and PlotPulse rejection
- private-self ownership and scene-pair membership
- Plot executable enums, cumulative pressure, option topology, and rejected-pulse no-adjudication
- candidate lifecycle and read isolation
- direct observation, public membership, encounter, and private-memory separation
- Narrator overclaim and invisible-event skip
- atomic rollback after late failure
- World-driven-only private-to-public seal verification and re-sealing
- missing, forged, reused, or blocking projection-evidence export rejection
- provider token consistency plus per-call and total transition blocks

The current full suite passes 100 tests and 16 subtests.

Run only this module:

```powershell
python -m pytest -q tests/test_world_runtime.py
```

## Current Limits

- no persistent campaign database
- no automatic cross-scene deferred pressure handoff
- no Plot content or authority repair loop; semantic World, Character, and Narrator repairs remain narrow and bounded, while every role shares one syntax-only JSON retransmission
- no in-loop publication or Canon Steward promotion
- candidate expiry is validated but not aged across persistent scene time
- one active Character decision at a time
- semantic causal and prose judgments still depend on Authority Judge quality
- Codex CLI incurs one process startup per model-agent call

## Related Documents

- `../protocol/world-driven-runtime-v0.1.md`
- `../protocol/agent-context-packet-and-field-visibility-v0.1.md`
- `../protocol/resolution-state-delta-commit-pipeline-v0.1.md`
- `../protocol/scene-pressure-packet-and-plot-budget-v0.1.md`
- `mvp-runner-v0.1.md` for the legacy compatibility path
