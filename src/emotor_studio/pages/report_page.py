"""Session report page."""

from __future__ import annotations

from pathlib import Path
import os
from statistics import mean
from typing import Callable

from PySide6 import QtWidgets

from emotor_studio.ui.components import InfoBox, KpiCard, PageHeader, SectionCard


SampleProvider = Callable[[], list[dict[str, object]]]


class ReportPage(QtWidgets.QWidget):
    def __init__(
        self,
        sample_provider: SampleProvider | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._sample_provider = sample_provider or (lambda: [])
        self._last_export_path: Path | None = None

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("调试报告", "从数据记录样本生成 Markdown 报告，用于课程记录和调试复盘。"))

        top = QtWidgets.QHBoxLayout()
        self.sample_card = KpiCard("报告样本", "当前 Logger 样本数", "idle")
        self.path_card = KpiCard("最近报告", "Markdown 路径", "idle")
        self.sample_card.setMaximumHeight(108)
        self.path_card.setMaximumHeight(108)
        top.addWidget(self.sample_card)
        top.addWidget(self.path_card, 2)
        top.addWidget(InfoBox("报告说明", "报告内容保持 Markdown，便于复制到课程文档、故障记录或后续知识库。"), 2)
        layout.addLayout(top)

        toolbar_card = SectionCard("操作栏")
        toolbar = QtWidgets.QHBoxLayout()
        refresh_button = QtWidgets.QPushButton("生成报告")
        refresh_button.setProperty("variant", "primary")
        refresh_button.clicked.connect(self.refresh)
        export_button = QtWidgets.QPushButton("导出 Markdown")
        export_button.clicked.connect(self._choose_export_path)
        open_dir_button = QtWidgets.QPushButton("打开报告目录")
        open_dir_button.setProperty("variant", "ghost")
        open_dir_button.clicked.connect(self._open_report_dir)
        self.status_label = QtWidgets.QLabel("报告状态：等待生成")
        self.status_label.setObjectName("hintText")
        toolbar.addWidget(refresh_button)
        toolbar.addWidget(export_button)
        toolbar.addWidget(open_dir_button)
        toolbar.addStretch(1)
        toolbar.addWidget(self.status_label)
        toolbar_card.body.addLayout(toolbar)
        layout.addWidget(toolbar_card)

        preview_card = SectionCard("报告预览")
        self.report_text = QtWidgets.QPlainTextEdit()
        self.report_text.setReadOnly(True)
        preview_card.body.addWidget(self.report_text)
        layout.addWidget(preview_card, 1)
        self.refresh()

    def refresh(self) -> None:
        self.report_text.setPlainText(self.build_report())
        sample_count = len(self._sample_provider())
        self.sample_card.set_value(str(sample_count), "samples", "idle")
        self.status_label.setText("报告状态：已生成预览")

    def build_report(self) -> str:
        samples = self._sample_provider()
        if not samples:
            return "# eMotor-Studio 调试报告\n\n当前还没有记录到遥测样本。\n"

        first = self._float_value(samples[0].get("timestamp"))
        last = self._float_value(samples[-1].get("timestamp"))
        duration = max(0.0, last - first)
        lines = [
            "# eMotor-Studio 调试报告",
            "",
            "## 摘要",
            "",
            f"- Samples: {len(samples)}",
            f"- Duration: {duration:.2f} s",
            "- Backend: Mock",
            "",
            "## 关键信号",
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
                "## 备注",
                "",
                "- 本报告由 AxDr_L 对齐的 MockBackend 遥测数据生成。",
                "- 当前阶段尚未实现真实硬件通信。",
                "",
            ]
        )
        return "\n".join(lines)

    def export_markdown(self, path: str | Path) -> Path:
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        export_path.write_text(self.build_report(), encoding="utf-8")
        self._last_export_path = export_path
        self.path_card.set_value(str(export_path), "Markdown", "idle")
        self.status_label.setText(f"报告状态：已导出 {export_path}")
        return export_path

    def _choose_export_path(self) -> None:
        path, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "导出调试报告",
            "emotor_studio_report.md",
            "Markdown Files (*.md)",
        )
        if path:
            self.export_markdown(path)

    def _open_report_dir(self) -> None:
        path = self._last_export_path.parent if self._last_export_path else Path.cwd()
        os.startfile(path)  # type: ignore[attr-defined]

    @staticmethod
    def _is_number(value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @staticmethod
    def _float_value(value: object) -> float:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return 0.0
