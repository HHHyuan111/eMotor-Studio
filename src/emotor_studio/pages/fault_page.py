"""Fault diagnostics page."""

from __future__ import annotations

from PySide6 import QtWidgets

from emotor_studio.config import load_fault_codes
from emotor_studio.models import FaultEvent, TelemetrySample
from emotor_studio.ui.components import KpiCard, PageHeader, SectionCard


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
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("故障诊断", "显示当前故障字、活动故障和 Mock 故障历史。"))

        top = QtWidgets.QHBoxLayout()
        top.setSpacing(12)
        layout.addLayout(top)
        self.current_card = KpiCard("当前故障", "活动故障数量", "ok")
        self.fault_word_card = KpiCard("故障字", "PMSM fault bitmask", "ok")
        top.addWidget(self.current_card)
        top.addWidget(self.fault_word_card)
        clear_button = QtWidgets.QPushButton("清空故障历史")
        clear_button.setProperty("variant", "ghost")
        clear_button.clicked.connect(self.clear_events)
        top.addWidget(clear_button)
        top.addStretch(1)

        active_card = SectionCard("活动故障")
        self.active_table = QtWidgets.QTableWidget(0, 5)
        self.active_table.setHorizontalHeaderLabels(["位", "故障码", "等级", "名称", "说明"])
        self.active_table.horizontalHeader().setStretchLastSection(True)
        self.active_table.setAlternatingRowColors(True)
        active_card.body.addWidget(self.active_table)
        layout.addWidget(active_card)

        history_card = SectionCard("故障历史")
        self.table = QtWidgets.QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["时间", "故障码", "等级", "名称", "消息", "是否激活"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        history_card.body.addWidget(self.table)
        layout.addWidget(history_card, 1)
        self.update_fault_word(0)

    def add_fault(self, fault: FaultEvent) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        schema = self._fault_by_code.get(fault.code, {})
        values = [
            f"{fault.timestamp:.3f}",
            fault.code,
            self._level_text(fault.level.value),
            str(schema.get("display_name") or fault.code),
            fault.message,
            "是" if fault.active else "否",
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
        if active:
            self.current_card.set_value(f"{len(active)} 项", "当前存在活动故障", "fault")
            self.fault_word_card.set_value(f"0x{fault_word:08X}", "请检查活动故障表", "fault")
        else:
            self.current_card.set_value("当前无故障", "系统状态正常", "ok")
            self.fault_word_card.set_value(f"0x{fault_word:08X}", "无活动故障位", "ok")
        self.active_table.setRowCount(len(active))
        for row, item in enumerate(active):
            values = [
                str(item.get("bit", "")),
                str(item.get("code", "")),
                self._level_text(str(item.get("level", ""))),
                str(item.get("display_name", "")),
                str(item.get("description", "")),
            ]
            for column, value in enumerate(values):
                self.active_table.setItem(row, column, QtWidgets.QTableWidgetItem(value))

    def clear_events(self) -> None:
        self.table.setRowCount(0)

    @staticmethod
    def _level_text(value: str) -> str:
        return {
            "info": "信息",
            "warning": "警告",
            "critical": "严重",
        }.get(value, value)
