"""Session report page."""

from __future__ import annotations

from pathlib import Path
from statistics import mean
from typing import Callable

from PySide6 import QtWidgets


SampleProvider = Callable[[], list[dict[str, object]]]


class ReportPage(QtWidgets.QWidget):
    def __init__(
        self,
        sample_provider: SampleProvider | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._sample_provider = sample_provider or (lambda: [])

        layout = QtWidgets.QVBoxLayout(self)
        toolbar = QtWidgets.QHBoxLayout()
        refresh_button = QtWidgets.QPushButton("Refresh Report")
        refresh_button.clicked.connect(self.refresh)
        export_button = QtWidgets.QPushButton("Export Markdown")
        export_button.clicked.connect(self._choose_export_path)
        toolbar.addWidget(refresh_button)
        toolbar.addWidget(export_button)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        self.report_text = QtWidgets.QPlainTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)
        self.refresh()

    def refresh(self) -> None:
        self.report_text.setPlainText(self.build_report())

    def build_report(self) -> str:
        samples = self._sample_provider()
        if not samples:
            return "# eMotor-Studio Session Report\n\nNo telemetry samples recorded yet.\n"

        first = self._float_value(samples[0].get("timestamp"))
        last = self._float_value(samples[-1].get("timestamp"))
        duration = max(0.0, last - first)
        lines = [
            "# eMotor-Studio Session Report",
            "",
            "## Summary",
            "",
            f"- Samples: {len(samples)}",
            f"- Duration: {duration:.2f} s",
            "",
            "## Key Signals",
            "",
            "| Signal | Min | Mean | Max |",
            "|---|---:|---:|---:|",
        ]
        for key in [
            "rpm",
            "target_rpm",
            "mechanical_speed",
            "speed_target_mechanical",
            "bus_voltage",
            "bus_current",
            "current_d",
            "current_q",
            "mos_temperature",
            "coil_temperature",
            "fault_word",
        ]:
            values = [self._float_value(sample.get(key)) for sample in samples if self._is_number(sample.get(key))]
            if not values:
                continue
            lines.append(f"| {key} | {min(values):.3f} | {mean(values):.3f} | {max(values):.3f} |")
        lines.extend(
            [
                "",
                "## Notes",
                "",
                "- Generated from MockBackend telemetry aligned to AxDr_L signal naming.",
                "- Real hardware communication is not implemented in this phase.",
                "",
            ]
        )
        return "\n".join(lines)

    def export_markdown(self, path: str | Path) -> Path:
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(self.build_report(), encoding="utf-8")
        return export_path

    def _choose_export_path(self) -> None:
        path, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Session Report",
            "emotor_studio_report.md",
            "Markdown Files (*.md)",
        )
        if path:
            self.export_markdown(path)

    @staticmethod
    def _is_number(value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @staticmethod
    def _float_value(value: object) -> float:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return 0.0
