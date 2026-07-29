"""Run two committed World-driven scenes with an audited campaign handoff."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import replace


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from a2a_literary_agents.campaign_study import (
    MAX_STUDY_ROUNDS,
    build_followup_fixture,
    evaluate_continuity_study,
    materialize_scene_one,
    render_study_report,
)
from a2a_literary_agents.config import RunnerConfig
from a2a_literary_agents.json_util import load_json_file, write_json_file
from a2a_literary_agents.runner import run_trace


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run a two-scene World-driven continuity study."
    )
    parser.add_argument("--scene-one", required=True)
    parser.add_argument(
        "--reuse-scene-one-trace",
        help="Reuse one committed Scene 1 trace and run only the follow-up scene.",
    )
    parser.add_argument("--scene-two-template", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--llm-mode",
        choices=["auto", "real", "codex-cli", "mock"],
        default="codex-cli",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=MAX_STUDY_ROUNDS,
        help="Hard cap applied to both World ticks and LLM calls per scene.",
    )
    args = parser.parse_args()

    if not 1 <= args.max_rounds <= MAX_STUDY_ROUNDS:
        parser.error(f"--max-rounds must be between 1 and {MAX_STUDY_ROUNDS}")

    scene_two_template = load_json_file(args.scene_two_template)
    if args.llm_mode == "mock" and not isinstance(
        scene_two_template.get("mock_agent_outputs"), dict
    ):
        parser.error(
            "--llm-mode mock requires mock_agent_outputs in the Scene 2 "
            "template; the bundled real-study template intentionally omits them"
        )

    study_dir = os.path.abspath(args.out)
    input_dir = os.path.join(study_dir, "inputs")
    run_dir = os.path.join(study_dir, "runs")
    os.makedirs(input_dir, exist_ok=True)
    os.makedirs(run_dir, exist_ok=True)

    environment_config = RunnerConfig.from_env(llm_mode=args.llm_mode)
    config = replace(
        environment_config,
        max_llm_calls_per_trace=args.max_rounds,
        total_output_token_budget=max(
            environment_config.total_output_token_budget,
            1_000_000,
        ),
    )

    scene_one_fixture = materialize_scene_one(
        load_json_file(args.scene_one),
        max_rounds=args.max_rounds,
    )
    scene_one_path = os.path.join(input_dir, "scene_one.materialized.json")
    write_json_file(scene_one_path, scene_one_fixture)

    if args.reuse_scene_one_trace:
        scene_one_trace = load_json_file(args.reuse_scene_one_trace)
        scene_one_elapsed = float(scene_one_trace.get("elapsed_seconds", 0.0))
    else:
        scene_one_started = time.perf_counter()
        scene_one_trace = run_trace(scene_one_path, run_dir, config)
        scene_one_wall_elapsed = time.perf_counter() - scene_one_started
        scene_one_elapsed = float(
            scene_one_trace.get("elapsed_seconds", scene_one_wall_elapsed)
        )

    partial = {
        "study_type": "two_scene_continuity",
        "study_version": "v0.3",
        "max_rounds_per_scene": args.max_rounds,
        "scene_one": {
            "trace_id": scene_one_trace.get("trace_id"),
            "run_id": scene_one_trace.get("run_id"),
            "final_decision": scene_one_trace.get("final_decision"),
            "runtime_status": scene_one_trace.get("runtime_status"),
            "transaction_status": scene_one_trace.get("transaction", {}).get(
                "status"
            ),
            "elapsed_seconds": round(scene_one_elapsed, 6),
            "artifact_paths": scene_one_trace.get("artifacts", {}),
        },
    }
    if (
        scene_one_trace.get("final_decision") != "allowed"
        or scene_one_trace.get("transaction", {}).get("status") != "committed"
    ):
        partial["continuity_verdict"] = "not_run_scene_one_failed"
        write_json_file(os.path.join(study_dir, "study.partial.json"), partial)
        return 2

    try:
        scene_two_fixture = build_followup_fixture(
            scene_one_fixture,
            scene_two_template,
            scene_one_trace,
            max_rounds=args.max_rounds,
        )
    except ValueError as exc:
        partial["continuity_verdict"] = "not_run_invalid_scene_one_handoff"
        partial["error"] = str(exc)
        write_json_file(
            os.path.join(study_dir, "study.partial.json"),
            partial,
        )
        print(str(exc), file=sys.stderr)
        return 2
    scene_two_path = os.path.join(input_dir, "scene_two.materialized.json")
    write_json_file(scene_two_path, scene_two_fixture)

    scene_two_started = time.perf_counter()
    scene_two_trace = run_trace(scene_two_path, run_dir, config)
    scene_two_wall_elapsed = time.perf_counter() - scene_two_started
    scene_two_elapsed = float(
        scene_two_trace.get("elapsed_seconds", scene_two_wall_elapsed)
    )

    study = evaluate_continuity_study(
        scene_one_fixture,
        scene_two_fixture,
        scene_one_trace,
        scene_two_trace,
        scene_elapsed_seconds={
            "scene_one": scene_one_elapsed,
            "scene_two": scene_two_elapsed,
        },
        max_rounds=args.max_rounds,
    )
    study["runner_config"] = {
        "llm_mode": config.llm_mode,
        "model": config.model,
        "codex_reasoning_effort": config.codex_reasoning_effort,
        "max_llm_calls_per_trace": config.max_llm_calls_per_trace,
        "total_output_token_budget": config.total_output_token_budget,
        "per_agent_max_output_tokens": config.per_agent_max_output_tokens,
        "timeout_seconds": config.timeout_seconds,
    }
    study_json_path = os.path.join(study_dir, "study.json")
    study_report_path = os.path.join(study_dir, "study.md")
    write_json_file(study_json_path, study)
    with open(study_report_path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(render_study_report(study))

    print(
        json.dumps(
            {
                "continuity_verdict": study["continuity_verdict"],
                "study_json": study_json_path,
                "study_report": study_report_path,
                "combined": study["combined"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if study["continuity_verdict"] == "pass" else 3


if __name__ == "__main__":
    raise SystemExit(main())
