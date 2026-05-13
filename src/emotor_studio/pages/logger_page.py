"""Telemetry logger page."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from PySide6 import QtWidgets

from emotor_studio.config import load_signals
from emotor_studio.models import TelemetrySample


class LoggerPage(QtWidgets.QWidget):
    def __init__(
        self,
        signal_schema: list[dict[str, Any]] | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._signal_schema = [signal for signal in (signal_schema or load_signals()) if signal.get("logger", False)]
        self._signal_names = [str(signal["name"]) for signal in self._signal_schema]
        self._samples: list[dict[str, object]] = []
        self._recording = True
        self._max_table_rows = 250

        layout = QtWidgets.QVBoxLayout(self)
        toolbar = QtWidgets.QHBoxLayout()
        self.record_box = QtWidgets.QCheckBox("Record")
        self.record_box.setChecked(True)
        self.record_box.toggled.connect(self._set_recording)
        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.clicked.connect(self.clear)
        export_button = QtWidgets.QPushButton("Export CSV")
        export_button.clicked.connect(self._choose_export_path)
        self.counter = QtWidgets.QLabel("Samples: 0")
        toolbar.addWidget(self.record_box)
        toolbar.addWidget(clear_button)
        toolbar.addWidget(export_button)
        toolbar.addWidget(self.counter, 1)
        layout.addLayout(toolbar)

        columns = ["timestamp", "rpm", "target_rpm", *self._signal_names]
        self.table = QtWidgets.QTableWidget(0, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    @property
    def samples(self) -> list[dict[str, object]]:
        return list(self._samples)

    @property
    def signal_names(self) -> list[str]:
        return list(self._signal_names)

    def update_telemetry(self, sample: TelemetrySample) -> None:
        if not self._recording:
            return
        row_data = self._sample_to_row(sample)
        self._samples.append(row_data)
        self._append_table_row(row_data)
        self.counter.setText(f"Samples: {len(self._samples)}")

    def clear(self) -> None:
        self._samples.clear()
        self.table.setRowCount(0)
        self.counter.setText("Samples: 0")

    def export_csv(self, path: str | Path) -> Path:
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        columns = ["timestamp", "rpm", "target_rpm", *self._signal_names]
        with export_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self._samples)
        return export_path

    def _sample_to_row(self, sample: TelemetrySample) -> dict[str, object]:
        row: dict[str, object] = {
            "timestamp": sample.timestamp,
            "rpm": sample.rpm,
            "target_rpm": sample.target_rpm,
        }
        for name in self._signal_names:
            row[name] = sample.signals.get(name, "")
        return row

    def _append_table_row(self, row_data: dict[str, object]) -> None:
        if self.table.rowCount() >= self._max_table_rows:
            self.table.removeRow(0)
        row = self.table.rowCount()
        self.table.insertRow(row)
        for column in range(self.table.columnCount()):
            key = self.table.horizontalHeaderItem(column).text()
            value = row_data.get(key, "")
            self.table.setItem(row, column, QtWidgets.QTableWidgetItem(self._format_value(value)))

    def _choose_export_path(self) -> None:
        path, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Export Telemetry CSV",
            "emotor_studio_log.csv",
            "CSV Files (*.csv)",
        )
        if path:
            self.export_csv(path)

    def _set_recording(self, enabled: bool) -> None:
        self._recording = enabled

    @staticmethod
    def _format_value(value: object) -> str:
        if isinstance(value, float):
            return f"{value:.6g}"
        return str(value)
