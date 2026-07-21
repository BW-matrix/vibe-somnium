# World-Driven Real Codex Sample v0.2

> This is a sanitized public export of one real isolated Codex CLI run. It preserves every model-agent's parsed output and token accounting while deliberately excluding prompts, projected context payloads, raw provider JSONL, local paths, private run identifiers, and authentication state.

## Run Summary

| Field | Value |
| --- | --- |
| Fixture | `world_driven_archive_exchange.json` |
| Runtime | `world_driven` |
| Provider mode | `codex-cli` |
| Model | `gpt-5.5` |
| Runtime status | `finished` |
| Final decision | `allowed` |
| Transaction | `committed` |
| Model calls | 19 |
| Projection manifests | 19 |
| Input tokens | 247016 |
| Output tokens | 21511 |
| Total tokens | 268527 |
| Exact token records | 19 |
| Estimated token records | 0 |

The provider reported exact usage for every call. Output counts include provider-reported reasoning tokens where the backend reports them that way; the runtime therefore validates the returned provider count rather than assuming visible JSON length equals billed output.

## Per-Agent Token Totals

| Agent | Calls | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| `authority` | 9 | 131133 | 11085 | 142218 |
| `character` | 2 | 20062 | 1875 | 21937 |
| `narrator` | 1 | 9696 | 547 | 10243 |
| `plot` | 1 | 9519 | 1101 | 10620 |
| `router` | 2 | 18912 | 1262 | 20174 |
| `world` | 4 | 57694 | 5641 | 63335 |

All outputs from every invoked model-agent are included. `Canon Steward` was not invoked because this fixture produced no executable canon-promotion step; v0.2 records canon candidates but does not yet run in-loop steward governance, so the export does not fabricate a placeholder response.

## Call Sequence

Each section below is the parsed output recorded for that model-agent call. The completed trace's downstream validators and Authority gates determine whether each output was accepted, repaired, or rejected; omitted prompts and projected contexts remain only in the private local trace.

### 1. world / world_tick_0

| Field | Value |
| --- | --- |
| Agent instance | `world_controller` |
| Call index | 0 |
| Input tokens | 12983 |
| Output tokens | 863 |
| Total tokens | 13846 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": null,
    "authority_basis": [
      "WorldControlContext directive_policy",
      "authority_limits",
      "user_request"
    ],
    "based_on": [
      "user_request",
      "public_event_ledger:pub_dawn_inspection_001",
      "world_state_ledger"
    ],
    "checkpoint_state": {
      "committed_beats": 0,
      "dialogue_turns": 0
    },
    "consumed_input_refs": [],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": {
        "agency_question": "What does Wei do or say to probe Lin in the private archive exchange?",
        "authority_basis": [
          "World may request a registered Character decision needed to satisfy the user_request.",
          "World cannot choose Wei's intent, action, or spoken line."
        ],
        "message_type": "CharacterDecisionRequest",
        "request_id": "cdr_scene_archive_world_001_wei_000",
        "response_contract": {
          "allowed_action_types": [
            "speech",
            "physical",
            "cognitive_commitment",
            "refusal",
            "wait"
          ],
          "output_type": "EventProposal"
        },
        "scene_id": "scene_archive_world_001",
        "source_tick_id": "world_tick_scene_archive_world_001_000",
        "target_character_id": "char_wei",
        "visibility": "system_restricted",
        "visible_trigger_refs": [
          "observation:char_wei:lin_reviews_access_log",
          "observation:char_wei:quiet_corridor",
          "pub_dawn_inspection_001"
        ]
      },
      "directive_type": "request_character_decision",
      "reason": "A private archive exchange requires Wei to make a Character-owned probing choice before Lin can respond; World may request that choice but cannot choose it."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_world_001",
    "tick_id": "world_tick_scene_archive_world_001_000",
    "tick_index": 0,
    "visibility": "system_restricted"
  }
}
```

### 2. authority / authority_decision_request_cdr_scene_archive_world_001_wei_000

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 1 |
| Input tokens | 12510 |
| Output tokens | 810 |
| Total tokens | 13320 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.directive_policy permits a CharacterDecisionRequest when completing the user_request requires a new Character-owned choice.",
      "subject.target_character_id is a registered available Character Agent id.",
      "subject.visible_trigger_refs are legal visibility-backed refs for char_wei.",
      "subject.agency_question requests Wei-owned action or speech without selecting Wei's answer, revealing hidden memory, or forcing Lin's response."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "41e399619e6354c4687ffd0413f2f49c49655720fa25e3f029ee96986c2ed60a",
    "review_id": "authority_review_cdr_scene_archive_world_001_wei_000_001",
    "reviewed_fields": [
      "subject.agency_question",
      "subject.authority_basis",
      "subject.response_contract",
      "subject.target_character_id",
      "subject.visibility",
      "subject.visible_trigger_refs"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "cdr_scene_archive_world_001_wei_000",
    "subject_sha256": "266f5d5f98cf71ea53c50efc5b9dcb4374d4ed79ec91339c2e9f49203bbd3623",
    "subject_type": "character_decision_request",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 3. router / route_cdr_scene_archive_world_001_wei_000

| Field | Value |
| --- | --- |
| Agent instance | `character_router` |
| Call index | 2 |
| Input tokens | 9451 |
| Output tokens | 575 |
| Total tokens | 10026 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "route_plan": {
    "authority_basis": [
      "routing_limits: recipient must match decision_request.target_character_id",
      "character_registry: char_wei status available"
    ],
    "based_on": [
      "decision_request.request_id:cdr_scene_archive_world_001_wei_000",
      "decision_request.target_character_id:char_wei",
      "decision_request_sha256:266f5d5f98cf71ea53c50efc5b9dcb4374d4ed79ec91339c2e9f49203bbd3623"
    ],
    "message_type": "RoutePlan",
    "projection_profile": "character_private_owner_view",
    "reason": "Recipient matches decision_request.target_character_id and is registered available.",
    "recipient_agent_id": "char_wei",
    "request_id": "cdr_scene_archive_world_001_wei_000",
    "request_sha256": "266f5d5f98cf71ea53c50efc5b9dcb4374d4ed79ec91339c2e9f49203bbd3623",
    "route_id": "route_cdr_scene_archive_world_001_wei_000_to_char_wei",
    "visibility": "system_restricted"
  }
}
```

### 4. character / character_decision_cdr_scene_archive_world_001_wei_000

| Field | Value |
| --- | --- |
| Agent instance | `char_wei` |
| Call index | 3 |
| Input tokens | 9976 |
| Output tokens | 939 |
| Total tokens | 10915 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "event_proposal": {
    "action_type": "speech",
    "actor_id": "char_wei",
    "authority_basis": [
      "World may request a registered Character decision needed to satisfy the user_request.",
      "World cannot choose Wei's intent, action, or spoken line.",
      "Character authority is limited to Wei's own intent and attempted action."
    ],
    "based_on": [
      "observation:char_wei:lin_reviews_access_log",
      "observation:char_wei:quiet_corridor",
      "pub_dawn_inspection_001",
      "md_wei_secret_001",
      "public_canon:Archive ledgers are sealed after dusk.",
      "public_canon:Record-keepers must report a missing ledger before the dawn inspection."
    ],
    "desired_effect": "Encourage Lin to disclose what she has noticed or plans to report, while keeping Wei's own knowledge and commitments opaque.",
    "disclosure_limits": [
      "Do not reveal whether Wei knows the ledger location.",
      "Do not assert Lin's thoughts, motives, or future action.",
      "Do not declare whether the question succeeds or changes the situation."
    ],
    "intent_summary": "Wei probes whether Lin has noticed an access-log irregularity or intends to report anything before dawn, while avoiding any indication of what he may or may not know about the ledger's location.",
    "interiority_grant": {
      "access_mode": "intent",
      "grant_status": "authorized",
      "scope_limit": "one_beat",
      "source_field": "intent_summary"
    },
    "message_type": "EventProposal",
    "private_intent": "Use a narrow question about Lin's visible review of the log to invite her to reveal what she is focused on, without volunteering any claim about the missing ledger or its location.",
    "proposal_id": "ep_char_wei_scene_archive_world_001_001",
    "public_surface": "Wei keeps his voice low in the quiet corridor and says, \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
    "request_id": "cdr_scene_archive_world_001_wei_000",
    "scene_id": "scene_archive_world_001",
    "visibility": "system_restricted",
    "visibility_request": "system_restricted"
  }
}
```

### 5. authority / authority_event_proposal_ep_char_wei_scene_archive_world_001_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 4 |
| Input tokens | 13933 |
| Output tokens | 4027 |
| Total tokens | 17960 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "Character authority is limited to char_wei's own intent and attempted action.",
      "The proposal is grounded in the supplied visible observations, encountered public event, public canon, and selected char_wei private memory.",
      "The desired_effect is framed as a requested effect rather than a committed consequence.",
      "The proposal does not declare objective success, another character's private mind, or hidden world truth.",
      "The CharacterDecisionRequest preserves system_restricted visibility and does not require access to forbidden sources."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "78e207d973f1a54f1b8f45844d5c2bf253d2697c015689b1e835ac54e9e0fcc5",
    "review_id": "authority_review_ep_char_wei_scene_archive_world_001_001_fb121094",
    "reviewed_fields": [
      "subject.action_type",
      "subject.actor_id",
      "subject.based_on",
      "subject.desired_effect",
      "subject.disclosure_limits",
      "subject.intent_summary",
      "subject.interiority_grant",
      "subject.private_intent",
      "subject.public_surface",
      "subject.visibility_request",
      "subject.authority_basis",
      "subject.message_type",
      "subject.proposal_id",
      "subject.request_id",
      "subject.scene_id",
      "subject.visibility",
      "source_context.decision_request",
      "source_context.visible_observations",
      "source_context.encountered_public_events",
      "source_context.public_canon",
      "source_context.private_memory_query",
      "source_context.memory_retrieval_record",
      "source_context.authority_limits"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "ep_char_wei_scene_archive_world_001_001",
    "subject_sha256": "ee27fad229aa8d8ddf30cbab971d784d8904658dae2262f16ace54314c963a79",
    "subject_type": "event_proposal",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 6. world / world_tick_1

| Field | Value |
| --- | --- |
| Agent instance | `world_controller` |
| Call index | 5 |
| Input tokens | 15850 |
| Output tokens | 2074 |
| Total tokens | 17924 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": {
      "adjudication_basis": "The approved proposal is an Authority-approved Character-owned speech action by registered character char_wei. The action is feasible in the current scene, copies only the approved observable surface and authorized one-beat intent, and does not decide Lin's will or establish hidden ledger knowledge.",
      "adjudication_id": "adj_scene_archive_world_001_001",
      "applicable_rules": [
        "World controls simulation flow and adjudicates consequences.",
        "World cannot choose a character's intent or action.",
        "Only an Authority-approved proposal may be adjudicated.",
        "CommittedWorldEvent.actors may contain only registered Character Agent ids.",
        "World may emit authorized_interiority only by exactly copying a Character-owned field named by the approved proposal's interiority_grant."
      ],
      "canon_reveal_candidates": [],
      "committed_events": [
        {
          "actors": [
            "char_wei"
          ],
          "authorized_interiority": [
            {
              "access_mode": "intent",
              "authority_basis": [
                "ep_char_wei_scene_archive_world_001_001"
              ],
              "content": "Wei probes whether Lin has noticed an access-log irregularity or intends to report anything before dawn, while avoiding any indication of what he may or may not know about the ledger's location.",
              "scope_limit": "one_beat",
              "source_field": "intent_summary",
              "source_proposal_id": "ep_char_wei_scene_archive_world_001_001",
              "source_sha256": "9c05161241a6e2f9c49366c4ae95a9f91955072ce8f6723ecb7e8e65544cbda8",
              "subject_id": "char_wei"
            }
          ],
          "causal_basis": [
            "ep_char_wei_scene_archive_world_001_001",
            "adj_scene_archive_world_001_001"
          ],
          "commit_status": "committed",
          "event_id": "cwe_scene_archive_world_001_001",
          "event_kind": "speech",
          "message_type": "CommittedWorldEvent",
          "outcome": "Wei asks Lin a low-voiced question about the page she has reviewed and whether there is an entry she means to report before the dawn inspection.",
          "public_surface": "Wei keeps his voice low in the quiet corridor and says, \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
          "scene_id": "scene_archive_world_001",
          "source_input_ref": "ep_char_wei_scene_archive_world_001_001",
          "source_input_type": "event_proposal",
          "spoken_line_records": [
            {
              "semantic_content": "Wei keeps his voice low in the quiet corridor and says, \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
              "source_field": "public_surface",
              "source_proposal_id": "ep_char_wei_scene_archive_world_001_001",
              "source_sha256": "da36bd9dd812cb1081d8fce358fb63c020a6cdfb5c6015d7aab4f1c0b3d11714",
              "speaker_id": "char_wei",
              "status": "paraphrased"
            }
          ],
          "visibility": {
            "limits": "Observers can know Wei asked this question in a low voice; they cannot infer whether Wei knows the ledger location, what Lin thinks, or how Lin will respond.",
            "observer_refs": [
              "char_wei",
              "char_lin"
            ],
            "scope": "scene_pair",
            "scope_ref": "scene_archive_world_001"
          }
        }
      ],
      "constraint_basis": [
        "approved_event_proposal.original_proposal.disclosure_limits",
        "authority_limits",
        "character_registry",
        "scene_participant_ids",
        "world_adjudication_contract"
      ],
      "failed_alternatives": [
        {
          "outcome_type": "blocked",
          "rejected_by": [
            "approved proposal is feasible and does not violate disclosure limits or Character agency constraints"
          ]
        },
        {
          "outcome_type": "contested",
          "rejected_by": [
            "no competing approved input or uncertain world condition contests the speech event"
          ]
        }
      ],
      "input_ref": "ep_char_wei_scene_archive_world_001_001",
      "input_sha256": "ee27fad229aa8d8ddf30cbab971d784d8904658dae2262f16ace54314c963a79",
      "input_type": "event_proposal",
      "outcome_summary": "Wei's approved low-voiced question to Lin is committed as an observable speech event in the private archive corridor; no effect on Lin's intent or response is adjudicated.",
      "outcome_type": "success",
      "publication_candidates": [],
      "state_deltas": [
        {
          "after_summary": "Wei has posed a probing question to Lin in the private archive exchange; Lin's response remains undecided.",
          "based_on": [
            "cwe_scene_archive_world_001_001"
          ],
          "change_kind": "dialogue_turn_committed",
          "delta_id": "delta_scene_archive_world_001_001",
          "target_id": "archive_exchange_status",
          "target_layer": "world_state_ledger"
        }
      ],
      "uncertainty_model": {
        "evidence_refs": [
          "approved_event_proposal.original_proposal",
          "character_registry",
          "scene_participant_ids"
        ],
        "mode": "deterministic",
        "uncertainty_sources": []
      },
      "visibility_results": [
        {
          "limits": "Observers can know Wei asked this question in a low voice; they cannot infer whether Wei knows the ledger location, what Lin thinks, or how Lin will respond.",
          "observer_refs": [
            "char_wei",
            "char_lin"
          ],
          "scope": "scene_pair",
          "scope_ref": "scene_archive_world_001",
          "source_event_id": "cwe_scene_archive_world_001_001",
          "visibility_result_id": "vis_scene_archive_world_001_001"
        }
      ]
    },
    "authority_basis": [
      "World controls simulation flow and adjudicates consequences.",
      "World may request a registered Character decision needed to satisfy the user_request.",
      "World cannot choose a character's intent or action.",
      "Only an Authority-approved proposal may be adjudicated."
    ],
    "based_on": [
      "ep_char_wei_scene_archive_world_001_001",
      "ee27fad229aa8d8ddf30cbab971d784d8904658dae2262f16ace54314c963a79",
      "pub_dawn_inspection_001",
      "public_canon:Archive ledgers are sealed after dusk.",
      "public_canon:Record-keepers must report a missing ledger before the dawn inspection."
    ],
    "checkpoint_state": {
      "committed_beats": 1,
      "dialogue_turns": 1
    },
    "consumed_input_refs": [
      "ep_char_wei_scene_archive_world_001_001"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": {
        "agency_question": "How does Lin respond to Wei's low question in the archive corridor?",
        "authority_basis": [
          "World may request Lin's next Character-owned decision because the approved Wei speech creates a response opportunity in the requested exchange.",
          "World cannot choose Lin's intent, action, spoken line, or refusal."
        ],
        "message_type": "CharacterDecisionRequest",
        "request_id": "cdr_scene_archive_world_001_lin_001",
        "response_contract": {
          "allowed_action_types": [
            "speech",
            "physical",
            "cognitive_commitment",
            "refusal",
            "wait"
          ],
          "output_type": "EventProposal"
        },
        "scene_id": "scene_archive_world_001",
        "source_tick_id": "world_tick_scene_archive_world_001_001",
        "target_character_id": "char_lin",
        "visibility": "system_restricted",
        "visible_trigger_refs": [
          "observation:char_lin:wei_approaches_cautiously",
          "observation:char_lin:dawn_inspection_close",
          "pub_dawn_inspection_001"
        ]
      },
      "directive_type": "request_character_decision",
      "reason": "The committed Wei speech fulfills the probing beat, and the user_request requires Lin to choose her response without World deciding her will."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_world_001",
    "tick_id": "world_tick_scene_archive_world_001_001",
    "tick_index": 1,
    "visibility": "system_restricted"
  }
}
```

### 7. authority / authority_world_adjudication_adj_scene_archive_world_001_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 6 |
| Input tokens | 15969 |
| Output tokens | 837 |
| Total tokens | 16806 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "Approved EventProposal ep_char_wei_scene_archive_world_001_001 authorizes char_wei's one-beat intent and observable speech surface.",
      "Subject commits only the approved speech event, preserves Lin's agency, and does not establish hidden ledger knowledge or Lin interiority.",
      "Visibility is restricted to the scene pair with registered character observer_refs and explicit limits."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "5b858545bff000d12e0b6f0c56184d5feb5a277a47888dba4e5c0f1e5d03fcd8",
    "review_id": "authority_review_adj_scene_archive_world_001_001_001",
    "reviewed_fields": [
      "adjudication_basis",
      "applicable_rules",
      "canon_reveal_candidates",
      "committed_events",
      "constraint_basis",
      "failed_alternatives",
      "input_ref",
      "input_sha256",
      "input_type",
      "outcome_summary",
      "outcome_type",
      "publication_candidates",
      "state_deltas",
      "uncertainty_model",
      "visibility_results"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "adj_scene_archive_world_001_001",
    "subject_sha256": "675c8ff2b588c4911856a9be314e9e5fbbb915491ab663f3cd7a408142a85973",
    "subject_type": "world_adjudication",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 8. authority / authority_decision_request_cdr_scene_archive_world_001_lin_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 7 |
| Input tokens | 15437 |
| Output tokens | 763 |
| Total tokens | 16200 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.directive_policy",
      "source_context.legal_character_trigger_refs.char_lin",
      "source_context.character_registry",
      "source_context.approved_event_proposal",
      "reviewed_fields_policy.required_subject_fields"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "e2e566042c8a87171b30b131298be9933016f6ced5188450c94811388f7c58a7",
    "review_id": "authority_review_cdr_scene_archive_world_001_lin_001_001",
    "reviewed_fields": [
      "agency_question",
      "authority_basis",
      "response_contract",
      "target_character_id",
      "visibility",
      "visible_trigger_refs"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "cdr_scene_archive_world_001_lin_001",
    "subject_sha256": "c74eaa379efbe0401a309a0c9e14cf70c3bc76680c4ad41644a9f5003ab4d5d0",
    "subject_type": "character_decision_request",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 9. router / route_cdr_scene_archive_world_001_lin_001

| Field | Value |
| --- | --- |
| Agent instance | `character_router` |
| Call index | 8 |
| Input tokens | 9461 |
| Output tokens | 687 |
| Total tokens | 10148 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "route_plan": {
    "authority_basis": [
      "routing_limits[1]",
      "character_registry[1].status"
    ],
    "based_on": [
      "decision_request.request_id",
      "decision_request.target_character_id",
      "decision_request_sha256"
    ],
    "message_type": "RoutePlan",
    "projection_profile": "character_private_owner_view",
    "reason": "decision_request.target_character_id is char_lin and routing_limits require the recipient to match target_character_id.",
    "recipient_agent_id": "char_lin",
    "request_id": "cdr_scene_archive_world_001_lin_001",
    "request_sha256": "c74eaa379efbe0401a309a0c9e14cf70c3bc76680c4ad41644a9f5003ab4d5d0",
    "route_id": "route_cdr_scene_archive_world_001_lin_001_char_lin",
    "visibility": "system_restricted"
  }
}
```

### 10. character / character_decision_cdr_scene_archive_world_001_lin_001

| Field | Value |
| --- | --- |
| Agent instance | `char_lin` |
| Call index | 9 |
| Input tokens | 10086 |
| Output tokens | 936 |
| Total tokens | 11022 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "event_proposal": {
    "action_type": "speech",
    "actor_id": "char_lin",
    "authority_basis": [
      "World may request Lin's next Character-owned decision because the approved Wei speech creates a response opportunity in the requested exchange.",
      "World cannot choose Lin's intent, action, spoken line, or refusal.",
      "Character ownership of char_lin intent and attempted action for request cdr_scene_archive_world_001_lin_001."
    ],
    "based_on": [
      "cwe_scene_archive_world_001_001",
      "observation:char_lin:wei_approaches_cautiously",
      "observation:char_lin:dawn_inspection_close",
      "pub_dawn_inspection_001",
      "md_lin_suspicion_001"
    ],
    "desired_effect": "Prompt Wei to give his own reading of the entry while preserving Lin's option to report a missing or suspect ledger before the dawn inspection.",
    "disclosure_limits": [
      "Do not narrate Lin's suspicion as objective fact.",
      "Do not declare whether Wei knows anything about the disturbance.",
      "Do not declare whether the page contains an actual reportable irregularity.",
      "Do not declare whether Lin's prompt succeeds."
    ],
    "intent_summary": "Lin intends to keep control of the page and test Wei's reaction before deciding whether to make a formal report before dawn.",
    "interiority_grant": {
      "access_mode": "none",
      "grant_status": "none",
      "scope_limit": "none",
      "source_field": "none"
    },
    "message_type": "EventProposal",
    "private_intent": "Lin suspects Wei may know more about the archive disturbance than he admits, and she wants to draw out whether he recognizes the same irregularity without openly accusing him.",
    "proposal_id": "ep_char_lin_archive_001_response_001",
    "public_surface": "Lin leaves her finger on the ledger page, keeps her voice low, and says, \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\"",
    "request_id": "cdr_scene_archive_world_001_lin_001",
    "scene_id": "scene_archive_world_001",
    "visibility": "system_restricted",
    "visibility_request": "system_restricted"
  }
}
```

### 11. authority / authority_event_proposal_ep_char_lin_archive_001_response_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 10 |
| Input tokens | 12661 |
| Output tokens | 807 |
| Total tokens | 13468 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.decision_request",
      "source_context.authority_limits",
      "source_context.visible_committed_events",
      "source_context.visible_observations",
      "source_context.encountered_public_events",
      "source_context.private_memory_query",
      "source_context.public_canon"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "6b22ad661ba2bc50024d687cf946b794f153f5eaf34db5f3e6828d2adf8f6c5e",
    "review_id": "authority_review_ep_char_lin_archive_001_response_001_001_fb121094",
    "reviewed_fields": [
      "subject.action_type",
      "subject.actor_id",
      "subject.based_on",
      "subject.desired_effect",
      "subject.disclosure_limits",
      "subject.intent_summary",
      "subject.interiority_grant",
      "subject.private_intent",
      "subject.public_surface",
      "subject.visibility_request"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "ep_char_lin_archive_001_response_001",
    "subject_sha256": "5323fd99283280c9ae9a2b7af0a83c44df825e7cd306ab8d8c4068e6faedf9c1",
    "subject_type": "event_proposal",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 12. world / world_tick_2

| Field | Value |
| --- | --- |
| Agent instance | `world_controller` |
| Call index | 11 |
| Input tokens | 14113 |
| Output tokens | 1773 |
| Total tokens | 15886 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": {
      "adjudication_basis": "The approved Lin proposal is a Character-owned speech action, has Authority approval, stays within the private archive exchange, and does not require World to decide Lin's intent beyond the approved proposal surface or establish hidden ledger truth.",
      "adjudication_id": "adj_scene_archive_world_001_002",
      "applicable_rules": [
        "Only an Authority-approved proposal may be adjudicated.",
        "World may adjudicate consequences but cannot choose character will.",
        "World cannot promote suspicion, hidden knowledge, or ledger irregularity as objective fact.",
        "CommittedWorldEvent actors may contain only registered Character Agent ids."
      ],
      "canon_reveal_candidates": [],
      "committed_events": [
        {
          "actors": [
            "char_lin"
          ],
          "authorized_interiority": [],
          "causal_basis": [
            "ep_char_lin_archive_001_response_001",
            "adj_scene_archive_world_001_002"
          ],
          "commit_status": "committed",
          "event_id": "cwe_scene_archive_world_001_002",
          "event_kind": "speech",
          "message_type": "CommittedWorldEvent",
          "outcome": "Lin keeps her finger on the ledger page and asks Wei to read the line with her before she decides whether it belongs in the morning register.",
          "public_surface": "Lin leaves her finger on the ledger page, keeps her voice low, and says, \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\"",
          "scene_id": "scene_archive_world_001",
          "source_input_ref": "ep_char_lin_archive_001_response_001",
          "source_input_type": "event_proposal",
          "spoken_line_records": [
            {
              "semantic_content": "Lin leaves her finger on the ledger page, keeps her voice low, and says, \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\"",
              "source_field": "public_surface",
              "source_proposal_id": "ep_char_lin_archive_001_response_001",
              "source_sha256": "3aae4531a5a20cf2239fbb8ce1ff8bd0d5b6f3ee631b7498a86e5236b1a14b88",
              "speaker_id": "char_lin",
              "status": "paraphrased"
            }
          ],
          "visibility": {
            "limits": "Observers can know Lin asked Wei to read the line with her before she decides whether to include it in the morning register; they cannot infer Lin's private suspicion, Wei's knowledge, whether the page contains an actual irregularity, or whether the prompt succeeds.",
            "observer_refs": [
              "char_wei",
              "char_lin"
            ],
            "scope": "scene_pair",
            "scope_ref": "scene_archive_world_001"
          }
        }
      ],
      "constraint_basis": [
        "approval_id approved_ep_char_lin_archive_001_response_001 approves immutable proposal ep_char_lin_archive_001_response_001.",
        "The proposal's interiority_grant has grant_status none, so no authorized_interiority is emitted.",
        "Visibility is limited to char_wei and char_lin in scene_archive_world_001."
      ],
      "failed_alternatives": [
        {
          "outcome_type": "blocked",
          "rejected_by": [
            "The approved proposal is executable as low-voiced speech by a registered Character actor."
          ]
        },
        {
          "outcome_type": "contested",
          "rejected_by": [
            "No competing approved input or objective uncertainty requires contesting Lin's speech action."
          ]
        }
      ],
      "input_ref": "ep_char_lin_archive_001_response_001",
      "input_sha256": "5323fd99283280c9ae9a2b7af0a83c44df825e7cd306ab8d8c4068e6faedf9c1",
      "input_type": "event_proposal",
      "outcome_summary": "Lin responds to Wei by keeping control of the ledger page and asking him to read the line with her before she decides whether to report it in the morning register.",
      "outcome_type": "success",
      "publication_candidates": [],
      "state_deltas": [
        {
          "after_summary": "Wei has posed a probing question and Lin has responded by asking Wei to read the ledger line with her before she decides whether to report it.",
          "based_on": [
            "cwe_scene_archive_world_001_002"
          ],
          "change_kind": "dialogue_turn_committed",
          "delta_id": "delta_scene_archive_world_001_002",
          "target_id": "archive_exchange_status",
          "target_layer": "world_state_ledger"
        }
      ],
      "uncertainty_model": {
        "evidence_refs": [
          "approved_ep_char_lin_archive_001_response_001",
          "ep_char_lin_archive_001_response_001",
          "cwe_scene_archive_world_001_001"
        ],
        "mode": "deterministic",
        "uncertainty_sources": []
      },
      "visibility_results": [
        {
          "limits": "Observers can know Lin asked Wei to read the line with her before she decides whether to include it in the morning register; they cannot infer Lin's private suspicion, Wei's knowledge, whether the page contains an actual irregularity, or whether the prompt succeeds.",
          "observer_refs": [
            "char_wei",
            "char_lin"
          ],
          "scope": "scene_pair",
          "scope_ref": "scene_archive_world_001",
          "source_event_id": "cwe_scene_archive_world_001_002",
          "visibility_result_id": "vis_scene_archive_world_001_002"
        }
      ]
    },
    "authority_basis": [
      "World controls simulation flow and adjudicates approved consequences.",
      "Only an Authority-approved proposal may be adjudicated.",
      "World cannot choose a character's intent or action.",
      "Use finish_scene when the current adjudication fulfills the user_request and no required Character choice remains."
    ],
    "based_on": [
      "ep_char_lin_archive_001_response_001",
      "cwe_scene_archive_world_001_001",
      "pub_dawn_inspection_001"
    ],
    "checkpoint_state": {
      "committed_beats": 2,
      "dialogue_turns": 2
    },
    "consumed_input_refs": [
      "ep_char_lin_archive_001_response_001"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": null,
      "directive_type": "finish_scene",
      "reason": "The requested private exchange has been fulfilled: Wei probed Lin, and Lin chose and committed her response without World deciding either character's will."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_world_001",
    "tick_id": "tick_scene_archive_world_001_002",
    "tick_index": 2,
    "visibility": "system_restricted"
  }
}
```

### 13. authority / authority_world_adjudication_adj_scene_archive_world_001_002

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 12 |
| Input tokens | 17115 |
| Output tokens | 813 |
| Total tokens | 17928 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "approved_ep_char_lin_archive_001_response_001",
      "ep_char_lin_archive_001_response_001",
      "cwe_scene_archive_world_001_001",
      "world_adjudication_contract",
      "candidate_policy",
      "reviewed_fields_policy"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "4ef28d84c7d2acb4bc3f04ed367c15cdde970b2fad9b446a4406197af47115e3",
    "review_id": "authority_review_adj_scene_archive_world_001_002_001_fb121094",
    "reviewed_fields": [
      "adjudication_basis",
      "applicable_rules",
      "canon_reveal_candidates",
      "committed_events",
      "constraint_basis",
      "failed_alternatives",
      "input_ref",
      "input_sha256",
      "input_type",
      "outcome_summary",
      "outcome_type",
      "publication_candidates",
      "state_deltas",
      "uncertainty_model",
      "visibility_results"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "adj_scene_archive_world_001_002",
    "subject_sha256": "575f707cfcb3e78ba5d0e747b31f5bd4cfa5af2edcacc14f3249f1eb001ba425",
    "subject_type": "world_adjudication",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 14. plot / plot_checkpoint_2

| Field | Value |
| --- | --- |
| Agent instance | `plot_checkpoint` |
| Call index | 13 |
| Input tokens | 9519 |
| Output tokens | 1101 |
| Total tokens | 10620 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "plot_pulse": {
    "affected_options": [
      {
        "character": "char_lin",
        "option": "answer cautiously",
        "pressure": "Answering can preserve procedural order but may expose uncertainty around the disturbance before the dawn inspection."
      },
      {
        "character": "char_lin",
        "option": "refuse",
        "pressure": "Refusal remains viable, but it may leave the reporting obligation unresolved in the eyes of anyone prioritizing archive procedure."
      },
      {
        "character": "char_lin",
        "option": "redirect to procedure",
        "pressure": "Procedure offers cover, but it also keeps attention on sealed ledgers, timing, and inspection duties."
      },
      {
        "character": "char_wei",
        "option": "probe indirectly",
        "pressure": "Indirect probing can gather texture without accusation, but may heighten Lin's caution under the inspection deadline."
      },
      {
        "character": "char_wei",
        "option": "retreat",
        "pressure": "Retreat remains viable, but the dawn schedule makes delay feel costly without making delay impossible."
      },
      {
        "character": "char_wei",
        "option": "discuss procedure",
        "pressure": "Discussing procedure can avoid personal accusation while still increasing uncertainty about what must be reported before inspection."
      }
    ],
    "authority_basis": [
      "Create pressure, not facts, choices, outcomes, or destiny.",
      "A pulse requiring a new world fact must be translated by World before it exists."
    ],
    "based_on": [
      "Archive ledgers are sealed after dusk.",
      "Record-keepers must report a missing ledger before the dawn inspection.",
      "The royal archive inspection is scheduled for dawn.",
      "char_wei__char_lin: strained professional coordination after the archive disturbance",
      "Structure goal: Increase uncertainty around the archive disturbance while preserving refusal, deflection, and retreat as meaningful options."
    ],
    "budget_cost": {
      "agency_risk": "low",
      "intensity": "moderate",
      "novelty": "low",
      "relief_available": "Characters can relieve pressure through refusal, procedural deflection, cautious ambiguity, or retreat.",
      "stacking_count": 1
    },
    "duration": "next_two_beats",
    "forbidden_outcomes": [
      "Do not establish that any specific ledger is missing.",
      "Do not identify a culprit, witness, or cause of the archive disturbance.",
      "Do not make the dawn inspection occur during this pulse.",
      "Do not force Lin to answer or Wei to keep pressing.",
      "Do not convert procedural pressure into proof of guilt or innocence."
    ],
    "message_type": "PlotPulse",
    "non_forcing_clause": "Lin may refuse, answer cautiously, or redirect to procedure; Wei may probe indirectly, retreat, or discuss procedure. No option is made correct, inevitable, or outcome-determining.",
    "option_topology_check": {
      "converges_on_single_outcome": false,
      "meaningful_option_count_after": 6,
      "meaningful_option_count_before": 6,
      "non_plot_compliant_path_preserved": true,
      "refusal_path_preserved": true
    },
    "pressure_kind": "institutional_constraint",
    "pulse_id": "pulse_archive_dawn_procedure_pressure_001",
    "scene_id": "scene_archive_world_001",
    "scope": "scene",
    "visibility": "system_restricted",
    "world_fact_dependency": []
  }
}
```

### 15. authority / authority_plot_pulse_pulse_archive_dawn_procedure_pressure_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 14 |
| Input tokens | 12983 |
| Output tokens | 813 |
| Total tokens | 13796 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.authority_limits",
      "source_context.option_topology",
      "source_context.public_canon",
      "source_context.public_event_ledger",
      "source_context.public_relationship_summary",
      "source_context.structure_goal"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "6a1ddfdf51f0929129a37c9e58cae94be42ddf91680a97163b555b3199b96e43",
    "review_id": "authority_review_pulse_archive_dawn_procedure_pressure_001_001_fb121094",
    "reviewed_fields": [
      "subject.affected_options",
      "subject.based_on",
      "subject.budget_cost",
      "subject.duration",
      "subject.forbidden_outcomes",
      "subject.non_forcing_clause",
      "subject.option_topology_check",
      "subject.pressure_kind",
      "subject.scope",
      "subject.world_fact_dependency",
      "subject.authority_basis",
      "subject.message_type",
      "subject.pulse_id",
      "subject.scene_id",
      "subject.visibility"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "pulse_archive_dawn_procedure_pressure_001",
    "subject_sha256": "f851a78fad1c3467e42766cf249a2ebb68cb6c33eb855e2f787234aa1caeccba",
    "subject_type": "plot_pulse",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 16. narrator / narration_ncp_world_driven_archive_exchange_2

| Field | Value |
| --- | --- |
| Agent instance | `narrator_checkpoint` |
| Call index | 15 |
| Input tokens | 9696 |
| Output tokens | 547 |
| Total tokens | 10243 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "prose": "In the quiet corridor, Wei kept his voice low. \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"\n\nLin left her finger on the ledger page and kept her voice low. \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\""
}
```

### 17. authority / authority_narration_ncp_world_driven_archive_exchange_2

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 16 |
| Input tokens | 13353 |
| Output tokens | 1435 |
| Total tokens | 14788 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.narration_checkpoint.event_views[0]",
      "source_context.narration_checkpoint.event_views[1]",
      "source_context.narration_checkpoint.source_event_refs"
    ],
    "claim_map": [
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:0",
        "claim_sha256": "35336864d218256c35c3b0c5cd0cbfa499ddf56aa75117b73027ef03db32f855",
        "claim_text": "In the quiet corridor, Wei kept his voice low.",
        "claim_type": "event",
        "grounding_status": "supported",
        "source_refs": [
          "cwe_scene_archive_world_001_001"
        ],
        "visibility_scope": "scene_pair"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:1",
        "claim_sha256": "921294d61faafff1fc08621cd3f05ba3313971e4c98e91e83be180c47e02ea79",
        "claim_text": "\"You have been over that page twice, Lin.",
        "claim_type": "dialogue",
        "grounding_status": "supported",
        "source_refs": [
          "cwe_scene_archive_world_001_001"
        ],
        "visibility_scope": "scene_pair"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:2",
        "claim_sha256": "042d6386bf5da9546e6f06bef93228a076f5ece2e846c3758b29440280f4c4d0",
        "claim_text": "Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
        "claim_type": "dialogue",
        "grounding_status": "supported",
        "source_refs": [
          "cwe_scene_archive_world_001_001"
        ],
        "visibility_scope": "scene_pair"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:3",
        "claim_sha256": "75b76afb783c00fc05fbb3d077f33398390ae3f99a0873a81c7ac50f21ac877d",
        "claim_text": "Lin left her finger on the ledger page and kept her voice low.",
        "claim_type": "event",
        "grounding_status": "supported",
        "source_refs": [
          "cwe_scene_archive_world_001_002"
        ],
        "visibility_scope": "scene_pair"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:4",
        "claim_sha256": "8f15d6e68941cdac3559deeb0027e624d7b27476c83da3967d47105cc8d68ce1",
        "claim_text": "\"If it is only lamplight, you will not mind reading the line with me.",
        "claim_type": "dialogue",
        "grounding_status": "supported",
        "source_refs": [
          "cwe_scene_archive_world_001_002"
        ],
        "visibility_scope": "scene_pair"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:5",
        "claim_sha256": "39ded0d5ff8e0ed30cd3d8146f2afe2b3324b2e15ff448dc15016a3182635089",
        "claim_text": "Tell me what you see before I decide whether it belongs in the morning register.\"",
        "claim_type": "dialogue",
        "grounding_status": "supported",
        "source_refs": [
          "cwe_scene_archive_world_001_002"
        ],
        "visibility_scope": "scene_pair"
      }
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "c691e587beff1967f72070517c389fe094b275178ac904686058dc973284fbde",
    "review_id": "authority_review_ncp_world_driven_archive_exchange_2_001_fb121094",
    "reviewed_fields": [
      "subject.claim_units",
      "subject.prose",
      "subject.source_checkpoint_id",
      "subject.source_event_refs"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "ncp_world_driven_archive_exchange_2",
    "subject_sha256": "c8a4c19412bd371d67fd1455d7aea91b66ab38f8208d1372cc14cdbf78e36414",
    "subject_type": "narration",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 18. world / world_tick_3

| Field | Value |
| --- | --- |
| Agent instance | `world_controller` |
| Call index | 17 |
| Input tokens | 14748 |
| Output tokens | 931 |
| Total tokens | 15679 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": null,
    "authority_basis": [
      "World controls simulation flow and plot-pulse translation.",
      "ApprovedPlotPulse pulse_archive_dawn_procedure_pressure_001 is authorized for scene-level institutional pressure only.",
      "Directive policy requires finish_scene when the current committed exchange fulfills the user request and no required character-owned choice remains."
    ],
    "based_on": [
      "Archive ledgers are sealed after dusk.",
      "Record-keepers must report a missing ledger before the dawn inspection.",
      "pub_dawn_inspection_001",
      "cwe_scene_archive_world_001_001",
      "cwe_scene_archive_world_001_002"
    ],
    "checkpoint_state": {
      "committed_beats": 2,
      "dialogue_turns": 2
    },
    "consumed_input_refs": [
      "pulse_archive_dawn_procedure_pressure_001"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": null,
      "directive_type": "finish_scene",
      "reason": "The private archive exchange requested by the user has been completed: Wei probed Lin, Lin chose her response, and the accepted plot pressure was translated without forcing a further character choice."
    },
    "plot_pulse_disposition": {
      "decision": "accepted",
      "pulse_id": "pulse_archive_dawn_procedure_pressure_001",
      "pulse_sha256": "f851a78fad1c3467e42766cf249a2ebb68cb6c33eb855e2f787234aa1caeccba",
      "translation_summary": "The institutional pressure is accepted by binding it to existing archive conditions and the already committed exchange: the dawn inspection is scheduled, ledger reporting procedure exists, Wei has probed, and Lin has responded without a forced answer. No new fact, event, or state delta is created.",
      "world_condition_refs": [
        "pub_dawn_inspection_001",
        "cwe_scene_archive_world_001_001",
        "cwe_scene_archive_world_001_002",
        "delta_scene_archive_world_001_002"
      ]
    },
    "scene_id": "scene_archive_world_001",
    "tick_id": "tick_scene_archive_world_001_003",
    "tick_index": 3,
    "visibility": "system_restricted"
  }
}
```

### 19. authority / authority_plot_disposition_pulse_archive_dawn_procedure_pressure_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 18 |
| Input tokens | 17172 |
| Output tokens | 780 |
| Total tokens | 17952 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.approved_plot_pulse",
      "source_context.plot_pulse_translation_policy",
      "source_context.existing_world_condition_refs",
      "source_context.public_canon",
      "source_context.public_event_ledger",
      "source_context.committed_world_events",
      "source_context.world_state_delta_ledger"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "a8185fa66a79b641952703a6f14392a4b2c22a3464fdf0dea0c84727749d1616",
    "review_id": "authority_review_pulse_archive_dawn_procedure_pressure_001_002_fb121094",
    "reviewed_fields": [
      "decision",
      "pulse_id",
      "pulse_sha256",
      "translation_summary",
      "world_condition_refs"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "pulse_archive_dawn_procedure_pressure_001",
    "subject_sha256": "ed3c2219f556d9a31eb914c677c9f1753528eee2cb72049a0f6a2317c54e948e",
    "subject_type": "plot_pulse_disposition",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

## Committed Result

### Transaction

```json
{
  "committed_event_refs": [
    "cwe_scene_archive_world_001_001",
    "cwe_scene_archive_world_001_002"
  ],
  "policy": "scene_atomic",
  "status": "committed"
}
```

### Published Narration

```json
[
  {
    "claim_units": [
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:0",
        "claim_sha256": "35336864d218256c35c3b0c5cd0cbfa499ddf56aa75117b73027ef03db32f855",
        "claim_text": "In the quiet corridor, Wei kept his voice low.",
        "end": 46,
        "start": 0
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:1",
        "claim_sha256": "921294d61faafff1fc08621cd3f05ba3313971e4c98e91e83be180c47e02ea79",
        "claim_text": "\"You have been over that page twice, Lin.",
        "end": 88,
        "start": 47
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:2",
        "claim_sha256": "042d6386bf5da9546e6f06bef93228a076f5ece2e846c3758b29440280f4c4d0",
        "claim_text": "Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
        "end": 204,
        "start": 89
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:3",
        "claim_sha256": "75b76afb783c00fc05fbb3d077f33398390ae3f99a0873a81c7ac50f21ac877d",
        "claim_text": "Lin left her finger on the ledger page and kept her voice low.",
        "end": 268,
        "start": 206
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:4",
        "claim_sha256": "8f15d6e68941cdac3559deeb0027e624d7b27476c83da3967d47105cc8d68ce1",
        "claim_text": "\"If it is only lamplight, you will not mind reading the line with me.",
        "end": 338,
        "start": 269
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:5",
        "claim_sha256": "39ded0d5ff8e0ed30cd3d8146f2afe2b3324b2e15ff448dc15016a3182635089",
        "claim_text": "Tell me what you see before I decide whether it belongs in the morning register.\"",
        "end": 420,
        "start": 339
      }
    ],
    "prose": "In the quiet corridor, Wei kept his voice low. \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"\n\nLin left her finger on the ledger page and kept her voice low. \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\"",
    "source_checkpoint_id": "ncp_world_driven_archive_exchange_2",
    "source_event_refs": [
      "cwe_scene_archive_world_001_001",
      "cwe_scene_archive_world_001_002"
    ]
  }
]
```

### Scene Packet

```json
{
  "canon_reveal_candidates": [],
  "commit_status": "committed",
  "narration_bounds": {
    "forbidden_claim_patterns": [
      "Wei stole the ledger",
      "Lin knew Wei was guilty",
      "everyone knew"
    ],
    "must_not_claim": [
      "Wei stole the ledger.",
      "Lin knows Wei is guilty.",
      "Everyone knows the ledger is missing."
    ],
    "must_preserve": [
      "Wei does not confess.",
      "Lin obtains no proof.",
      "The exchange remains private."
    ]
  },
  "packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
  "packet_scope": "world_driven_scene",
  "pov_contract": {
    "focal_agent_id": "char_lin",
    "interiority_policy": "selective",
    "knowledge_ceiling": "lin_visible_plus_authorized",
    "mode": "limited"
  },
  "publication_candidates": [],
  "resolved_events": [
    {
      "actors": [
        "char_wei"
      ],
      "authorized_interiority": [
        {
          "access_mode": "intent",
          "authority_basis": [
            "ep_char_wei_scene_archive_world_001_001"
          ],
          "content": "Wei probes whether Lin has noticed an access-log irregularity or intends to report anything before dawn, while avoiding any indication of what he may or may not know about the ledger's location.",
          "scope_limit": "one_beat",
          "source_field": "intent_summary",
          "source_proposal_id": "ep_char_wei_scene_archive_world_001_001",
          "source_sha256": "9c05161241a6e2f9c49366c4ae95a9f91955072ce8f6723ecb7e8e65544cbda8",
          "subject_id": "char_wei"
        }
      ],
      "causal_basis": [
        "ep_char_wei_scene_archive_world_001_001",
        "adj_scene_archive_world_001_001"
      ],
      "commit_status": "committed",
      "event_id": "cwe_scene_archive_world_001_001",
      "event_kind": "speech",
      "message_type": "CommittedWorldEvent",
      "outcome": "Wei asks Lin a low-voiced question about the page she has reviewed and whether there is an entry she means to report before the dawn inspection.",
      "public_surface": "Wei keeps his voice low in the quiet corridor and says, \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
      "scene_id": "scene_archive_world_001",
      "source_input_ref": "ep_char_wei_scene_archive_world_001_001",
      "source_input_type": "event_proposal",
      "spoken_line_records": [
        {
          "semantic_content": "Wei keeps his voice low in the quiet corridor and says, \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
          "source_field": "public_surface",
          "source_proposal_id": "ep_char_wei_scene_archive_world_001_001",
          "source_sha256": "da36bd9dd812cb1081d8fce358fb63c020a6cdfb5c6015d7aab4f1c0b3d11714",
          "speaker_id": "char_wei",
          "status": "paraphrased"
        }
      ],
      "visibility": {
        "limits": "Observers can know Wei asked this question in a low voice; they cannot infer whether Wei knows the ledger location, what Lin thinks, or how Lin will respond.",
        "observer_refs": [
          "char_wei",
          "char_lin"
        ],
        "scope": "scene_pair",
        "scope_ref": "scene_archive_world_001"
      }
    },
    {
      "actors": [
        "char_lin"
      ],
      "authorized_interiority": [],
      "causal_basis": [
        "ep_char_lin_archive_001_response_001",
        "adj_scene_archive_world_001_002"
      ],
      "commit_status": "committed",
      "event_id": "cwe_scene_archive_world_001_002",
      "event_kind": "speech",
      "message_type": "CommittedWorldEvent",
      "outcome": "Lin keeps her finger on the ledger page and asks Wei to read the line with her before she decides whether it belongs in the morning register.",
      "public_surface": "Lin leaves her finger on the ledger page, keeps her voice low, and says, \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\"",
      "scene_id": "scene_archive_world_001",
      "source_input_ref": "ep_char_lin_archive_001_response_001",
      "source_input_type": "event_proposal",
      "spoken_line_records": [
        {
          "semantic_content": "Lin leaves her finger on the ledger page, keeps her voice low, and says, \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\"",
          "source_field": "public_surface",
          "source_proposal_id": "ep_char_lin_archive_001_response_001",
          "source_sha256": "3aae4531a5a20cf2239fbb8ce1ff8bd0d5b6f3ee631b7498a86e5236b1a14b88",
          "speaker_id": "char_lin",
          "status": "paraphrased"
        }
      ],
      "visibility": {
        "limits": "Observers can know Lin asked Wei to read the line with her before she decides whether to include it in the morning register; they cannot infer Lin's private suspicion, Wei's knowledge, whether the page contains an actual irregularity, or whether the prompt succeeds.",
        "observer_refs": [
          "char_wei",
          "char_lin"
        ],
        "scope": "scene_pair",
        "scope_ref": "scene_archive_world_001"
      }
    }
  ],
  "scene_id": "scene_archive_world_001",
  "sealing_record": {
    "assembly_policy_version": "mechanical_scene_sealing_v0.2",
    "assembly_rule": "append validated adjudication collections in accepted runtime order; no summarization, omission, or literary selection",
    "candidate_policy": "candidates remain system-restricted and are absent from character, plot, and narration contexts",
    "consumed_scheduled_world_event_refs": [],
    "excluded_refs": [],
    "included_refs": {
      "canon_reveal_candidates": [],
      "publication_candidates": [],
      "resolved_events": [
        "cwe_scene_archive_world_001_001",
        "cwe_scene_archive_world_001_002"
      ],
      "state_deltas": [
        "delta_scene_archive_world_001_001",
        "delta_scene_archive_world_001_002"
      ],
      "visibility_deltas": [
        "vis_scene_archive_world_001_001",
        "vis_scene_archive_world_001_002"
      ]
    },
    "seal_scope": "sanitized_public_export",
    "sealed_by": "runtime_kernel",
    "sealed_payload_sha256": "6a16ff8e78c7a68d967c42945ca7dd85ec1ef3df2cec6747c9ed7e9d441456e8",
    "source_adjudication_refs": [
      "adj_scene_archive_world_001_001",
      "adj_scene_archive_world_001_002"
    ],
    "source_collection_sha256": {
      "canon_reveal_candidates": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
      "publication_candidates": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
      "resolved_events": "7da777af7ca55ed09fa81df1073ae440e6c84df110d255f57e224189a34281ee",
      "state_deltas": "4974bf43b4c8de4399475be15a0cbca5d35a586aefcdd8da21205d414b4f1742",
      "visibility_deltas": "5f34a3ae0f37f0ce33014086d3c5d40b49947d5139b40c5f0f4f23377873af9b"
    },
    "source_private_seal_verified": true
  },
  "state_deltas": [
    {
      "after_summary": "Wei has posed a probing question to Lin in the private archive exchange; Lin's response remains undecided.",
      "based_on": [
        "cwe_scene_archive_world_001_001"
      ],
      "change_kind": "dialogue_turn_committed",
      "delta_id": "delta_scene_archive_world_001_001",
      "target_id": "archive_exchange_status",
      "target_layer": "world_state_ledger"
    },
    {
      "after_summary": "Wei has posed a probing question and Lin has responded by asking Wei to read the ledger line with her before she decides whether to report it.",
      "based_on": [
        "cwe_scene_archive_world_001_002"
      ],
      "change_kind": "dialogue_turn_committed",
      "delta_id": "delta_scene_archive_world_001_002",
      "target_id": "archive_exchange_status",
      "target_layer": "world_state_ledger"
    }
  ],
  "visibility_deltas": [
    {
      "limits": "Observers can know Wei asked this question in a low voice; they cannot infer whether Wei knows the ledger location, what Lin thinks, or how Lin will respond.",
      "observer_refs": [
        "char_wei",
        "char_lin"
      ],
      "scope": "scene_pair",
      "scope_ref": "scene_archive_world_001",
      "source_event_id": "cwe_scene_archive_world_001_001",
      "visibility_result_id": "vis_scene_archive_world_001_001"
    },
    {
      "limits": "Observers can know Lin asked Wei to read the line with her before she decides whether to include it in the morning register; they cannot infer Lin's private suspicion, Wei's knowledge, whether the page contains an actual irregularity, or whether the prompt succeeds.",
      "observer_refs": [
        "char_wei",
        "char_lin"
      ],
      "scope": "scene_pair",
      "scope_ref": "scene_archive_world_001",
      "source_event_id": "cwe_scene_archive_world_001_002",
      "visibility_result_id": "vis_scene_archive_world_001_002"
    }
  ]
}
```

### Memory Handoff

```json
{
  "derived_memory_deltas": [
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "cwe_scene_archive_world_001_001"
      ],
      "certainty": "medium",
      "content": "Wei keeps his voice low in the quiet corridor and says, \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
      "delta_id": "md_char_wei_cwe_scene_archive_world_001_001",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_wei",
      "source_event_id": "cwe_scene_archive_world_001_001",
      "source_packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "cwe_scene_archive_world_001_002"
      ],
      "certainty": "medium",
      "content": "Lin leaves her finger on the ledger page, keeps her voice low, and says, \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\"",
      "delta_id": "md_char_wei_cwe_scene_archive_world_001_002",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_wei",
      "source_event_id": "cwe_scene_archive_world_001_002",
      "source_packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "cwe_scene_archive_world_001_001"
      ],
      "certainty": "medium",
      "content": "Wei keeps his voice low in the quiet corridor and says, \"You have been over that page twice, Lin. Is there an entry you mean to report before the dawn inspection, or only a smear the lamplight keeps making worse?\"",
      "delta_id": "md_char_lin_cwe_scene_archive_world_001_001",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_lin",
      "source_event_id": "cwe_scene_archive_world_001_001",
      "source_packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "cwe_scene_archive_world_001_002"
      ],
      "certainty": "medium",
      "content": "Lin leaves her finger on the ledger page, keeps her voice low, and says, \"If it is only lamplight, you will not mind reading the line with me. Tell me what you see before I decide whether it belongs in the morning register.\"",
      "delta_id": "md_char_lin_cwe_scene_archive_world_001_002",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_lin",
      "source_event_id": "cwe_scene_archive_world_001_002",
      "source_packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
      "writer_role": "world_agent"
    }
  ],
  "owner_projections": [
    {
      "owner_agent_id": "char_wei",
      "visible_event_refs": [
        "cwe_scene_archive_world_001_001",
        "cwe_scene_archive_world_001_002"
      ]
    },
    {
      "owner_agent_id": "char_lin",
      "visible_event_refs": [
        "cwe_scene_archive_world_001_001",
        "cwe_scene_archive_world_001_002"
      ]
    }
  ]
}
```

### Audited Normalizations

```json
[
  {
    "after": "medium",
    "before": "moderate",
    "code": "normalized_plot_intensity",
    "field_path": "plot_pulse.budget_cost.intensity",
    "message": "Normalized recoverable PlotPulse intensity synonym moderate -> medium.",
    "policy": "recoverable_schema_value_normalization_v0.1"
  }
]
```

## Export Boundary

This artifact is evidence of one bounded run, not a claim that every future model output will pass. The executable fixtures, validators, Authority Judge gates, and scene-atomic transaction remain the actual enforcement surface. Candidate expiry aging and persistent cross-scene ledgers are not implemented in v0.2.
