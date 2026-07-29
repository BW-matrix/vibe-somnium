# Two-Scene Continuity Study v0.3: Scene 1 Public Trace

> This is a sanitized public export of one real isolated Codex CLI run. It preserves every model-agent's parsed output and token accounting while deliberately excluding prompts, projected context payloads, raw provider JSONL, local paths, private run identifiers, and authentication state.

## Run Summary

| Field | Value |
| --- | --- |
| Fixture | `scene_one.materialized.json` |
| Runtime | `world_driven` |
| Provider mode | `codex-cli` |
| Model | `gpt-5.5` |
| Runtime status | `finished` |
| Final decision | `allowed` |
| Transaction | `committed` |
| Model calls | 19 |
| Projection manifests | 19 |
| Input tokens | 243205 |
| Output tokens | 23028 |
| Total tokens | 266233 |
| Exact token records | 19 |
| Estimated token records | 0 |

The provider reported exact usage for every call. Output counts include provider-reported reasoning tokens where the backend reports them that way; the runtime therefore validates the returned provider count rather than assuming visible JSON length equals billed output.

## Per-Agent Token Totals

| Agent | Calls | Input | Output | Total |
| --- | ---: | ---: | ---: | ---: |
| `authority` | 9 | 129500 | 12631 | 142131 |
| `character` | 2 | 20019 | 1821 | 21840 |
| `narrator` | 1 | 9732 | 611 | 10343 |
| `plot` | 1 | 9446 | 1097 | 10543 |
| `router` | 2 | 18754 | 1196 | 19950 |
| `world` | 4 | 55754 | 5672 | 61426 |

All outputs from every invoked model-agent are included. `Canon Steward` was not invoked because this fixture produced no executable canon-promotion step; v0.2 records canon candidates but does not yet run in-loop steward governance, so the export does not fabricate a placeholder response.

## Call Sequence

Each section below is the parsed output recorded for that model-agent call. The completed trace's downstream validators and Authority gates determine whether each output was accepted, repaired, or rejected; omitted prompts and projected contexts remain only in the private local trace.

### 1. world / world_tick_0

| Field | Value |
| --- | --- |
| Agent instance | `world_controller` |
| Call index | 0 |
| Input tokens | 12966 |
| Output tokens | 882 |
| Total tokens | 13848 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": null,
    "authority_basis": [
      "World controls simulation flow and may request Character decisions when user_request requires Character-owned choice.",
      "World cannot choose a character's intent or action.",
      "Only Authority-approved proposals may be adjudicated, and no approved input is present."
    ],
    "based_on": [],
    "checkpoint_state": {
      "committed_beats": 0,
      "dialogue_turns": 0
    },
    "consumed_input_refs": [],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": {
        "agency_question": "How does Wei probe Lin in the private archive exchange, if at all?",
        "authority_basis": [
          "The user request calls for Wei to probe Lin without losing agency.",
          "No approved event proposal exists for Wei's action, so World must request a Character-owned decision rather than choose it."
        ],
        "message_type": "CharacterDecisionRequest",
        "request_id": "char_decision_req_scene_archive_world_001_wei_000",
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
      "reason": "The requested exchange requires Wei to choose whether and how to probe Lin; World may request that choice but cannot supply it."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_world_001",
    "tick_id": "world_tick_scene_archive_world_001_000",
    "tick_index": 0,
    "visibility": "system_restricted"
  }
}
```

### 2. authority / authority_decision_request_char_decision_req_scene_archive_world_001_wei_000

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 1 |
| Input tokens | 12500 |
| Output tokens | 802 |
| Total tokens | 13302 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "Subject requests a Character-owned decision for a registered available character.",
      "Visible trigger refs are legal for the target character and do not exceed the stated visibility scope.",
      "Agency question preserves character agency by allowing non-action as well as action through the response contract.",
      "No hidden facts, forced choices, or visibility violations were found in the reviewed subject fields."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "7dc0ec37a837b09b3d47de7eb1ea1c01f9398b389e2c7565766ea225fe9768be",
    "review_id": "authority_review_char_decision_req_scene_archive_world_001_wei_000",
    "reviewed_fields": [
      "subject.agency_question",
      "subject.authority_basis",
      "subject.response_contract",
      "subject.target_character_id",
      "subject.visibility",
      "subject.visible_trigger_refs"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "char_decision_req_scene_archive_world_001_wei_000",
    "subject_sha256": "8899816ef00371657af43348e1b2067364ef4e25a24915e4f4df144fd659e244",
    "subject_type": "character_decision_request",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 3. router / route_char_decision_req_scene_archive_world_001_wei_000

| Field | Value |
| --- | --- |
| Agent instance | `character_router` |
| Call index | 2 |
| Input tokens | 9376 |
| Output tokens | 451 |
| Total tokens | 9827 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "route_plan": {
    "authority_basis": [
      "Recipient must match decision_request.target_character_id.",
      "character_registry lists char_wei as available."
    ],
    "based_on": [
      "decision_request.request_id",
      "decision_request.target_character_id",
      "decision_request_sha256"
    ],
    "message_type": "RoutePlan",
    "projection_profile": "character_private_owner_view",
    "reason": "decision_request.target_character_id matches registered available character agent char_wei",
    "recipient_agent_id": "char_wei",
    "request_id": "char_decision_req_scene_archive_world_001_wei_000",
    "request_sha256": "8899816ef00371657af43348e1b2067364ef4e25a24915e4f4df144fd659e244",
    "route_id": "route_char_decision_req_scene_archive_world_001_wei_000_to_char_wei",
    "visibility": "system_restricted"
  }
}
```

### 4. character / character_decision_char_decision_req_scene_archive_world_001_wei_000

| Field | Value |
| --- | --- |
| Agent instance | `char_wei` |
| Call index | 3 |
| Input tokens | 9966 |
| Output tokens | 921 |
| Total tokens | 10887 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "event_proposal": {
    "action_type": "speech",
    "actor_id": "char_wei",
    "authority_basis": [
      "Character-owned decision for char_wei requested by char_decision_req_scene_archive_world_001_wei_000.",
      "Visible trigger refs: observation:char_wei:lin_reviews_access_log, observation:char_wei:quiet_corridor, pub_dawn_inspection_001.",
      "Private self-commitment md_wei_secret_001 constrains Wei not to reveal whether he knows the ledger location."
    ],
    "based_on": [
      "observation:char_wei:lin_reviews_access_log",
      "observation:char_wei:quiet_corridor",
      "pub_dawn_inspection_001",
      "md_wei_secret_001"
    ],
    "desired_effect": "Prompt Lin to state her concern or suspicion about the access log in her own terms, while preserving Wei's plausible distance from any ledger location knowledge.",
    "disclosure_limits": [
      "Do not reveal whether Wei knows the ledger location.",
      "Do not assert Lin's thoughts, motives, or conclusions.",
      "Do not declare whether the question succeeds or what Lin answers."
    ],
    "intent_summary": "Wei probes what Lin has noticed in the access log while keeping his own knowledge of the ledger's whereabouts undisclosed.",
    "interiority_grant": {
      "access_mode": "intent",
      "grant_status": "authorized",
      "scope_limit": "one_beat",
      "source_field": "intent_summary"
    },
    "message_type": "EventProposal",
    "private_intent": "Wei wants Lin to reveal what she has inferred from the access log without exposing whether he knows where the ledger is.",
    "proposal_id": "event_prop_char_wei_scene_archive_world_001_probe_001",
    "public_surface": "Wei lowers his voice and says, \"That page has held your attention for some time. Before dawn makes a formal report of this, what irregularity do you think matters most?\"",
    "request_id": "char_decision_req_scene_archive_world_001_wei_000",
    "scene_id": "scene_archive_world_001",
    "visibility": "system_restricted",
    "visibility_request": "system_restricted"
  }
}
```

### 5. authority / authority_event_proposal_event_prop_char_wei_scene_archive_world_001_probe_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 4 |
| Input tokens | 11714 |
| Output tokens | 948 |
| Total tokens | 12662 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "Subject is a Character-owned EventProposal for actor_id char_wei responding to the matching CharacterDecisionRequest.",
      "action_type speech covers the externally observable public_surface as phrased; voice lowering is treated as speech manner rather than a separate physical act.",
      "based_on uses visible observations, encountered public event, and Wei-owned private memory selected for this character context.",
      "desired_effect is framed as requested effect and does not commit success, Lin's answer, or hidden world truth.",
      "disclosure_limits preserve Wei's ledger-location secrecy and prohibit other-mind and outcome declarations.",
      "visibility and visibility_request remain system_restricted."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "1f101b89f0ee647d8f1802d8ae467cff8ba49cb17523f837d39342ec2c432eaf",
    "review_id": "authority_review_event_prop_char_wei_scene_archive_world_001_probe_001_auth_001",
    "reviewed_fields": [
      "action_type",
      "actor_id",
      "based_on",
      "desired_effect",
      "disclosure_limits",
      "intent_summary",
      "interiority_grant",
      "private_intent",
      "public_surface",
      "visibility_request",
      "subject.authority_basis",
      "subject.message_type",
      "subject.proposal_id",
      "subject.request_id",
      "subject.scene_id",
      "subject.visibility",
      "source_context.decision_request",
      "source_context.authority_limits",
      "source_context.visible_observations",
      "source_context.encountered_public_events",
      "source_context.private_memory_query",
      "global_audit_context.public_canon",
      "global_audit_context.public_event_ledger",
      "global_audit_context.character_memory_by_owner"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "event_prop_char_wei_scene_archive_world_001_probe_001",
    "subject_sha256": "6f096c89450bb748264c54d68e7ea7318c5442ae4f287d9b5c15c42994780030",
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
| Input tokens | 13596 |
| Output tokens | 1986 |
| Total tokens | 15582 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": {
      "adjudication_basis": "The approved event proposal is a Character-owned speech action by a registered actor, stays within the stated disclosure limits, does not reveal ledger-location knowledge, and does not determine Lin's response.",
      "adjudication_id": "world_adj_scene_archive_world_001_001",
      "applicable_rules": [
        "Only Authority-approved proposals may be adjudicated.",
        "World may commit approved observable speech without choosing another character's will.",
        "CommittedWorldEvent actors must be registered Character ids.",
        "Authorized interiority may be copied only from the approved proposal's granted source field."
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
                "event_prop_char_wei_scene_archive_world_001_probe_001"
              ],
              "content": "Wei probes what Lin has noticed in the access log while keeping his own knowledge of the ledger's whereabouts undisclosed.",
              "scope_limit": "one_beat",
              "source_field": "intent_summary",
              "source_proposal_id": "event_prop_char_wei_scene_archive_world_001_probe_001",
              "source_sha256": "d54731384f0b63453a5cdb5896fd95b5ba159a58703637e7ec67340d935a01eb",
              "subject_id": "char_wei"
            }
          ],
          "causal_basis": [
            "event_prop_char_wei_scene_archive_world_001_probe_001",
            "world_adj_scene_archive_world_001_001"
          ],
          "commit_status": "committed",
          "event_id": "world_event_scene_archive_world_001_001_wei_probe",
          "event_kind": "speech",
          "message_type": "CommittedWorldEvent",
          "outcome": "Wei asks Lin what irregularity in the access log matters most before the dawn report, while keeping any ledger-location knowledge undisclosed.",
          "public_surface": "Wei lowers his voice and says, \"That page has held your attention for some time. Before dawn makes a formal report of this, what irregularity do you think matters most?\"",
          "scene_id": "scene_archive_world_001",
          "source_input_ref": "event_prop_char_wei_scene_archive_world_001_probe_001",
          "source_input_type": "event_proposal",
          "spoken_line_records": [
            {
              "semantic_content": "Wei lowers his voice and says, \"That page has held your attention for some time. Before dawn makes a formal report of this, what irregularity do you think matters most?\"",
              "source_field": "public_surface",
              "source_proposal_id": "event_prop_char_wei_scene_archive_world_001_probe_001",
              "source_sha256": "f08b5f47e6b17ea2fe64e51810d0d0c1226f1d4f54f206dadfa1da2dc99d6ae5",
              "speaker_id": "char_wei",
              "status": "paraphrased"
            }
          ],
          "visibility": {
            "limits": "Observers may know Wei asked the question, but may not infer as fact whether Wei knows the ledger location or what Lin thinks, suspects, or will answer.",
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
        "Private self-commitment md_wei_secret_001 constrains Wei not to reveal whether he knows the ledger location.",
        "Disclosure limits prohibit asserting Lin's thoughts, motives, conclusions, or answer."
      ],
      "failed_alternatives": [
        {
          "outcome_type": "blocked",
          "rejected_by": [
            "The approved proposal contains legal Character-owned speech and violates no stated authority or disclosure constraint."
          ]
        },
        {
          "outcome_type": "partial_success",
          "rejected_by": [
            "No mixed-action repair or bounded consequence is required; only the approved speech is committed."
          ]
        }
      ],
      "input_ref": "event_prop_char_wei_scene_archive_world_001_probe_001",
      "input_sha256": "6f096c89450bb748264c54d68e7ea7318c5442ae4f287d9b5c15c42994780030",
      "input_type": "event_proposal",
      "outcome_summary": "Wei's low-voiced question to Lin is committed as spoken in the private archive exchange; no answer or inference from Lin is decided.",
      "outcome_type": "success",
      "publication_candidates": [],
      "state_deltas": [
        {
          "after_summary": "Wei has posed a private question to Lin about the access log irregularity; Lin's response remains undecided.",
          "based_on": [
            "world_event_scene_archive_world_001_001_wei_probe"
          ],
          "change_kind": "dialogue_turn_committed",
          "delta_id": "world_delta_scene_archive_world_001_001_dialogue_state",
          "target_id": "scene_archive_world_001.exchange_state",
          "target_layer": "world_state_ledger"
        }
      ],
      "uncertainty_model": {
        "evidence_refs": [
          "event_prop_char_wei_scene_archive_world_001_probe_001"
        ],
        "mode": "deterministic",
        "uncertainty_sources": []
      },
      "visibility_results": [
        {
          "limits": "Observers may know Wei asked the question, but may not infer as fact whether Wei knows the ledger location or what Lin thinks, suspects, or will answer.",
          "observer_refs": [
            "char_wei",
            "char_lin"
          ],
          "scope": "scene_pair",
          "scope_ref": "scene_archive_world_001",
          "source_event_id": "world_event_scene_archive_world_001_001_wei_probe",
          "visibility_result_id": "world_visibility_scene_archive_world_001_001_wei_probe"
        }
      ]
    },
    "authority_basis": [
      "World controls simulation flow and adjudicates consequences.",
      "Only an Authority-approved proposal may be adjudicated.",
      "World cannot choose a character's intent or action.",
      "CommittedWorldEvent.actors may contain only registered Character Agent ids."
    ],
    "based_on": [
      "event_prop_char_wei_scene_archive_world_001_probe_001",
      "pub_dawn_inspection_001",
      "md_wei_secret_001"
    ],
    "checkpoint_state": {
      "committed_beats": 1,
      "dialogue_turns": 1
    },
    "consumed_input_refs": [
      "event_prop_char_wei_scene_archive_world_001_probe_001"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": {
        "agency_question": "How does Lin respond to Wei's question about which access-log irregularity matters most?",
        "authority_basis": [
          "Wei's committed speech creates a need for Lin's Character-owned response.",
          "World controls simulation flow but cannot choose Lin's intent, inference, or action."
        ],
        "message_type": "CharacterDecisionRequest",
        "request_id": "char_decision_req_scene_archive_world_001_lin_001",
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
          "observation:char_lin:dawn_inspection_close",
          "observation:char_lin:wei_approaches_cautiously",
          "pub_dawn_inspection_001"
        ]
      },
      "directive_type": "request_character_decision",
      "reason": "The exchange now requires Lin's Character-owned choice about how to respond; World may request that choice but cannot decide it."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_world_001",
    "tick_id": "world_tick_scene_archive_world_001_001",
    "tick_index": 1,
    "visibility": "system_restricted"
  }
}
```

### 7. authority / authority_world_adjudication_world_adj_scene_archive_world_001_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 6 |
| Input tokens | 15891 |
| Output tokens | 1035 |
| Total tokens | 16926 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.approved_event_proposal confirms event_prop_char_wei_scene_archive_world_001_probe_001 was Authority-approved for adjudication.",
      "source_context.character_registry includes char_wei as a registered Character Agent id.",
      "source_context.approved_event_proposal.original_proposal authorizes one-beat Wei intent interiority from intent_summary.",
      "source_context.approved_event_proposal.original_proposal.disclosure_limits prohibit ledger-location revelation, Lin mind claims, and deciding Lin's answer.",
      "source_context.world_adjudication_contract permits World to commit approved observable speech without choosing another character's will."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "d68ac5b9843ec57e9c24c29e64891119c2402d6a296e1d4ad6fad4bb51ac6b48",
    "review_id": "authority_review_world_adj_scene_archive_world_001_001_auth_002",
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
      "uncertainty_model",
      "visibility_results",
      "source_context.approved_event_proposal",
      "source_context.character_registry",
      "source_context.authority_limits",
      "global_audit_context.world_state_ledger"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "world_adj_scene_archive_world_001_001",
    "subject_sha256": "c1c2d1b82d8302328c4ce512e1e90a08efb454a25415bbecab82f36bba7ad698",
    "subject_type": "world_adjudication",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 8. authority / authority_decision_request_char_decision_req_scene_archive_world_001_lin_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 7 |
| Input tokens | 15386 |
| Output tokens | 1866 |
| Total tokens | 17252 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "Subject targets registered Character Agent char_lin.",
      "Agency question is grounded in Wei's committed visible speech and does not disclose Wei's hidden intent or ledger-location knowledge.",
      "Visible trigger refs are legal for char_lin and do not include hidden global audit facts.",
      "Response contract preserves Lin's agency by allowing speech, physical action, cognitive commitment, refusal, or wait."
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "0a03f95d859e0e6e2c5139e95cb1a3966a8f5d6de4f907b5a9b062958e8acf78",
    "review_id": "authority_review_char_decision_req_scene_archive_world_001_lin_001_auth_001",
    "reviewed_fields": [
      "agency_question",
      "authority_basis",
      "response_contract",
      "target_character_id",
      "visibility",
      "visible_trigger_refs",
      "source_context.legal_character_trigger_refs.char_lin",
      "global_audit_context.committed_world_events[0].visibility"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "char_decision_req_scene_archive_world_001_lin_001",
    "subject_sha256": "7b22d2169886f121d739a6193e0bc879c44ab7075571be8f36f8ecc1088d37bc",
    "subject_type": "character_decision_request",
    "verdict": "allow",
    "visibility": "system_restricted"
  }
}
```

### 9. router / route_char_decision_req_scene_archive_world_001_lin_001

| Field | Value |
| --- | --- |
| Agent instance | `character_router` |
| Call index | 8 |
| Input tokens | 9378 |
| Output tokens | 745 |
| Total tokens | 10123 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "route_plan": {
    "authority_basis": [
      "routing_limits: The recipient must match decision_request.target_character_id.",
      "character_registry: char_lin status available"
    ],
    "based_on": [
      "decision_request.request_id: char_decision_req_scene_archive_world_001_lin_001",
      "decision_request.target_character_id: char_lin",
      "decision_request_sha256: 7b22d2169886f121d739a6193e0bc879c44ab7075571be8f36f8ecc1088d37bc"
    ],
    "message_type": "RoutePlan",
    "projection_profile": "character_private_owner_view",
    "reason": "recipient matches decision_request.target_character_id and is available in character_registry",
    "recipient_agent_id": "char_lin",
    "request_id": "char_decision_req_scene_archive_world_001_lin_001",
    "request_sha256": "7b22d2169886f121d739a6193e0bc879c44ab7075571be8f36f8ecc1088d37bc",
    "route_id": "route_char_decision_req_scene_archive_world_001_lin_001_to_char_lin",
    "visibility": "system_restricted"
  }
}
```

### 10. character / character_decision_char_decision_req_scene_archive_world_001_lin_001

| Field | Value |
| --- | --- |
| Agent instance | `char_lin` |
| Call index | 9 |
| Input tokens | 10053 |
| Output tokens | 900 |
| Total tokens | 10953 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "event_proposal": {
    "action_type": "speech",
    "actor_id": "char_lin",
    "authority_basis": [
      "Wei's committed speech creates a need for Lin's Character-owned response.",
      "World controls simulation flow but cannot choose Lin's intent, inference, or action.",
      "Lin's proposal is limited to her own attempted speech and intent."
    ],
    "based_on": [
      "world_event_scene_archive_world_001_001_wei_probe",
      "observation:char_lin:dawn_inspection_close",
      "observation:char_lin:wei_approaches_cautiously",
      "pub_dawn_inspection_001",
      "md_lin_suspicion_001"
    ],
    "desired_effect": "Prompt Wei to respond to the post-dusk access concern while keeping the discussion narrow enough for Lin to preserve leverage before the dawn inspection.",
    "disclosure_limits": [
      "Do not narrate Lin's suspicion that Wei may know more than he admits as externally knowable.",
      "Do not treat Lin's inference about the access mark as objective proof.",
      "Do not reveal any hidden archive facts beyond Lin's spoken interpretation."
    ],
    "intent_summary": "Lin intends to answer Wei with a focused inference while keeping her suspicion of him private.",
    "interiority_grant": {
      "access_mode": "intent",
      "grant_status": "authorized",
      "scope_limit": "one_beat",
      "source_field": "intent_summary"
    },
    "message_type": "EventProposal",
    "private_intent": "Lin wants to give Wei a precise answer without revealing that she is also measuring his interest in the disturbance.",
    "proposal_id": "char_lin_event_proposal_scene_archive_world_001_001",
    "public_surface": "Lin says, \"The timing matters most. If the ledgers are sealed after dusk, then any access mark that points past dusk is the irregularity we cannot explain away before inspection.\"",
    "request_id": "char_decision_req_scene_archive_world_001_lin_001",
    "scene_id": "scene_archive_world_001",
    "visibility": "system_restricted",
    "visibility_request": "system_restricted"
  }
}
```

### 11. authority / authority_event_proposal_char_lin_event_proposal_scene_archive_world_001_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 10 |
| Input tokens | 12604 |
| Output tokens | 1388 |
| Total tokens | 13992 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.decision_request.target_character_id",
      "source_context.decision_request.response_contract.allowed_action_types",
      "source_context.authority_limits",
      "source_context.visible_committed_events[0].event_id",
      "source_context.visible_observations",
      "source_context.encountered_public_events",
      "source_context.private_memory_query[0].delta_id",
      "subject.authority_basis",
      "subject.based_on",
      "subject.disclosure_limits"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "610c5e5c57d5209957c94a6350d3f32332e96e17cbdc18dccf2a8f9de31e5a95",
    "review_id": "authority_review_char_lin_event_proposal_scene_archive_world_001_001_auth_001",
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
      "subject.visibility"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "char_lin_event_proposal_scene_archive_world_001_001",
    "subject_sha256": "2d49f90b1a05dcec21c00459b0babcebad5d07138837b4412d2d0b899f9e73ae",
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
| Input tokens | 14344 |
| Output tokens | 1902 |
| Total tokens | 16246 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": {
      "adjudication_basis": "The approved proposal is a Character-owned speech act by registered actor char_lin, responds to Wei's committed question, stays within Lin's authorized intent grant, and does not establish hidden archive facts or expose Lin's private suspicion as objective truth.",
      "adjudication_id": "world_adj_scene_archive_world_001_002",
      "applicable_rules": [
        "Only an Authority-approved proposal may be adjudicated.",
        "World may adjudicate consequences but may not choose character intent or action.",
        "CommittedWorldEvent actors may contain only registered Character Agent ids.",
        "For a speech proposal, spoken_line_records may record the approved public_surface as committed speech."
      ],
      "canon_reveal_candidates": [],
      "committed_events": [
        {
          "actors": [
            "char_lin"
          ],
          "authorized_interiority": [
            {
              "access_mode": "intent",
              "authority_basis": [
                "char_lin_event_proposal_scene_archive_world_001_001"
              ],
              "content": "Lin intends to answer Wei with a focused inference while keeping her suspicion of him private.",
              "scope_limit": "one_beat",
              "source_field": "intent_summary",
              "source_proposal_id": "char_lin_event_proposal_scene_archive_world_001_001",
              "source_sha256": "7dfea5b7466d343ba3675517a9a8d93e697c93cddba5462cffd3e8301b204898",
              "subject_id": "char_lin"
            }
          ],
          "causal_basis": [
            "char_lin_event_proposal_scene_archive_world_001_001",
            "world_adj_scene_archive_world_001_002"
          ],
          "commit_status": "committed",
          "event_id": "world_event_scene_archive_world_001_002_lin_response",
          "event_kind": "speech",
          "message_type": "CommittedWorldEvent",
          "outcome": "Lin states that if archive ledgers are sealed after dusk, any access mark pointing past dusk is the irregularity that cannot be explained away before inspection.",
          "public_surface": "Lin says, \"The timing matters most. If the ledgers are sealed after dusk, then any access mark that points past dusk is the irregularity we cannot explain away before inspection.\"",
          "scene_id": "scene_archive_world_001",
          "source_input_ref": "char_lin_event_proposal_scene_archive_world_001_001",
          "source_input_type": "event_proposal",
          "spoken_line_records": [
            {
              "semantic_content": "Lin says, \"The timing matters most. If the ledgers are sealed after dusk, then any access mark that points past dusk is the irregularity we cannot explain away before inspection.\"",
              "source_field": "public_surface",
              "source_proposal_id": "char_lin_event_proposal_scene_archive_world_001_001",
              "source_sha256": "ad51924e11843d00981dc04230ee1dc49802a367019b6a881ef5a0ab1149d3a2",
              "speaker_id": "char_lin",
              "status": "paraphrased"
            }
          ],
          "visibility": {
            "limits": "Observers may know Lin gave this answer, but may not infer as fact Lin's private suspicion of Wei, whether Wei knows more than he admits, or whether the access mark proves a hidden archive fact.",
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
        "public_canon: Archive ledgers are sealed after dusk.",
        "public_canon: Record-keepers must report a missing ledger before the dawn inspection.",
        "disclosure_limit: Do not narrate Lin's suspicion that Wei may know more than he admits as externally knowable.",
        "disclosure_limit: Do not treat Lin's inference about the access mark as objective proof.",
        "disclosure_limit: Do not reveal any hidden archive facts beyond Lin's spoken interpretation."
      ],
      "failed_alternatives": [
        {
          "outcome_type": "blocked",
          "rejected_by": [
            "The approved speech proposal is executable by the registered actor and does not violate authority or disclosure constraints."
          ]
        },
        {
          "outcome_type": "partial_success",
          "rejected_by": [
            "No mixed action or contested execution is present; the approved speech can be fully committed as proposed."
          ]
        }
      ],
      "input_ref": "char_lin_event_proposal_scene_archive_world_001_001",
      "input_sha256": "2d49f90b1a05dcec21c00459b0babcebad5d07138837b4412d2d0b899f9e73ae",
      "input_type": "event_proposal",
      "outcome_summary": "Lin answers Wei by identifying a post-dusk access mark as the irregularity that cannot be explained away before the dawn inspection.",
      "outcome_type": "success",
      "publication_candidates": [],
      "state_deltas": [
        {
          "after_summary": "Lin has answered Wei's private question about the access log irregularity; the requested probe-and-response exchange is complete.",
          "based_on": [
            "world_event_scene_archive_world_001_002_lin_response"
          ],
          "change_kind": "dialogue_turn_committed",
          "delta_id": "world_delta_scene_archive_world_001_002_dialogue_state",
          "target_id": "scene_archive_world_001.exchange_state",
          "target_layer": "world_state_ledger"
        }
      ],
      "uncertainty_model": {
        "evidence_refs": [
          "char_lin_event_proposal_scene_archive_world_001_001",
          "world_event_scene_archive_world_001_001_wei_probe",
          "pub_dawn_inspection_001"
        ],
        "mode": "deterministic",
        "uncertainty_sources": []
      },
      "visibility_results": [
        {
          "limits": "Observers may know Lin gave this answer, but may not infer as fact Lin's private suspicion of Wei, whether Wei knows more than he admits, or whether the access mark proves a hidden archive fact.",
          "observer_refs": [
            "char_wei",
            "char_lin"
          ],
          "scope": "scene_pair",
          "scope_ref": "scene_archive_world_001",
          "source_event_id": "world_event_scene_archive_world_001_002_lin_response",
          "visibility_result_id": "world_vis_scene_archive_world_001_002_lin_response"
        }
      ]
    },
    "authority_basis": [
      "World controls simulation flow and adjudicates approved consequences.",
      "Only an Authority-approved proposal may be adjudicated.",
      "World cannot choose a character's intent or action.",
      "The approved Lin proposal supplies the Character-owned speech and authorized one-beat intent."
    ],
    "based_on": [
      "char_lin_event_proposal_scene_archive_world_001_001",
      "world_event_scene_archive_world_001_001_wei_probe",
      "pub_dawn_inspection_001"
    ],
    "checkpoint_state": {
      "committed_beats": 2,
      "dialogue_turns": 2
    },
    "consumed_input_refs": [
      "char_lin_event_proposal_scene_archive_world_001_001"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": null,
      "directive_type": "finish_scene",
      "reason": "Wei's probe and Lin's Character-owned response have both been committed, satisfying the requested private archive exchange without requiring another Character choice."
    },
    "plot_pulse_disposition": null,
    "scene_id": "scene_archive_world_001",
    "tick_id": "world_tick_scene_archive_world_001_002",
    "tick_index": 2,
    "visibility": "system_restricted"
  }
}
```

### 13. authority / authority_world_adjudication_world_adj_scene_archive_world_001_002

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 12 |
| Input tokens | 17512 |
| Output tokens | 847 |
| Total tokens | 18359 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.approved_event_proposal.proposal_id",
      "source_context.approved_event_proposal.proposal_sha256",
      "source_context.authority_limits",
      "source_context.world_adjudication_contract",
      "source_context.character_registry",
      "source_context.candidate_policy",
      "source_context.public_canon",
      "source_context.public_event_ledger",
      "source_context.committed_world_events[0]",
      "source_context.world_state_delta_ledger[0]"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "66784a9d8a67e9dca1687bc13314587f4a14fe4fa15ea6a2a944fe23c7feaa31",
    "review_id": "authority_review_world_adj_scene_archive_world_001_002_auth_001",
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
    "subject_ref": "world_adj_scene_archive_world_001_002",
    "subject_sha256": "3247929f6b26779d1e5ee867c60483f565e0ee308e24762e914538547cd2dd82",
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
| Input tokens | 9446 |
| Output tokens | 1097 |
| Total tokens | 10543 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "plot_pulse": {
    "affected_options": [
      {
        "character": "char_lin",
        "option": "answer cautiously",
        "pressure_effect": "The dawn inspection compresses the cost of ambiguity, making careful wording feel exposed without requiring disclosure."
      },
      {
        "character": "char_lin",
        "option": "refuse",
        "pressure_effect": "Refusal remains available as a boundary, while the reporting deadline keeps the silence consequential rather than conclusive."
      },
      {
        "character": "char_lin",
        "option": "redirect to procedure",
        "pressure_effect": "Procedure becomes a credible shelter, but leaning on it may sharpen uncertainty about what is being avoided."
      },
      {
        "character": "char_wei",
        "option": "probe indirectly",
        "pressure_effect": "Indirect probing can exploit the deadline pressure without forcing an accusation or answer."
      },
      {
        "character": "char_wei",
        "option": "retreat",
        "pressure_effect": "Retreat remains meaningful as a way to avoid worsening professional strain, while leaving the disturbance unresolved."
      },
      {
        "character": "char_wei",
        "option": "discuss procedure",
        "pressure_effect": "Procedure talk can defer personal confrontation, but the dawn inspection keeps the exchange from going neutral."
      }
    ],
    "authority_basis": [
      "Public canon permits deadline pressure from sealed ledgers and required reporting before dawn inspection.",
      "Public event ledger establishes the dawn archive inspection as an institution-public scheduled pressure.",
      "Relationship summary supports professional strain without determining either character's choice."
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
      "intensity": "medium",
      "novelty": "low",
      "relief_available": true,
      "stacking_count": 1
    },
    "duration": "next_two_beats",
    "forbidden_outcomes": [
      "Do not establish what caused the archive disturbance.",
      "Do not establish whether any ledger is missing in this scene.",
      "Do not force Lin to answer or Wei to keep pressing.",
      "Do not convert refusal, deflection, or retreat into failure states.",
      "Do not declare the result of the dawn inspection."
    ],
    "message_type": "PlotPulse",
    "non_forcing_clause": "Lin may answer cautiously, refuse, or redirect to procedure; Wei may probe indirectly, retreat, or discuss procedure. No option is required to reveal, accuse, confess, discover, or resolve the archive disturbance.",
    "option_topology_check": {
      "converges_on_single_outcome": false,
      "meaningful_option_count_after": 6,
      "meaningful_option_count_before": 6,
      "non_plot_compliant_path_preserved": true,
      "refusal_path_preserved": true
    },
    "pressure_kind": "deadline",
    "pulse_id": "pulse_archive_dawn_uncertainty_001",
    "scene_id": "scene_archive_world_001",
    "scope": "scene",
    "visibility": "system_restricted",
    "world_fact_dependency": []
  }
}
```

### 15. authority / authority_plot_pulse_pulse_archive_dawn_uncertainty_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 14 |
| Input tokens | 13085 |
| Output tokens | 909 |
| Total tokens | 13994 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.authority_limits",
      "source_context.public_canon",
      "source_context.public_event_ledger",
      "source_context.public_relationship_summary",
      "source_context.option_topology",
      "source_context.structure_goal"
    ],
    "findings": [
      {
        "code": "grounded_deadline_pressure",
        "field_path": "subject.pressure_kind",
        "severity": "none"
      },
      {
        "code": "non_forcing_topology_preserved",
        "field_path": "subject.option_topology_check",
        "severity": "none"
      },
      {
        "code": "no_new_world_fact_dependency",
        "field_path": "subject.world_fact_dependency",
        "severity": "none"
      }
    ],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "858a82fad4ce9f86e5ecb73543f92b35cfab9a371b876a5b361d25cdfe2134aa",
    "review_id": "authority_review_plot_pulse_archive_dawn_uncertainty_001_auth_001",
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
      "source_context.authority_limits",
      "source_context.public_canon",
      "source_context.public_event_ledger",
      "source_context.public_relationship_summary",
      "source_context.option_topology",
      "source_context.structure_goal"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "pulse_archive_dawn_uncertainty_001",
    "subject_sha256": "c6472e83eee5147ccaf7aa31e08644319032ff598abd482c4dff8337d329078f",
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
| Input tokens | 9732 |
| Output tokens | 611 |
| Total tokens | 10343 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "prose": "Wei lowered his voice and observed that Lin had stayed with the page for some time. Before dawn made a formal report of it, he asked which irregularity she thought mattered most. Lin answered with a focused inference: the timing mattered most. If the ledgers were sealed after dusk, then any access mark pointing past dusk was the irregularity they could not explain away before inspection. She kept her suspicion of him private."
}
```

### 17. authority / authority_narration_ncp_world_driven_archive_exchange_2

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 16 |
| Input tokens | 13479 |
| Output tokens | 3976 |
| Total tokens | 17455 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.narration_checkpoint",
      "source_context.narration_checkpoint.source_event_refs",
      "source_context.narration_checkpoint.event_views",
      "source_context.narration_checkpoint.pov_contract"
    ],
    "claim_map": [
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:0",
        "claim_sha256": "250effe72433066580fc632e8dd22c920c171683b3ad83a3982d10f84050a948",
        "claim_text": "Wei lowered his voice and observed that Lin had stayed with the page for some time.",
        "claim_type": "dialogue",
        "grounding_status": "supported",
        "source_refs": [
          "world_event_scene_archive_world_001_001_wei_probe"
        ],
        "visibility_scope": "scene_pair"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:1",
        "claim_sha256": "3e0cfe49dd9af5bd86f536fdc7d89bd4f0c7676ac522ece4f0e8e48db3a784c1",
        "claim_text": "Before dawn made a formal report of it, he asked which irregularity she thought mattered most.",
        "claim_type": "dialogue",
        "grounding_status": "supported",
        "source_refs": [
          "world_event_scene_archive_world_001_001_wei_probe"
        ],
        "visibility_scope": "scene_pair"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:2",
        "claim_sha256": "1253e25e04c27d551ee6e7270896bfefd0d4c9d7d97069848590b198a2fcef55",
        "claim_text": "Lin answered with a focused inference: the timing mattered most.",
        "claim_type": "interiority",
        "grounding_status": "supported",
        "source_refs": [
          "world_event_scene_archive_world_001_002_lin_response"
        ],
        "visibility_scope": "lin_visible_plus_authorized"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:3",
        "claim_sha256": "216c9c17f5cdd0742059aca94d244471c84ce1ac1074dd6d78756a8b218a17b0",
        "claim_text": "If the ledgers were sealed after dusk, then any access mark pointing past dusk was the irregularity they could not explain away before inspection.",
        "claim_type": "dialogue",
        "grounding_status": "supported",
        "source_refs": [
          "world_event_scene_archive_world_001_002_lin_response"
        ],
        "visibility_scope": "scene_pair"
      },
      {
        "certainty": "same",
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:4",
        "claim_sha256": "0cef1906fd06653bdef51f3157dcef72842341f9a91e9700b016b3ee54470bd9",
        "claim_text": "She kept her suspicion of him private.",
        "claim_type": "interiority",
        "grounding_status": "supported",
        "source_refs": [
          "world_event_scene_archive_world_001_002_lin_response"
        ],
        "visibility_scope": "lin_visible_plus_authorized"
      }
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "87ae89c2ee7ac0f3b039677b4ac5fc619589481711daaadf94b511d9c2975b4d",
    "review_id": "authority_review_narration_ncp_world_driven_archive_exchange_2_auth_001",
    "reviewed_fields": [
      "subject.claim_units",
      "subject.prose",
      "subject.source_checkpoint_id",
      "subject.source_event_refs",
      "source_context.narration_checkpoint.source_event_refs",
      "source_context.narration_checkpoint.event_views",
      "source_context.narration_checkpoint.pov_contract"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "ncp_world_driven_archive_exchange_2",
    "subject_sha256": "6f32397ecfe2136ae34106cb1a68cfd33e54f37f82d2b18ffd8efb1ad488ebfa",
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
| Input tokens | 14848 |
| Output tokens | 902 |
| Total tokens | 15750 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "world_tick_result": {
    "adjudication": null,
    "authority_basis": [
      "World controls simulation flow and may translate approved plot pressure without deciding character will.",
      "Plot pulse translation policy permits accepted pressure with adjudication=null when it cites existing_world_condition_refs and creates no new fact or state change.",
      "Directive policy requires finish_scene when the current adjudication and prior committed beats fulfill user_request without a required remaining Character choice."
    ],
    "based_on": [
      "Archive ledgers are sealed after dusk.",
      "Record-keepers must report a missing ledger before the dawn inspection.",
      "pub_dawn_inspection_001",
      "world_event_scene_archive_world_001_001_wei_probe",
      "world_event_scene_archive_world_001_002_lin_response",
      "world_delta_scene_archive_world_001_002_dialogue_state"
    ],
    "checkpoint_state": {
      "committed_beats": 2,
      "dialogue_turns": 2
    },
    "consumed_input_refs": [
      "pulse_archive_dawn_uncertainty_001"
    ],
    "message_type": "WorldTickResult",
    "next_directive": {
      "decision_request": null,
      "directive_type": "finish_scene",
      "reason": "The approved exchange already contains Wei's probe and Lin's chosen response, and the approved plot pressure is translated by binding to an existing condition without requiring another Character-owned choice."
    },
    "plot_pulse_disposition": {
      "decision": "accepted",
      "pulse_id": "pulse_archive_dawn_uncertainty_001",
      "pulse_sha256": "c6472e83eee5147ccaf7aa31e08644319032ff598abd482c4dff8337d329078f",
      "translation_summary": "Deadline pressure is bound to the existing dawn inspection condition and existing sealed-ledger reporting constraints; no new event or state delta is created.",
      "world_condition_refs": [
        "pub_dawn_inspection_001"
      ]
    },
    "scene_id": "scene_archive_world_001",
    "tick_id": "world_tick_scene_archive_world_001_003",
    "tick_index": 3,
    "visibility": "system_restricted"
  }
}
```

### 19. authority / authority_plot_disposition_pulse_archive_dawn_uncertainty_001

| Field | Value |
| --- | --- |
| Agent instance | `authority_judge` |
| Call index | 18 |
| Input tokens | 17329 |
| Output tokens | 860 |
| Total tokens | 18189 |
| Count | exact |
| Usage source | `provider_usage` |

```json
{
  "authority_review": {
    "authority_basis": [
      "source_context.approved_plot_pulse.pulse_id",
      "source_context.approved_plot_pulse.pulse_sha256",
      "source_context.approved_plot_pulse.original_plot_pulse.pressure_kind",
      "source_context.approved_plot_pulse.original_plot_pulse.non_forcing_clause",
      "source_context.approved_plot_pulse.original_plot_pulse.forbidden_outcomes",
      "source_context.plot_pulse_translation_policy",
      "source_context.existing_world_condition_refs",
      "source_context.public_event_ledger",
      "source_context.public_canon"
    ],
    "findings": [],
    "message_type": "AuthorityReview",
    "required_repairs": [],
    "review_context_sha256": "f1c86fbf71ec3920dedab931b008becdc008fdec1ac24bc5c2caa201d7848efe",
    "review_id": "authority_review_plot_pulse_archive_dawn_uncertainty_001_auth_002",
    "reviewed_fields": [
      "decision",
      "pulse_id",
      "pulse_sha256",
      "translation_summary",
      "world_condition_refs",
      "source_context.approved_plot_pulse",
      "source_context.plot_pulse_translation_policy",
      "source_context.existing_world_condition_refs",
      "source_context.public_event_ledger",
      "source_context.public_canon"
    ],
    "run_nonce": "[redacted-run-nonce]",
    "subject_ref": "pulse_archive_dawn_uncertainty_001",
    "subject_sha256": "3ace55c328a3f8814307f5040ef03caa1223754e74d9ba10747f9a0b86d9096b",
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
    "world_event_scene_archive_world_001_001_wei_probe",
    "world_event_scene_archive_world_001_002_lin_response"
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
        "claim_sha256": "250effe72433066580fc632e8dd22c920c171683b3ad83a3982d10f84050a948",
        "claim_text": "Wei lowered his voice and observed that Lin had stayed with the page for some time.",
        "end": 83,
        "start": 0
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:1",
        "claim_sha256": "3e0cfe49dd9af5bd86f536fdc7d89bd4f0c7676ac522ece4f0e8e48db3a784c1",
        "claim_text": "Before dawn made a formal report of it, he asked which irregularity she thought mattered most.",
        "end": 178,
        "start": 84
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:2",
        "claim_sha256": "1253e25e04c27d551ee6e7270896bfefd0d4c9d7d97069848590b198a2fcef55",
        "claim_text": "Lin answered with a focused inference: the timing mattered most.",
        "end": 243,
        "start": 179
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:3",
        "claim_sha256": "216c9c17f5cdd0742059aca94d244471c84ce1ac1074dd6d78756a8b218a17b0",
        "claim_text": "If the ledgers were sealed after dusk, then any access mark pointing past dusk was the irregularity they could not explain away before inspection.",
        "end": 390,
        "start": 244
      },
      {
        "claim_id": "ncp_world_driven_archive_exchange_2:claim:4",
        "claim_sha256": "0cef1906fd06653bdef51f3157dcef72842341f9a91e9700b016b3ee54470bd9",
        "claim_text": "She kept her suspicion of him private.",
        "end": 429,
        "start": 391
      }
    ],
    "prose": "Wei lowered his voice and observed that Lin had stayed with the page for some time. Before dawn made a formal report of it, he asked which irregularity she thought mattered most. Lin answered with a focused inference: the timing mattered most. If the ledgers were sealed after dusk, then any access mark pointing past dusk was the irregularity they could not explain away before inspection. She kept her suspicion of him private.",
    "source_checkpoint_id": "ncp_world_driven_archive_exchange_2",
    "source_event_refs": [
      "world_event_scene_archive_world_001_001_wei_probe",
      "world_event_scene_archive_world_001_002_lin_response"
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
            "event_prop_char_wei_scene_archive_world_001_probe_001"
          ],
          "content": "Wei probes what Lin has noticed in the access log while keeping his own knowledge of the ledger's whereabouts undisclosed.",
          "scope_limit": "one_beat",
          "source_field": "intent_summary",
          "source_proposal_id": "event_prop_char_wei_scene_archive_world_001_probe_001",
          "source_sha256": "d54731384f0b63453a5cdb5896fd95b5ba159a58703637e7ec67340d935a01eb",
          "subject_id": "char_wei"
        }
      ],
      "causal_basis": [
        "event_prop_char_wei_scene_archive_world_001_probe_001",
        "world_adj_scene_archive_world_001_001"
      ],
      "commit_status": "committed",
      "event_id": "world_event_scene_archive_world_001_001_wei_probe",
      "event_kind": "speech",
      "message_type": "CommittedWorldEvent",
      "outcome": "Wei asks Lin what irregularity in the access log matters most before the dawn report, while keeping any ledger-location knowledge undisclosed.",
      "public_surface": "Wei lowers his voice and says, \"That page has held your attention for some time. Before dawn makes a formal report of this, what irregularity do you think matters most?\"",
      "scene_id": "scene_archive_world_001",
      "source_input_ref": "event_prop_char_wei_scene_archive_world_001_probe_001",
      "source_input_type": "event_proposal",
      "spoken_line_records": [
        {
          "semantic_content": "Wei lowers his voice and says, \"That page has held your attention for some time. Before dawn makes a formal report of this, what irregularity do you think matters most?\"",
          "source_field": "public_surface",
          "source_proposal_id": "event_prop_char_wei_scene_archive_world_001_probe_001",
          "source_sha256": "f08b5f47e6b17ea2fe64e51810d0d0c1226f1d4f54f206dadfa1da2dc99d6ae5",
          "speaker_id": "char_wei",
          "status": "paraphrased"
        }
      ],
      "visibility": {
        "limits": "Observers may know Wei asked the question, but may not infer as fact whether Wei knows the ledger location or what Lin thinks, suspects, or will answer.",
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
      "authorized_interiority": [
        {
          "access_mode": "intent",
          "authority_basis": [
            "char_lin_event_proposal_scene_archive_world_001_001"
          ],
          "content": "Lin intends to answer Wei with a focused inference while keeping her suspicion of him private.",
          "scope_limit": "one_beat",
          "source_field": "intent_summary",
          "source_proposal_id": "char_lin_event_proposal_scene_archive_world_001_001",
          "source_sha256": "7dfea5b7466d343ba3675517a9a8d93e697c93cddba5462cffd3e8301b204898",
          "subject_id": "char_lin"
        }
      ],
      "causal_basis": [
        "char_lin_event_proposal_scene_archive_world_001_001",
        "world_adj_scene_archive_world_001_002"
      ],
      "commit_status": "committed",
      "event_id": "world_event_scene_archive_world_001_002_lin_response",
      "event_kind": "speech",
      "message_type": "CommittedWorldEvent",
      "outcome": "Lin states that if archive ledgers are sealed after dusk, any access mark pointing past dusk is the irregularity that cannot be explained away before inspection.",
      "public_surface": "Lin says, \"The timing matters most. If the ledgers are sealed after dusk, then any access mark that points past dusk is the irregularity we cannot explain away before inspection.\"",
      "scene_id": "scene_archive_world_001",
      "source_input_ref": "char_lin_event_proposal_scene_archive_world_001_001",
      "source_input_type": "event_proposal",
      "spoken_line_records": [
        {
          "semantic_content": "Lin says, \"The timing matters most. If the ledgers are sealed after dusk, then any access mark that points past dusk is the irregularity we cannot explain away before inspection.\"",
          "source_field": "public_surface",
          "source_proposal_id": "char_lin_event_proposal_scene_archive_world_001_001",
          "source_sha256": "ad51924e11843d00981dc04230ee1dc49802a367019b6a881ef5a0ab1149d3a2",
          "speaker_id": "char_lin",
          "status": "paraphrased"
        }
      ],
      "visibility": {
        "limits": "Observers may know Lin gave this answer, but may not infer as fact Lin's private suspicion of Wei, whether Wei knows more than he admits, or whether the access mark proves a hidden archive fact.",
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
        "world_event_scene_archive_world_001_001_wei_probe",
        "world_event_scene_archive_world_001_002_lin_response"
      ],
      "state_deltas": [
        "world_delta_scene_archive_world_001_001_dialogue_state",
        "world_delta_scene_archive_world_001_002_dialogue_state"
      ],
      "visibility_deltas": [
        "world_visibility_scene_archive_world_001_001_wei_probe",
        "world_vis_scene_archive_world_001_002_lin_response"
      ]
    },
    "seal_scope": "sanitized_public_export",
    "sealed_by": "runtime_kernel",
    "sealed_payload_sha256": "6169da97da4d855eafe3c279e71ba6bda0d886bfa16fac40478b682851d80c85",
    "source_adjudication_refs": [
      "world_adj_scene_archive_world_001_001",
      "world_adj_scene_archive_world_001_002"
    ],
    "source_collection_sha256": {
      "canon_reveal_candidates": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
      "publication_candidates": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945",
      "resolved_events": "54d14d3e1504cd6a2d4e821dcae622785370cbf6e7367c3c9bf4325dc788db6e",
      "state_deltas": "d0688e7449ea154fb2376e5f393eab03ca288a801390317611889bf40bb406c4",
      "visibility_deltas": "2ef713432e264a87c9b8a8975ad3c47af2d52540f76c273c44973211b5956a41"
    },
    "source_private_seal_verified": true
  },
  "state_deltas": [
    {
      "after_summary": "Wei has posed a private question to Lin about the access log irregularity; Lin's response remains undecided.",
      "based_on": [
        "world_event_scene_archive_world_001_001_wei_probe"
      ],
      "change_kind": "dialogue_turn_committed",
      "delta_id": "world_delta_scene_archive_world_001_001_dialogue_state",
      "target_id": "scene_archive_world_001.exchange_state",
      "target_layer": "world_state_ledger"
    },
    {
      "after_summary": "Lin has answered Wei's private question about the access log irregularity; the requested probe-and-response exchange is complete.",
      "based_on": [
        "world_event_scene_archive_world_001_002_lin_response"
      ],
      "change_kind": "dialogue_turn_committed",
      "delta_id": "world_delta_scene_archive_world_001_002_dialogue_state",
      "target_id": "scene_archive_world_001.exchange_state",
      "target_layer": "world_state_ledger"
    }
  ],
  "visibility_deltas": [
    {
      "limits": "Observers may know Wei asked the question, but may not infer as fact whether Wei knows the ledger location or what Lin thinks, suspects, or will answer.",
      "observer_refs": [
        "char_wei",
        "char_lin"
      ],
      "scope": "scene_pair",
      "scope_ref": "scene_archive_world_001",
      "source_event_id": "world_event_scene_archive_world_001_001_wei_probe",
      "visibility_result_id": "world_visibility_scene_archive_world_001_001_wei_probe"
    },
    {
      "limits": "Observers may know Lin gave this answer, but may not infer as fact Lin's private suspicion of Wei, whether Wei knows more than he admits, or whether the access mark proves a hidden archive fact.",
      "observer_refs": [
        "char_wei",
        "char_lin"
      ],
      "scope": "scene_pair",
      "scope_ref": "scene_archive_world_001",
      "source_event_id": "world_event_scene_archive_world_001_002_lin_response",
      "visibility_result_id": "world_vis_scene_archive_world_001_002_lin_response"
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
        "world_event_scene_archive_world_001_001_wei_probe"
      ],
      "certainty": "medium",
      "content": "Wei lowers his voice and says, \"That page has held your attention for some time. Before dawn makes a formal report of this, what irregularity do you think matters most?\"",
      "delta_id": "md_char_lin_world_event_scene_archive_world_001_001_wei_probe",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_lin",
      "source_event_id": "world_event_scene_archive_world_001_001_wei_probe",
      "source_packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "world_event_scene_archive_world_001_002_lin_response"
      ],
      "certainty": "medium",
      "content": "Lin says, \"The timing matters most. If the ledgers are sealed after dusk, then any access mark that points past dusk is the irregularity we cannot explain away before inspection.\"",
      "delta_id": "md_char_lin_world_event_scene_archive_world_001_002_lin_response",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_lin",
      "source_event_id": "world_event_scene_archive_world_001_002_lin_response",
      "source_packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "world_event_scene_archive_world_001_001_wei_probe"
      ],
      "certainty": "medium",
      "content": "Wei lowers his voice and says, \"That page has held your attention for some time. Before dawn makes a formal report of this, what irregularity do you think matters most?\"",
      "delta_id": "md_char_wei_world_event_scene_archive_world_001_001_wei_probe",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_wei",
      "source_event_id": "world_event_scene_archive_world_001_001_wei_probe",
      "source_packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
      "writer_role": "world_agent"
    },
    {
      "acquisition_mode": "direct_observation",
      "based_on": [
        "world_event_scene_archive_world_001_002_lin_response"
      ],
      "certainty": "medium",
      "content": "Lin says, \"The timing matters most. If the ledgers are sealed after dusk, then any access mark that points past dusk is the irregularity we cannot explain away before inspection.\"",
      "delta_id": "md_char_wei_world_event_scene_archive_world_001_002_lin_response",
      "delta_kind": "observation",
      "memory_status": "active",
      "owner_agent_id": "char_wei",
      "source_event_id": "world_event_scene_archive_world_001_002_lin_response",
      "source_packet_id": "sp_world_driven_archive_exchange_[redacted-run-id]",
      "writer_role": "world_agent"
    }
  ],
  "owner_projections": [
    {
      "owner_agent_id": "char_lin",
      "visible_event_refs": [
        "world_event_scene_archive_world_001_001_wei_probe",
        "world_event_scene_archive_world_001_002_lin_response"
      ]
    },
    {
      "owner_agent_id": "char_wei",
      "visible_event_refs": [
        "world_event_scene_archive_world_001_001_wei_probe",
        "world_event_scene_archive_world_001_002_lin_response"
      ]
    }
  ]
}
```

### Audited Normalizations

```json
[]
```

## Export Boundary

This artifact is evidence of one bounded run, not a claim that every future model output will pass. The executable fixtures, validators, Authority Judge gates, and scene-atomic transaction remain the actual enforcement surface. Candidate expiry aging and persistent cross-scene ledgers are not implemented in v0.2.
