from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile
import unittest


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from a2a_literary_agents.campaign_study import (
    build_followup_fixture,
    collect_protocol_ids,
    content_hash,
    evaluate_continuity_study,
    materialize_scene_one,
)
from a2a_literary_agents.config import RunnerConfig
from a2a_literary_agents.runner import run_trace


class CampaignStudyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="a2a_campaign_study_test_")
        self.scene_one_path = os.path.join(
            ROOT,
            "fixtures",
            "traces",
            "world_driven_archive_exchange.json",
        )
        self.scene_two_path = os.path.join(
            ROOT,
            "fixtures",
            "traces",
            "world_driven_dawn_inspection_followup.json",
        )
        with open(self.scene_one_path, "r", encoding="utf-8") as handle:
            self.scene_one_fixture = materialize_scene_one(json.load(handle))
        with open(self.scene_two_path, "r", encoding="utf-8") as handle:
            self.scene_two_template = json.load(handle)

        scene_one_materialized_path = os.path.join(
            self.tmp, "scene_one.materialized.json"
        )
        with open(
            scene_one_materialized_path, "w", encoding="utf-8"
        ) as handle:
            json.dump(
                self.scene_one_fixture,
                handle,
                ensure_ascii=False,
                indent=2,
            )
        self.scene_one_trace = run_trace(
            scene_one_materialized_path,
            self.tmp,
            RunnerConfig(
                llm_mode="mock",
                model="mock-world-runtime",
                max_llm_calls_per_trace=100,
                total_output_token_budget=1_000_000,
            ),
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def test_followup_handoff_is_committed_owner_specific_and_bounded(self) -> None:
        followup = build_followup_fixture(
            self.scene_one_fixture,
            self.scene_two_template,
            self.scene_one_trace,
        )

        self.assertEqual(followup["max_world_ticks"], 100)
        self.assertEqual(
            followup["campaign_handoff"]["source_packet_sha256"],
            content_hash(self.scene_one_trace["scene_packet"]),
        )
        prior_events = followup["world_state_ledger"]["campaign_handoff"][
            "committed_event_history"
        ]
        self.assertEqual(len(prior_events), 2)
        self.assertTrue(all("authorized_interiority" not in event for event in prior_events))
        self.assertFalse(
            {
                "publication_candidates",
                "canon_reveal_candidates",
                "published_narration_segments",
            }
            & set(followup["world_state_ledger"]["campaign_handoff"])
        )

        expected_by_owner = followup["campaign_handoff"][
            "transferred_memory_delta_refs_by_owner"
        ]
        for owner_id, character in followup["characters"].items():
            delivered = {
                item["delta_id"]
                for item in character["private_memory"]
                if "delta_id" in item
            }
            self.assertTrue(set(expected_by_owner[owner_id]) <= delivered)
            for other_owner, other_ids in expected_by_owner.items():
                if other_owner != owner_id:
                    self.assertFalse(delivered & set(other_ids))

        self.assertEqual(
            followup["pressure_history"],
            self.scene_one_trace["runtime_state"]["pressure_ledger"],
        )
        self.assertEqual(
            followup["reserved_protocol_ids"],
            collect_protocol_ids(self.scene_one_trace),
        )
        self.assertIn(
            self.scene_one_trace["scene_packet"]["packet_id"],
            followup["reserved_protocol_ids"],
        )
        self.assertTrue(
            {
                item["delta_id"]
                for item in self.scene_one_trace["memory_handoff"][
                    "derived_memory_deltas"
                ]
            }
            <= set(followup["reserved_protocol_ids"])
        )

    def test_uncommitted_scene_cannot_materialize_followup(self) -> None:
        blocked = copy.deepcopy(self.scene_one_trace)
        blocked["transaction"]["status"] = "rolled_back"

        with self.assertRaisesRegex(ValueError, "not committed"):
            build_followup_fixture(
                self.scene_one_fixture,
                self.scene_two_template,
                blocked,
            )

        mismatched_fixture = copy.deepcopy(self.scene_one_fixture)
        mismatched_fixture["trace_id"] = "unrelated_scene_one"
        with self.assertRaisesRegex(ValueError, "does not match"):
            build_followup_fixture(
                mismatched_fixture,
                self.scene_two_template,
                self.scene_one_trace,
            )

        content_mismatched_fixture = copy.deepcopy(self.scene_one_fixture)
        content_mismatched_fixture["public_canon"].append(
            "This fact was not present in the executed fixture."
        )
        with self.assertRaisesRegex(ValueError, "content hash"):
            build_followup_fixture(
                content_mismatched_fixture,
                self.scene_two_template,
                self.scene_one_trace,
            )

        colliding_fixture = copy.deepcopy(self.scene_one_fixture)
        derived_memory = self.scene_one_trace["memory_handoff"][
            "derived_memory_deltas"
        ][0]
        owner_id = derived_memory["owner_agent_id"]
        colliding_fixture["characters"][owner_id]["private_memory"].append(
            {
                "delta_id": derived_memory["delta_id"],
                "owner_agent_id": owner_id,
                "content": "Conflicting pre-existing memory.",
            }
        )
        collision_trace = copy.deepcopy(self.scene_one_trace)
        collision_trace["fixture_sha256"] = content_hash(colliding_fixture)
        with self.assertRaisesRegex(ValueError, "Conflicting private memory"):
            build_followup_fixture(
                colliding_fixture,
                self.scene_two_template,
                collision_trace,
            )

    def test_continuity_evaluator_requires_both_owner_views_and_unique_ids(self) -> None:
        followup = build_followup_fixture(
            self.scene_one_fixture,
            self.scene_two_template,
            self.scene_one_trace,
        )
        scene_two_trace = self._synthetic_scene_two_trace(followup)
        scene_two_trace["token_usage"]["agents"].reverse()

        study = evaluate_continuity_study(
            self.scene_one_fixture,
            followup,
            self.scene_one_trace,
            scene_two_trace,
            scene_elapsed_seconds={"scene_one": 1.0, "scene_two": 2.0},
        )

        self.assertEqual(study["continuity_verdict"], "pass")
        self.assertEqual(study["combined"]["elapsed_seconds"], 3.0)
        self.assertEqual(
            [
                item["input_tokens"]
                for item in study["scene_two"]["agent_calls"]
            ],
            [10, 11, 12],
        )

        fallback_elapsed = evaluate_continuity_study(
            self.scene_one_fixture,
            followup,
            self.scene_one_trace,
            scene_two_trace,
        )
        self.assertEqual(
            fallback_elapsed["combined"]["elapsed_seconds"],
            round(self.scene_one_trace["elapsed_seconds"] + 0.3, 6),
        )

        memory_tampered = copy.deepcopy(scene_two_trace)
        memory_tampered["agent_runs"][1]["projected_context"][
            "private_memory_query"
        ][0]["content"] = "tampered memory content"
        memory_tampered["agent_runs"][2]["projected_context"][
            "private_memory_query"
        ].append(
            {
                "delta_id": "md_wei_secret_001",
                "owner_agent_id": "char_wei",
                "content": "Foreign memory injected into Lin or Wei context.",
            }
        )
        memory_failed = evaluate_continuity_study(
            self.scene_one_fixture,
            followup,
            self.scene_one_trace,
            memory_tampered,
        )
        owner_check = next(
                item
                for item in memory_failed["continuity_checks"]
                if item["check_id"] == "char_lin_received_owner_memory_only"
        )
        self.assertEqual(owner_check["status"], "fail")
        self.assertIn(
            "md_wei_secret_001",
            owner_check["evidence"]["unauthorized_memory_refs"],
        )

        scene_two_trace["runtime_state"]["used_protocol_ids"].append(
            collect_protocol_ids(self.scene_one_trace)[0]
        )
        failed = evaluate_continuity_study(
            self.scene_one_fixture,
            followup,
            self.scene_one_trace,
            scene_two_trace,
        )
        self.assertEqual(failed["continuity_verdict"], "fail")
        self.assertEqual(
            next(
                item
                for item in failed["continuity_checks"]
                if item["check_id"] == "cross_scene_protocol_id_non_replay"
            )["status"],
            "fail",
        )

    def test_round_cap_cannot_exceed_study_limit(self) -> None:
        with self.assertRaisesRegex(ValueError, "between 1 and 100"):
            materialize_scene_one(self.scene_one_fixture, max_rounds=101)

    def _synthetic_scene_two_trace(
        self, followup: dict[str, object]
    ) -> dict[str, object]:
        packet = {
            "packet_id": "sp_scene_two_synthetic",
            "scene_id": followup["scene_id"],
            "commit_status": "committed",
            "resolved_events": [],
            "state_deltas": [],
        }
        handoff = followup["campaign_handoff"]
        character_runs = []
        for call_index, owner_id in enumerate(
            ["char_wei", "char_lin"], start=1
        ):
            expected_ids = set(
                handoff["transferred_memory_delta_refs_by_owner"][owner_id]
            )
            character_runs.append(
                {
                    "call_index": call_index,
                    "agent_name": "character",
                    "agent_instance_id": owner_id,
                    "protocol_stage": f"character_{owner_id}",
                    "elapsed_seconds": 0.1,
                    "projected_context": {
                        "private_memory_query": [
                            copy.deepcopy(item)
                            for item in followup["characters"][owner_id][
                                "private_memory"
                            ]
                            if item.get("delta_id") in expected_ids
                        ]
                    },
                }
            )
        agent_runs = [
            {
                "call_index": 0,
                "agent_name": "world",
                "agent_instance_id": "world_controller",
                "protocol_stage": "world_tick_0",
                "elapsed_seconds": 0.1,
                "projected_context": {
                    "world_state_ledger": followup["world_state_ledger"]
                },
            },
            *character_runs,
        ]
        usage = [
            {
                "agent_name": run["agent_name"],
                "input_tokens": 10 + index,
                "output_tokens": 5,
                "total_tokens": 15 + index,
                "source": "provider_usage",
                "is_estimated": False,
            }
            for index, run in enumerate(agent_runs)
        ]
        for run, record in zip(agent_runs, usage):
            run["token_usage"] = copy.deepcopy(record)
        return {
            "trace_id": followup["trace_id"],
            "run_id": "synthetic_scene_two",
            "final_decision": "allowed",
            "runtime_status": "finished",
            "transaction": {"status": "committed"},
            "scene_packet": packet,
            "world_ticks": [{}],
            "agent_runs": agent_runs,
            "runtime_state": {
                "used_protocol_ids": ["wt_scene_two_synthetic"],
                "committed_world_events": [],
                "pressure_ledger": followup["pressure_history"],
            },
            "memory_handoff": {"derived_memory_deltas": []},
            "authority_reviews": [],
            "repair_attempts": [],
            "published_narration_segments": [],
            "elapsed_seconds": 0.3,
            "token_usage": {
                "agents": usage,
                "totals": {
                    "input_tokens": 33,
                    "output_tokens": 15,
                    "total_tokens": 48,
                    "exact_agent_count": 3,
                    "estimated_agent_count": 0,
                    "sources": ["provider_usage"],
                },
            },
            "artifacts": {},
        }


if __name__ == "__main__":
    unittest.main()
