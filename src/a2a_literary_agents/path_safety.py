"""Fail-closed filesystem paths for persisted runtime traces."""

from __future__ import annotations

import os
import re
from pathlib import Path


_SAFE_PATH_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,127}$")
_SAFE_PATH_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{index}" for index in range(1, 10)),
    *(f"LPT{index}" for index in range(1, 10)),
}


def is_safe_path_id(value: object) -> bool:
    """Return whether an identifier is safe as one filesystem segment."""

    return (
        isinstance(value, str)
        and bool(_SAFE_PATH_ID.fullmatch(value))
        and not value.endswith(".")
        and value.split(".", 1)[0].upper() not in _WINDOWS_RESERVED_NAMES
    )


def resolve_run_directory(out_dir: str, trace_id: str, run_id: str) -> str:
    """Resolve a run directory and prove that it remains below ``out_dir``."""

    if not is_safe_path_id(trace_id):
        raise ValueError("trace_id must be a safe protocol identifier")
    if (
        not isinstance(run_id, str)
        or not _SAFE_PATH_SEGMENT.fullmatch(run_id)
        or run_id.endswith(".")
        or run_id.split(".", 1)[0].upper() in _WINDOWS_RESERVED_NAMES
    ):
        raise ValueError("run_id must be a safe path segment")

    root = Path(out_dir).resolve()
    candidate = (root / trace_id / run_id).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError("resolved run directory escapes out_dir") from exc

    if os.path.commonpath((os.fspath(root), os.fspath(candidate))) != os.fspath(root):
        raise ValueError("resolved run directory escapes out_dir")
    return os.fspath(candidate)
