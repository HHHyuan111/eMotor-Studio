"""Telemetry logger page."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from PySide6 import QtWidgets

from emotor_studio.config import load_signals
from emotor_studio.models import TelemetrySample
from emotor_studio.ui.components import KpiCard, PageHeader, SectionCard


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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("数据记录", "记录 Mock 遥测样本并导出 CSV，后续真实通信复用同一字段集合。"))

        status_row = QtWidgets.QHBoxLayout()
        self.record_card = KpiCard("记录状态", "当前采样开关", "ok")
        self.count_card = KpiCard("样本数量", "已记录样本", "idle")
        self.path_card = KpiCard("导出路径", "最近一次导出", "idle")
        status_row.addWidget(self.record_card)
        status_row.addWidget(self.count_card)
        status_row.addWidget(self.path_card, 2)
        layout.addLayout(status_row)

        toolbar_card = SectionCard("操作栏")
        toolbar = QtWidgets.QHBoxLayout()
        self.record_box = QtWidgets.QCheckBox("停止记录")
        self.record_box.setChecked(True)
        self.record_box.toggled.connect(self._set_recording)
        clear_button = QtWidgets.QPushButton("清空记录")
        clear_button.setProperty("variant", "ghost")
        clear_button.clicked.connect(self.clear)
        export_button = QtWidgets.QPushButton("导出 CSV")
        export_button.setProperty("variant", "primary")
        export_button.clicked.connect(self._choose_export_path)
        toolbar.addWidget(self.record_box)
        toolbar.addWidget(clear_button)
        toolbar.addWidget(export_button)
        toolbar.addStretch(1)
        toolbar_card.body.addLayout(toolbar)
        layout.addWidget(toolbar_card)

        table_card = SectionCard("最近样本")
        columns = ["timestamp", "rpm", "target_rpm", *self._signal_names]
        self.table = QtWidgets.QTableWidget(0, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(28)
        table_card.body.addWidget(self.table)
        layout.addWidget(table_card, 1)
        self._update_cards("-")

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
        self._update_cards()

    def clear(self) -> None:
        self._samples.clear()
        self.table.setRowCount(0)
        self._update_cards("-")

    def export_csv(self, path: str | Path) -> Path:
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        columns = ["timestamp", "rpm", "target_rpm", *self._signal_names]
        with export_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(self._samples)
        self._update_cards(str(export_path))
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
            "导出记录 CSV",
            "emotor_studio_log.csv",
            "CSV Files (*.csv)",
        )
        if path:
            self.export_csv(path)

    def _set_recording(self, enabled: bool) -> None:
        self._recording = enabled
        self.record_box.setText("停止记录" if enabled else "开始记录")
        self._update_cards()

    def _update_cards(self, export_path: str | None = None) -> None:
        self.record_card.set_value("记录中" if self._recording else "已暂停", "telemetry logger", "ok" if self._recording else "stop")
        self.count_card.set_value(str(len(self._samples)), "samples", "idle")
        if export_path is not None:
            self.path_card.set_value(export_path, "CSV", "idle")

    @staticmethod
    def _format_value(value: object) -> str:
        if isinstance(value, float):
            return f"{value:.6g}"
        return str(value)
