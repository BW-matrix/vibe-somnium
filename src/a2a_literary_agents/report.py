"""Human-readable trace reports."""

from __future__ import annotations

from typing import Any

from .json_util import stable_json


def write_report(path: str, trace: dict[str, Any]) -> None:
    lines: list[str] = []
    lines.append(f"# Trace Report: {trace['trace_id']}")
    lines.append("")
    lines.append(f"- Final decision: `{trace.get('final_decision', 'unknown')}`")
    lines.append(f"- LLM mode: `{trace.get('llm_mode')}`")
    lines.append(f"- Model: `{trace.get('model')}`")
    if trace.get("runtime_mode"):
        lines.append(f"- Runtime mode: `{trace.get('runtime_mode')}`")
    if trace.get("runtime_status"):
        lines.append(f"- Runtime status: `{trace.get('runtime_status')}`")
    if trace.get("run_id"):
        lines.append(f"- Run ID: `{trace.get('run_id')}`")
    if trace.get("run_nonce"):
        lines.append(f"- Run nonce: `{trace.get('run_nonce')}`")
    lines.append("")

    token_usage = trace.get("token_usage", {})
    if token_usage:
        lines.append("## Token Usage")
        lines.append("")
        lines.append("```json")
        lines.append(stable_json(token_usage))
        lines.append("```")
        lines.append("")

    if trace.get("interface_normalization"):
        lines.append("## Interface Normalization")
        lines.append("")
        lines.append("```json")
        lines.append(stable_json(trace.get("interface_normalization", [])))
        lines.append("```")
        lines.append("")

    lines.append("## Projection Manifests")
    lines.append("")
    for manifest in trace.get("projection_manifests", []):
        lines.append("```json")
        lines.append(stable_json(manifest))
        lines.append("```")
        lines.append("")

    lines.append("## Agent Runs")
    lines.append("")
    for run in trace.get("agent_runs", []):
        instance = run.get("agent_instance_id")
        stage = run.get("protocol_stage")
        label = f"{run['agent_name']} Agent"
        if instance:
            label += f" / {instance}"
        lines.append(f"### {label}")
        lines.append("")
        if stage:
            lines.append(f"- Protocol stage: `{stage}`")
            lines.append("")
        lines.append("#### Projected Context")
        lines.append("```json")
        lines.append(stable_json(run.get("projected_context")))
        lines.append("```")
        lines.append("")
        lines.append("#### Raw Output")
        lines.append("```json")
        lines.append(run.get("raw_output") or "")
        lines.append("```")
        if run.get("error"):
            lines.append("")
            lines.append(f"- Error: `{run['error']}`")
        lines.append("")

    if "scene_packet" in trace:
        lines.append("## Sealed ScenePacket")
        lines.append("")
        lines.append("```json")
        lines.append(stable_json(trace["scene_packet"]))
        lines.append("```")
        lines.append("")

    if "memory_handoff" in trace:
        lines.append("## Memory Handoff")
        lines.append("")
        lines.append("```json")
        lines.append(stable_json(trace["memory_handoff"]))
        lines.append("```")
        lines.append("")

    if trace.get("runtime_mode") == "world_driven":
        lines.append("## World-Driven Runtime")
        lines.append("")
        for key in [
            "transaction",
            "world_ticks",
            "route_plans",
            "event_proposals",
            "approved_event_proposals",
            "authority_reviews",
            "repair_attempts",
            "world_adjudications",
            "plot_pulses",
            "plot_pulse_dispositions",
            "consumed_plot_pulses",
            "deferred_plot_pulses",
            "narration_segments",
            "published_narration_segments",
            "quarantined_narration_segments",
            "skipped_narration_checkpoints",
            "normalization_records",
            "runtime_state",
            "quarantined_runtime_state",
        ]:
            if key not in trace:
                continue
            lines.append(f"### {key}")
            lines.append("```json")
            lines.append(stable_json(trace.get(key, [])))
            lines.append("```")
            lines.append("")

    lines.append("## Validation")
    lines.append("")
    lines.append("```json")
    lines.append(stable_json(trace.get("validation", {})))
    lines.append("```")
    lines.append("")

    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))
        handle.write("\n")
