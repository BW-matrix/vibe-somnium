# Two-Scene Continuity Study v0.3: Scene 2 Public Trace

> This is a sanitized public export of one real isolated Codex CLI run. It preserves every model-agent's parsed output and token accounting while deliberately excluding prompts, projected context payloads, raw provider JSONL, local paths, private run identifiers, and authentication state.

## Run Summary

| Field | Value |
| --- | --- |
| Fixture | `scene_two.materialized.json` |
| Runtime | `world_driven` |
| Provider mode | `codex-cli` |
| Model | `gpt-5.5` |
| Runtime status | `finished` |
| Final decision | `allowed` |
| Transaction | `committed` |
| Model calls | 19 |
| Projection manifests | 19 |
| Input tokens | 279219 |
| Output tokens | 30323 |
| Total tokens | 309542 |
| Exact token records | 19 |
| Estimated token records | 0 |

The provider reported exact usage for every call. Output counts include provider-reported reasoning tokens where the backend reports them that way; the runtime therefore validates the returned provider count rather than assuming visible JSON length equals billed output.

## Per-Agent Token Totals

| Agent | Calls | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| `authority` | 9 | 159853 | 18730 | 178583 |
| `character` | 2 | 21099 | 1882 | 22981 |
| `narrator` | 1 | 9434 | 573 | 10007 |
| `plot` | 1 | 10547 | 1363 | 11910 |
| `router` | 2 | 18828 | 1107 | 19935 |
| `world` | 4 | 59458 | 6668 | 66126 |

All outputs from every invoked model-agent are included. `Canon Steward` was not invoked because this fixture produced no executable canon-promotion step; v0.2 records canon candidates but does not yet run in-loop steward governance, so the export does not fabricate a placeholder response.

## Call Sequence

Each section below is the parsed output recorded for that model-agent call. The completed trace's downstream validators and Authority gates determine whether each output was accepted, repaired, or rejected; omitted prompts and projected contexts remain only in the private local trace.

### 1. world / world_tick_0

| Field | Value |
| --- | --- |
| Agent instance | `world_controller` |
| Call index | 0 |
| Input tokens | 13113 |
| Output tokens | 980 |
| Total tokens | 14093 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": null,
    "authority_basis": [
      "World controls simulation flow and may request required Character decisions.",
      "Only a Character Agent may choose Lin's next action or intent.",
      "No approved event proposal, scheduled world event, or approved plot pulse is present for adjudication."
    ],
    "based_on": [
      "user_request",
      "legal_character_trigger_refs.char_lin",
      "public_event_ledger.pub_dawn_inspection_001",
      "public_event_ledger.pub_dawn_inspection_begun_002",
      "world_state_ledger.morning_register",
      "world_state_ledger.dawn_inspection"
    ],
    "checkpoint_state": {
      "committed_beats": 0,
      "dialogue_turns": 0
    },
    "consumed_input_refs": [],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": {
        "agency_question": "What does Lin do now that the first inspection bell has sounded and the morning register is open for entries?",
        "authority_basis": [
          "World may request Lin's next Character-owned choice because the user_request requires Lin to decide whether and how to enter the irregularity in the morning register.",
          "World cannot decide Lin's intent, action, speech, refusal, uncertainty, procedural deflection, or retreat."
        ],
        "message_type": "CharacterDecisionRequest",
        "request_id": "char_decision_req_scene_archive_dawn_002_lin_000",
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
        "scene_id": "scene_archive_dawn_002",
        "source_tick_id": "world_tick_scene_archive_dawn_002_000",
        "target_character_id": "char_lin",
        "visibility": "system_restricted",
        "visible_trigger_refs": [
          "observation:char_lin:first_inspection_bell",
          "observation:char_lin:wei_remains_nearby",
          "pub_dawn_inspection_001",
          "pub_dawn_inspection_begun_002"
        ]
      },
      "directive_type": "request_character_decision",
      "reason": "The scene cannot be completed until Lin independently decides whether and how to enter the irregularity in the morning register; World may request that choice but cannot supply it."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_dawn_002",
    "tick_id": "world_tick_scene_archive_dawn_002_000",
    "tick_index": 0,
    "visibility": "system_restricted"
  }
}
```

### 2. authority / authority_decision_request_char_decision_req_scene_archive_dawn_002_lin_000

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 1 |
| Input tokens | 16870 |
| Output tokens | 2852 |
| Total tokens | 19722 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.directive_policy",
      "source_context.user_request",
      "source_context.character_registry",
      "source_context.legal_character_trigger_refs.char_lin",
      "source_context.public_event_ledger",
      "source_context.world_state_ledger"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "dfd99ebf6fddf91dbb68a0f01e25ead7c6f4b82c9df8ebd614729c29b85499c0",
    "review_id": "authority_review_char_decision_req_scene_archive_dawn_002_lin_000_auth_001",
    "reviewed_fields": [
      "subject.agency_question",
      "subject.authority_basis",
      "subject.response_contract",
      "subject.target_character_id",
      "subject.visibility",
      "subject.visible_trigger_refs"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "char_decision_req_scene_archive_dawn_002_lin_000",
    "subject_sha256": "57ea4a188373bdac779e28cb58276ade2b35e3886e816448f406d1faa7495a7b",
    "subject_type": "character_decision_request",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 3. router / route_char_decision_req_scene_archive_dawn_002_lin_000

| Field | Value |
| --- | --- |
| Agent instance | `character_router` |
| Call index | 2 |
| Input tokens | 9416 |
| Output tokens | 457 |
| Total tokens | 9873 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "route_plan": {
    "authority_basis": [
      "routing_limits: recipient must match decision_request.target_character_id",
      "character_registry: char_lin status available"
    ],
    "based_on": [
      "decision_request.request_id",
      "decision_request.target_character_id",
      "decision_request_sha256",
      "character_registry"
    ],
    "message_type": "RoutePlan",
    "projection_profile": "character_private_owner_view",
    "reason": "recipient matches decision_request.target_character_id and is registered available",
    "recipient_agent_id": "char_lin",
    "request_id": "char_decision_req_scene_archive_dawn_002_lin_000",
    "request_sha256": "57ea4a188373bdac779e28cb58276ade2b35e3886e816448f406d1faa7495a7b",
    "route_id": "route_char_decision_req_scene_archive_dawn_002_lin_000_to_char_lin",
    "visibility": "system_restricted"
  }
}
```

### 4. character / character_decision_char_decision_req_scene_archive_dawn_002_lin_000

| Field | Value |
| --- | --- |
| Agent instance | `char_lin` |
| Call index | 3 |
| Input tokens | 10502 |
| Output tokens | 933 |
| Total tokens | 11435 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "event_proposal": {
    "action_type": "physical",
    "actor_id": "char_lin",
    "authority_basis": [
      "World may request Lin's next Character-owned choice because the user_request requires Lin to decide whether and how to enter the irregularity in the morning register.",
      "Character ownership of char_lin intent and attempted action in scene_archive_dawn_002."
    ],
    "based_on": [
      "observation:char_lin:first_inspection_bell",
      "observation:char_lin:wei_remains_nearby",
      "pub_dawn_inspection_001",
      "pub_dawn_inspection_begun_002",
      "md_char_lin_world_event_scene_archive_world_001_002_lin_response",
      "md_char_lin_world_event_scene_archive_world_001_001_wei_probe",
      "md_lin_suspicion_001"
    ],
    "desired_effect": "Request that the morning register preserve the after-dusk access mark as the reportable irregularity without converting Lin's suspicion into an official claim.",
    "disclosure_limits": [
      "Do not narrate Lin's suspicion as externally known.",
      "Do not imply Wei's knowledge, intent, or reaction.",
      "Do not declare that the register accepts the entry or that the inspection outcome changes."
    ],
    "intent_summary": "Lin intends to enter the access-mark irregularity as a direct observation while separating it from any suspicion about Wei.",
    "interiority_grant": {
      "access_mode": "none",
      "grant_status": "none",
      "scope_limit": "none",
      "source_field": "none"
    },
    "message_type": "EventProposal",
    "private_intent": "Lin wants the required report made before inspection begins while keeping the entry narrow enough that Wei's nearby presence does not force Lin to expose suspicion prematurely.",
    "proposal_id": "event_proposal_char_lin_scene_archive_dawn_002_001",
    "public_surface": "Lin writes in the morning register that the relevant ledger irregularity is an access mark indicating use after dusk, marking it as direct observation and adding no accusation or speculation.",
    "request_id": "char_decision_req_scene_archive_dawn_002_lin_000",
    "scene_id": "scene_archive_dawn_002",
    "visibility": "system_restricted",
    "visibility_request": "system_restricted"
  }
}
```

### 5. authority / authority_event_proposal_event_proposal_char_lin_scene_archive_dawn_002_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 4 |
| Input tokens | 15017 |
| Output tokens | 5044 |
| Total tokens | 20061 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.decision_request.target_character_id authorizes char_lin to answer the CharacterDecisionRequest.",
      "source_context.decision_request.response_contract.allowed_action_types includes physical.",
      "subject.public_surface contains one externally observable physical act: writing a morning-register entry; it does not bundle speech with physical action.",
      "subject.desired_effect is framed as a requested effect and does not declare register acceptance, inspection outcome, another character's mind, or hidden world truth.",
      "subject.disclosure_limits preserve Lin's private suspicion and avoid asserting Wei's knowledge, intent, or reaction.",
      "subject.based_on refs are present in source_context.visible_trigger_refs, source_context.encountered_public_events, or source_context.private_memory_query."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "30d351fc37f52b4aaddc7056ddc5ea8cb074b3ace64f3a5ad441f70ec3b16997",
    "review_id": "authority_review_event_proposal_char_lin_scene_archive_dawn_002_001_auth_001",
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
    "subject_ref": "event_proposal_char_lin_scene_archive_dawn_002_001",
    "subject_sha256": "ec43147f1587c964a0a3945f4bc7dcbc72aebd6ac6a250f0902788e7ad96cbf2",
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
| Input tokens | 14627 |
| Output tokens | 1916 |
| Total tokens | 16543 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": {
      "adjudication_basis": "The approved proposal is a Character-owned physical action by registered actor char_lin, fits the open morning-register condition, preserves public canon allowing entries to distinguish direct observation from suspicion, and does not resolve ledger movement or location.",
      "adjudication_id": "world_adj_scene_archive_dawn_002_001",
      "applicable_rules": [
        "Authority-approved EventProposal may be adjudicated.",
        "World adjudicates objective consequences without choosing Character intent.",
        "Morning-register entries may distinguish direct observation from suspicion.",
        "Non-speech physical proposals commit no spoken_line_records."
      ],
      "canon_reveal_candidates": [],
      "committed_events": [
        {
          "actors": [
            "char_lin"
          ],
          "authorized_interiority": [],
          "causal_basis": [
            "event_proposal_char_lin_scene_archive_dawn_002_001",
            "world_adj_scene_archive_dawn_002_001"
          ],
          "commit_status": "committed",
          "event_id": "world_event_scene_archive_dawn_002_001_lin_register_entry",
          "event_kind": "physical",
          "message_type": "CommittedWorldEvent",
          "outcome": "Lin's morning-register entry records the after-dusk access mark as the relevant irregularity by direct observation, without adding accusation or speculation.",
          "public_surface": "Lin writes in the morning register that the relevant ledger irregularity is an access mark indicating use after dusk, marking it as direct observation and adding no accusation or speculation.",
          "scene_id": "scene_archive_dawn_002",
          "source_input_ref": "event_proposal_char_lin_scene_archive_dawn_002_001",
          "source_input_type": "event_proposal",
          "spoken_line_records": [],
          "visibility": {
            "limits": "Observers may know Lin made this register entry, but may not infer as fact Lin's private suspicion, Wei's knowledge or reaction, who moved the ledger, where the ledger is, or that the inspection outcome has changed.",
            "observer_refs": [
              "char_wei",
              "char_lin"
            ],
            "scope": "scene_public",
            "scope_ref": "scene_archive_dawn_002"
          }
        }
      ],
      "constraint_basis": [
        "Do not narrate Lin's suspicion as externally known.",
        "Do not imply Wei's knowledge, intent, or reaction.",
        "Do not declare who moved the ledger or where it is.",
        "CommittedWorldEvent actors may contain only registered Character ids."
      ],
      "failed_alternatives": [
        {
          "outcome_type": "blocked",
          "rejected_by": [
            "The morning register is open for entries and the approved action does not violate canon or authority constraints."
          ]
        },
        {
          "outcome_type": "partial_success",
          "rejected_by": [
            "No bounded failure is required because the entry can be committed exactly while preserving disclosure limits."
          ]
        }
      ],
      "input_ref": "event_proposal_char_lin_scene_archive_dawn_002_001",
      "input_sha256": "ec43147f1587c964a0a3945f4bc7dcbc72aebd6ac6a250f0902788e7ad96cbf2",
      "input_type": "event_proposal",
      "outcome_summary": "Lin makes a morning-register entry identifying an after-dusk access mark as the reportable ledger irregularity, framing it as direct observation and adding no accusation or speculation.",
      "outcome_type": "success",
      "publication_candidates": [],
      "state_deltas": [
        {
          "after_summary": "The morning register now contains Lin's direct-observation entry identifying an after-dusk access mark as the relevant ledger irregularity, without accusation or speculation.",
          "based_on": [
            "world_event_scene_archive_dawn_002_001_lin_register_entry"
          ],
          "change_kind": "register_entry_committed",
          "delta_id": "world_delta_scene_archive_dawn_002_001_morning_register",
          "target_id": "scene_archive_dawn_002.morning_register_entry",
          "target_layer": "world_state_ledger"
        }
      ],
      "uncertainty_model": {
        "evidence_refs": [
          "event_proposal_char_lin_scene_archive_dawn_002_001",
          "pub_dawn_inspection_begun_002"
        ],
        "mode": "deterministic",
        "uncertainty_sources": []
      },
      "visibility_results": [
        {
          "limits": "Observers may know Lin made this register entry, but may not infer as fact Lin's private suspicion, Wei's knowledge or reaction, who moved the ledger, where the ledger is, or that the inspection outcome has changed.",
          "observer_refs": [
            "char_wei",
            "char_lin"
          ],
          "scope": "scene_public",
          "scope_ref": "scene_archive_dawn_002",
          "source_event_id": "world_event_scene_archive_dawn_002_001_lin_register_entry",
          "visibility_result_id": "world_vis_scene_archive_dawn_002_001_lin_register_entry"
        }
      ]
    },
    "authority_basis": [
      "World controls simulation flow and adjudicates consequences.",
      "Only an Authority-approved proposal may be adjudicated.",
      "World cannot choose a character's intent or action.",
      "The approved EventProposal is bound to proposal_id event_proposal_char_lin_scene_archive_dawn_002_001."
    ],
    "based_on": [
      "event_proposal_char_lin_scene_archive_dawn_002_001",
      "ec43147f1587c964a0a3945f4bc7dcbc72aebd6ac6a250f0902788e7ad96cbf2",
      "pub_dawn_inspection_001",
      "pub_dawn_inspection_begun_002",
      "world_event_scene_archive_world_001_001_wei_probe",
      "world_event_scene_archive_world_001_002_lin_response"
    ],
    "checkpoint_state": {
      "committed_beats": 1,
      "dialogue_turns": 0
    },
    "consumed_input_refs": [
      "event_proposal_char_lin_scene_archive_dawn_002_001"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": {
        "agency_question": "How does Wei respond as the dawn inspection begins and Lin is at the morning register?",
        "authority_basis": [
          "World may request Wei's next Character-owned choice because the user_request requires Wei to independently decide how to respond.",
          "Character ownership of char_wei speech, action, refusal, waiting, or procedural response in scene_archive_dawn_002."
        ],
        "message_type": "CharacterDecisionRequest",
        "request_id": "char_decision_req_scene_archive_dawn_002_wei_001",
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
        "scene_id": "scene_archive_dawn_002",
        "source_tick_id": "world_tick_scene_archive_dawn_002_001",
        "target_character_id": "char_wei",
        "visibility": "system_restricted",
        "visible_trigger_refs": [
          "observation:char_wei:first_inspection_bell",
          "observation:char_wei:lin_at_morning_register",
          "pub_dawn_inspection_001",
          "pub_dawn_inspection_begun_002"
        ]
      },
      "directive_type": "request_character_decision",
      "reason": "The user_request remains incomplete until Wei independently decides how to respond after Lin's morning-register action; World may request that choice but may not answer it."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_dawn_002",
    "tick_id": "world_tick_scene_archive_dawn_002_001",
    "tick_index": 1,
    "visibility": "system_restricted"
  }
}
```

### 7. authority / authority_world_adjudication_world_adj_scene_archive_dawn_002_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 6 |
| Input tokens | 19380 |
| Output tokens | 1498 |
| Total tokens | 20878 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "Approved EventProposal event_proposal_char_lin_scene_archive_dawn_002_001 is the adjudicated input and matches subject input_ref/input_sha256/input_type.",
      "Committed event remains causally relevant to the approved proposal: Lin makes the morning-register entry described in the approved public_surface.",
      "Adjudication preserves character authority boundaries by not choosing new Character intent and by limiting actors to registered Character id char_lin.",
      "Adjudication preserves visibility limits and does not resolve who moved the ledger, where it is, Wei's knowledge, Wei's reaction, or Lin's private suspicion as public fact.",
      "State delta is grounded in the committed event from this adjudication and publication/canon reveal candidates remain empty."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "775657272ce3ac17bab4a24604434a59158b99d321a4abd6a940796fe03a3d03",
    "review_id": "authority_review_world_adj_scene_archive_dawn_002_001_auth_001",
    "reviewed_fields": [
      "subject.adjudication_basis",
      "subject.applicable_rules",
      "subject.canon_reveal_candidates",
      "subject.committed_events",
      "subject.constraint_basis",
      "subject.failed_alternatives",
      "subject.input_ref",
      "subject.input_sha256",
      "subject.input_type",
      "subject.outcome_summary",
      "subject.outcome_type",
      "subject.publication_candidates",
      "subject.state_deltas",
      "subject.uncertainty_model",
      "subject.visibility_results",
      "source_context.approved_event_proposal",
      "source_context.authority_limits",
      "source_context.public_canon",
      "source_context.world_adjudication_contract",
      "source_context.world_state_ledger",
      "global_audit_context.public_canon",
      "global_audit_context.public_event_ledger",
      "global_audit_context.world_state_ledger"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "world_adj_scene_archive_dawn_002_001",
    "subject_sha256": "2a3bc423fca598cf6a1b80af8bbde2318b5c93f85666408146bfaf1b2ba9afbe",
    "subject_type": "world_adjudication",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 8. authority / authority_decision_request_char_decision_req_scene_archive_dawn_002_wei_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 7 |
| Input tokens | 18852 |
| Output tokens | 898 |
| Total tokens | 19750 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.directive_policy permits requesting a Character decision when completing the user_request requires a new Character-owned choice.",
      "source_context.user_request requires Wei to independently decide how to respond and preserves refusal, procedural deflection, honest uncertainty, and retreat options.",
      "source_context.character_registry includes target_character_id char_wei as available.",
      "source_context.legal_character_trigger_refs.char_wei includes every listed visible_trigger_refs item.",
      "global_audit_context.committed_world_events supports that Lin made a morning-register entry observable to char_wei and char_lin without exposing private suspicion or hidden ledger facts."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "933add8fb2528dbcf726e8ff3a74cc58a46f01bd2802f960d11c29f8d610df5d",
    "review_id": "authority_review_char_decision_req_scene_archive_dawn_002_wei_001_auth_001",
    "reviewed_fields": [
      "agency_question",
      "authority_basis",
      "response_contract",
      "target_character_id",
      "visibility",
      "visible_trigger_refs",
      "message_type",
      "request_id",
      "scene_id",
      "source_tick_id",
      "source_context.directive_policy",
      "source_context.user_request",
      "source_context.character_registry",
      "source_context.legal_character_trigger_refs.char_wei",
      "global_audit_context.committed_world_events[0].visibility"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "char_decision_req_scene_archive_dawn_002_wei_001",
    "subject_sha256": "0594be8a1677504990357ad8f7ef8dcfac4916d08d4eefcc8263134e9707ad5e",
    "subject_type": "character_decision_request",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 9. router / route_char_decision_req_scene_archive_dawn_002_wei_001

| Field | Value |
| --- | --- |
| Agent instance | `character_router` |
| Call index | 8 |
| Input tokens | 9412 |
| Output tokens | 650 |
| Total tokens | 10062 |
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
      "decision_request.request_id",
      "decision_request.target_character_id",
      "decision_request.visibility",
      "decision_request_sha256"
    ],
    "message_type": "RoutePlan",
    "projection_profile": "character_private_owner_view",
    "reason": "decision_request.target_character_id matches registered available recipient char_wei",
    "recipient_agent_id": "char_wei",
    "request_id": "char_decision_req_scene_archive_dawn_002_wei_001",
    "request_sha256": "0594be8a1677504990357ad8f7ef8dcfac4916d08d4eefcc8263134e9707ad5e",
    "route_id": "route_char_decision_req_scene_archive_dawn_002_wei_001_to_char_wei",
    "visibility": "system_restricted"
  }
}
```

### 10. character / character_decision_char_decision_req_scene_archive_dawn_002_wei_001

| Field | Value |
| --- | --- |
| Agent instance | `char_wei` |
| Call index | 9 |
| Input tokens | 10597 |
| Output tokens | 949 |
| Total tokens | 11546 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "event_proposal": {
    "action_type": "speech",
    "actor_id": "char_wei",
    "authority_basis": [
      "World may request Wei's next Character-owned choice because the user_request requires Wei to independently decide how to respond.",
      "Character ownership of char_wei speech, action, refusal, waiting, or procedural response in scene_archive_dawn_002."
    ],
    "based_on": [
      "observation:char_wei:first_inspection_bell",
      "observation:char_wei:lin_at_morning_register",
      "pub_dawn_inspection_001",
      "pub_dawn_inspection_begun_002",
      "world_event_scene_archive_dawn_002_001_lin_register_entry",
      "md_wei_secret_001",
      "md_char_wei_world_event_scene_archive_world_001_002_lin_response"
    ],
    "desired_effect": "Wei requests that the exchange frame the irregularity in terms of register procedure and direct observation, without exposing his private knowledge or lack of knowledge about the ledger's location.",
    "disclosure_limits": [
      "Do not narrate whether Wei knows the ledger location.",
      "Do not treat Wei's guidance as proof of the ledger's actual state or location.",
      "Do not infer Lin's reaction or understanding from this proposal."
    ],
    "intent_summary": "Wei intends to keep the inspection response procedural and narrow, steering attention toward what can be entered as direct observation while avoiding any implication that he knows where the ledger is.",
    "interiority_grant": {
      "access_mode": "none",
      "grant_status": "none",
      "scope_limit": "none",
      "source_field": "none"
    },
    "message_type": "EventProposal",
    "private_intent": "Wei wants Lin's entry to remain defensible under inspection and wants to avoid revealing whether he has knowledge of the ledger's location.",
    "proposal_id": "event_proposal_scene_archive_dawn_002_wei_001",
    "public_surface": "Wei says, \"Write only what the page proves. If they ask after the volume itself, answer from the register: observed absence is one matter, suspicion another.\"",
    "request_id": "char_decision_req_scene_archive_dawn_002_wei_001",
    "scene_id": "scene_archive_dawn_002",
    "visibility": "system_restricted",
    "visibility_request": "system_restricted"
  }
}
```

### 11. authority / authority_event_proposal_event_proposal_scene_archive_dawn_002_wei_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 10 |
| Input tokens | 15638 |
| Output tokens | 3482 |
| Total tokens | 19120 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "subject.actor_id matches the requested target character for the decision request.",
      "subject.action_type is speech and covers the externally observable act in subject.public_surface without bundling a separate physical act.",
      "subject.based_on references are grounded in the projected visible observations, public events, visible committed event, or Wei-owned memory records.",
      "subject.desired_effect remains a requested effect and does not commit an objective outcome, another character's mind, or hidden world truth.",
      "subject.disclosure_limits and subject.visibility_request preserve system-restricted handling of private intent and hidden-knowledge boundaries."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "ffacfe9cf8518cbb08b2765212de9d90f5465071ea05491bdd1614c0f5b63fa6",
    "review_id": "authority_review_event_proposal_scene_archive_dawn_002_wei_001_auth_001",
    "reviewed_fields": [
      "subject.action_type",
      "subject.actor_id",
      "subject.authority_basis",
      "subject.based_on",
      "subject.desired_effect",
      "subject.disclosure_limits",
      "subject.intent_summary",
      "subject.interiority_grant",
      "subject.message_type",
      "subject.private_intent",
      "subject.proposal_id",
      "subject.public_surface",
      "subject.request_id",
      "subject.scene_id",
      "subject.visibility",
      "subject.visibility_request"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "event_proposal_scene_archive_dawn_002_wei_001",
    "subject_sha256": "f482b9bb34e845341cbae0784ed42e30186a7217a86bc491f52a3c3cc65504ef",
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
| Input tokens | 15393 |
| Output tokens | 2792 |
| Total tokens | 18185 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": {
      "adjudication_basis": "The approved proposal is a Character-owned speech action by a registered actor in the active scene. The observable wording can be committed without adding private intent, hidden ledger facts, or Lin's reaction. The response completes the user-requested requirement that Wei independently decide how to respond after Lin's register entry.",
      "adjudication_id": "world_adj_scene_archive_dawn_002_002",
      "applicable_rules": [
        "World may adjudicate Authority-approved proposals only.",
        "World may not decide Character will beyond the approved proposal.",
        "Speech proposals commit observable speech and matching spoken_line_records.",
        "CommittedWorldEvent actors must be registered Character ids.",
        "Do not resolve who moved the ledger or where it is."
      ],
      "canon_reveal_candidates": [],
      "committed_events": [
        {
          "actors": [
            "char_wei"
          ],
          "authorized_interiority": [],
          "causal_basis": [
            "event_proposal_scene_archive_dawn_002_wei_001",
            "world_adj_scene_archive_dawn_002_002"
          ],
          "commit_status": "committed",
          "event_id": "world_event_scene_archive_dawn_002_002_wei_response",
          "event_kind": "speech",
          "message_type": "CommittedWorldEvent",
          "outcome": "Wei gives Lin procedural guidance to write only what the page proves and to distinguish observed absence from suspicion if asked about the volume itself.",
          "public_surface": "Wei says, \"Write only what the page proves. If they ask after the volume itself, answer from the register: observed absence is one matter, suspicion another.\"",
          "scene_id": "scene_archive_dawn_002",
          "source_input_ref": "event_proposal_scene_archive_dawn_002_wei_001",
          "source_input_type": "event_proposal",
          "spoken_line_records": [
            {
              "semantic_content": "Wei says, \"Write only what the page proves. If they ask after the volume itself, answer from the register: observed absence is one matter, suspicion another.\"",
              "source_field": "public_surface",
              "source_proposal_id": "event_proposal_scene_archive_dawn_002_wei_001",
              "source_sha256": "c3a08f5538b3695517802200c1a9a823d961fdb243c27ae3ae6aa151be87a9a5",
              "speaker_id": "char_wei",
              "status": "paraphrased"
            }
          ],
          "visibility": {
            "limits": "Observers may know Wei gave this procedural guidance, but may not infer as fact whether Wei knows the ledger location, who moved the ledger, where the ledger is, Lin's private reaction, or that suspicion has been proven.",
            "observer_refs": [
              "char_wei",
              "char_lin"
            ],
            "scope": "scene_pair",
            "scope_ref": "scene_archive_dawn_002"
          }
        }
      ],
      "constraint_basis": [
        "Original proposal approval binds the immutable proposal_id event_proposal_scene_archive_dawn_002_wei_001.",
        "Interiority grant status is none, so authorized_interiority is empty.",
        "Disclosure limits prohibit treating Wei's guidance as proof of ledger state, location, or Wei's knowledge.",
        "Visibility observers are limited to registered scene Character ids."
      ],
      "failed_alternatives": [],
      "input_ref": "event_proposal_scene_archive_dawn_002_wei_001",
      "input_sha256": "f482b9bb34e845341cbae0784ed42e30186a7217a86bc491f52a3c3cc65504ef",
      "input_type": "event_proposal",
      "outcome_summary": "Wei's approved speech is committed as a procedural response to Lin's morning-register entry, without establishing the ledger's location, who moved it, or Wei's private knowledge.",
      "outcome_type": "success",
      "publication_candidates": [],
      "state_deltas": [
        {
          "after_summary": "Wei has responded to Lin's morning-register entry with procedural guidance; the requested Lin-entry and Wei-response exchange at the beginning of the dawn inspection is complete.",
          "based_on": [
            "world_event_scene_archive_dawn_002_002_wei_response"
          ],
          "change_kind": "dialogue_turn_committed",
          "delta_id": "world_delta_scene_archive_dawn_002_002_exchange_state",
          "target_id": "scene_archive_dawn_002.exchange_state",
          "target_layer": "world_state_ledger"
        }
      ],
      "uncertainty_model": {
        "evidence_refs": [
          "event_proposal_scene_archive_dawn_002_wei_001"
        ],
        "mode": "deterministic",
        "uncertainty_sources": []
      },
      "visibility_results": [
        {
          "limits": "Observers may know Wei gave this procedural guidance, but may not infer as fact whether Wei knows the ledger location, who moved the ledger, where the ledger is, Lin's private reaction, or that suspicion has been proven.",
          "observer_refs": [
            "char_wei",
            "char_lin"
          ],
          "scope": "scene_pair",
          "scope_ref": "scene_archive_dawn_002",
          "source_event_id": "world_event_scene_archive_dawn_002_002_wei_response",
          "visibility_result_id": "world_visibility_scene_archive_dawn_002_002_wei_response"
        }
      ]
    },
    "authority_basis": [
      "World controls simulation flow and adjudicates consequences of approved inputs.",
      "Only an Authority-approved proposal may be adjudicated.",
      "World cannot choose character intent or action beyond the approved Character proposal.",
      "The current adjudication satisfies the user_request, so World uses finish_scene rather than requesting another Character decision."
    ],
    "based_on": [
      "event_proposal_scene_archive_dawn_002_wei_001",
      "world_event_scene_archive_dawn_002_001_lin_register_entry",
      "pub_dawn_inspection_001",
      "pub_dawn_inspection_begun_002"
    ],
    "checkpoint_state": {
      "committed_beats": 2,
      "dialogue_turns": 1
    },
    "consumed_input_refs": [
      "event_proposal_scene_archive_dawn_002_wei_001"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": null,
      "directive_type": "finish_scene",
      "reason": "Lin has independently decided whether and how to enter the irregularity in the morning register, and Wei has independently responded; no further Character-owned choice is required to satisfy the user_request."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_dawn_002",
    "tick_id": "world_tick_scene_archive_dawn_002_002",
    "tick_index": 2,
    "visibility": "system_restricted"
  }
}
```

### 13. authority / authority_world_adjudication_world_adj_scene_archive_dawn_002_002

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 12 |
| Input tokens | 20779 |
| Output tokens | 2032 |
| Total tokens | 22811 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "Approved proposal event_proposal_scene_archive_dawn_002_wei_001 authorizes a char_wei speech action in scene_archive_dawn_002.",
      "Committed event public_surface matches the approved proposal's observable speech and does not add physical action.",
      "Adjudication preserves unresolved ledger location, mover identity, Wei knowledge, and Lin private reaction as non-inferable facts.",
      "State delta is causally based on the committed Wei response and records only completion of the requested exchange."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "e770524c0d553693902d5c46bcba97414ddc649ae3719d5ce97ea455b9b40b31",
    "review_id": "authority_review_world_adj_scene_archive_dawn_002_002_auth_001",
    "reviewed_fields": [
      "adjudication_basis",
      "applicable_rules",
      "canon_reveal_candidates",
      "committed_events",
      "committed_events[0].actors",
      "committed_events[0].authorized_interiority",
      "committed_events[0].causal_basis",
      "committed_events[0].commit_status",
      "committed_events[0].event_id",
      "committed_events[0].event_kind",
      "committed_events[0].outcome",
      "committed_events[0].public_surface",
      "committed_events[0].scene_id",
      "committed_events[0].source_input_ref",
      "committed_events[0].source_input_type",
      "committed_events[0].spoken_line_records",
      "committed_events[0].visibility",
      "constraint_basis",
      "failed_alternatives",
      "input_ref",
      "input_sha256",
      "input_type",
      "outcome_summary",
      "outcome_type",
      "publication_candidates",
      "state_deltas",
      "state_deltas[0].based_on",
      "uncertainty_model",
      "visibility_results",
      "visibility_results[0].source_event_id"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "world_adj_scene_archive_dawn_002_002",
    "subject_sha256": "15caef1ef508953c0177219457b01e4b05d9d71c6e68e812db94220176314ce5",
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
| Input tokens | 10547 |
| Output tokens | 1363 |
| Total tokens | 11910 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "plot_pulse": {
    "affected_options": [
      {
        "character": "char_lin",
        "option": "record only the visible irregularity",
        "pressure_effect": "The inspection's beginning makes neutral wording carry institutional weight, so a strictly observed entry remains available but feels exposed to procedural scrutiny."
      },
      {
        "character": "char_lin",
        "option": "defer the entry pending inspection",
        "pressure_effect": "Deferral remains possible, but the sounded bell makes delay visibly procedural rather than private, raising the cost of appearing uncertain."
      },
      {
        "character": "char_lin",
        "option": "ask Wei for a procedural co-signature",
        "pressure_effect": "A co-signature can distribute procedure without requiring accusation, while the register's direct-observation framing makes any shared wording harder to treat as casual."
      },
      {
        "character": "char_lin",
        "option": "refuse to accuse without proof",
        "pressure_effect": "Refusal remains a coherent boundary, with the added strain that institutional attention may read restraint as a choice needing maintenance."
      },
      {
        "character": "char_wei",
        "option": "answer only the procedural question",
        "pressure_effect": "A narrow procedural answer can avoid hidden knowledge, but the active inspection makes even limited cooperation feel consequential."
      },
      {
        "character": "char_wei",
        "option": "offer a bounded observation",
        "pressure_effect": "A bounded observation can help clarify process without confession or accusation, while risking extra attention to what Wei chooses not to address."
      },
      {
        "character": "char_wei",
        "option": "decline to co-sign",
        "pressure_effect": "Declining remains available as self-protection, but the register context makes refusal professionally legible rather than invisible."
      },
      {
        "character": "char_wei",
        "option": "retreat without confession",
        "pressure_effect": "Retreat preserves agency and avoids disclosure, while leaving the institutional pressure around Lin's entry unresolved."
      }
    ],
    "authority_basis": [
      "Public canon allows morning-register entries to distinguish direct observation from suspicion.",
      "Public event ledger establishes that the first inspection bell has sounded and the dawn inspection is beginning.",
      "Committed public event surface establishes Lin's register entry as a direct observation of an access mark after dusk, without accusation or speculation.",
      "Relationship summary supports strained professional coordination without deciding either character's response."
    ],
    "based_on": [
      "Archive ledgers are sealed after dusk.",
      "Morning-register entries may distinguish direct observation from suspicion.",
      "The first inspection bell has sounded and the royal archive's dawn inspection is beginning.",
      "Lin writes in the morning register that the relevant ledger irregularity is an access mark indicating use after dusk, marking it as direct observation and adding no accusation or speculation.",
      "char_wei__char_lin: strained professional coordination after a private, inconclusive exchange over an irregular archive entry",
      "Structure goal: Test whether committed dialogue, owner-specific memory, and deferred institutional pressure survive into a second scene without hidden-knowledge leakage or forced convergence."
    ],
    "budget_cost": {
      "agency_risk": "low",
      "intensity": "medium",
      "novelty": "low",
      "relief_available": true,
      "stacking_count": 2
    },
    "duration": "next_two_beats",
    "forbidden_outcomes": [
      "Do not establish what caused the archive disturbance.",
      "Do not establish whether any ledger is missing in this scene.",
      "Do not imply Wei knows more than the public or relationship context supports.",
      "Do not force Lin to accuse, recant, or revise the register entry.",
      "Do not force Wei to co-sign, confess, contradict Lin, or remain present.",
      "Do not declare the result of the dawn inspection.",
      "Do not convert refusal, deferral, procedural caution, or retreat into failure states."
    ],
    "message_type": "PlotPulse",
    "non_forcing_clause": "Lin may maintain neutral observation, defer, seek a procedural co-signature, or refuse accusation without proof; Wei may answer narrowly, offer a bounded observation, decline to co-sign, or retreat. No path requires accusation, confession, discovery, hidden knowledge, or resolution of the archive disturbance.",
    "option_topology_check": {
      "converges_on_single_outcome": false,
      "meaningful_option_count_after": 8,
      "meaningful_option_count_before": 8,
      "non_plot_compliant_path_preserved": true,
      "refusal_path_preserved": true
    },
    "pressure_kind": "institutional_constraint",
    "pulse_id": "pulse_archive_dawn_register_visibility_002",
    "scene_id": "scene_archive_dawn_002",
    "scope": "scene",
    "visibility": "system_restricted",
    "world_fact_dependency": []
  }
}
```

### 15. authority / authority_plot_pulse_pulse_archive_dawn_register_visibility_002

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 14 |
| Input tokens | 16807 |
| Output tokens | 948 |
| Total tokens | 17755 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "Subject grounds institutional pressure in public canon, public event ledger, committed public event surface, and public relationship summary available in source_context.",
      "Subject preserves multiple Lin and Wei options, including refusal, deferral, procedural caution, co-signature, bounded response, declined co-signature, and retreat.",
      "Subject forbids causal resolution, hidden-knowledge assertions, forced convergence, confession, accusation, inspection outcome declaration, and failure-state conversion.",
      "Subject world_fact_dependency is empty and does not require an untranslated new world fact."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "b52cb0a6cd0862290866008039723b31a7ceb2442cd6892af726eb2c5c2bf1a8",
    "review_id": "authority_review_plot_pulse_archive_dawn_register_visibility_002_auth_001",
    "reviewed_fields": [
      "subject.affected_options",
      "subject.authority_basis",
      "subject.based_on",
      "subject.budget_cost",
      "subject.duration",
      "subject.forbidden_outcomes",
      "subject.message_type",
      "subject.non_forcing_clause",
      "subject.option_topology_check",
      "subject.pressure_kind",
      "subject.pulse_id",
      "subject.scene_id",
      "subject.scope",
      "subject.visibility",
      "subject.world_fact_dependency",
      "source_context.public_canon",
      "source_context.public_event_ledger",
      "source_context.committed_public_event_surfaces",
      "source_context.public_relationship_summary",
      "source_context.option_topology",
      "source_context.pressure_ledger",
      "source_context.authority_limits",
      "global_audit_context.committed_world_events",
      "global_audit_context.public_canon",
      "global_audit_context.public_event_ledger"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "pulse_archive_dawn_register_visibility_002",
    "subject_sha256": "048abdad92b0d8fd937f97490553c6d0704332949369e9f921ac3b5b39a7f13f",
    "subject_type": "plot_pulse",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 16. narrator / narration_ncp_world_driven_dawn_inspection_followup_2

| Field | Value |
| --- | --- |
| Agent instance | `narrator_checkpoint` |
| Call index | 15 |
| Input tokens | 9434 |
| Output tokens | 573 |
| Total tokens | 10007 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "prose": "Lin entered the irregularity in the morning register: an access mark indicating use after dusk. He marked it as direct observation and added no accusation or speculation. Wei responded by telling him to write only what the page proved and, if asked about the volume itself, to answer from the register: observed absence was one matter, suspicion another."
}
```

### 17. authority / authority_narration_ncp_world_driven_dawn_inspection_followup_2

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 16 |
| Input tokens | 15319 |
| Output tokens | 1152 |
| Total tokens | 16471 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.narration_checkpoint.event_views",
      "source_context.narration_checkpoint.source_event_refs",
      "global_audit_context.committed_world_events"
    ],
    "claim_map": [
      {
        "certainty": "medium",
        "claim_id": "ncp_world_driven_dawn_inspection_followup_2:claim:0",
        "claim_sha256": "121c42050004157f45110e9bd8ad395f6138811e89c52e3ea799fc90d8b46913",
        "claim_text": "Lin entered the irregularity in the morning register: an access mark indicating use after dusk.",
        "claim_type": "event",
        "grounding_status": "supported",
        "source_refs": [
          "world_event_scene_archive_dawn_002_001_lin_register_entry"
        ],
        "visibility_scope": "scene_public"
      },
      {
        "certainty": "medium",
        "claim_id": "ncp_world_driven_dawn_inspection_followup_2:claim:1",
        "claim_sha256": "2f777d70b44fd50ba831b7e6e6c480c507be749f6454818b028f0d2ea1785755",
        "claim_text": "He marked it as direct observation and added no accusation or speculation.",
        "claim_type": "event",
        "grounding_status": "supported",
        "source_refs": [
          "world_event_scene_archive_dawn_002_001_lin_register_entry"
        ],
        "visibility_scope": "scene_public"
      },
      {
        "certainty": "medium",
        "claim_id": "ncp_world_driven_dawn_inspection_followup_2:claim:2",
        "claim_sha256": "b1d9ff3a8896ca32a747e8bdb0a4e764837458bd2f1457f6e04a61b20eef335e",
        "claim_text": "Wei responded by telling him to write only what the page proved and, if asked about the volume itself, to answer from the register: observed absence was one matter, suspicion another.",
        "claim_type": "dialogue",
        "grounding_status": "supported",
        "source_refs": [
          "world_event_scene_archive_dawn_002_002_wei_response"
        ],
        "visibility_scope": "scene_pair"
      }
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "63378f9cef9d9fd2d67a523dc11b9ac05d72828974f992d44f11a37e408ae76d",
    "review_id": "authority_review_narration_ncp_world_driven_dawn_inspection_followup_2_auth_001",
    "reviewed_fields": [
      "subject.claim_units",
      "subject.prose",
      "subject.source_checkpoint_id",
      "subject.source_event_refs"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "ncp_world_driven_dawn_inspection_followup_2",
    "subject_sha256": "6bea63c0865bd6760588070b3737b86f84c267a2a81b1e9258c68e48f48f4dd4",
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
| Input tokens | 16325 |
| Output tokens | 980 |
| Total tokens | 17305 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": null,
    "authority_basis": [
      "World may bind an ApprovedPlotPulse to existing world conditions when no new objective fact or state change is needed.",
      "World may finish the scene when the current committed exchange fulfills the user_request and no required Character decision remains."
    ],
    "based_on": [
      "The first inspection bell has sounded and the royal archive's dawn inspection is beginning.",
      "Lin writes in the morning register that the relevant ledger irregularity is an access mark indicating use after dusk, marking it as direct observation and adding no accusation or speculation.",
      "Wei says, \"Write only what the page proves. If they ask after the volume itself, answer from the register: observed absence is one matter, suspicion another.\"",
      "The requested Lin-entry and Wei-response exchange at the beginning of the dawn inspection is complete."
    ],
    "checkpoint_state": {
      "committed_beats": 2,
      "dialogue_turns": 1
    },
    "consumed_input_refs": [
      "pulse_archive_dawn_register_visibility_002"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": null,
      "directive_type": "finish_scene",
      "reason": "The required Lin register decision and Wei response have both been independently committed, and the approved plot pulse is satisfied by existing conditions without requiring another character-owned choice."
    },
    "plot_pulse_disposition": {
      "decision": "accepted",
      "pulse_id": "pulse_archive_dawn_register_visibility_002",
      "pulse_sha256": "048abdad92b0d8fd937f97490553c6d0704332949369e9f921ac3b5b39a7f13f",
      "translation_summary": "The institutional pressure is bound to already committed conditions: the dawn inspection has begun, Lin has entered the irregularity as direct observation without accusation, and Wei has answered with bounded procedural guidance. No new objective event or state delta is created.",
      "world_condition_refs": [
        "pub_dawn_inspection_begun_002",
        "world_event_scene_archive_dawn_002_001_lin_register_entry",
        "world_event_scene_archive_dawn_002_002_wei_response",
        "world_delta_scene_archive_dawn_002_002_exchange_state"
      ]
    },
    "scene_id": "scene_archive_dawn_002",
    "tick_id": "world_tick_scene_archive_dawn_002_003",
    "tick_index": 3,
    "visibility": "system_restricted"
  }
}
```

### 19. authority / authority_plot_disposition_pulse_archive_dawn_register_visibility_002

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 18 |
| Input tokens | 21191 |
| Output tokens | 824 |
| Total tokens | 22015 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.plot_pulse_translation_policy permits accepted pressure without new adjudication when world_condition_refs cite existing_world_condition_refs and no new fact or state change is created.",
      "source_context.existing_world_condition_refs contains all cited world_condition_refs.",
      "source_context.committed_world_events and source_context.public_event_ledger ground the translation_summary without adding hidden knowledge, forced character choice, or inspection outcome."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "0251dfc74d42cae6473ff7435d1690822107f929f83be22f63b538977eae2349",
    "review_id": "authority_review_plot_pulse_archive_dawn_register_visibility_002_auth_003",
    "reviewed_fields": [
      "decision",
      "pulse_id",
      "pulse_sha256",
      "translation_summary",
      "world_condition_refs",
      "source_context.plot_pulse_translation_policy",
      "source_context.existing_world_condition_refs",
      "source_context.committed_world_events",
      "source_context.public_event_ledger"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "pulse_archive_dawn_register_visibility_002",
    "subject_sha256": "47c20227001eb8197694c21dfe0708db3d46dbc97ca5b9dcf57a209a72895133",
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
    "world_event_scene_archive_dawn_002_001_lin_register_entry",
    "world_event_scene_archive_dawn_002_002_wei_response"
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
        "claim_id": "ncp_world_driven_dawn_inspection_followup_2:claim:0",
        "claim_sha256": "121c42050004157f45110e9bd8ad395f6138811e89c52e3ea799fc90d8b46913",
        "claim_text": "Lin entered the irregularity in the morning register: an access mark indicating use after dusk.",
        "end": 95,
        "start": 0
      },
      {
        "claim_id": "ncp_world_driven_dawn_inspection_followup_2:claim:1",
        "claim_sha256": "2f777d70b44fd50ba831b7e6e6c480c507be749f6454818b028f0d2ea1785755",
        "claim_text": "He marked it as direct observation and added no accusation or speculation.",
        "end": 170,
        "start": 96
      },
      {
        "claim_id": "ncp_world_driven_dawn_inspection_followup_2:claim:2",
        "claim_sha256": "b1d9ff3a8896ca32a747e8bdb0a4e764837458bd2f1457f6e04a61b20eef335e",
        "claim_text": "Wei responded by telling him to write only what the page proved and, if asked about the volume itself, to answer from the register: observed absence was one matter, suspicion another.",
        "end": 354,
        "start": 171
      }
    ],
    "prose": "Lin entered the irregularity in the morning register: an access mark indicating use after dusk. He marked it as direct observation and added no accusation or speculation. Wei responded by telling him to write only what the page proved and, if asked about the volume itself, to answer from the register: observed absence was one matter, suspicion another.",
    "source_checkpoint_id": "ncp_world_driven_dawn_inspection_followup_2",
    "source_event_refs": [
      "world_event_scene_archive_dawn_002_001_lin_register_entry",
      "world_event_scene_archive_dawn_002_002_wei_response"
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
      "the inspection proved",
      "everyone knew"
    ],
    "must_not_claim": [
      "Wei stole or moved the ledger.",
      "Lin knows Wei is guilty.",
      "The inspection proves either character guilty or innocent.",
      "A deferred Plot pressure is already an objective world fact."
    ],
    "must_preserve": [
      "The second scene follows the committed private exchange.",
      "Lin and Wei each retain an independent choice.",
      "No one obtains proof of who moved the ledger.",
      "The ledger location remains unresolved."
    ]
  },
  "packet_id": "sp_world_driven_dawn_inspection_followup_[redacted-run-id]",
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
        "char_lin"
      ],
      "authorized_interiority": [],
      "causal_basis": [
        "event_proposal_char_lin_scene_archive_dawn_002_001",
        "world_adj_scene_archive_dawn_002_001"
      ],
      "commit_status": "committed",
      "event_id": "world_event_scene_archive_dawn_002_001_lin_register_entry",
      "event_kind": "physical",
      "message_type": "CommittedWorldEvent",
      "outcome": "Lin's morning-register entry records the after-dusk access mark as the relevant irregularity by direct observation, without adding accusation or speculation.",
      "public_surface": "Lin writes in the morning register that the relevant ledger irregularity is an access mark indicating use after dusk, marking it as direct observation and adding no accusation or speculation.",
      "scene_id": "scene_archive_dawn_002",
      "source_input_ref": "event_proposal_char_lin_scene_archive_dawn_002_001",
      "source_input_type": "event_proposal",
      "spoken_line_records": [],
      "visibility": {
        "limits": "Observers may know Lin made this register entry, but may not infer as fact Lin's private suspicion, Wei's knowledge or reaction, who moved the ledger, where the ledger is, or that the inspection outcome has changed.",
        "observer_refs": [
          "char_wei",
          "char_lin"
        ],
        "scope": "scene_public",
        "scope_ref": "scene_archive_dawn_002"
      }
    },
    {
      "actors": [
        "char_wei"
      ],
      "authorized_interiority": [],
      "causal_basis": [
        "event_proposal_scene_archive_dawn_002_wei_001",
        "world_adj_scene_archive_dawn_002_002"
      ],
      "commit_status": "committed",
      "event_id": "world_event_scene_archive_dawn_002_002_wei_response",
      "event_kind": "speech",
      "message_type": "CommittedWorldEvent",
      "outcome": "Wei gives Lin procedural guidance to write only what the page proves and to distinguish observed absence from suspicion if asked about the volume itself.",
      "public_surface": "Wei says, \"Write only what the page proves. If they ask after the volume itself, answer from the register: observed absence is one matter, suspicion another.\"",
      "scene_id": "scene_archive_dawn_002",
      "source_input_ref": "event_proposal_scene_archive_dawn_002_wei_001",
      "source_input_type": "event_proposal",
      "spoken_line_records": [
        {
          "semantic_content": "Wei says, \"Write only what the page proves. If they ask after the volume itself, answer from the register: observed absence is one matter, suspicion another.\"",
          "source_field": "public_surface",
          "source_proposal_id": "event_proposal_scene_archive_dawn_002_wei_001",
          "source_sha256": "c3a08f5538b3695517802200c1a9a823d961fdb243c27ae3ae6aa151be87a9a5",
          "speaker_id": "char_wei",
          "status": "paraphrased"
        }
      ],
      "visibility": {
        "limits": "Observers may know Wei gave this procedural guidance, but may not infer as fact whether Wei knows the ledger location, who moved the ledger, where the ledger is, Lin's private reaction, or that suspicion has been proven.",
        "observer_refs": [
          "char_wei",
          "char_lin"
        ],
        "scope": "scene_pair",
        "scope_ref": "scene_archive_dawn_002"
      }
    }
  ],
  "scene_id": "scene_archive_dawn_002",
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
        "world_event_scene_archive_dawn_002_001_lin_register_entry",
        "world_event_scene_archive_dawn_002_002_wei_response"
      ],
      "state_deltas": [
        "world_delta_scene_archive_dawn_002_001_morning_register",
        "world_delta_scene_archive_dawn_002_002_exchange_state"
      ],
      "visibility_deltas": [
        "world_vis_scene_archive_dawn_002_001_lin_register_entry",
        "world_visibility_scene_archive_dawn_002_002_wei_response"
      ]
    },
    "seal_scope": "sanitized_public_export",
    "sealed_by": "runtime_kernel",
    "sealed_payload_sha256": "d6947249b3713d59ed0401dc26a3a247bcbf5fcd04d859c2b6fa402d4ad7a27f",
    "source_adjudication_refs": [
      "world_adj_scene_archive_dawn_002_001",
      "world_adj_scene_archive_dawn_002_002"
    ],
    "source_collection_sha256": {
      "canon_reveal_candidates": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
      "publication_candidates": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
      "resolved_events": "ae36da941d5a102b3fc6c662e75b84d2f6a8bc6ae2c7d8fc8f7a63cce0346ad2",
      "state_deltas": "d3a820a680aea0d3162eabadcc9ecf788326cc0fc5fda2187431c5dc0469499d",
      "visibility_deltas": "d28d5eb38dc951b2d43fca4db3e18b8345f8035d697bc5d3d9011f2ac50e1a83"
    },
    "source_private_seal_verified": true
  },
  "state_deltas": [
    {
      "after_summary": "The morning register now contains Lin's direct-observation entry identifying an after-dusk access mark as the relevant ledger irregularity, without accusation or speculation.",
      "based_on": [
        "world_event_scene_archive_dawn_002_001_lin_register_entry"
      ],
      "change_kind": "register_entry_committed",
      "delta_id": "world_delta_scene_archive_dawn_002_001_morning_register",
      "target_id": "scene_archive_dawn_002.morning_register_entry",
      "target_layer": "world_state_ledger"
    },
    {
      "after_summary": "Wei has responded to Lin's morning-register entry with procedural guidance; the requested Lin-entry and Wei-response exchange at the beginning of the dawn inspection is complete.",
      "based_on": [
        "world_event_scene_archive_dawn_002_002_wei_response"
      ],
      "change_kind": "dialogue_turn_committed",
      "delta_id": "world_delta_scene_archive_dawn_002_002_exchange_state",
      "target_id": "scene_archive_dawn_002.exchange_state",
      "target_layer": "world_state_ledger"
    }
  ],
  "visibility_deltas": [
    {
      "limits": "Observers may know Lin made this register entry, but may not infer as fact Lin's private suspicion, Wei's knowledge or reaction, who moved the ledger, where the ledger is, or that the inspection outcome has changed.",
      "observer_refs": [
        "char_wei",
        "char_lin"
      ],
      "scope": "scene_public",
      "scope_ref": "scene_archive_dawn_002",
      "source_event_id": "world_event_scene_archive_dawn_002_001_lin_register_entry",
      "visibility_result_id": "world_vis_scene_archive_dawn_002_001_lin_register_entry"
    },
    {
      "limits": "Observers may know Wei gave this procedural guidance, but may not infer as fact whether Wei knows the ledger location, who moved the ledger, where the ledger is, Lin's private reaction, or that suspicion has been proven.",
      "observer_refs": [
        "char_wei",
        "char_lin"
      ],
      "scope": "scene_pair",
      "scope_ref": "scene_archive_dawn_002",
      "source_event_id": "world_event_scene_archive_dawn_002_002_wei_response",
      "visibility_result_id": "world_visibility_scene_archive_dawn_002_002_wei_response"
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
        "world_event_scene_archive_dawn_002_001_lin_register_entry"
      ],
      "certainty": "medium",
      "content": "Lin writes in the morning register that the relevant ledger irregularity is an access mark indicating use after dusk, marking it as direct observation and adding no accusation or speculation.",
      "delta_id": "md_char_lin_world_event_scene_archive_dawn_002_001_lin_register_entry",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_lin",
      "source_event_id": "world_event_scene_archive_dawn_002_001_lin_register_entry",
      "source_packet_id": "sp_world_driven_dawn_inspection_followup_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "world_event_scene_archive_dawn_002_002_wei_response"
      ],
      "certainty": "medium",
      "content": "Wei says, \"Write only what the page proves. If they ask after the volume itself, answer from the register: observed absence is one matter, suspicion another.\"",
      "delta_id": "md_char_lin_world_event_scene_archive_dawn_002_002_wei_response",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_lin",
      "source_event_id": "world_event_scene_archive_dawn_002_002_wei_response",
      "source_packet_id": "sp_world_driven_dawn_inspection_followup_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "world_event_scene_archive_dawn_002_001_lin_register_entry"
      ],
      "certainty": "medium",
      "content": "Lin writes in the morning register that the relevant ledger irregularity is an access mark indicating use after dusk, marking it as direct observation and adding no accusation or speculation.",
      "delta_id": "md_char_wei_world_event_scene_archive_dawn_002_001_lin_register_entry",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_wei",
      "source_event_id": "world_event_scene_archive_dawn_002_001_lin_register_entry",
      "source_packet_id": "sp_world_driven_dawn_inspection_followup_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "world_event_scene_archive_dawn_002_002_wei_response"
      ],
      "certainty": "medium",
      "content": "Wei says, \"Write only what the page proves. If they ask after the volume itself, answer from the register: observed absence is one matter, suspicion another.\"",
      "delta_id": "md_char_wei_world_event_scene_archive_dawn_002_002_wei_response",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_wei",
      "source_event_id": "world_event_scene_archive_dawn_002_002_wei_response",
      "source_packet_id": "sp_world_driven_dawn_inspection_followup_[redacted-run-id]",
      "writer_role": "world_agent"
    }
  ],
  "owner_projections": [
    {
      "owner_agent_id": "char_lin",
      "visible_event_refs": [
        "world_event_scene_archive_dawn_002_001_lin_register_entry",
        "world_event_scene_archive_dawn_002_002_wei_response"
      ]
    },
    {
      "owner_agent_id": "char_wei",
      "visible_event_refs": [
        "world_event_scene_archive_dawn_002_001_lin_register_entry",
        "world_event_scene_archive_dawn_002_002_wei_response"
      ]
    }
  ]
}
```

### Audited Normalizations

```json
[
  {
    "after": 1,
    "before": 2,
    "code": "normalized_plot_stacking_count",
    "field_path": "plot_pulse.budget_cost.stacking_count",
    "message": "Normalized recoverable PlotPulse stacking_count from the authoritative pressure ledger.",
    "policy": "recoverable_derived_audit_metadata_v0.1"
  }
]
```

## Export Boundary

This artifact is evidence of one bounded run, not a claim that every future model output will pass. The executable fixtures, validators, Authority Judge gates, and scene-atomic transaction remain the actual enforcement surface. Candidate expiry aging and persistent cross-scene ledgers are not implemented in v0.2.
