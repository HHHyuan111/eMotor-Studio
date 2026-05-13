"""Fault page."""

from __future__ import annotations

from PySide6 import QtWidgets

from emotor_studio.config import load_fault_codes
from emotor_studio.models import FaultEvent, TelemetrySample


class FaultPage(QtWidgets.QWidget):
    def __init__(
        self,
        fault_schema: list[dict[str, object]] | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._fault_schema = fault_schema or load_fault_codes()
        self._fault_by_code = {str(item["code"]): item for item in self._fault_schema}

        layout = QtWidgets.QVBoxLayout(self)
        toolbar = QtWidgets.QHBoxLayout()
        clear_button = QtWidgets.QPushButton("Clear Event Log")
        clear_button.clicked.connect(self.clear_events)
        self.summary_label = QtWidgets.QLabel("Fault word: 0x00000000")
        toolbar.addWidget(clear_button)
        toolbar.addWidget(self.summary_label, 1)
        layout.addLayout(toolbar)

        self.active_table = QtWidgets.QTableWidget(0, 5)
        self.active_table.setHorizontalHeaderLabels(["Bit", "Code", "Level", "Name", "Description"])
        self.active_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.active_table)

        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Time", "Code", "Level", "Name", "Message", "Active"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

    def add_fault(self, fault: FaultEvent) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        schema = self._fault_by_code.get(fault.code, {})
        values = [
            f"{fault.timestamp:.3f}",
            fault.code,
            fault.level.value,
            str(schema.get("display_name") or fault.code),
            fault.message,
            "yes" if fault.active else "no",
        ]
        for column, value in enumerate(values):
            self.table.setItem(row, column, QtWidgets.QTableWidgetItem(value))

    def update_telemetry(self, sample: TelemetrySample) -> None:
        self.update_fault_word(sample.fault_word)

    def update_fault_word(self, fault_word: int) -> None:
        active = [
            item
            for item in self._fault_schema
            if fault_word & (1 << int(item.get("bit", -1)))
        ]
        self.summary_label.setText(f"Fault word: 0x{fault_word:08X}  Active faults: {len(active)}")
        self.active_table.setRowCount(len(active))
        for row, item in enumerate(active):
            values = [
                str(item.get("bit", "")),
                str(item.get("code", "")),
                str(item.get("level", "")),
                str(item.get("display_name", "")),
                str(item.get("description", "")),
            ]
            for column, value in enumerate(values):
                self.active_table.setItem(row, column, QtWidgets.QTableWidgetItem(value))

    def clear_events(self) -> None:
        self.table.setRowCount(0)
