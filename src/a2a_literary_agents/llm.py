"""LLM adapters for model-agents.

The runner supports real OpenAI-compatible chat completions, but the protocol
does not depend on a live model. Mock mode is used for deterministic fixtures
and tests.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

from .config import RunnerConfig
from .json_util import parse_json_object
from .token_usage import build_token_usage


@dataclass
class AgentCompletion:
    agent_name: str
    mode: str
    prompt: str
    raw_output: str
    parsed_output: dict[str, Any] | None
    error: str | None = None
    token_usage: dict[str, Any] | None = None


class AgentProvider:
    def complete(
        self,
        agent_name: str,
        prompt: str,
        fixture: dict[str, Any],
        runtime_bindings: dict[str, str] | None = None,
    ) -> AgentCompletion:
        raise NotImplementedError


class MockAgentProvider(AgentProvider):
    def __init__(self, config: RunnerConfig | None = None):
        self.config = config or RunnerConfig(llm_mode="mock", model="mock")
        self.call_counts: dict[str, int] = {}

    def complete(
        self,
        agent_name: str,
        prompt: str,
        fixture: dict[str, Any],
        runtime_bindings: dict[str, str] | None = None,
    ) -> AgentCompletion:
        output = fixture.get("mock_agent_outputs", {}).get(agent_name)
        if isinstance(output, list):
            call_index = self.call_counts.get(agent_name, 0)
            self.call_counts[agent_name] = call_index + 1
            output = output[call_index] if call_index < len(output) else None
        output = _resolve_mock_bindings(output, runtime_bindings or {})
        if output is None:
            output = {
                "agent": agent_name,
                "status": "mock_missing",
                "summary": f"No mock output configured for {agent_name}.",
            }
        raw = json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True)
        return AgentCompletion(
            agent_name=agent_name,
            mode="mock",
            prompt=prompt,
            raw_output=raw,
            parsed_output=output,
            token_usage=build_token_usage(
                agent_name=agent_name,
                mode="mock",
                model=self.config.model,
                input_text=prompt,
                output_text=raw,
                max_output_tokens=self.config.max_tokens_for(agent_name),
                input_text_basis="runner_prompt",
            ),
        )


class OpenAICompatibleAgentProvider(AgentProvider):
    def __init__(self, config: RunnerConfig):
        self.config = config
        self.calls_made = 0

    def complete(
        self,
        agent_name: str,
        prompt: str,
        fixture: dict[str, Any],
        runtime_bindings: dict[str, str] | None = None,
    ) -> AgentCompletion:
        if not self.config.api_key:
            return AgentCompletion(
                agent_name=agent_name,
                mode="real",
                prompt=prompt,
                raw_output="",
                parsed_output=None,
                error="missing_api_key",
            )
        if self.calls_made >= self.config.max_llm_calls_per_trace:
            return AgentCompletion(
                agent_name=agent_name,
                mode="real",
                prompt=prompt,
                raw_output="",
                parsed_output=None,
                error="max_llm_calls_exceeded",
            )

        self.calls_made += 1
        system_prompt = (
            "You are one bounded model-agent inside the a2a-literary-agents protocol. "
            "Use only the projected context in the user message. Return valid JSON only. "
            "Do not invent hidden facts, broaden visibility, or bypass authority boundaries."
        )
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": self.config.temperature,
        }
        payload[self.config.token_field] = self.config.max_tokens_for(agent_name)
        request_text = json.dumps(payload["messages"], ensure_ascii=False, sort_keys=True)

        request = urllib.request.Request(
            url=f"{self.config.base_url.rstrip('/')}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
                body = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            return AgentCompletion(agent_name, "real", prompt, detail, None, f"http_error_{exc.code}")
        except Exception as exc:  # pragma: no cover - environment dependent
            return AgentCompletion(agent_name, "real", prompt, "", None, f"request_error: {exc}")

        raw = body.get("choices", [{}])[0].get("message", {}).get("content", "")
        parsed, parse_error = parse_json_object(raw)
        return AgentCompletion(
            agent_name=agent_name,
            mode="real",
            prompt=prompt,
            raw_output=raw,
            parsed_output=parsed,
            error=parse_error,
            token_usage=build_token_usage(
                agent_name=agent_name,
                mode="real",
                model=self.config.model,
                input_text=request_text,
                output_text=raw,
                max_output_tokens=self.config.max_tokens_for(agent_name),
                provider_usage=body.get("usage"),
                input_text_basis="chat_messages",
            ),
        )


class CodexCliAgentProvider(AgentProvider):
    """Use an isolated headless Codex CLI process as the model backend."""

    def __init__(self, config: RunnerConfig):
        self.config = config
        self.calls_made = 0

    def complete(
        self,
        agent_name: str,
        prompt: str,
        fixture: dict[str, Any],
        runtime_bindings: dict[str, str] | None = None,
    ) -> AgentCompletion:
        if self.calls_made >= self.config.max_llm_calls_per_trace:
            return AgentCompletion(
                agent_name=agent_name,
                mode="codex-cli",
                prompt=prompt,
                raw_output="",
                parsed_output=None,
                error="max_llm_calls_exceeded",
            )

        self.calls_made += 1
        os.makedirs(self.config.codex_home, exist_ok=True)
        os.makedirs(self.config.codex_workdir, exist_ok=True)

        try:
            reasoning_effort = _normalize_codex_reasoning_effort(
                self.config.codex_reasoning_effort
            )
        except ValueError as exc:
            return AgentCompletion(
                agent_name=agent_name,
                mode="codex-cli",
                prompt=prompt,
                raw_output="",
                parsed_output=None,
                error=f"invalid_codex_reasoning_effort: {exc}",
            )

        with tempfile.TemporaryDirectory(prefix=f"a2a_codex_{agent_name}_") as tmp:
            output_path = os.path.join(tmp, "last-message.json")

            command = [
                self.config.codex_binary,
                "exec",
                "--model",
                self.config.model,
                "--sandbox",
                "read-only",
                "-c",
                "approval_policy=\"never\"",
                "-c",
                f"model_reasoning_effort=\"{reasoning_effort}\"",
                "-c",
                "web_search=\"disabled\"",
                "-c",
                "shell_environment_policy.inherit=\"none\"",
                "-c",
                "shell_environment_policy.ignore_default_excludes=false",
                "-c",
                "allow_login_shell=false",
                "--disable",
                "shell_tool",
                "--strict-config",
                "--ephemeral",
                "--ignore-rules",
                "--ignore-user-config",
                "--skip-git-repo-check",
                "--cd",
                self.config.codex_workdir,
                "--json",
                "--output-last-message",
                output_path,
                "--color",
                "never",
                "-",
            ]
            env = _isolated_codex_env(self.config.codex_home)

            provider_prompt = _codex_cli_prompt(agent_name, prompt, self.config.max_tokens_for(agent_name))
            try:
                completed = subprocess.run(
                    command,
                    input=provider_prompt,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    timeout=self.config.timeout_seconds,
                    env=env,
                    cwd=self.config.codex_workdir,
                    check=False,
                )
            except subprocess.TimeoutExpired:
                return AgentCompletion(agent_name, "codex-cli", prompt, "", None, "codex_cli_timeout")
            except FileNotFoundError:
                return AgentCompletion(agent_name, "codex-cli", prompt, "", None, "codex_cli_not_found")
            except Exception as exc:  # pragma: no cover - environment dependent
                return AgentCompletion(agent_name, "codex-cli", prompt, "", None, f"codex_cli_error: {exc}")

            raw = _read_text_if_exists(output_path) or completed.stdout.strip()
            provider_usage = _usage_from_codex_jsonl(completed.stdout)
            token_usage = build_token_usage(
                agent_name=agent_name,
                mode="codex-cli",
                model=self.config.model,
                input_text=provider_prompt,
                output_text=raw,
                max_output_tokens=self.config.max_tokens_for(agent_name),
                provider_usage=provider_usage,
                input_text_basis="codex_cli_stdin",
            )
            if completed.returncode != 0:
                detail = completed.stderr.strip() or completed.stdout.strip() or f"exit_code={completed.returncode}"
                return AgentCompletion(agent_name, "codex-cli", prompt, raw, None, f"codex_cli_failed: {detail}", token_usage)

            parsed, parse_error = parse_json_object(raw)
            if parsed and isinstance(parsed.get("payload"), dict):
                parsed = parsed["payload"]
            return AgentCompletion(
                agent_name=agent_name,
                mode="codex-cli",
                prompt=prompt,
                raw_output=raw,
                parsed_output=parsed,
                error=parse_error,
                token_usage=token_usage,
            )


class AutoAgentProvider(AgentProvider):
    def __init__(self, config: RunnerConfig):
        self.real = OpenAICompatibleAgentProvider(config)
        self.mock = MockAgentProvider(config)
        self.has_key = bool(config.api_key)

    def complete(
        self,
        agent_name: str,
        prompt: str,
        fixture: dict[str, Any],
        runtime_bindings: dict[str, str] | None = None,
    ) -> AgentCompletion:
        if not self.has_key:
            return self.mock.complete(agent_name, prompt, fixture, runtime_bindings)
        # Mixing real and fixture outputs mid-trace breaks call ordering and can
        # launder a provider failure into an apparently valid protocol result.
        return self.real.complete(agent_name, prompt, fixture, runtime_bindings)


def build_provider(config: RunnerConfig) -> AgentProvider:
    if config.llm_mode == "mock":
        return MockAgentProvider(config)
    if config.llm_mode == "codex-cli":
        return CodexCliAgentProvider(config)
    if config.llm_mode == "real":
        return OpenAICompatibleAgentProvider(config)
    if config.llm_mode == "auto":
        return AutoAgentProvider(config)
    raise ValueError(f"Unknown llm mode: {config.llm_mode}")


def _generic_json_object_schema() -> dict[str, Any]:
    return {"type": "object", "additionalProperties": True}


def _normalize_codex_reasoning_effort(value: str) -> str:
    normalized = value.strip().lower() if isinstance(value, str) else ""
    if normalized == "max":
        return "xhigh"
    if normalized in {"none", "minimal", "low", "medium", "high", "xhigh"}:
        return normalized
    raise ValueError(
        "expected max, none, minimal, low, medium, high, or xhigh"
    )


def _codex_cli_prompt(agent_name: str, prompt: str, max_output_tokens: int) -> str:
    return (
        "You are being called as a headless model backend for a2a-literary-agents.\n"
        "Do not inspect files, edit files, run shell commands, use network tools, or ask follow-up questions.\n"
        "Return only the JSON object requested by the projected protocol prompt.\n"
        f"Agent name: {agent_name}\n"
        f"Approximate maximum output budget: {max_output_tokens} tokens.\n\n"
        f"{prompt}"
    )


def _isolated_codex_env(codex_home: str) -> dict[str, str]:
    # The model backend must not inherit API keys, GitHub tokens, or arbitrary
    # application secrets from the parent runner. Codex auth comes only from
    # the dedicated CODEX_HOME; shell tools are disabled separately.
    safe_parent_keys = {
        "COMSPEC",
        "NUMBER_OF_PROCESSORS",
        "OS",
        "PATH",
        "PATHEXT",
        "PROCESSOR_ARCHITECTURE",
        "SYSTEMDRIVE",
        "SYSTEMROOT",
        "TEMP",
        "TMP",
        "WINDIR",
    }
    env = {
        key: value
        for key, value in os.environ.items()
        if key.upper() in safe_parent_keys and isinstance(value, str)
    }
    isolated_home = os.path.abspath(codex_home)
    isolated_appdata = os.path.join(isolated_home, "AppData", "Roaming")
    isolated_localappdata = os.path.join(isolated_home, "AppData", "Local")
    os.makedirs(isolated_appdata, exist_ok=True)
    os.makedirs(isolated_localappdata, exist_ok=True)
    env["CODEX_HOME"] = isolated_home
    env["HOME"] = isolated_home
    env["USERPROFILE"] = isolated_home
    env["APPDATA"] = isolated_appdata
    env["LOCALAPPDATA"] = isolated_localappdata
    env["NO_COLOR"] = "1"
    return env


def _read_text_if_exists(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def _resolve_mock_bindings(value: Any, bindings: dict[str, str]) -> Any:
    """Resolve explicit fixture placeholders that model an Agent echoing run data."""

    if isinstance(value, dict):
        return {key: _resolve_mock_bindings(item, bindings) for key, item in value.items()}
    if isinstance(value, list):
        return [_resolve_mock_bindings(item, bindings) for item in value]
    if isinstance(value, str) and value.startswith("$"):
        binding = bindings.get(value[1:])
        if binding is not None:
            return binding
    return value


def _usage_from_codex_jsonl(stdout: str) -> dict[str, Any] | None:
    """Extract token usage from `codex exec --json` event streams."""

    usage: dict[str, Any] | None = None
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed" and isinstance(event.get("usage"), dict):
            usage = event["usage"]
    return usage
