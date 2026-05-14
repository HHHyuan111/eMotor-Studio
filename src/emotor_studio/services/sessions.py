"""Experiment-session export helpers.

Session packages keep reports, traces, metrics, and safety notes together so
future hardware runs can be reviewed, reproduced, and analyzed without relying
on scattered files.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime
from io import StringIO
from pathlib import Path
from time import time
from typing import Any

from emotor_studio.models import CurrentLoopPiSuggestion, ExperimentResult
from emotor_studio.services.tuning import build_current_loop_tuning_report


SESSION_SCHEMA_VERSION = "emotor_studio_session_v0"


def build_pi_suggestions_csv(suggestions: tuple[CurrentLoopPiSuggestion, ...]) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(
        [
            "axis",
            "kp",
            "ki",
            "unit_kp",
            "unit_ki",
            "target_bandwidth_hz",
            "resistance_ohm",
            "inductance_h",
            "note",
        ]
    )
    for item in suggestions:
        writer.writerow(
            [
                item.axis,
                f"{item.kp:.12g}",
                f"{item.ki:.12g}",
                item.unit_kp,
                item.unit_ki,
                f"{item.target_bandwidth_hz:.12g}",
                f"{item.resistance_ohm:.12g}",
                f"{item.inductance_h:.12g}",
                item.note,
            ]
        )
    return buffer.getvalue()


def build_validation_trace_csv(validation: ExperimentResult) -> str:
    buffer = StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["time_s", "target", "response", "unit"])
    for time_s, target, response in zip(
        validation.trace.time_s,
        validation.trace.target,
        validation.trace.response,
    ):
        writer.writerow([f"{time_s:.12g}", f"{target:.12g}", f"{response:.12g}", validation.trace.unit])
    return buffer.getvalue()


def build_validation_metrics_payload(validation: ExperimentResult) -> dict[str, Any]:
    metrics = validation.metrics
    return {
        "task": validation.task.name,
        "target_signal": validation.task.target,
        "unit": validation.trace.unit,
        "metrics": {
            "initial_value": metrics.initial_value,
            "final_value": metrics.final_value,
            "target_value": metrics.target_value,
            "rise_time_s": metrics.rise_time_s,
            "settling_time_s": metrics.settling_time_s,
            "overshoot_percent": metrics.overshoot_percent,
            "steady_state_error": metrics.steady_state_error,
        },
        "summary": validation.summary,
    }


def build_current_loop_session_manifest(
    suggestions: tuple[CurrentLoopPiSuggestion, ...],
    validation: ExperimentResult,
    session_name: str,
    generated_at: float | None = None,
) -> dict[str, Any]:
    generated_at = time() if generated_at is None else generated_at
    return {
        "schema_version": SESSION_SCHEMA_VERSION,
        "session_type": "current_loop_tuning",
        "session_name": session_name,
        "generated_at_unix": generated_at,
        "generated_at_local": datetime.fromtimestamp(generated_at).isoformat(timespec="seconds"),
        "backend": "Mock",
        "target_firmware": "AxDr_L-aligned Mock",
        "hardware_connection": "not_connected",
        "artifacts": [
            "session_manifest.json",
            "tuning_report.md",
            "pi_suggestions.csv",
            "validation_trace.csv",
            "validation_metrics.json",
            "config_snapshot.json",
            "safety_notes.md",
        ],
        "pi_suggestions": [
            {
                "axis": item.axis,
                "kp": item.kp,
                "ki": item.ki,
                "target_bandwidth_hz": item.target_bandwidth_hz,
                "resistance_ohm": item.resistance_ohm,
                "inductance_h": item.inductance_h,
                "unit_kp": item.unit_kp,
                "unit_ki": item.unit_ki,
            }
            for item in suggestions
        ],
        "validation": build_validation_metrics_payload(validation),
        "safety": {
            "mock_only": True,
            "real_write_back_enabled": False,
            "requires_manual_confirmation_before_hardware": True,
        },
    }


def save_current_loop_tuning_session(
    suggestions: tuple[CurrentLoopPiSuggestion, CurrentLoopPiSuggestion],
    validation: ExperimentResult,
    directory: str | Path,
    session_name: str = "current_loop_tuning",
) -> dict[str, Path]:
    output_root = Path(directory)
    output_root.mkdir(parents=True, exist_ok=True)
    timestamp = int(time())
    session_dir = _unique_directory(output_root / f"{session_name}_{timestamp}")
    session_dir.mkdir(parents=True, exist_ok=False)

    manifest = build_current_loop_session_manifest(suggestions, validation, session_dir.name, timestamp)
    artifacts = {
        "directory": session_dir,
        "manifest": session_dir / "session_manifest.json",
        "report": session_dir / "tuning_report.md",
        "pi_suggestions": session_dir / "pi_suggestions.csv",
        "validation_trace": session_dir / "validation_trace.csv",
        "validation_metrics": session_dir / "validation_metrics.json",
        "config_snapshot": session_dir / "config_snapshot.json",
        "safety_notes": session_dir / "safety_notes.md",
    }

    artifacts["manifest"].write_text(_json(manifest), encoding="utf-8")
    artifacts["report"].write_text(build_current_loop_tuning_report(suggestions, validation), encoding="utf-8")
    artifacts["pi_suggestions"].write_text(build_pi_suggestions_csv(suggestions), encoding="utf-8")
    artifacts["validation_trace"].write_text(build_validation_trace_csv(validation), encoding="utf-8")
    artifacts["validation_metrics"].write_text(_json(build_validation_metrics_payload(validation)), encoding="utf-8")
    artifacts["config_snapshot"].write_text(_json(_config_snapshot_placeholder()), encoding="utf-8")
    artifacts["safety_notes"].write_text(_safety_notes(), encoding="utf-8")
    return artifacts


def _unique_directory(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(1, 1000):
        candidate = path.with_name(f"{path.name}_{index:02d}")
        if not candidate.exists():
            return candidate
    raise RuntimeError(f"Cannot allocate unique session directory below {path.parent}.")


def _config_snapshot_placeholder() -> dict[str, Any]:
    return {
        "status": "placeholder",
        "backend": "Mock",
        "note": "Real firmware/config snapshots will be attached after AxDr_L protocol integration.",
        "expected_future_sources": [
            "configs/signals.json",
            "configs/parameters.json",
            "configs/commands.json",
            "configs/fault_codes.json",
            "firmware_info",
        ],
    }


def _safety_notes() -> str:
    return "\n".join(
        [
            "# Safety Notes",
            "",
            "- This session package is generated from Mock data.",
            "- Do not write PI values to real AxDr_L hardware without protocol support, range checks, safe-state checks, and manual confirmation.",
            "- Validate current-loop response before enabling speed or position loops.",
            "- Keep raw telemetry and config snapshots together with the report once real hardware is connected.",
            "",
        ]
    )


def _json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
