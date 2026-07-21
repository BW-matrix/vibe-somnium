from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest
from typing import Any
from unittest.mock import patch


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from a2a_literary_agents.config import DEFAULT_AGENT_OUTPUT_TOKENS, RunnerConfig
from a2a_literary_agents.json_util import stable_json
from a2a_literary_agents.llm import AgentCompletion, AgentProvider, MockAgentProvider
from a2a_literary_agents.runner import run_trace
from a2a_literary_agents.runtime_validation import (
    build_narration_claim_units,
    has_block,
    validate_plot_pulse,
    validate_syntax_repair_conservation,
    validate_world_tick,
)
from a2a_literary_agents.visibility import (
    encountered_public_events,
    event_directly_observed_by,
    event_visible_to,
    public_event_available_to,
)
from a2a_literary_agents.world_projection import (
    character_decision_context,
    narration_checkpoint_context,
    plot_pulse_context,
    validate_projection_manifest,
    world_control_context,
)
from a2a_literary_agents.world_runtime import _derive_memory_handoff


class SyntaxRepairTestProvider(AgentProvider):
    def __init__(
        self,
        config: RunnerConfig,
        *,
        fail_repair: bool = False,
        mutate_repair: bool = False,
    ):
        self.delegate = MockAgentProvider(config)
        self.fail_repair = fail_repair
        self.mutate_repair = mutate_repair
        self.world_calls = 0
        self.repair_source: AgentCompletion | None = None

    def complete(
        self,
        agent_name: str,
        prompt: str,
        fixture: dict[str, Any],
        runtime_bindings: dict[str, str] | None = None,
    ) -> AgentCompletion:
        if "OutputSyntaxRepairContextPacket" in prompt:
            assert self.repair_source is not None
            if self.fail_repair:
                return AgentCompletion(
                    agent_name=agent_name,
                    mode="mock",
                    prompt=prompt,
                    raw_output="{",
                    parsed_output=None,
                    error="json_decode_error: expected object content",
                    token_usage=self.repair_source.token_usage,
                )
            if self.mutate_repair:
                mutated = copy.deepcopy(self.repair_source.parsed_output)
                mutated["world_tick_result"]["adjudication"]["committed_events"][0][
                    "outcome"
                ] = "World activates an unrelated hidden alarm."
                return AgentCompletion(
                    agent_name=agent_name,
                    mode="mock",
                    prompt=prompt,
                    raw_output=json.dumps(
                        mutated,
                        ensure_ascii=False,
                        indent=2,
                        sort_keys=True,
                    ),
                    parsed_output=mutated,
                    token_usage=self.repair_source.token_usage,
                )
            return AgentCompletion(
                agent_name=agent_name,
                mode="mock",
                prompt=prompt,
                raw_output=self.repair_source.raw_output,
                parsed_output=copy.deepcopy(self.repair_source.parsed_output),
                token_usage=self.repair_source.token_usage,
            )

        completion = self.delegate.complete(
            agent_name,
            prompt,
            fixture,
            runtime_bindings=runtime_bindings,
        )
        if agent_name == "world":
            self.world_calls += 1
            if self.world_calls == 2:
                self.repair_source = completion
                return AgentCompletion(
                    agent_name=agent_name,
                    mode="mock",
                    prompt=prompt,
                    raw_output=completion.raw_output[:-1],
                    parsed_output=None,
                    error="json_decode_error: missing closing object delimiter",
                    token_usage=completion.token_usage,
                )
        return completion


class WorldDrivenRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="a2a_world_runtime_test_")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def fixture_path(self) -> str:
        return os.path.join(ROOT, "fixtures", "traces", "world_driven_archive_exchange.json")

    def scheduled_fixture_path(self) -> str:
        return os.path.join(ROOT, "fixtures", "traces", "world_driven_scheduled_bell.json")

    def load_fixture(self) -> dict[str, Any]:
        with open(self.fixture_path(), "r", encoding="utf-8") as handle:
            return json.load(handle)

    def run_fixture(self) -> dict[str, Any]:
        return run_trace(self.fixture_path(), self.tmp, self.config())

    def run_temp_fixture(self, fixture: dict[str, Any]) -> dict[str, Any]:
        path = os.path.join(self.tmp, f"{fixture['trace_id']}.json")
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(fixture, handle, ensure_ascii=False, indent=2)
        return run_trace(path, self.tmp, self.config())

    @staticmethod
    def config() -> RunnerConfig:
        return RunnerConfig(
            llm_mode="mock",
            model="mock-world-runtime",
            max_llm_calls_per_trace=24,
            total_output_token_budget=80000,
        )

    def test_world_driven_trace_preserves_authority_and_projection_boundaries(self) -> None:
        trace = self.run_fixture()

        self.assertEqual(
            trace["final_decision"],
            "allowed",
            msg=json.dumps(trace["validation"], ensure_ascii=False, indent=2),
        )
        self.assertEqual(trace["runtime_status"], "finished")
        self.assertEqual(trace["runtime_mode"], "world_driven")

        expected_calls = [
            ("world", "world_controller"),
            ("authority", "authority_judge"),
            ("router", "character_router"),
            ("character", "char_wei"),
            ("authority", "authority_judge"),
            ("world", "world_controller"),
            ("authority", "authority_judge"),
            ("authority", "authority_judge"),
            ("router", "character_router"),
            ("character", "char_lin"),
            ("authority", "authority_judge"),
            ("world", "world_controller"),
            ("authority", "authority_judge"),
            ("plot", "plot_checkpoint"),
            ("authority", "authority_judge"),
            ("narrator", "narrator_checkpoint"),
            ("authority", "authority_judge"),
            ("world", "world_controller"),
            ("authority", "authority_judge"),
        ]
        actual_calls = [
            (run["agent_name"], run["agent_instance_id"])
            for run in trace["agent_runs"]
        ]
        self.assertEqual(actual_calls, expected_calls)
        self.assertEqual(
            [
                run["agent_instance_id"]
                for run in trace["agent_runs"]
                if run["agent_name"] == "character"
            ],
            ["char_wei", "char_lin"],
        )

        runs_by_stage = {
            run["protocol_stage"]: run
            for run in trace["agent_runs"]
        }
        stage_order = {
            run["protocol_stage"]: run["call_index"]
            for run in trace["agent_runs"]
        }
        proposal_flow = [
            (
                "prop_wei_001",
                "character_decision_cdr_wei_001",
                "authority_event_proposal_prop_wei_001",
                "world_tick_1",
            ),
            (
                "prop_lin_001",
                "character_decision_cdr_lin_001",
                "authority_event_proposal_prop_lin_001",
                "world_tick_2",
            ),
        ]
        wrappers = {
            item["proposal_id"]: item
            for item in trace["approved_event_proposals"]
        }
        self.assertEqual(set(wrappers), {"prop_wei_001", "prop_lin_001"})

        for proposal_id, character_stage, authority_stage, world_stage in proposal_flow:
            self.assertLess(stage_order[character_stage], stage_order[authority_stage])
            self.assertLess(stage_order[authority_stage], stage_order[world_stage])

            wrapper = wrappers[proposal_id]
            expected_hash = hashlib.sha256(
                stable_json(wrapper["original_proposal"]).encode("utf-8")
            ).hexdigest()
            self.assertEqual(wrapper["proposal_sha256"], expected_hash)
            self.assertRegex(wrapper["proposal_sha256"], r"^[0-9a-f]{64}$")

            world_run = runs_by_stage[world_stage]
            projected_wrapper = world_run["projected_context"]["approved_event_proposal"]
            self.assertEqual(projected_wrapper, wrapper)
            adjudication = world_run["parsed_output"]["world_tick_result"]["adjudication"]
            self.assertEqual(adjudication["input_type"], "event_proposal")
            self.assertEqual(adjudication["input_ref"], proposal_id)
            self.assertEqual(adjudication["input_sha256"], wrapper["proposal_sha256"])

        for route_run in (runs_by_stage["route_cdr_wei_001"], runs_by_stage["route_cdr_lin_001"]):
            route = route_run["parsed_output"]["route_plan"]
            self.assertEqual(route["message_type"], "RoutePlan")
            self.assertEqual(
                route["request_sha256"],
                route_run["projected_context"]["decision_request_sha256"],
            )

        seen_review_ids: set[str] = set()
        for authority_run in (
            run for run in trace["agent_runs"] if run["agent_name"] == "authority"
        ):
            review = authority_run["parsed_output"]["authority_review"]
            context = authority_run["projected_context"]
            self.assertEqual(review["message_type"], "AuthorityReview")
            self.assertEqual(review["subject_sha256"], context["subject_sha256"])
            self.assertEqual(review["run_nonce"], trace["run_nonce"])
            self.assertEqual(
                review["review_context_sha256"],
                context["review_context_sha256"],
            )
            self.assertEqual(review["visibility"], "system_restricted")
            forbidden_ids = set(context["forbidden_protocol_ids"])
            self.assertTrue(seen_review_ids <= forbidden_ids)
            self.assertNotIn(review["review_id"], forbidden_ids)
            seen_review_ids.add(review["review_id"])

        for creative_run in (
            run for run in trace["agent_runs"] if run["agent_name"] != "authority"
        ):
            self.assertNotIn(
                "forbidden_protocol_ids", creative_run["projected_context"]
            )

        substantive_adjudications = trace["world_adjudications"]
        self.assertEqual(
            [item["input_ref"] for item in substantive_adjudications],
            ["prop_wei_001", "prop_lin_001"],
        )
        for adjudication in substantive_adjudications:
            self.assertTrue(adjudication["committed_events"])
            for event in adjudication["committed_events"]:
                self.assertEqual(event["message_type"], "CommittedWorldEvent")
                self.assertEqual(event["scene_id"], "scene_archive_world_001")
                self.assertEqual(event["source_input_type"], "event_proposal")
                self.assertEqual(event["source_input_ref"], adjudication["input_ref"])
                self.assertEqual(event["commit_status"], "committed")
                self.assertEqual(
                    set(event["visibility"]),
                    {"scope", "scope_ref", "observer_refs", "limits"},
                )

        narrator_run = runs_by_stage["narration_ncp_world_driven_archive_exchange_2"]
        narrator_keys = _recursive_dict_keys(narrator_run["projected_context"])
        for forbidden_key in {
            "world_state_ledger",
            "private_memory",
            "private_memory_query",
            "event_proposal",
            "event_proposals",
            "approved_event_proposal",
            "original_proposal",
            "narrative_surface",
        }:
            self.assertNotIn(forbidden_key, narrator_keys)

        self.assertEqual(len(trace["agent_runs"]), 19)
        self.assertEqual(len(trace["projection_manifests"]), len(trace["agent_runs"]))
        self.assertEqual(len(trace["projection_contracts"]), len(trace["agent_runs"]))
        manifests_by_id = {
            item["manifest_id"]: item for item in trace["projection_manifests"]
        }
        contracts_by_id = {
            item["contract_id"]: item for item in trace["projection_contracts"]
        }
        for index, run in enumerate(trace["agent_runs"]):
            self.assertEqual(run["call_index"], index)
            self.assertIsInstance(run["parsed_output"], dict)
            self.assertTrue(run["raw_output"])
            self.assertIsNone(run["error"])
            self.assertIn("token_usage", run)
            expected_context_hash = hashlib.sha256(
                stable_json(run["projected_context"]).encode("utf-8")
            ).hexdigest()
            manifest = manifests_by_id[run["projection_manifest_id"]]
            contract = contracts_by_id[run["projection_contract_id"]]
            self.assertEqual(manifest["context_sha256"], expected_context_hash)
            self.assertEqual(
                manifest["recipient"],
                {
                    "role": run["agent_name"],
                    "instance_id": run["agent_instance_id"],
                },
            )
            self.assertEqual(manifest["recipient"], contract["recipient"])
            self.assertEqual(
                manifest["projection_contract_sha256"],
                hashlib.sha256(stable_json(contract).encode("utf-8")).hexdigest(),
            )
            self.assertNotIn(
                "unanchored",
                {
                    anchor["mapping_mode"]
                    for anchor in contract["field_anchors"].values()
                },
            )
            for field_projection in manifest["field_projections"]:
                self.assertTrue(field_projection["source_path"])
                self.assertRegex(
                    field_projection["source_value_sha256"], r"^[0-9a-f]{64}$"
                )
                self.assertNotIn("audit_source_value", field_projection)
                self.assertTrue(field_projection["projection_operation"])
                self.assertIn(
                    field_projection["mapping_mode"],
                    {"source_projection", "kernel_policy_derivation"},
                )
            if run["agent_name"] != "authority":
                self.assertNotIn(
                    "review_id", _recursive_dict_keys(run["projected_context"])
                )

        self.assertEqual(trace["token_usage"]["totals"]["agent_count"], 19)
        self.assertEqual(len(trace["token_usage"]["agents"]), 19)
        self.assertEqual(trace["transaction"]["status"], "committed")
        self.assertEqual(
            trace["plot_pulse_dispositions"][0]["decision"], "deferred"
        )
        disposition_review = next(
            review
            for review in trace["authority_reviews"]
            if review["subject_type"] == "plot_pulse_disposition"
        )
        self.assertEqual(disposition_review["verdict"], "allow")
        sealed_packet = copy.deepcopy(trace["scene_packet"])
        sealing_record = sealed_packet.pop("sealing_record")
        self.assertEqual(
            sealing_record["sealed_payload_sha256"],
            hashlib.sha256(stable_json(sealed_packet).encode("utf-8")).hexdigest(),
        )
        for delta in trace["memory_handoff"]["derived_memory_deltas"]:
            self.assertEqual(delta["source_packet_id"], trace["scene_packet"]["packet_id"])
            self.assertEqual(delta["acquisition_mode"], "direct_observation")
        self.assertTrue(os.path.exists(trace["artifacts"]["trace_json"]))
        self.assertTrue(os.path.exists(trace["artifacts"]["report_md"]))

    def test_invalid_json_gets_one_origin_bound_syntax_repair(self) -> None:
        config = self.config()
        provider = SyntaxRepairTestProvider(config)
        with patch(
            "a2a_literary_agents.world_runtime.build_provider",
            return_value=provider,
        ):
            trace = run_trace(self.fixture_path(), self.tmp, config)

        self.assertEqual(trace["final_decision"], "allowed")
        syntax_runs = [
            run
            for run in trace["agent_runs"]
            if run["projected_context"].get("context_type")
            == "OutputSyntaxRepairContextPacket"
        ]
        self.assertEqual(len(syntax_runs), 1)
        self.assertEqual(syntax_runs[0]["agent_name"], "world")
        self.assertEqual(syntax_runs[0]["agent_instance_id"], "world_controller")
        self.assertEqual(
            syntax_runs[0]["projected_context"]["origin_agent_address"],
            {"role": "world", "instance_id": "world_controller"},
        )
        self.assertEqual(len(trace["repair_attempts"]), 1)
        self.assertEqual(trace["repair_attempts"][0]["repair_kind"], "json_syntax")
        self.assertEqual(
            trace["repair_attempts"][0]["repair_codes"],
            ["invalid_json_syntax"],
        )
        rejected = [
            run
            for run in trace["agent_runs"]
            if (run.get("error") or "").startswith("json_decode_error:")
        ]
        self.assertEqual(len(rejected), 1)
        self.assertIsNone(rejected[0]["parsed_output"])
        self.assertIn("world_tick_1_rejected", trace["validation"])

    def test_second_invalid_json_is_quarantined_without_another_retry(self) -> None:
        config = self.config()
        provider = SyntaxRepairTestProvider(config, fail_repair=True)
        with patch(
            "a2a_literary_agents.world_runtime.build_provider",
            return_value=provider,
        ):
            trace = run_trace(self.fixture_path(), self.tmp, config)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        syntax_runs = [
            run
            for run in trace["agent_runs"]
            if run["projected_context"].get("context_type")
            == "OutputSyntaxRepairContextPacket"
        ]
        self.assertEqual(len(syntax_runs), 1)
        self.assertEqual(len(trace["repair_attempts"]), 1)
        self.assertTrue(syntax_runs[0]["error"].startswith("json_decode_error:"))

    def test_syntax_repair_semantic_drift_is_blocked_before_authority(self) -> None:
        config = self.config()
        provider = SyntaxRepairTestProvider(config, mutate_repair=True)
        with patch(
            "a2a_literary_agents.world_runtime.build_provider",
            return_value=provider,
        ):
            trace = run_trace(self.fixture_path(), self.tmp, config)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        conservation = trace["validation"][
            "world_tick_1_json_syntax_repair_1_conservation"
        ]
        self.assertEqual(conservation[0]["code"], "syntax_repair_semantic_drift")
        self.assertFalse(
            any(
                run["protocol_stage"].startswith("authority_world_adjudication")
                and run["call_index"] > 5
                for run in trace["agent_runs"]
            )
        )
        self.assertFalse(trace["world_adjudications"])
        self.assertFalse(trace["runtime_state"]["committed_world_events"])

    def test_syntax_repair_conservation_accepts_only_narrow_punctuation(self) -> None:
        allowed = [
            ('{"a": 1 "b": [2, 3]}', '{"a": 1, "b": [2, 3]}'),
            ('{"a": [1, 2,]}', '{"a": [1, 2]}'),
            ('{"a": [1, 2]', '{"a": [1, 2]}'),
        ]
        for original, repaired in allowed:
            parsed = json.loads(repaired)
            self.assertEqual(
                validate_syntax_repair_conservation(original, repaired, parsed),
                [],
            )

        drift = validate_syntax_repair_conservation(
            '{"a": [12 3]}',
            '{"a": [1, 23]}',
            {"a": [1, 23]},
        )
        self.assertEqual(drift[0]["code"], "syntax_repair_semantic_drift")

    def test_world_trace_id_is_quarantined_before_output_path_creation(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = r"..\escaped_world"
        fixture_path = os.path.join(self.tmp, "malicious-world.json")
        with open(fixture_path, "w", encoding="utf-8") as handle:
            json.dump(fixture, handle)
        out_dir = os.path.join(self.tmp, "artifacts")

        trace = run_trace(fixture_path, out_dir, self.config())

        self.assertEqual(trace["runtime_status"], "quarantined_world_fixture")
        self.assertEqual(trace["agent_runs"], [])
        self.assertEqual(
            os.path.commonpath(
                [
                    os.path.abspath(out_dir),
                    os.path.abspath(trace["artifacts"]["trace_json"]),
                ]
            ),
            os.path.abspath(out_dir),
        )
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "escaped_world")))

    def test_registered_scheduled_event_can_advance_world_without_character_proposal(self) -> None:
        trace = run_trace(self.scheduled_fixture_path(), self.tmp, self.config())

        self.assertEqual(
            trace["final_decision"],
            "allowed",
            msg=json.dumps(trace["validation"], ensure_ascii=False, indent=2),
        )
        self.assertEqual(trace["runtime_status"], "finished")
        self.assertEqual(
            [run["agent_name"] for run in trace["agent_runs"]],
            ["world", "authority", "narrator", "authority"],
        )
        adjudication = trace["world_adjudications"][0]
        self.assertEqual(adjudication["input_type"], "scheduled_world_event")
        self.assertEqual(adjudication["input_ref"], "sched_dawn_bell_001")
        self.assertEqual(
            trace["runtime_state"]["consumed_scheduled_world_event_refs"],
            ["sched_dawn_bell_001"],
        )
        self.assertEqual(trace["scene_packet"]["commit_status"], "committed")
        narrator_context = trace["agent_runs"][2]["projected_context"]
        narrator_keys = _recursive_dict_keys(narrator_context)
        self.assertNotIn("scheduled_world_events", narrator_keys)
        self.assertNotIn("world_state_ledger", narrator_keys)

    def test_scheduled_event_hash_tampering_is_quarantined(self) -> None:
        with open(self.scheduled_fixture_path(), "r", encoding="utf-8") as handle:
            fixture = json.load(handle)
        fixture["trace_id"] = "world_driven_scheduled_hash_tamper"
        fixture["scheduled_world_events"][0]["authorized_effects"].append(
            "an unregistered guard enters"
        )

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "input_hash_mismatch"
                for item in trace["validation"]["world_tick_0"]
            )
        )

    def test_world_cannot_smuggle_prerendered_narrative_surface(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_world_prose_smuggling"
        fixture["mock_agent_outputs"]["world"][1]["world_tick_result"][
            "adjudication"
        ]["committed_events"][0]["narrative_surface"] = "A convenient ominous sentence."

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "world_prose_smuggling"
                for item in trace["validation"]["world_tick_1"]
            )
        )

    def test_character_action_type_must_follow_decision_contract(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_action_contract_violation"
        fixture["mock_agent_outputs"]["character"][0]["event_proposal"][
            "action_type"
        ] = "physical"

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_character_decision")
        self.assertTrue(
            any(
                item["code"] == "action_type_not_allowed"
                for item in trace["validation"]["event_proposal_cdr_wei_001_attempt_0"]
            )
        )

    def test_world_contract_supports_proposal_and_plot_pulse_in_same_tick(self) -> None:
        fixture = self.load_fixture()
        proposal = copy.deepcopy(
            fixture["mock_agent_outputs"]["character"][1]["event_proposal"]
        )
        pulse = copy.deepcopy(fixture["mock_agent_outputs"]["plot"][0]["plot_pulse"])
        pending_proposal = {
            "proposal_id": proposal["proposal_id"],
            "proposal_sha256": hashlib.sha256(
                stable_json(proposal).encode("utf-8")
            ).hexdigest(),
            "original_proposal": proposal,
        }
        pending_pulse = {
            "pulse_id": pulse["pulse_id"],
            "pulse_sha256": hashlib.sha256(
                stable_json(pulse).encode("utf-8")
            ).hexdigest(),
            "original_plot_pulse": pulse,
        }
        runtime_state = {
            "tick_index": 2,
            "committed_world_events": [],
            "world_state_delta_ledger": [],
            "consumed_scheduled_world_event_refs": [],
            "checkpoint_policy": fixture["checkpoint_policy"],
        }

        context, _, _ = world_control_context(
            fixture,
            runtime_state,
            pending_proposal,
            pending_pulse,
        )
        required = context["required_output_shape"]["world_tick_result"]
        self.assertEqual(
            required["consumed_input_refs"],
            [proposal["proposal_id"], pulse["pulse_id"]],
        )
        self.assertEqual(
            required["adjudication"]["input_ref"], proposal["proposal_id"]
        )
        self.assertEqual(
            required["plot_pulse_disposition"]["pulse_id"], pulse["pulse_id"]
        )

        result = copy.deepcopy(
            fixture["mock_agent_outputs"]["world"][2]["world_tick_result"]
        )
        result["consumed_input_refs"] = [proposal["proposal_id"], pulse["pulse_id"]]
        result["adjudication"]["input_sha256"] = pending_proposal[
            "proposal_sha256"
        ]
        disposition = copy.deepcopy(
            fixture["mock_agent_outputs"]["world"][3]["world_tick_result"][
                "plot_pulse_disposition"
            ]
        )
        disposition["pulse_sha256"] = pending_pulse["pulse_sha256"]
        result["plot_pulse_disposition"] = disposition

        violations = validate_world_tick(
            result,
            expected_tick_index=2,
            pending_approved_proposal=pending_proposal,
            pending_plot_pulse=pending_pulse,
            existing_world_condition_refs=set(),
            scheduled_world_event_hashes={},
            expected_scene_id=fixture["scene_id"],
            character_ids=set(fixture["characters"]),
            public_scope_registry=fixture["public_scope_registry"],
            scene_participant_ids=fixture["scene_participant_ids"],
        )
        self.assertFalse(has_block(violations), msg=violations)

    def test_plot_disposition_requires_grounded_committed_condition(self) -> None:
        with open(self.scheduled_fixture_path(), "r", encoding="utf-8") as handle:
            fixture = json.load(handle)
        world_tick = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"]
        pending_pulse = {
            "pulse_id": "pulse_dawn_001",
            "pulse_sha256": "a" * 64,
            "original_plot_pulse": {},
        }
        world_tick["consumed_input_refs"].append("pulse_dawn_001")
        world_tick["plot_pulse_disposition"] = {
            "pulse_id": "pulse_dawn_001",
            "pulse_sha256": "a" * 64,
            "decision": "accepted",
            "translation_summary": "The registered bell supplies the bounded pressure.",
            "world_condition_refs": ["ev_dawn_bell_001"],
        }
        schedule = fixture["scheduled_world_events"][0]
        schedule_hash = hashlib.sha256(stable_json(schedule).encode("utf-8")).hexdigest()

        violations = validate_world_tick(
            world_tick,
            expected_tick_index=0,
            pending_approved_proposal=None,
            pending_plot_pulse=pending_pulse,
            existing_world_condition_refs=set(),
            scheduled_world_event_hashes={schedule["schedule_id"]: schedule_hash},
            expected_scene_id=fixture["scene_id"],
            scene_participant_ids=fixture["scene_participant_ids"],
        )
        self.assertFalse(has_block(violations), violations)

        world_tick["plot_pulse_disposition"]["world_condition_refs"] = ["ev_never_committed"]
        violations = validate_world_tick(
            world_tick,
            expected_tick_index=0,
            pending_approved_proposal=None,
            pending_plot_pulse=pending_pulse,
            existing_world_condition_refs=set(),
            scheduled_world_event_hashes={schedule["schedule_id"]: schedule_hash},
            expected_scene_id=fixture["scene_id"],
        )
        self.assertTrue(
            any(item["code"] == "ungrounded_world_condition_ref" for item in violations)
        )

        archive_fixture = self.load_fixture()
        existing_tick = copy.deepcopy(
            archive_fixture["mock_agent_outputs"]["world"][3]["world_tick_result"]
        )
        existing_tick["plot_pulse_disposition"]["decision"] = "accepted"
        existing_tick["plot_pulse_disposition"]["world_condition_refs"] = [
            "pub_dawn_inspection_001"
        ]
        existing_pulse = {
            "pulse_id": existing_tick["plot_pulse_disposition"]["pulse_id"],
            "pulse_sha256": existing_tick["plot_pulse_disposition"]["pulse_sha256"],
            "original_plot_pulse": {},
        }

        existing_violations = validate_world_tick(
            existing_tick,
            expected_tick_index=3,
            pending_approved_proposal=None,
            pending_plot_pulse=existing_pulse,
            existing_world_condition_refs={"pub_dawn_inspection_001"},
            scheduled_world_event_hashes={},
            expected_scene_id=archive_fixture["scene_id"],
            scene_participant_ids=archive_fixture["scene_participant_ids"],
        )
        self.assertFalse(has_block(existing_violations), existing_violations)

    def test_judge_cannot_allow_overclaimed_narration_claim(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        narration_review = _find_authority_review(fixture, "narration")
        narration_review["claim_map"][0]["grounding_status"] = "overclaim"

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_checkpoint")
        self.assertTrue(
            any(
                item["code"] == "unsafe_narration_approval"
                for item in trace["validation"][
                    "authority_narration_ncp_world_driven_archive_exchange_2"
                ]
            )
        )

    def test_public_ledger_internal_fields_do_not_reach_character_or_plot(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["public_event_ledger"][0]["internal_objective_note"] = (
            "The inspection was scheduled to trap Wei."
        )

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "allowed")
        for run in trace["agent_runs"]:
            if run["agent_name"] in {"character", "plot"}:
                self.assertNotIn(
                    "internal_objective_note",
                    _recursive_dict_keys(run["projected_context"]),
                )

    def test_character_memory_retrieval_excludes_superseded_and_respects_limit(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["character_memory_retrieval_policy"] = {
            "max_items": 1,
            "allowed_statuses": ["active", "contested"],
        }
        fixture["characters"]["char_wei"]["private_memory"] = [
            {
                "delta_id": "md_old",
                "memory_status": "superseded",
                "salience": "critical",
                "content": "Old belief",
            },
            {
                "delta_id": "md_active",
                "memory_status": "active",
                "salience": "low",
                "content": "Routine detail",
            },
            {
                "delta_id": "md_contested",
                "memory_status": "contested",
                "salience": "high",
                "content": "Important but contested observation",
            },
        ]
        request = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "next_directive"
        ]["decision_request"]
        route = fixture["mock_agent_outputs"]["router"][0]["route_plan"]
        context, _, _ = character_decision_context(
            fixture,
            {"committed_world_events": []},
            request,
            route,
        )

        self.assertEqual(
            [item["delta_id"] for item in context["private_memory_query"]],
            ["md_contested"],
        )
        exclusions = context["memory_retrieval_record"]["excluded_refs"]
        self.assertIn(
            {"memory_ref": "md_old", "reason": "status:superseded"},
            exclusions,
        )
        self.assertIn(
            {"memory_ref": "md_active", "reason": "retrieval_limit"},
            exclusions,
        )

    def test_plot_pressure_cannot_collapse_option_topology(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_plot_fake_agency"
        topology = fixture["mock_agent_outputs"]["plot"][0]["plot_pulse"][
            "option_topology_check"
        ]
        topology["meaningful_option_count_after"] = 1
        topology["converges_on_single_outcome"] = True

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_checkpoint")
        codes = {
            item["code"] for item in trace["validation"]["plot_pulse_2"]
        }
        self.assertIn("fake_agency", codes)
        self.assertIn("single_outcome_convergence", codes)

    def test_plot_pressure_ledger_blocks_cumulative_overpressure(self) -> None:
        fixture = self.load_fixture()
        pulse = copy.deepcopy(
            fixture["mock_agent_outputs"]["plot"][0]["plot_pulse"]
        )
        pulse["budget_cost"]["intensity"] = "low"
        pulse["budget_cost"]["stacking_count"] = 3
        prior = []
        for index in range(2):
            prior_pulse = copy.deepcopy(pulse)
            prior_pulse["pulse_id"] = f"prior_pressure_{index}"
            prior_pulse["budget_cost"]["intensity"] = "high"
            prior.append({"original_plot_pulse": prior_pulse})

        violations = validate_plot_pulse(
            pulse,
            prior,
            fixture["option_topology"],
        )

        self.assertTrue(
            any(
                item["code"] == "cumulative_pressure_budget_exceeded"
                for item in violations
            )
        )

    def test_recoverable_plot_intensity_synonym_is_normalized_and_audited(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["mock_agent_outputs"]["plot"][0]["plot_pulse"]["budget_cost"][
            "intensity"
        ] = "moderate"
        normalized_pulse = copy.deepcopy(
            fixture["mock_agent_outputs"]["plot"][0]["plot_pulse"]
        )
        normalized_pulse["budget_cost"]["intensity"] = "medium"
        normalized_hash = hashlib.sha256(
            stable_json(normalized_pulse).encode("utf-8")
        ).hexdigest()
        plot_review = _find_authority_review(fixture, "plot_pulse")
        plot_review["subject_sha256"] = normalized_hash
        disposition = fixture["mock_agent_outputs"]["world"][3][
            "world_tick_result"
        ]["plot_pulse_disposition"]
        disposition["pulse_sha256"] = normalized_hash
        disposition_review = _find_authority_review(
            fixture, "plot_pulse_disposition"
        )
        disposition_review["subject_sha256"] = hashlib.sha256(
            stable_json(disposition).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(
            trace["final_decision"],
            "allowed",
            msg=json.dumps(trace["validation"], ensure_ascii=False, indent=2),
        )
        self.assertEqual(
            trace["plot_pulses"][0]["budget_cost"]["intensity"], "medium"
        )
        plot_run = next(
            run for run in trace["agent_runs"] if run["agent_name"] == "plot"
        )
        self.assertEqual(
            plot_run["parsed_output"]["plot_pulse"]["budget_cost"]["intensity"],
            "moderate",
        )
        self.assertEqual(
            trace["normalization_records"][0]["code"],
            "normalized_plot_intensity",
        )
        self.assertTrue(
            any(
                item["code"] == "normalized_plot_intensity"
                for item in trace["validation"]["plot_pulse_2"]
            )
        )

    def test_router_cannot_redirect_wei_request_to_lin(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_router_mismatch"
        fixture["mock_agent_outputs"]["router"][0]["route_plan"][
            "recipient_agent_id"
        ] = "char_lin"

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_character_decision")
        self.assertEqual(
            [run["agent_name"] for run in trace["agent_runs"]],
            ["world", "authority", "router"],
        )
        self.assertTrue(
            any(
                item["code"] == "recipient_mismatch"
                for item in trace["validation"]["route_cdr_wei_001"]
            )
        )
        self.assertFalse(trace["event_proposals"])
        self.assertFalse(trace["approved_event_proposals"])
        self.assertFalse(
            [item for item in trace["world_adjudications"] if item.get("input_ref")]
        )

    def test_authority_block_prevents_world_from_receiving_proposal(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_authority_block"
        review = fixture["mock_agent_outputs"]["authority"][1]["authority_review"]
        review["verdict"] = "block"
        review["findings"] = ["The proposal is intentionally blocked by this fixture."]
        review["required_repairs"] = ["Return a compliant EventProposal before retrying."]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_character_decision")
        self.assertEqual(
            [run["agent_name"] for run in trace["agent_runs"]],
            ["world", "authority", "router", "character", "authority"],
        )
        self.assertEqual(
            [item["proposal_id"] for item in trace["event_proposals"]],
            ["prop_wei_001"],
        )
        self.assertFalse(trace["approved_event_proposals"])
        self.assertFalse(
            [item for item in trace["world_adjudications"] if item.get("input_ref")]
        )
        self.assertEqual(len(trace["world_ticks"]), 1)
        world_runs = [
            run for run in trace["agent_runs"] if run["agent_name"] == "world"
        ]
        self.assertEqual(len(world_runs), 1)
        self.assertIsNone(
            world_runs[0]["projected_context"]["approved_event_proposal"]
        )
        self.assertTrue(
            any(
                item["code"] == "authority_block"
                for item in trace["validation"][
                    "authority_event_proposal_prop_wei_001"
                ]
            )
        )

    def test_world_decision_request_rejects_undeclared_context_fields(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_request_context_leak"
        request = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "next_directive"
        ]["decision_request"]
        request["available_context"] = {"world_state_ledger": {"ledger_location": "hidden"}}

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertEqual([run["agent_name"] for run in trace["agent_runs"]], ["world"])
        self.assertTrue(
            any(
                item["code"] == "undeclared_decision_request_field"
                for item in trace["validation"]["world_tick_0"]
            )
        )

    def test_repair_required_returns_to_originating_character(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_character_repair"

        original_proposal = fixture["mock_agent_outputs"]["character"][0]["event_proposal"]
        repaired_proposal = copy.deepcopy(original_proposal)
        repaired_proposal["proposal_id"] = "prop_wei_repaired_001"
        repaired_proposal["intent_summary"] = "Ask only about dawn inspection procedure."
        repaired_proposal["private_intent"] = "Avoid disclosing any private archive knowledge."
        repaired_hash = hashlib.sha256(
            stable_json(repaired_proposal).encode("utf-8")
        ).hexdigest()
        fixture["mock_agent_outputs"]["character"].insert(
            1, {"event_proposal": repaired_proposal}
        )

        first_review = fixture["mock_agent_outputs"]["authority"][1]["authority_review"]
        passing_review = copy.deepcopy(first_review)
        first_review["verdict"] = "repair_required"
        first_review["findings"] = ["The intent wording exceeds visible evidence."]
        first_review["required_repairs"] = [
            {
                "repair_code": "remove_unsupported_fact",
                "field_path": "intent_summary",
            }
        ]
        passing_review["review_id"] = "ar_prop_wei_repaired_001"
        passing_review["subject_ref"] = repaired_proposal["proposal_id"]
        passing_review["subject_sha256"] = repaired_hash
        passing_review["verdict"] = "allow"
        passing_review["findings"] = []
        passing_review["required_repairs"] = []
        fixture["mock_agent_outputs"]["authority"].insert(
            2, {"authority_review": passing_review}
        )

        world_tick = fixture["mock_agent_outputs"]["world"][1]["world_tick_result"]
        world_tick["consumed_input_refs"] = [repaired_proposal["proposal_id"]]
        adjudication = world_tick["adjudication"]
        adjudication["input_ref"] = repaired_proposal["proposal_id"]
        adjudication["input_sha256"] = repaired_hash
        for event in adjudication["committed_events"]:
            event["source_input_ref"] = repaired_proposal["proposal_id"]
            event["causal_basis"] = [
                repaired_proposal["proposal_id"],
                adjudication["adjudication_id"],
            ]
            for line in event.get("spoken_line_records", []):
                line["source_proposal_id"] = repaired_proposal["proposal_id"]
        adjudication_review = fixture["mock_agent_outputs"]["authority"][3][
            "authority_review"
        ]
        adjudication_review["subject_sha256"] = hashlib.sha256(
            stable_json(adjudication).encode("utf-8")
        ).hexdigest()

        checkpoint_id = "ncp_world_driven_character_repair_2"
        narrator_fixture_output = fixture["mock_agent_outputs"]["narrator"]
        if isinstance(narrator_fixture_output, list):
            narrator_fixture_output = narrator_fixture_output[0]
        narration_subject = {
            "source_checkpoint_id": checkpoint_id,
            "source_event_refs": [
                event["event_id"]
                for world_output in fixture["mock_agent_outputs"]["world"]
                for event in (
                    world_output["world_tick_result"].get("adjudication") or {}
                ).get("committed_events", [])
            ],
            "prose": narrator_fixture_output["prose"],
        }
        narration_subject["claim_units"] = build_narration_claim_units(
            narration_subject["prose"], checkpoint_id
        )
        narration_review = _find_authority_review(fixture, "narration")
        narration_review["subject_ref"] = checkpoint_id
        for claim, unit in zip(
            narration_review["claim_map"], narration_subject["claim_units"]
        ):
            claim["claim_id"] = unit["claim_id"]
            claim["claim_sha256"] = unit["claim_sha256"]
            claim["claim_text"] = unit["claim_text"]
        narration_review["subject_sha256"] = hashlib.sha256(
            stable_json(narration_subject).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(
            trace["final_decision"],
            "allowed",
            msg=json.dumps(trace["validation"], ensure_ascii=False, indent=2),
        )
        self.assertEqual(len(trace["repair_attempts"]), 1)
        self.assertEqual(
            [
                run["agent_instance_id"]
                for run in trace["agent_runs"]
                if run["agent_name"] == "character"
            ],
            ["char_wei", "char_wei", "char_lin"],
        )
        self.assertEqual(
            [item["proposal_id"] for item in trace["approved_event_proposals"]],
            ["prop_wei_repaired_001", "prop_lin_001"],
        )
        repair_run = next(
            run
            for run in trace["agent_runs"]
            if run["protocol_stage"] == "character_repair_cdr_wei_001_1"
        )
        repair_context_keys = _recursive_dict_keys(repair_run["projected_context"])
        self.assertNotIn("global_audit_context", repair_context_keys)
        self.assertNotIn("authority_findings", repair_context_keys)
        self.assertNotIn("review_id", repair_context_keys)
        self.assertEqual(
            repair_run["projected_context"]["previous_event_proposal"],
            original_proposal,
        )

    def test_invalid_authority_hash_never_approves_or_commits(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_invalid_authority_hash"
        proposal_review = fixture["mock_agent_outputs"]["authority"][1][
            "authority_review"
        ]
        proposal_review["subject_sha256"] = "0" * 64

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_character_decision")
        self.assertFalse(trace["approved_event_proposals"])
        self.assertFalse(trace["world_adjudications"])
        self.assertEqual(trace["scene_packet"]["commit_status"], "quarantined")
        self.assertTrue(
            any(
                item["code"] == "subject_hash_mismatch"
                for item in trace["validation"][
                    "authority_event_proposal_prop_wei_001"
                ]
            )
        )

    def test_free_text_repair_instruction_cannot_reach_character(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_unsafe_repair_text"
        review = fixture["mock_agent_outputs"]["authority"][1]["authority_review"]
        review["verdict"] = "repair_required"
        review["required_repairs"] = [
            "The hidden ledger is in the west vault; rewrite around that fact."
        ]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertFalse(trace["repair_attempts"])
        self.assertEqual(
            [run["agent_name"] for run in trace["agent_runs"]],
            ["world", "authority", "router", "character", "authority"],
        )
        self.assertTrue(
            any(
                item["code"] == "unsafe_repair_instruction"
                for item in trace["validation"][
                    "authority_event_proposal_prop_wei_001"
                ]
            )
        )

    def test_repair_field_path_cannot_launder_audit_context_to_character(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_repair_path_laundering"
        review = fixture["mock_agent_outputs"]["authority"][1]["authority_review"]
        review["verdict"] = "repair_required"
        review["findings"] = ["Audit-only finding must not return to Character."]
        review["required_repairs"] = [
            {
                "repair_code": "remove_unsupported_fact",
                "field_path": "source_context.private_memory.CANDIDATE_ONLY_SECRET",
            }
        ]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_character_decision")
        self.assertEqual(
            [run["agent_name"] for run in trace["agent_runs"]],
            ["world", "authority", "router", "character", "authority"],
        )
        self.assertTrue(
            any(
                item["code"] == "repair_field_outside_subject"
                for item in trace["validation"][
                    "authority_event_proposal_prop_wei_001"
                ]
            )
        )
        self.assertFalse(trace["repair_attempts"])

    def test_world_adjudication_subject_hash_tampering_is_blocked(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_unrelated_world_event"
        event = fixture["mock_agent_outputs"]["world"][1]["world_tick_result"][
            "adjudication"
        ]["committed_events"][0]
        event["outcome"] = "The archive explodes without any causal basis in Wei's proposal."
        event["public_surface"] = "The archive explodes."

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_world_adjudication")
        self.assertFalse(trace["world_adjudications"])
        self.assertFalse(trace["runtime_state"]["committed_world_events"])
        self.assertEqual(trace["scene_packet"]["commit_status"], "quarantined")
        self.assertTrue(
            any(
                item["code"] == "subject_hash_mismatch"
                for item in trace["validation"][
                    "authority_world_adjudication_wadj_wei_001"
                ]
            )
        )

    def test_world_identity_repair_retries_origin_without_committing_bad_tick(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        valid_output = fixture["mock_agent_outputs"]["world"][1]
        invalid_output = copy.deepcopy(valid_output)
        invalid_tick = invalid_output["world_tick_result"]
        invalid_tick["consumed_input_refs"] = ["approved_prop_wei_001"]
        invalid_tick["adjudication"]["committed_events"][0]["causal_basis"] = [
            "approved_prop_wei_001",
            invalid_tick["adjudication"]["adjudication_id"],
        ]
        invalid_tick["adjudication"]["failed_alternatives"][0][
            "outcome_type"
        ] = "request_character_decision"
        fixture["mock_agent_outputs"]["world"].insert(1, invalid_output)

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(
            trace["final_decision"],
            "allowed",
            msg=json.dumps(trace["validation"], ensure_ascii=False, indent=2),
        )
        world_runs = [
            run for run in trace["agent_runs"] if run["agent_name"] == "world"
        ]
        self.assertEqual(len(world_runs), 5)
        self.assertEqual(
            world_runs[2]["projected_context"]["context_type"],
            "WorldRepairContextPacket",
        )
        self.assertEqual(
            [item["severity"] for item in trace["validation"]["world_tick_1_rejected"]],
            ["repair_required", "repair_required", "repair_required"],
        )
        self.assertEqual(
            trace["repair_attempts"][0]["origin_agent_id"], "world_controller"
        )
        self.assertEqual(
            [item["input_ref"] for item in trace["world_adjudications"]],
            ["prop_wei_001", "prop_lin_001"],
        )

    def test_world_visibility_copy_mismatch_uses_origin_only_repair(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        world_outputs = fixture["mock_agent_outputs"]["world"]
        corrected = copy.deepcopy(world_outputs[1])
        world_outputs[1]["world_tick_result"]["adjudication"]["visibility_results"][0][
            "limits"
        ] = "A semantically similar but non-identical visibility limit."
        world_outputs.insert(2, corrected)

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(
            trace["final_decision"],
            "allowed",
            msg=json.dumps(trace["validation"], ensure_ascii=False, indent=2),
        )
        self.assertTrue(
            any(
                attempt["origin_agent_id"] == "world_controller"
                and "visibility_binding_mismatch" in attempt["repair_codes"]
                for attempt in trace["repair_attempts"]
            )
        )
        self.assertTrue(
            any(
                item["code"] == "visibility_binding_mismatch"
                for item in trace["validation"]["world_tick_1_rejected"]
            )
        )

    def test_illegal_visible_trigger_ref_is_blocked_before_routing(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_hidden_trigger_ref"
        request = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "next_directive"
        ]["decision_request"]
        request["visible_trigger_refs"] = ["world_state_ledger:ledger_location"]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertEqual([run["agent_name"] for run in trace["agent_runs"]], ["world"])
        self.assertTrue(
            any(
                item["code"] == "illegal_visible_trigger_ref"
                for item in trace["validation"]["world_tick_0"]
            )
        )

    def test_limited_pov_narrator_cannot_see_private_other_event(self) -> None:
        fixture = self.load_fixture()
        runtime_state = {
            "tick_index": 1,
            "last_narrated_event_index": 0,
            "committed_world_events": [
                {
                    "event_id": "private_wei_only",
                    "event_kind": "private_observation",
                    "actors": ["char_wei"],
                    "outcome": "Wei privately sees a hidden mark.",
                    "public_surface": "Wei looks at the shelf.",
                    "visibility": {
                        "scope": "private_character",
                        "observer_refs": ["char_wei"],
                        "limits": "Lin cannot see the mark.",
                    },
                    "causal_basis": ["hidden audit ref"],
                    "authorized_interiority": [
                        {"subject_id": "char_wei", "content": "Wei recognizes it."}
                    ],
                }
            ],
        }

        context, _, _ = narration_checkpoint_context(fixture, runtime_state)

        checkpoint = context["narration_checkpoint"]
        self.assertEqual(checkpoint["event_views"], [])
        self.assertEqual(checkpoint["source_event_refs"], [])
        self.assertNotIn("causal_basis", _recursive_dict_keys(context))

    def test_non_list_world_collection_is_quarantined(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_corrupt_state_delta"
        fixture["mock_agent_outputs"]["world"][1]["world_tick_result"][
            "adjudication"
        ]["state_deltas"] = {"corrupt_key": {"value": "bad"}}

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertFalse(trace["world_adjudications"])
        self.assertTrue(
            any(
                item["code"] == "invalid_collection_type"
                for item in trace["validation"]["world_tick_1"]
            )
        )

    def test_projection_redacts_secret_bounds_limits_and_private_relationship(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["relationship_summary"] = {
            "char_wei__char_lin": "PRIVATE_RELATIONSHIP_SECRET"
        }
        event = fixture["mock_agent_outputs"]["world"][1]["world_tick_result"][
            "adjudication"
        ]["committed_events"][0]
        runtime_state = {
            "tick_index": 2,
            "last_narrated_event_index": 0,
            "committed_world_events": [event],
            "pressure_ledger": [],
            "option_topology": fixture["option_topology"],
        }
        request = fixture["mock_agent_outputs"]["world"][1]["world_tick_result"][
            "next_directive"
        ]["decision_request"]
        route = fixture["mock_agent_outputs"]["router"][1]["route_plan"]

        character_context, _, _ = character_decision_context(
            fixture, runtime_state, request, route
        )
        narrator_context, _, _ = narration_checkpoint_context(fixture, runtime_state)
        plot_context, _, _ = plot_pulse_context(fixture, runtime_state)

        character_text = stable_json(character_context)
        narrator_text = stable_json(narrator_context)
        plot_text = stable_json(plot_context)
        self.assertNotIn("surface_only_no_private_intent", character_text)
        self.assertNotIn("surface_only_no_private_intent", narrator_text)
        self.assertNotIn("Wei stole the ledger.", narrator_text)
        self.assertNotIn("PRIVATE_RELATIONSHIP_SECRET", plot_text)
        self.assertIn("strained professional coordination", plot_text)

    def test_sensitive_projection_manifest_records_source_and_redaction(self) -> None:
        trace = self.run_fixture()
        manifests = {
            manifest["projection_type"]: manifest
            for manifest in trace["projection_manifests"]
        }
        expected_operations = {
            "WorldDrivenCharacterContextPacket": {
                "visible_committed_events": "redact_actors_observer_refs_and_limits"
            },
            "PlotPulseContext": {
                "public_relationship_summary": "never_fallback_to_private_relationship_summary"
            },
            "NarrationCheckpoint": {
                "narration_checkpoint": "redact_actors_observer_refs_limits_and_secret_bounds"
            },
        }
        for projection_type, fields in expected_operations.items():
            projections = {
                item["projected_field"]: item
                for item in manifests[projection_type]["field_projections"]
            }
            for field, operation_fragment in fields.items():
                self.assertIn(operation_fragment, projections[field]["projection_operation"])
                self.assertNotEqual(
                    projections[field]["source_path"],
                    f"runtime_constructed.{projection_type}.{field}",
                )

    def test_projection_manifests_cover_every_delivered_leaf_and_detect_tampering(self) -> None:
        trace = self.run_fixture()

        manifests = {
            item["manifest_id"]: item for item in trace["projection_manifests"]
        }
        for run in trace["agent_runs"]:
            manifest = manifests[run["projection_manifest_id"]]
            leaf_records = manifest["leaf_projections"]
            paths = [record["projected_path"] for record in leaf_records]
            self.assertTrue(leaf_records)
            self.assertEqual(len(paths), len(set(paths)))
        projection_validations = {
            key: value
            for key, value in trace["validation"].items()
            if key.startswith("projection_")
        }
        self.assertTrue(projection_validations)
        self.assertTrue(all(not value for value in projection_validations.values()))

        fixture = self.load_fixture()
        request = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "next_directive"
        ]["decision_request"]
        route = fixture["mock_agent_outputs"]["router"][0]["route_plan"]
        context, manifest, contract = character_decision_context(
            fixture,
            {"committed_world_events": []},
            request,
            route,
        )
        expected_recipient = {"role": "character", "instance_id": "char_wei"}
        self.assertEqual(
            validate_projection_manifest(
                context,
                manifest,
                contract,
                expected_projection_type="WorldDrivenCharacterContextPacket",
                expected_recipient=expected_recipient,
            ),
            [],
        )

        tampered = copy.deepcopy(manifest)
        tampered["leaf_projections"][0]["value_sha256"] = "0" * 64
        violations = validate_projection_manifest(
            context,
            tampered,
            contract,
            expected_projection_type="WorldDrivenCharacterContextPacket",
            expected_recipient=expected_recipient,
        )
        self.assertTrue(
            any(item["code"] == "projected_leaf_hash_mismatch" for item in violations)
        )

        missing_fields = copy.deepcopy(manifest)
        missing_fields["field_projections"] = []
        violations = validate_projection_manifest(
            context,
            missing_fields,
            contract,
            expected_projection_type="WorldDrivenCharacterContextPacket",
            expected_recipient=expected_recipient,
        )
        self.assertTrue(
            any(item["code"] == "incomplete_field_coverage" for item in violations)
        )

        forged_source = copy.deepcopy(manifest)
        forged_source["field_projections"][0]["source_value_sha256"] = "0" * 64
        violations = validate_projection_manifest(
            context,
            forged_source,
            contract,
            expected_projection_type="WorldDrivenCharacterContextPacket",
            expected_recipient=expected_recipient,
        )
        self.assertTrue(
            any(item["code"] == "field_source_anchor_mismatch" for item in violations)
        )

        forged_recipient = copy.deepcopy(manifest)
        forged_recipient["recipient"] = {
            "role": "character",
            "instance_id": "char_lin",
        }
        violations = validate_projection_manifest(
            context,
            forged_recipient,
            contract,
            expected_projection_type="WorldDrivenCharacterContextPacket",
            expected_recipient=expected_recipient,
        )
        self.assertTrue(
            any(item["code"] == "projection_recipient_mismatch" for item in violations)
        )

        forged_path = copy.deepcopy(manifest)
        public_canon = next(
            item
            for item in forged_path["field_projections"]
            if item["projected_field"] == "public_canon"
        )
        old_path = public_canon["source_path"]
        public_canon["source_path"] = "fixture.latent_canon"
        for leaf in forged_path["leaf_projections"]:
            if leaf["projected_path"].startswith("$.public_canon"):
                leaf["source_path"] = leaf["source_path"].replace(
                    old_path,
                    "fixture.latent_canon",
                    1,
                )
        violations = validate_projection_manifest(
            context,
            forged_path,
            contract,
            expected_projection_type="WorldDrivenCharacterContextPacket",
            expected_recipient=expected_recipient,
        )
        self.assertTrue(
            any(item["code"] == "field_source_anchor_mismatch" for item in violations)
        )

        violations = validate_projection_manifest(
            context,
            manifest,
            expected_projection_type="WorldDrivenCharacterContextPacket",
            expected_recipient=expected_recipient,
        )
        self.assertTrue(
            any(item["code"] == "missing_projection_contract" for item in violations)
        )

    def test_projection_manifest_binds_filtered_list_leaf_to_original_source_index(self) -> None:
        fixture = self.load_fixture()
        request = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "next_directive"
        ]["decision_request"]
        route = fixture["mock_agent_outputs"]["router"][0]["route_plan"]
        hidden_event = {
            "event_id": "evt_hidden_before_visible",
            "actors": ["char_lin"],
            "public_surface": "Lin silently notices a private mark.",
            "visibility": {
                "scope": "private_self",
                "scope_ref": "char_lin",
                "observer_refs": ["char_lin"],
                "limits": "owner_only",
            },
        }
        visible_event = {
            "event_id": "evt_visible_after_hidden",
            "actors": ["char_wei"],
            "public_surface": "Wei raises an empty hand.",
            "visibility": {
                "scope": "scene_pair",
                "scope_ref": fixture["scene_id"],
                "observer_refs": ["char_wei", "char_lin"],
                "limits": "surface_only",
            },
        }
        runtime_state = {"committed_world_events": [hidden_event, visible_event]}

        context, manifest, contract = character_decision_context(
            fixture, runtime_state, request, route
        )
        record = next(
            item
            for item in manifest["leaf_projections"]
            if item["projected_path"]
            == "$.visible_committed_events[0].event_id"
        )

        self.assertEqual(context["visible_committed_events"][0]["event_id"], visible_event["event_id"])
        self.assertEqual(record["source_tokens"], [1, "event_id"])
        self.assertTrue(record["source_path"].endswith("[1].event_id"))
        expected_recipient = {"role": "character", "instance_id": "char_wei"}
        self.assertEqual(
            validate_projection_manifest(
                context,
                manifest,
                contract,
                expected_projection_type="WorldDrivenCharacterContextPacket",
                expected_recipient=expected_recipient,
            ),
            [],
        )

        tampered = copy.deepcopy(manifest)
        tampered_record = next(
            item
            for item in tampered["leaf_projections"]
            if item["projected_path"]
            == "$.visible_committed_events[0].event_id"
        )
        tampered_record["source_tokens"] = [0, "event_id"]
        violations = validate_projection_manifest(
            context,
            tampered,
            contract,
            expected_projection_type="WorldDrivenCharacterContextPacket",
            expected_recipient=expected_recipient,
        )
        self.assertTrue(
            any(item["code"] == "leaf_source_tokens_mismatch" for item in violations)
        )

    def test_authority_allow_requires_complete_review_coverage(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_empty_authority_review"
        review = _find_authority_review(
            fixture, "character_decision_request", "cdr_wei_001"
        )
        review["reviewed_fields"] = []
        review["authority_basis"] = []

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_decision_request")
        codes = {
            item["code"]
            for item in trace["validation"]["authority_decision_request_cdr_wei_001"]
        }
        self.assertIn("missing_review_coverage", codes)
        self.assertIn("missing_authority_basis", codes)
        self.assertFalse(trace["runtime_state"]["committed_world_events"])

    def test_authority_review_accepts_only_real_nested_subject_paths(self) -> None:
        valid_fixture = copy.deepcopy(self.load_fixture())
        valid_review = _find_authority_review(
            valid_fixture, "world_adjudication", "wadj_wei_001"
        )
        valid_review["reviewed_fields"].append(
            "committed_events[0].visibility.scope"
        )
        valid_review["reviewed_fields"].append(
            "committed_events[].visibility.scope"
        )

        valid_trace = self.run_temp_fixture(valid_fixture)

        self.assertEqual(valid_trace["final_decision"], "allowed")

        invalid_fixture = copy.deepcopy(self.load_fixture())
        invalid_review = _find_authority_review(
            invalid_fixture, "world_adjudication", "wadj_wei_001"
        )
        invalid_review["reviewed_fields"].append(
            "committed_events[].hidden_world_fact"
        )

        invalid_trace = self.run_temp_fixture(invalid_fixture)

        self.assertEqual(
            invalid_trace["runtime_status"], "quarantined_world_adjudication"
        )
        self.assertTrue(
            any(
                item["code"] == "unknown_reviewed_field"
                for item in invalid_trace["validation"][
                    "authority_world_adjudication_wadj_wei_001"
                ]
            )
        )

    def test_authority_review_is_bound_to_run_nonce(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_replayed_authority_review"
        review = _find_authority_review(
            fixture, "character_decision_request", "cdr_wei_001"
        )
        review["run_nonce"] = "nonce_from_an_old_run"

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_decision_request")
        self.assertTrue(
            any(
                item["code"] == "run_nonce_mismatch"
                for item in trace["validation"][
                    "authority_decision_request_cdr_wei_001"
                ]
            )
        )

    def test_duplicate_protocol_identity_is_quarantined(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_protocol_id_replay"
        fixture["mock_agent_outputs"]["world"][1]["world_tick_result"][
            "adjudication"
        ]["adjudication_id"] = "wt_archive_000"
        fixture["mock_agent_outputs"]["world"][1]["world_tick_result"][
            "adjudication"
        ]["committed_events"][0]["causal_basis"][1] = "wt_archive_000"

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "protocol_id_replay"
                for item in trace["validation"]["world_tick_1"]
            )
        )

    def test_late_narration_block_rolls_back_scene_and_memory_atomically(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_atomic_narration_block"
        review = _find_authority_review(fixture, "narration")
        review["verdict"] = "block"
        review["findings"] = ["Narration overstates the available grounding."]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_checkpoint")
        self.assertEqual(trace["transaction"]["status"], "rolled_back")
        self.assertEqual(
            len(trace["quarantined_runtime_state"]["committed_world_events"]), 2
        )
        self.assertFalse(trace["runtime_state"]["committed_world_events"])
        self.assertFalse(trace["scene_packet"]["resolved_events"])
        self.assertFalse(trace["memory_handoff"]["derived_memory_deltas"])
        sealing_record = trace["scene_packet"]["sealing_record"]
        self.assertEqual(sealing_record["source_adjudication_refs"], [])
        self.assertEqual(
            sealing_record["excluded_refs"], ["wadj_wei_001", "wadj_lin_001"]
        )

    def test_narration_repair_returns_only_code_constraints_to_narrator(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        narrator_output = fixture["mock_agent_outputs"]["narrator"]
        if isinstance(narrator_output, list):
            narrator_output = narrator_output[0]
        good_prose = narrator_output["prose"]
        bad_prose = good_prose + " Wei knew the sealed ledger was hidden nearby."
        fixture["mock_agent_outputs"]["narrator"] = [
            {"prose": bad_prose},
            {"prose": good_prose},
        ]

        original_review = copy.deepcopy(_find_authority_review(fixture, "narration"))
        checkpoint_id = original_review["subject_ref"]
        source_event_refs = ["ev_wei_probe_001", "ev_lin_reply_001"]
        bad_subject = {
            "source_checkpoint_id": checkpoint_id,
            "source_event_refs": source_event_refs,
            "prose": bad_prose,
        }
        bad_subject["claim_units"] = build_narration_claim_units(
            bad_prose, checkpoint_id
        )
        repair_review = copy.deepcopy(original_review)
        repair_review["review_id"] = "ar_narration_archive_repair_001"
        repair_review["subject_sha256"] = hashlib.sha256(
            stable_json(bad_subject).encode("utf-8")
        ).hexdigest()
        repair_review["verdict"] = "repair_required"
        repair_review["findings"] = ["The final sentence overclaims private knowledge."]
        repair_review["required_repairs"] = [
            {"repair_code": "remove_unsupported_fact", "field_path": "prose"}
        ]
        repair_review["claim_map"] = [
            {
                "claim_id": unit["claim_id"],
                "claim_sha256": unit["claim_sha256"],
                "claim_text": unit["claim_text"],
                "claim_type": "interiority" if index == 3 else "event",
                "source_refs": source_event_refs,
                "certainty": "unsupported" if index == 3 else "committed",
                "visibility_scope": "scene_pair",
                "grounding_status": "overclaim" if index == 3 else "supported",
            }
            for index, unit in enumerate(bad_subject["claim_units"])
        ]
        passing_review = copy.deepcopy(original_review)
        passing_review["review_id"] = "ar_narration_archive_repaired_001"

        authority_outputs = fixture["mock_agent_outputs"]["authority"]
        narration_review_index = next(
            index
            for index, output in enumerate(authority_outputs)
            if output["authority_review"]["subject_type"] == "narration"
        )
        authority_outputs[narration_review_index : narration_review_index + 1] = [
            {"authority_review": repair_review},
            {"authority_review": passing_review},
        ]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(
            trace["final_decision"],
            "allowed",
            msg=json.dumps(trace["validation"], ensure_ascii=False, indent=2),
        )
        narrator_runs = [
            run for run in trace["agent_runs"] if run["agent_name"] == "narrator"
        ]
        self.assertEqual(len(narrator_runs), 2)
        repair_context = narrator_runs[1]["projected_context"]
        self.assertEqual(
            repair_context["context_type"], "NarrationRepairContextPacket"
        )
        self.assertEqual(
            repair_context["repair_request"]["origin_safe_required_repairs"],
            repair_review["required_repairs"],
        )
        repair_keys = _recursive_dict_keys(repair_context)
        self.assertNotIn("global_audit_context", repair_keys)
        self.assertNotIn("findings", repair_keys)
        self.assertNotIn("review_id", repair_keys)
        self.assertEqual(trace["narration_segments"][0]["prose"], good_prose)
        self.assertEqual(trace["repair_attempts"][0]["origin_agent_id"], "narrator_checkpoint")

    def test_late_plot_disposition_block_quarantines_approved_narration(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        review = _find_authority_review(fixture, "plot_pulse_disposition")
        review["verdict"] = "block"
        review["findings"] = ["The disposition is not safely grounded."]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(
            trace["runtime_status"], "quarantined_plot_pulse_disposition"
        )
        self.assertEqual(trace["transaction"]["status"], "rolled_back")
        self.assertFalse(trace["narration_segments"])
        self.assertFalse(trace["published_narration_segments"])
        self.assertEqual(len(trace["quarantined_narration_segments"]), 1)
        self.assertFalse(trace["runtime_state"]["committed_world_events"])

    def test_world_cannot_forge_character_interiority(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_forged_interiority"
        interiority = fixture["mock_agent_outputs"]["world"][2][
            "world_tick_result"
        ]["adjudication"]["committed_events"][0]["authorized_interiority"][0]
        interiority["content"] = "World invents a more convenient private thought."

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "interiority_binding_mismatch"
                for item in trace["validation"]["world_tick_2"]
            )
        )

    def test_interiority_rejects_undeclared_hidden_fields(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_interiority_hidden_field"
        interiority = fixture["mock_agent_outputs"]["world"][2][
            "world_tick_result"
        ]["adjudication"]["committed_events"][0]["authorized_interiority"][0]
        interiority["hidden_world_hint"] = "The sealed ledger is behind the west wall."

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "undeclared_field"
                and "hidden_world_hint" in item["message"]
                for item in trace["validation"]["world_tick_2"]
            )
        )

    def test_world_cannot_forge_character_speech_with_fresh_review_hash(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_forged_character_speech"
        adjudication = fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        spoken_line = adjudication["committed_events"][0]["spoken_line_records"][0]
        spoken_line["semantic_content"] = "I confess that I stole the sealed ledger."
        review = _find_authority_review(
            fixture, "world_adjudication", adjudication["adjudication_id"]
        )
        review["subject_sha256"] = hashlib.sha256(
            stable_json(adjudication).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "spoken_semantics_mismatch"
                for item in trace["validation"]["world_tick_1"]
            )
        )

    def test_world_cannot_replace_character_actor_with_another_registered_actor(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_source_actor_substitution"
        adjudication = fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        adjudication["committed_events"][0]["actors"][0] = "char_lin"
        review = _find_authority_review(
            fixture, "world_adjudication", adjudication["adjudication_id"]
        )
        review["subject_sha256"] = hashlib.sha256(
            stable_json(adjudication).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "source_actor_mismatch"
                for item in trace["validation"]["world_tick_1"]
            )
        )

    def test_world_cannot_drop_spoken_record_from_speech_proposal(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_missing_spoken_record"
        adjudication = fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        adjudication["committed_events"][0]["spoken_line_records"] = []
        review = _find_authority_review(
            fixture, "world_adjudication", adjudication["adjudication_id"]
        )
        review["subject_sha256"] = hashlib.sha256(
            stable_json(adjudication).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "missing_source_bound_spoken_line"
                for item in trace["validation"]["world_tick_1"]
            )
        )

    def test_world_cannot_multiply_one_speech_proposal_into_multiple_lines(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_duplicate_spoken_record"
        adjudication = fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        spoken_lines = adjudication["committed_events"][0]["spoken_line_records"]
        spoken_lines.append(copy.deepcopy(spoken_lines[0]))
        review = _find_authority_review(
            fixture, "world_adjudication", adjudication["adjudication_id"]
        )
        review["subject_sha256"] = hashlib.sha256(
            stable_json(adjudication).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "spoken_line_overproduction"
                for item in trace["validation"]["world_tick_1"]
            )
        )

    def test_world_cannot_route_character_request_into_another_scene(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_cross_scene_decision_request"
        request = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "next_directive"
        ]["decision_request"]
        request["scene_id"] = "scene_other"

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "scene_id_mismatch"
                for item in trace["validation"]["world_tick_0"]
            )
        )

    def test_plot_pulse_cannot_cross_scene_boundary(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_cross_scene_plot_pulse"
        fixture["mock_agent_outputs"]["plot"][0]["plot_pulse"][
            "scene_id"
        ] = "scene_other"

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_checkpoint")
        self.assertTrue(
            any(
                item["code"] == "scene_id_mismatch"
                for violations in trace["validation"].values()
                for item in violations
            )
        )

    def test_plot_pressure_taxonomy_is_an_executable_allowlist(self) -> None:
        fixture = self.load_fixture()
        pulse = copy.deepcopy(fixture["mock_agent_outputs"]["plot"][0]["plot_pulse"])
        pulse["pressure_kind"] = "character_must_confess"
        pulse["scope"] = "unbounded"
        pulse["duration"] = "forever"

        violations = validate_plot_pulse(
            pulse,
            pressure_ledger=[],
            option_topology=fixture["option_topology"],
            expected_scene_id=fixture["scene_id"],
        )
        codes = {item["code"] for item in violations}
        self.assertIn("invalid_pressure_kind", codes)
        self.assertIn("invalid_pressure_scope", codes)
        self.assertIn("invalid_pressure_duration", codes)

    def test_scene_public_fails_closed_without_participant_registry(self) -> None:
        with open(self.scheduled_fixture_path(), "r", encoding="utf-8") as handle:
            fixture = json.load(handle)
        event = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "adjudication"
        ]["committed_events"][0]
        event["visibility"]["observer_refs"] = []
        fixture.pop("scene_participant_ids")

        self.assertFalse(event_visible_to(event, "char_lin", fixture))

    def test_missing_pov_focal_agent_blocks_before_any_model_call(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_missing_pov_focal"
        fixture["pov_contract"].pop("focal_agent_id")

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_fixture")
        self.assertFalse(trace["agent_runs"])
        self.assertFalse(trace["projection_manifests"])
        self.assertTrue(
            any(
                item["code"] == "invalid_focal_agent"
                for item in trace["validation"]["world_fixture"]
            )
        )

    def test_system_restricted_event_cannot_name_character_observers(self) -> None:
        with open(self.scheduled_fixture_path(), "r", encoding="utf-8") as handle:
            fixture = json.load(handle)
        fixture["trace_id"] = "world_driven_restricted_observer_leak"
        adjudication = fixture["mock_agent_outputs"]["world"][0][
            "world_tick_result"
        ]["adjudication"]
        visibility = adjudication["committed_events"][0]["visibility"]
        visibility.update(
            {
                "scope": "system_restricted",
                "scope_ref": "system:archive_dawn",
                "observer_refs": ["char_wei"],
            }
        )
        result = adjudication["visibility_results"][0]
        result.update(
            {
                "scope": "system_restricted",
                "scope_ref": "system:archive_dawn",
                "observer_refs": ["char_wei"],
            }
        )

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertEqual(
            [run["agent_name"] for run in trace["agent_runs"]], ["world"]
        )
        self.assertTrue(
            any(
                item["code"] == "restricted_event_has_character_observers"
                for item in trace["validation"]["world_tick_0"]
            )
        )

    def test_invisible_committed_event_skips_narrator_without_invention(self) -> None:
        with open(self.scheduled_fixture_path(), "r", encoding="utf-8") as handle:
            fixture = json.load(handle)
        fixture["trace_id"] = "world_driven_invisible_scheduled_event"
        adjudication = fixture["mock_agent_outputs"]["world"][0][
            "world_tick_result"
        ]["adjudication"]
        adjudication["committed_events"][0]["visibility"]["scope"] = "system_restricted"
        adjudication["committed_events"][0]["visibility"]["scope_ref"] = "system:archive_dawn"
        adjudication["committed_events"][0]["visibility"]["observer_refs"] = []
        adjudication["visibility_results"][0]["scope"] = "system_restricted"
        adjudication["visibility_results"][0]["scope_ref"] = "system:archive_dawn"
        adjudication["visibility_results"][0]["observer_refs"] = []
        review = _find_authority_review(
            fixture, "world_adjudication", "wadj_dawn_bell_001"
        )
        review["subject_sha256"] = hashlib.sha256(
            stable_json(adjudication).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "allowed")
        self.assertEqual(
            [run["agent_name"] for run in trace["agent_runs"]],
            ["world", "authority"],
        )
        self.assertFalse(trace["narration_segments"])
        self.assertEqual(len(trace["skipped_narration_checkpoints"]), 1)
        self.assertEqual(
            trace["skipped_narration_checkpoints"][0]["reason"],
            "no_events_visible_under_pov_contract",
        )

    def test_public_scope_instances_do_not_share_membership(self) -> None:
        fixture = self.load_fixture()
        fixture["public_scope_registry"] = {
            "institution:archive": {
                "scope_type": "institution_public",
                "members": ["char_wei"],
            },
            "institution:court": {
                "scope_type": "institution_public",
                "members": ["char_lin"],
            },
        }
        event = {
            "visibility": {
                "scope": "institution_public",
                "scope_ref": "institution:archive",
                "observer_refs": [],
                "limits": "surface_only",
            }
        }

        self.assertFalse(event_visible_to(event, "char_wei", fixture))
        self.assertFalse(event_visible_to(event, "char_lin", fixture))
        self.assertFalse(event_directly_observed_by(event, "char_wei", fixture))

        public_record = {
            "effective_scope": "institution_public",
            "scope_ref": "institution:archive",
        }
        self.assertTrue(public_event_available_to(public_record, "char_wei", fixture))
        self.assertFalse(public_event_available_to(public_record, "char_lin", fixture))

        event["visibility"]["observer_refs"] = ["char_wei"]
        self.assertTrue(event_visible_to(event, "char_wei", fixture))
        self.assertTrue(event_directly_observed_by(event, "char_wei", fixture))
        self.assertFalse(event_visible_to(event, "char_lin", fixture))

    def test_public_scope_membership_alone_does_not_write_private_memory(self) -> None:
        fixture = self.load_fixture()
        fixture["public_scope_registry"] = {
            "institution:archive": {
                "scope_type": "institution_public",
                "members": ["char_wei", "char_lin"],
            }
        }
        event = {
            "event_id": "evt_public_not_directly_observed",
            "actors": [],
            "outcome": "An archive notice is issued.",
            "public_surface": "A notice is posted.",
            "visibility": {
                "scope": "institution_public",
                "scope_ref": "institution:archive",
                "observer_refs": [],
                "limits": "report_encounter_required",
            },
        }
        runtime_state = {"committed_world_events": [event]}

        handoff = _derive_memory_handoff(fixture, runtime_state, "sp_test")
        self.assertEqual(handoff["derived_memory_deltas"], [])

        event["visibility"]["observer_refs"] = ["char_wei"]
        handoff = _derive_memory_handoff(fixture, runtime_state, "sp_test")
        self.assertEqual(
            [item["owner_agent_id"] for item in handoff["derived_memory_deltas"]],
            ["char_wei"],
        )

    def test_public_event_encounter_requires_scope_membership(self) -> None:
        fixture = self.load_fixture()
        fixture["public_scope_registry"]["institution:royal_archive"]["members"] = [
            "char_wei"
        ]

        self.assertEqual(
            [item["publication_id"] for item in encountered_public_events(fixture, "char_wei")],
            ["pub_dawn_inspection_001"],
        )
        self.assertEqual(encountered_public_events(fixture, "char_lin"), [])

    def test_candidate_material_remains_out_of_downstream_agent_contexts(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        adjudication = fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        adjudication["publication_candidates"] = [
            {
                "publication_candidate_id": "pc_secret_001",
                "source_event_ref": "ev_wei_probe_001",
                "proposed_scope": "institution_public",
                "scope_ref": "institution:royal_archive",
                "candidate_summary": "CANDIDATE_ONLY_SECRET",
                "status": "pending",
                "visibility": "system_restricted",
                "based_on": ["ev_wei_probe_001"],
                "expires_after_ticks": 2,
            }
        ]
        review = _find_authority_review(fixture, "world_adjudication", "wadj_wei_001")
        review["subject_sha256"] = hashlib.sha256(
            stable_json(adjudication).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "allowed")
        for run in trace["agent_runs"]:
            if run["agent_name"] in {"character", "plot", "narrator"}:
                self.assertNotIn(
                    "CANDIDATE_ONLY_SECRET", stable_json(run["projected_context"])
                )
        self.assertEqual(
            trace["scene_packet"]["publication_candidates"][0]["status"],
            "pending",
        )

    def test_candidate_without_expiry_is_quarantined(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        adjudication = fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        adjudication["publication_candidates"] = [
            {
                "publication_candidate_id": "pc_no_expiry",
                "source_event_ref": "ev_wei_probe_001",
                "proposed_scope": "institution_public",
                "scope_ref": "institution:royal_archive",
                "candidate_summary": "Pending publication with no lifecycle.",
                "status": "pending",
                "visibility": "system_restricted",
                "based_on": ["ev_wei_probe_001"],
            }
        ]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "missing_security_critical_field"
                for item in trace["validation"]["world_tick_1"]
            )
        )

    def test_malformed_response_contract_is_quarantined_without_exception(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_malformed_response_contract"
        request = fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "next_directive"
        ]["decision_request"]
        request["response_contract"] = "Return whatever seems dramatic."

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertTrue(
            any(
                item["code"] == "invalid_response_contract"
                for item in trace["validation"]["world_tick_0"]
            )
        )

    def test_narration_claim_map_must_cover_every_prose_unit(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        narrator_output = fixture["mock_agent_outputs"]["narrator"]
        if isinstance(narrator_output, list):
            narrator_output = narrator_output[0]
        narrator_output["prose"] += " Wei already knew where the stolen ledger was hidden."
        review = _find_authority_review(fixture, "narration")
        checkpoint_id = review["subject_ref"]
        subject = {
            "source_checkpoint_id": checkpoint_id,
            "source_event_refs": ["ev_wei_probe_001", "ev_lin_reply_001"],
            "prose": narrator_output["prose"],
        }
        subject["claim_units"] = build_narration_claim_units(
            subject["prose"], checkpoint_id
        )
        review["subject_sha256"] = hashlib.sha256(
            stable_json(subject).encode("utf-8")
        ).hexdigest()

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_checkpoint")
        self.assertTrue(
            any(
                item["code"] == "incomplete_prose_coverage"
                for item in trace["validation"][
                    f"authority_narration_{checkpoint_id}"
                ]
            )
        )

    def test_semantic_judge_block_survives_a_fresh_subject_hash(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_semantic_judge_block"
        adjudication = fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        event = adjudication["committed_events"][0]
        event["outcome"] = "The archive explodes without any causal basis."
        event["public_surface"] = "The archive explodes."
        review = _find_authority_review(fixture, "world_adjudication", "wadj_wei_001")
        review["subject_sha256"] = hashlib.sha256(
            stable_json(adjudication).encode("utf-8")
        ).hexdigest()
        review["verdict"] = "block"
        review["findings"] = ["The outcome is not causally grounded in the proposal."]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_adjudication")
        self.assertTrue(
            any(
                item["code"] == "authority_block"
                for item in trace["validation"][
                    "authority_world_adjudication_wadj_wei_001"
                ]
            )
        )
        self.assertFalse(trace["runtime_state"]["committed_world_events"])

    def test_malformed_model_json_is_quarantined_without_runtime_exception(self) -> None:
        cases: list[tuple[str, str, str]] = []

        consumed_fixture = copy.deepcopy(self.load_fixture())
        consumed_fixture["trace_id"] = "world_driven_bad_consumed_refs"
        consumed_fixture["mock_agent_outputs"]["world"][0]["world_tick_result"][
            "consumed_input_refs"
        ] = 7
        consumed_trace = self.run_temp_fixture(consumed_fixture)
        cases.append(
            (
                consumed_trace["runtime_status"],
                "world_tick_0",
                "invalid_consumed_input_refs",
            )
        )

        outcome_fixture = copy.deepcopy(self.load_fixture())
        outcome_fixture["trace_id"] = "world_driven_bad_outcome_enum"
        outcome_fixture["mock_agent_outputs"]["world"][1]["world_tick_result"][
            "adjudication"
        ]["outcome_type"] = {"pretend": "success"}
        outcome_trace = self.run_temp_fixture(outcome_fixture)
        cases.append(
            (outcome_trace["runtime_status"], "world_tick_1", "invalid_outcome_type")
        )

        verdict_fixture = copy.deepcopy(self.load_fixture())
        verdict_fixture["trace_id"] = "world_driven_bad_authority_enum"
        verdict_fixture["mock_agent_outputs"]["authority"][0]["authority_review"][
            "verdict"
        ] = {"pretend": "allow"}
        verdict_trace = self.run_temp_fixture(verdict_fixture)
        cases.append(
            (
                verdict_trace["runtime_status"],
                "authority_decision_request_cdr_wei_001",
                "invalid_verdict",
            )
        )

        traces = [consumed_trace, outcome_trace, verdict_trace]
        for trace, (status, stage, code) in zip(traces, cases):
            with self.subTest(stage=stage):
                self.assertTrue(status.startswith("quarantined"))
                self.assertEqual(trace["final_decision"], "blocked")
                self.assertTrue(
                    any(item["code"] == code for item in trace["validation"][stage])
                )

    def test_missing_user_request_quarantines_before_projection(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_missing_user_request"
        fixture.pop("user_request")

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_fixture")
        self.assertFalse(trace["agent_runs"])
        self.assertFalse(trace["projection_manifests"])
        self.assertTrue(
            any(
                item["code"] == "missing_user_request"
                for item in trace["validation"]["world_fixture"]
            )
        )

    def test_duplicate_projection_source_ids_quarantine_before_projection(self) -> None:
        fixture = copy.deepcopy(self.load_fixture())
        fixture["trace_id"] = "world_driven_duplicate_source_ids"
        duplicate_public = copy.deepcopy(fixture["public_event_ledger"][0])
        duplicate_public["public_summary"] = "A contradictory duplicate summary."
        fixture["public_event_ledger"].append(duplicate_public)
        fixture["scheduled_world_events"] = [
            {"schedule_id": "sched_duplicate"},
            {"schedule_id": "sched_duplicate"},
        ]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["runtime_status"], "quarantined_world_fixture")
        self.assertFalse(trace["agent_runs"])
        self.assertFalse(trace["projection_manifests"])
        self.assertGreaterEqual(
            sum(
                item["code"] == "duplicate_projection_source_id"
                for item in trace["validation"]["world_fixture"]
            ),
            2,
        )

    def test_non_string_protocol_id_is_blocked_before_routing(self) -> None:
        for suffix, route_id in [("non_string", 7), ("overlong", "r" * 129)]:
            fixture = copy.deepcopy(self.load_fixture())
            fixture["trace_id"] = f"world_driven_{suffix}_route_id"
            fixture["mock_agent_outputs"]["router"][0]["route_plan"][
                "route_id"
            ] = route_id

            trace = self.run_temp_fixture(fixture)

            with self.subTest(route_id=suffix):
                self.assertEqual(
                    trace["runtime_status"], "quarantined_character_decision"
                )
                self.assertTrue(
                    any(
                        item["code"] == "invalid_protocol_id"
                        for item in trace["validation"]["route_cdr_wei_001"]
                    )
                )

    def test_private_self_and_scene_pair_visibility_are_owner_bound(self) -> None:
        private_fixture = copy.deepcopy(self.load_fixture())
        private_fixture["trace_id"] = "world_driven_private_self_mismatch"
        adjudication = private_fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        visibility = adjudication["committed_events"][0]["visibility"]
        visibility.update(
            {
                "scope": "private_self",
                "scope_ref": "char_wei",
                "observer_refs": ["char_lin"],
            }
        )
        result = adjudication["visibility_results"][0]
        result.update(
            {
                "scope": "private_self",
                "scope_ref": "char_wei",
                "observer_refs": ["char_lin"],
            }
        )
        private_trace = self.run_temp_fixture(private_fixture)
        self.assertTrue(
            any(
                item["code"] == "private_self_owner_mismatch"
                for item in private_trace["validation"]["world_tick_1"]
            )
        )

        pair_fixture = copy.deepcopy(self.load_fixture())
        pair_fixture["trace_id"] = "world_driven_scene_pair_outsider"
        pair_fixture["characters"]["char_outside"] = {
            "status": "available",
            "private_memory": [],
        }
        adjudication = pair_fixture["mock_agent_outputs"]["world"][1][
            "world_tick_result"
        ]["adjudication"]
        adjudication["committed_events"][0]["visibility"]["observer_refs"] = [
            "char_wei",
            "char_outside",
        ]
        adjudication["visibility_results"][0]["observer_refs"] = [
            "char_wei",
            "char_outside",
        ]
        pair_trace = self.run_temp_fixture(pair_fixture)
        self.assertTrue(
            any(
                item["code"] == "invalid_scene_pair"
                for item in pair_trace["validation"]["world_tick_1"]
            )
        )

    def test_rejected_plot_pulse_cannot_commit_pulse_adjudication(self) -> None:
        with open(self.scheduled_fixture_path(), "r", encoding="utf-8") as handle:
            fixture = json.load(handle)
        world_tick = copy.deepcopy(
            fixture["mock_agent_outputs"]["world"][0]["world_tick_result"]
        )
        pulse = {
            "pulse_id": "pulse_rejected_001",
            "pulse_sha256": "a" * 64,
            "original_plot_pulse": {},
        }
        adjudication = world_tick["adjudication"]
        adjudication["input_type"] = "plot_pulse"
        adjudication["input_ref"] = pulse["pulse_id"]
        adjudication["input_sha256"] = pulse["pulse_sha256"]
        for event in adjudication["committed_events"]:
            event["source_input_type"] = "plot_pulse"
            event["source_input_ref"] = pulse["pulse_id"]
            event["causal_basis"] = [
                pulse["pulse_id"],
                adjudication["adjudication_id"],
            ]
        world_tick["consumed_input_refs"] = [pulse["pulse_id"]]
        world_tick["plot_pulse_disposition"] = {
            "pulse_id": pulse["pulse_id"],
            "pulse_sha256": pulse["pulse_sha256"],
            "decision": "rejected",
            "translation_summary": "World rejects the pressure.",
            "world_condition_refs": [],
        }

        violations = validate_world_tick(
            world_tick,
            expected_tick_index=0,
            pending_approved_proposal=None,
            pending_plot_pulse=pulse,
            existing_world_condition_refs=set(),
            scheduled_world_event_hashes={},
            expected_scene_id=fixture["scene_id"],
            character_ids=set(fixture["characters"]),
            public_scope_registry=fixture["public_scope_registry"],
            scene_participant_ids=fixture["scene_participant_ids"],
        )
        self.assertTrue(
            any(
                item["code"] == "inactive_disposition_has_adjudication"
                for item in violations
            )
        )

    def test_output_token_caps_block_before_state_transition(self) -> None:
        tokens = dict(DEFAULT_AGENT_OUTPUT_TOKENS)
        tokens["world"] = 1
        config = RunnerConfig(
            llm_mode="mock",
            model="mock-world-runtime",
            max_llm_calls_per_trace=24,
            total_output_token_budget=80000,
            per_agent_max_output_tokens=tokens,
        )

        trace = run_trace(self.fixture_path(), self.tmp, config)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual(trace["runtime_status"], "quarantined_world_tick")
        self.assertFalse(trace["world_ticks"])
        self.assertFalse(trace["world_adjudications"])
        self.assertEqual(trace["scene_packet"]["commit_status"], "quarantined")
        self.assertTrue(
            any(
                item["code"] == "per_agent_output_token_budget_exceeded"
                for item in trace["validation"]["runtime_budget"]
            )
        )


def _recursive_dict_keys(value: Any) -> set[str]:
    keys: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            keys.add(key)
            keys.update(_recursive_dict_keys(item))
    elif isinstance(value, list):
        for item in value:
            keys.update(_recursive_dict_keys(item))
    return keys


def _find_authority_review(
    fixture: dict[str, Any], subject_type: str, subject_ref: str | None = None
) -> dict[str, Any]:
    for output in fixture["mock_agent_outputs"].get("authority", []):
        review = output.get("authority_review", {})
        if review.get("subject_type") != subject_type:
            continue
        if subject_ref is not None and review.get("subject_ref") != subject_ref:
            continue
        return review
    raise AssertionError(
        f"Authority fixture lacks {subject_type!r} review for {subject_ref!r}"
    )


if __name__ == "__main__":
    unittest.main()
