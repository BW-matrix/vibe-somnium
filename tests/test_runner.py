from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from a2a_literary_agents.config import RunnerConfig
from a2a_literary_agents.llm import CodexCliAgentProvider
from a2a_literary_agents.runner import run_trace
from a2a_literary_agents.token_usage import build_token_usage, estimate_tokens
from a2a_literary_agents.validation import validate_plot


class TraceRunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="a2a_trace_test_")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp)

    def fixture(self, name: str) -> str:
        return os.path.join(ROOT, "fixtures", "traces", name)

    def run_fixture(self, name: str):
        config = RunnerConfig.from_env(llm_mode="mock")
        return run_trace(self.fixture(name), self.tmp, config)

    def run_temp_fixture(self, fixture: dict):
        path = os.path.join(self.tmp, f"{fixture['trace_id']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fixture, f)
        config = RunnerConfig.from_env(llm_mode="mock")
        return run_trace(path, self.tmp, config)

    def test_runner_timeout_defaults_to_max_reasoning_safe_window(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(RunnerConfig.from_env(llm_mode="codex-cli").timeout_seconds, 240)

        with patch.dict(os.environ, {"A2A_LLM_TIMEOUT_SECONDS": "90"}, clear=True):
            self.assertEqual(RunnerConfig.from_env(llm_mode="codex-cli").timeout_seconds, 90)

    def test_allowed_trace_runs_full_pipeline(self) -> None:
        trace = self.run_fixture("allowed_archive_probe.json")
        self.assertEqual(trace["final_decision"], "allowed")
        self.assertEqual(trace["runtime_mode"], "legacy_window_v0.1")
        self.assertEqual([run["agent_name"] for run in trace["agent_runs"]], ["plot", "character", "world", "narrator", "judge"])
        self.assertIn("scene_packet", trace)
        self.assertEqual(trace["judge_report"]["verdict"], "allow")
        self.assertIn("memory_handoff", trace)
        self.assertIn("token_usage", trace)
        self.assertEqual(trace["token_usage"]["totals"]["agent_count"], 5)
        self.assertGreater(trace["token_usage"]["totals"]["total_tokens"], 0)
        self.assertTrue(trace["token_usage"]["totals"]["estimated_agent_count"] >= 5)
        self.assertIn("token_usage", trace["agent_runs"][0])
        self.assertTrue(os.path.exists(trace["artifacts"]["trace_json"]))
        self.assertTrue(os.path.exists(trace["artifacts"]["report_md"]))
        with open(trace["artifacts"]["report_md"], "r", encoding="utf-8") as f:
            self.assertIn("## Token Usage", f.read())

    def test_warning_does_not_stop_pipeline(self) -> None:
        with open(self.fixture("allowed_archive_probe.json"), "r", encoding="utf-8") as f:
            fixture = json.load(f)
        fixture["trace_id"] = "allowed_warning_budget"
        fixture["mock_agent_outputs"]["plot"]["scene_pressure_packet"]["budget_cost"] = "low"

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "allowed")
        self.assertEqual([run["agent_name"] for run in trace["agent_runs"]], ["plot", "character", "world", "narrator", "judge"])
        self.assertFalse(trace["validation"]["plot"])
        self.assertTrue(any(item["code"] == "normalized_string_budget_cost" for item in trace["interface_normalization"]))

    def test_world_alias_interfaces_feed_memory_handoff(self) -> None:
        with open(self.fixture("allowed_archive_probe.json"), "r", encoding="utf-8") as f:
            fixture = json.load(f)
        fixture["trace_id"] = "allowed_world_aliases"
        bundle = fixture["mock_agent_outputs"]["world"]["world_resolution_bundle"]
        bundle["resolved_events"] = [
            {
                "event_id": "ev_alias_001",
                "event_type": "private_procedural_probe",
                "participants": ["char_wei", "char_lin"],
                "summary": "Wei asks Lin a careful private procedural question.",
                "visibility": "scene_pair",
            }
        ]
        bundle["state_deltas"] = [
            {
                "state_delta_id": "sd_alias_001",
                "target_ref": "char_lin",
                "change_type": "add",
                "after": "Lin may privately read Wei as suspicious.",
            }
        ]
        bundle["visibility_results"] = [
            {
                "visibility_id": "vis_alias_001",
                "audience": ["char_wei", "char_lin"],
                "scope": "private_character_facing",
                "summary": "Wei and Lin witnessed the private procedural exchange.",
            }
        ]
        bundle["authorized_interiority"] = [
            {
                "character_id": "char_lin",
                "authorized_contents": ["Lin may interpret Wei's restraint as suspicious."],
                "scope_limit": "one_window",
            }
        ]

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "allowed")
        self.assertFalse(trace["validation"]["world"])
        codes = {item["code"] for item in trace["interface_normalization"]}
        self.assertIn("audience_alias", codes)
        self.assertIn("scope_alias", codes)
        self.assertIn("character_id_alias", codes)
        self.assertIn("state_delta_id_alias", codes)
        self.assertIn("target_ref_alias", codes)
        self.assertTrue(trace["memory_handoff"]["derived_memory_deltas"])
        lin_projection = next(item for item in trace["memory_handoff"]["owner_projections"] if item["owner_agent_id"] == "char_lin")
        self.assertIn("vis_alias_001", lin_projection["owner_visibility"])

    def test_missing_interiority_scope_limit_blocks(self) -> None:
        with open(self.fixture("allowed_archive_probe.json"), "r", encoding="utf-8") as f:
            fixture = json.load(f)
        fixture["trace_id"] = "missing_scope_limit"
        for item in fixture["mock_agent_outputs"]["world"]["world_resolution_bundle"]["authorized_interiority"]:
            item.pop("scope_limit", None)

        trace = self.run_temp_fixture(fixture)

        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual([run["agent_name"] for run in trace["agent_runs"]], ["plot", "character", "world"])
        self.assertTrue(any(item["code"] == "missing_interiority_field" for item in trace["validation"]["world"]))

    def test_repeated_runs_do_not_overwrite_previous_trace(self) -> None:
        first = self.run_fixture("allowed_archive_probe.json")
        second = self.run_fixture("allowed_archive_probe.json")

        self.assertNotEqual(first["artifacts"]["trace_json"], second["artifacts"]["trace_json"])
        self.assertTrue(os.path.exists(first["artifacts"]["trace_json"]))
        self.assertTrue(os.path.exists(second["artifacts"]["trace_json"]))

    def test_missing_or_unknown_runtime_mode_never_falls_back(self) -> None:
        with open(self.fixture("allowed_archive_probe.json"), "r", encoding="utf-8") as f:
            fixture = json.load(f)
        fixture.pop("runtime_mode")
        with self.assertRaisesRegex(ValueError, "runtime_mode"):
            self.run_temp_fixture(fixture)

    def test_legacy_trace_id_cannot_escape_output_directory(self) -> None:
        with open(self.fixture("allowed_archive_probe.json"), "r", encoding="utf-8") as f:
            fixture = json.load(f)
        fixture["trace_id"] = r"..\escaped_legacy"
        fixture_path = os.path.join(self.tmp, "malicious-legacy.json")
        with open(fixture_path, "w", encoding="utf-8") as handle:
            json.dump(fixture, handle)
        out_dir = os.path.join(self.tmp, "artifacts")

        with self.assertRaisesRegex(ValueError, "trace_id"):
            run_trace(
                fixture_path,
                out_dir,
                RunnerConfig.from_env(llm_mode="mock"),
            )

        self.assertFalse(os.path.exists(os.path.join(self.tmp, "escaped_legacy")))

        fixture["runtime_mode"] = "world_drivn"
        with self.assertRaisesRegex(ValueError, "runtime_mode"):
            self.run_temp_fixture(fixture)

    def test_narrator_leak_is_blocked_after_full_pipeline(self) -> None:
        trace = self.run_fixture("adversarial_narrator_leak.json")
        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual([run["agent_name"] for run in trace["agent_runs"]], ["plot", "character", "world", "narrator", "judge"])
        self.assertTrue(trace["validation"]["narrator"])
        self.assertTrue(trace["validation"]["judge"])
        self.assertEqual(trace["judge_report"]["verdict"], "block")

    def test_plot_railroading_is_blocked_early(self) -> None:
        trace = self.run_fixture("adversarial_plot_railroading.json")
        self.assertEqual(trace["final_decision"], "blocked")
        self.assertEqual([run["agent_name"] for run in trace["agent_runs"]], ["plot"])
        self.assertTrue(trace["validation"]["plot"])

    def test_config_loads_codex_oauth_auth_json(self) -> None:
        auth_path = os.path.join(self.tmp, "auth.json")
        with open(auth_path, "w", encoding="utf-8") as f:
            json.dump({"tokens": {"access_token": "oauth-token"}}, f)

        with patch.dict(os.environ, {"A2A_LLM_AUTH_JSON": auth_path}, clear=True):
            config = RunnerConfig.from_env(llm_mode="real")

        self.assertEqual(config.api_key, "oauth-token")
        self.assertEqual(config.auth_json_path, auth_path)

    def test_explicit_bearer_token_wins_over_auth_json(self) -> None:
        auth_path = os.path.join(self.tmp, "auth.json")
        with open(auth_path, "w", encoding="utf-8") as f:
            json.dump({"tokens": {"access_token": "oauth-token"}}, f)

        env = {
            "A2A_LLM_AUTH_JSON": auth_path,
            "A2A_LLM_BEARER_TOKEN": "explicit-token",
        }
        with patch.dict(os.environ, env, clear=True):
            config = RunnerConfig.from_env(llm_mode="real")

        self.assertEqual(config.api_key, "explicit-token")

    def test_trace_artifacts_never_serialize_provider_credentials(self) -> None:
        secret = "provider-secret-must-not-appear"
        auth_path = os.path.join(self.tmp, "private-auth.json")
        config = RunnerConfig(
            llm_mode="mock",
            model="mock-model",
            api_key=secret,
            auth_json_path=auth_path,
        )

        trace = run_trace(self.fixture("allowed_archive_probe.json"), self.tmp, config)
        serialized = json.dumps(trace, ensure_ascii=False)
        with open(trace["artifacts"]["report_md"], "r", encoding="utf-8") as handle:
            report = handle.read()

        self.assertNotIn(secret, serialized)
        self.assertNotIn(auth_path, serialized)
        self.assertNotIn(secret, report)
        self.assertNotIn(auth_path, report)

    def test_codex_cli_provider_uses_isolated_codex_home(self) -> None:
        codex_home = os.path.join(self.tmp, "codex-home")
        codex_workdir = os.path.join(self.tmp, "codex-workdir")
        config = RunnerConfig(
            llm_mode="codex-cli",
            model="gpt-5.5",
            codex_binary="codex",
            codex_home=codex_home,
            codex_workdir=codex_workdir,
        )
        captured = {}

        def fake_run(command, input, text, encoding, errors, capture_output, timeout, env, cwd, check):
            captured["command"] = command
            captured["input"] = input
            captured["env"] = env
            captured["cwd"] = cwd
            output_path = command[command.index("--output-last-message") + 1]
            with open(output_path, "w", encoding="utf-8") as f:
                f.write('{"agent": "plot", "ok": true}')

            class Completed:
                returncode = 0
                stdout = '{"type":"turn.completed","usage":{"input_tokens":42,"cached_input_tokens":7,"output_tokens":11,"reasoning_output_tokens":0}}\n'
                stderr = ""

            return Completed()

        with patch.dict(os.environ, {"DUMMY_SECRET_TOKEN": "must-not-leak"}):
            with patch("subprocess.run", fake_run):
                result = CodexCliAgentProvider(config).complete("plot", "Return JSON.", {})

        self.assertIsNone(result.error)
        self.assertEqual(result.parsed_output, {"agent": "plot", "ok": True})
        self.assertEqual(result.token_usage["mode"], "codex-cli")
        self.assertEqual(result.token_usage["source"], "provider_usage")
        self.assertFalse(result.token_usage["is_estimated"])
        self.assertEqual(result.token_usage["input_tokens"], 42)
        self.assertEqual(result.token_usage["output_tokens"], 11)
        self.assertEqual(captured["env"]["CODEX_HOME"], codex_home)
        self.assertNotIn("DUMMY_SECRET_TOKEN", captured["env"])
        self.assertFalse(any(key.startswith("A2A_") for key in captured["env"]))
        self.assertEqual(captured["cwd"], codex_workdir)
        self.assertIn("--ephemeral", captured["command"])
        self.assertIn("--json", captured["command"])
        self.assertIn("--ignore-user-config", captured["command"])
        self.assertIn("--ignore-rules", captured["command"])
        self.assertIn("--skip-git-repo-check", captured["command"])
        self.assertIn('approval_policy="never"', captured["command"])
        self.assertIn('model_reasoning_effort="xhigh"', captured["command"])
        self.assertIn('web_search="disabled"', captured["command"])
        self.assertIn('shell_environment_policy.inherit="none"', captured["command"])
        self.assertIn("--strict-config", captured["command"])
        disable_index = captured["command"].index("--disable")
        self.assertEqual(captured["command"][disable_index + 1], "shell_tool")
        self.assertIn("Do not inspect files", captured["input"])

    def test_codex_cli_rejects_unknown_reasoning_effort_without_fallback(self) -> None:
        config = RunnerConfig(
            llm_mode="codex-cli",
            model="gpt-5.5",
            codex_binary="codex",
            codex_home=os.path.join(self.tmp, "codex-home"),
            codex_workdir=os.path.join(self.tmp, "codex-workdir"),
            codex_reasoning_effort="dramatic",
        )

        with patch("subprocess.run") as run:
            result = CodexCliAgentProvider(config).complete("world", "Return JSON.", {})

        self.assertIn("invalid_codex_reasoning_effort", result.error or "")
        run.assert_not_called()

    def test_plot_validator_handles_non_object_budget(self) -> None:
        violations = validate_plot(
            {
                "pressure_kind": "deadline",
                "scope": "scene",
                "duration": "one_window",
                "affected_options": ["delay costs more"],
                "non_forcing_clause": "Either character may refuse.",
                "forbidden_outcomes": ["forced confession"],
                "visibility": "system_restricted",
                "budget_cost": "medium",
            }
        )

        self.assertTrue(any(item["code"] == "invalid_budget_cost" for item in violations))
        self.assertFalse(any(item["severity"] == "block" for item in violations))

    def test_token_estimator_counts_cjk_text_more_conservatively(self) -> None:
        self.assertGreaterEqual(estimate_tokens("中文中文"), 4)
        self.assertGreater(estimate_tokens("Return exactly one JSON object."), 0)

    def test_token_usage_rejects_negative_counts_and_marks_partial_usage(self) -> None:
        negative = build_token_usage(
            agent_name="world",
            mode="codex-cli",
            model="test",
            input_text="input",
            output_text="output",
            max_output_tokens=100,
            provider_usage={"input_tokens": -5, "output_tokens": -500, "total_tokens": -505},
        )
        self.assertEqual(negative["source"], "estimated_local")
        self.assertGreaterEqual(negative["input_tokens"], 0)
        self.assertGreaterEqual(negative["output_tokens"], 0)

        partial = build_token_usage(
            agent_name="world",
            mode="codex-cli",
            model="test",
            input_text="input text",
            output_text="output text",
            max_output_tokens=100,
            provider_usage={"total_tokens": 99},
        )
        self.assertEqual(partial["source"], "provider_usage_partial")
        self.assertTrue(partial["is_estimated"])
        self.assertEqual(partial["total_tokens"], 99)
        self.assertEqual(partial["count_provenance"]["input_tokens"], "estimated_local")

        inconsistent = build_token_usage(
            agent_name="world",
            mode="codex-cli",
            model="test",
            input_text="input text",
            output_text="output text",
            max_output_tokens=100,
            provider_usage={"input_tokens": 10, "output_tokens": 5, "total_tokens": 999},
        )
        self.assertEqual(inconsistent["source"], "estimated_local")
        self.assertTrue(inconsistent["is_estimated"])
        self.assertEqual(
            inconsistent["total_tokens"],
            inconsistent["input_tokens"] + inconsistent["output_tokens"],
        )


if __name__ == "__main__":
    unittest.main()
