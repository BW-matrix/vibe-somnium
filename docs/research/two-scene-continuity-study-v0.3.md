# Two-Scene Continuity and Runtime Cost Study v0.3

Date: 2026-07-30

## Executive Result

This study tested whether the World-driven runtime could execute two consecutive literary scenes while carrying only committed, authority-bounded state across the scene boundary.

The final hardening rerun passed all 13 current continuity and isolation checks:

- both scenes finished with committed scene transactions
- Scene 1's exact fixture and `ScenePacket` hashes were bound into Scene 2
- two committed events and two state deltas crossed into the World-only handoff view with exact content hashes
- each Character received exactly its own two derived `MemoryDelta` records and no unauthorized record
- the deferred pressure ledger crossed unchanged
- all 33 model/runtime and Kernel-generated Scene 1 identities were reserved, and no id was replayed
- both scenes stayed below independent 100-World-tick and 100-model-call caps

The accepted final pair used 38 model calls and 8 World ticks. Exact provider telemetry reported 522,424 input tokens, 53,351 output tokens, and 575,775 total tokens. Internal runtime elapsed time was 1,624.597 seconds, or 27.08 minutes.

The discovery campaign that preceded the final rerun included two fail-closed Scene 2 attempts and one historical accepted pair. Including the final hardening rerun, the whole research exercise consumed 96 model calls, 20 World ticks, 1,326,443 input tokens, 121,296 output tokens, and 1,447,739 total tokens. Recorded trace/orchestration time was approximately 4,784.20 seconds, or 79.74 minutes, excluding code edits and tests.

The final protocol trace is authority-safe under the implemented checks. It is not evidence of long-run narrative quality: Scene 2 contains a visible Lin pronoun inconsistency that the current protocol did not prevent.

## Research Question

The experiment asked four concrete questions:

1. Can committed scene reality become legal World input for a later scene without forwarding a complete private trace?
2. Can Character memory continue across scenes without copying one owner's private records into another owner's prompt?
3. Can unresolved Plot pressure continue without becoming an objective world fact?
4. What token and latency cost does the current strict, serial Authority-reviewed flow impose?

## Runtime Configuration

| Field | Value |
| --- | --- |
| Runtime | World-driven v0.2 |
| Provider harness | isolated Codex CLI |
| Model | `gpt-5.5` |
| Project reasoning setting | `max` |
| CLI reasoning value | `xhigh` |
| Scene transaction | atomic commit or rollback |
| World tick cap per scene | 100 |
| LLM call cap per scene | 100 |
| Output-token budget per scene | 1,000,000 |
| Per-call timeout | 360 seconds |
| Token records | exact provider usage for every call |
| Regression result after hardening | 107 tests and 16 subtests passed |

The two caps intentionally interpret "round" in both plausible runtime senses. A scene is blocked if either World simulation ticks or total model calls exceed 100.

## Cross-Scene Handoff

`campaign_study.py` materializes Scene 2 only after Scene 1 is `allowed`, `finished`, transaction-committed, and sealed as a committed `ScenePacket`.

The handoff now requires the exact `fixture_sha256` of the executed Scene 1 input and copies:

- a World-only event history stripped of `authorized_interiority`, candidate material, prose, and raw prompts
- committed `StateDelta` records
- owner-specific `MemoryDelta` records into only the matching Character's `private_memory`
- the exact prior `pressure_ledger`
- prior event and delta ids into the legal World condition registry
- every model/runtime identity plus Kernel-generated `ScenePacket` and `MemoryDelta` identities into `reserved_protocol_ids`

It does not copy raw projected contexts, foreign-owner memory, quarantined state, narration drafts as facts, unapproved candidates, credentials, or local Codex state.

In the final rerun, Scene 1 produced 33 reserved identities. Scene 2 received exactly those 33 and generated a disjoint set.

## Execution Record

The discovery executions use the originally recorded outer orchestration measurements. The final rerun uses the consistent internal runtime timer now stored in each trace.

| Phase | Execution | Result | Calls | World ticks | Input | Output | Total | Seconds | Terminal reason |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Discovery | Scene 1 | committed | 19 | 4 | 239,398 | 21,416 | 260,814 | 1,623.812 | `finished` |
| Discovery | Scene 2 attempt 0 | rolled back | 6 | 1 | 79,663 | 6,345 | 86,008 | 232.527 | `quarantined_world_tick` |
| Discovery | Scene 2 attempt 1 | rolled back | 14 | 3 | 203,079 | 19,189 | 222,268 | 599.982 | `quarantined_checkpoint` |
| Discovery | Scene 2 historical final | committed | 19 | 4 | 281,879 | 20,995 | 302,874 | 703.283 | `finished` |
| Final hardening | Scene 1 | committed | 19 | 4 | 243,205 | 23,028 | 266,233 | 739.151 | `finished` |
| Final hardening | Scene 2 | committed | 19 | 4 | 279,219 | 30,323 | 309,542 | 885.447 | `finished` |

Every token count is provider-reported rather than locally estimated.

## Negative Findings

### Mixed Character Action

Discovery Scene 2 attempt 0 used `action_type = physical`, but Lin's `public_surface` bundled both writing and speaking. Authority Judge incorrectly allowed it, and World emitted a spoken-line record for a non-speech proposal.

Deterministic validation blocked `invalid_spoken_line_status`, `undeclared_field`, and `speech_not_proposed`. The transaction rolled back; no event, state delta, narration, or memory was published.

The final policy is deliberately strict:

- Character instructions require one externally observable action type
- Authority instructions require repair for mixed action surfaces
- narrow spoken-line schema drift can use one World-origin repair
- `speech_not_proposed` itself remains a hard failure, because World must not launder an invalid Character action by rewriting it

### Plot Stacking Metadata

Discovery Scene 2 attempt 1 reached the Plot checkpoint, where Plot emitted `stacking_count = 2` for an `institutional_constraint` even though the inherited pressure was a different `deadline` kind. The ledger required `1`, so the scene rolled back.

The remediation moved this mechanically derivable integer to audited Kernel normalization. The raw Plot output remains in the private trace; `NormalizationRecord` preserves before, after, field path, and policy. Identity, visibility, authority, source, target, and canon fields remain ineligible.

The final hardening Scene 2 again emitted `2`; the Kernel normalized it to `1`, ordinary validation and Authority review then passed, and no repair call was added.

### Independent Review Gaps

Independent review found three additional weaknesses in the first study harness:

1. A retained Scene 1 trace was matched to a supplied fixture only by `trace_id` and `scene_id`.
2. The memory evaluator checked expected handoff ids but could miss an additional unauthorized private-memory record.
3. Historical `reserved_protocol_ids` covered 27 model/runtime ids but omitted one Kernel packet id and four Kernel memory ids.

The release fixes bind complete fixture content, enforce an exact owner-memory allowlist, reject conflicting memory ids, and require the complete reservation set. The historical pair scores 12/13 under the stricter evaluator solely because its retained Scene 2 fixture cannot retroactively contain the five omitted ids. No actual replay or foreign-memory delivery occurred in that trace.

The final hardening rerun closes this evidence gap: `fixture_sha256` is present, expected and observed reservations both contain 33 ids, and all 13 current checks pass.

## Accepted Pair Metrics

| Agent | Calls | Input | Output | Total | Token share | Seconds | Time share |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Authority | 18 | 289,353 | 31,361 | 320,714 | 55.7% | 866.002 | 53.3% |
| World | 8 | 115,212 | 12,340 | 127,552 | 22.2% | 364.778 | 22.5% |
| Character | 4 | 41,118 | 3,703 | 44,821 | 7.8% | 144.636 | 8.9% |
| Router | 4 | 37,582 | 2,303 | 39,885 | 6.9% | 112.235 | 6.9% |
| Plot | 2 | 19,993 | 2,460 | 22,453 | 3.9% | 82.715 | 5.1% |
| Narrator | 2 | 19,166 | 1,184 | 20,350 | 3.5% | 53.758 | 3.3% |
| **Total** | **38** | **522,424** | **53,351** | **575,775** | **100%** | **1,624.597** | **100%** |

Authority remains the largest cost center: 47.4% of calls, 55.7% of tokens, and 53.3% of runtime. Narrator accounts for only 3.5% of tokens, so prose generation is not the dominant cost.

## Total Research Spend

The cumulative spend includes the discovery campaign and the final hardening rerun:

| Agent | Calls | Input | Output | Total | Seconds |
| --- | ---: | ---: | ---: | ---: | ---: |
| Authority | 44 | 719,741 | 61,499 | 781,240 | 2,312.180 |
| World | 21 | 301,526 | 35,209 | 336,735 | 1,153.461 |
| Character | 11 | 113,815 | 10,393 | 124,208 | 503.069 |
| Router | 11 | 103,249 | 5,920 | 109,169 | 402.845 |
| Plot | 5 | 49,759 | 5,800 | 55,559 | 283.548 |
| Narrator | 4 | 38,353 | 2,475 | 40,828 | 127.610 |
| **Total** | **96** | **1,326,443** | **121,296** | **1,447,739** | **approximately 4,784.20** |

Late fail-closed detection is safe but expensive. Discovery attempt 1 consumed 222,268 tokens before one derivable Plot metadata error ended the scene. The final clean rerun was both stronger and faster, but one sample cannot establish a latency trend.

## Continuity Evidence

All 13 current checks passed in the final hardening pair:

| Check | Evidence |
| --- | --- |
| Scene commits | both `allowed`, `finished`, transaction `committed`, packet `committed` |
| Tick caps | 4 of 100 in each scene |
| Call caps | 19 of 100 in each scene |
| Fixture binding | Scene 1 `360e2d151d7a57783817b7dfd1cac24813adf109aff0184fce38863e66ad80d7`; Scene 2 `3ed1cad2769868d2e23c65cd5a0f02c101e1228fadbdfb420461e4d66b57066d` |
| Packet binding | expected and both observed copies equal `88f9cf570ee3f18762320e9c466e53815f11267d87205d8df231e905ca8cdc98` |
| Protocol replay | expected reservations = observed reservations = 33; generated-id intersection empty |
| World handoff | all 4 Scene 2 World contexts carried the bound source packet hash |
| Lin memory | 2 expected exact-content owner records; 0 foreign or unauthorized records |
| Wei memory | 2 expected exact-content owner records; 0 foreign or unauthorized records |
| Pressure handoff | 1 record; source and follow-up hash `c0e5f06b3da486b2cab1b05f3455ccc0de2f48920b554c370a0ddf4ef7645ef0` |
| World-history handoff | committed event history hash `e78b493b6724232db035311d5ac846e12baffe1f9a21b18a96a8d0370bb8f152` |
| State-delta handoff | committed state history hash `d0688e7449ea154fb2376e5f393eab03ca288a801390317611889bf40bb406c4` |

State-chain hashes:

| Object | SHA-256 |
| --- | --- |
| Scene 1 packet | `88f9cf570ee3f18762320e9c466e53815f11267d87205d8df231e905ca8cdc98` |
| Materialized Scene 2 fixture | `3ed1cad2769868d2e23c65cd5a0f02c101e1228fadbdfb420461e4d66b57066d` |
| Scene 2 packet | `a5c6081619d708cf8299144023a15f5ac1734ffd341a1fe0837806a4c05767db` |
| Campaign chain | `8d9afc9ce7ed551a02bf580cfda654147509b90fb854b3f261e24dab0a05593c` |

## Story Output

### Scene 1

> Wei lowered his voice and observed that Lin had stayed with the page for some time. Before dawn made a formal report of it, he asked which irregularity she thought mattered most. Lin answered with a focused inference: the timing mattered most. If the ledgers were sealed after dusk, then any access mark pointing past dusk was the irregularity they could not explain away before inspection. She kept her suspicion of him private.

### Scene 2

> Lin entered the irregularity in the morning register: an access mark indicating use after dusk. He marked it as direct observation and added no accusation or speculation. Wei responded by telling him to write only what the page proved and, if asked about the volume itself, to answer from the register: observed absence was one matter, suspicion another.

The event-level content is continuous: Lin preserves observation versus suspicion, Wei avoids confession, and the ledger location remains unresolved. However, Scene 1 uses `she/her` for Lin while Scene 2 uses `he/him`. The protocol correctly does not promote prior narration into world truth, but it also lacks a stable, public Character presentation profile containing names, pronouns, and other reader-facing identity invariants. This is a literary continuity failure that authority checks did not catch.

## Complete Public Agent Outputs

The sanitized exports preserve every parsed output and exact token record from all 38 final accepted calls:

- [Scene 1 public trace](two-scene-continuity-scene-1-public-trace-v0.3.md)
- [Scene 2 public trace](two-scene-continuity-scene-2-public-trace-v0.3.md)

They exclude prompts, projected private contexts, raw provider JSONL, local paths, private run identifiers, and authentication state. Blocked discovery attempts remain local-only because the public exporter accepts only committed traces.

`Canon Steward` was not invoked: neither scene produced an executable canon-promotion step. The runtime does not fabricate placeholder agent output.

## Conclusions

1. The final runtime executed a two-scene committed chain under the complete current fixture, memory, pressure, and identity-continuity checks.
2. Projection-based owner isolation worked in the final pair: neither Character received an unauthorized memory record.
3. Deterministic validation caught a semantic Authority miss before state publication.
4. Derived audit metadata is better computed and audited by the Kernel than repeatedly generated and judged by models.
5. Authority and World dominate operational cost; Narrator is comparatively small.
6. Scene-atomic persistence protects correctness but makes late rejection expensive.
7. Protocol continuity is not literary continuity: stable Character presentation data needs its own authority-bounded cross-scene layer.

## Limits and Next Discussion

- This is two sampled two-scene campaigns, not a statistical evaluation.
- The handoff is a materialized fixture boundary, not a persistent campaign database.
- There is no direct-API latency comparison.
- Codex CLI launches one isolated process per model call and includes harness instruction overhead.
- No publication, canon promotion, long-term memory decay, contradiction engine, or multi-scene public-scope propagation was exercised.
- The study does not evaluate player-perceived latency or interaction design.
- The pronoun inconsistency shows that reader-facing Character presentation continuity is not yet protocolized.
- Call slimming, Judge consolidation, parallel review, early validation, and checkpoint persistence were intentionally deferred until after this baseline.

The next design discussion should use the final trace as the authority baseline, add a bounded Character presentation profile, and optimize cost without weakening projection or transaction guarantees.
