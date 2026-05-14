"""VESC-like framework pages localized for AxDr_L."""

from __future__ import annotations

import math

from PySide6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from emotor_studio.services import (
    CurrentLoopStepExperiment,
    MockInductanceIdentification,
    MockResistanceIdentification,
    save_current_loop_tuning_report,
    save_current_loop_tuning_session,
    build_experiment_report,
    save_experiment_artifacts,
    suggest_current_loop_pi,
    validate_current_loop_pi,
)
from emotor_studio.ui.components import InfoBox, KpiCard, PageHeader, SectionCard
from emotor_studio.ui.theme import COLORS


class WorkflowCard(QtWidgets.QFrame):
    def __init__(
        self,
        title: str,
        tag: str,
        lines: list[str],
        actions: list[str] | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("workflowCard")
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        header = QtWidgets.QHBoxLayout()
        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("workflowTitle")
        tag_label = QtWidgets.QLabel(tag)
        tag_label.setObjectName("workflowTag")
        header.addWidget(title_label)
        header.addStretch(1)
        header.addWidget(tag_label)
        layout.addLayout(header)
        for line in lines:
            label = QtWidgets.QLabel(line)
            label.setObjectName("hintText")
            label.setWordWrap(True)
            layout.addWidget(label)
        if actions:
            row = QtWidgets.QHBoxLayout()
            row.setSpacing(8)
            for text in actions:
                button = QtWidgets.QPushButton(text)
                button.setEnabled(False)
                row.addWidget(button)
            row.addStretch(1)
            layout.addLayout(row)


class PlaceholderWorkbenchPage(QtWidgets.QWidget):
    """Reusable framework page for sections that are not wired to hardware yet."""

    def __init__(
        self,
        title: str,
        subtitle: str,
        cards: list[tuple[str, str, str, str]],
        sections: list[tuple[str, list[str]]],
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader(title, subtitle))

        overview = SectionCard("页面总览", "先搭建与 VESC Tool 类似的工程页结构，后续逐步接入 AxDr_L 协议。")
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        for index, (card_title, value, unit, state) in enumerate(cards):
            card = KpiCard(card_title, unit, state)
            card.set_value(value, unit, state)
            grid.addWidget(card, index // 3, index % 3)
        overview.body.addLayout(grid)
        layout.addWidget(overview)

        section_grid = QtWidgets.QGridLayout()
        section_grid.setSpacing(12)
        for index, (section_title, rows) in enumerate(sections):
            card = SectionCard(section_title)
            card.setMinimumWidth(360)
            for row in rows:
                label = QtWidgets.QLabel(row)
                label.setObjectName("hintText")
                label.setWordWrap(True)
                card.body.addWidget(label)
            section_grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(section_grid)

        layout.addWidget(
            InfoBox(
                "实现边界",
                "本页当前只提供框架、字段和操作入口。真实读写、识别、升级和硬件动作将在协议确认后接入。",
            )
        )
        layout.addStretch(1)


class FirmwarePage(PlaceholderWorkbenchPage):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(
            "固件",
            "固件信息、版本、构建记录和后续升级入口。",
            [
                ("目标固件", "AxDr_L", "基准程序", "idle"),
                ("通信状态", "未接入", "Phase 7.2 后读取", "stop"),
                ("升级功能", "预留", "后续阶段", "warning"),
            ],
            [
                ("固件信息", ["MCU / board id", "git commit / build time", "protocol version"]),
                ("固件升级", ["本阶段不实现", "后续考虑 bootloader / DFU / 串口升级流程"]),
                ("安全策略", ["升级前校验供电与状态", "运行中禁止写入固件"]),
                ("开发者信息", ["AxDr_L 同步状态", "协议兼容性检查"]),
            ],
            parent,
        )


class MotorSettingsPage(PlaceholderWorkbenchPage):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(
            "电机设置",
            "AxDr_L 电机参数、限幅、保护、辨识和传感器配置总入口。",
            [
                ("电机参数", "已映射", "parameters.json", "ok"),
                ("保护阈值", "已映射", "fault/limits", "ok"),
                ("参数辨识", "预留", "后续接入", "warning"),
            ],
            [
                ("General", ["电机极对数、电阻、电感、磁链", "母线电压、电流、速度和转矩限幅"]),
                ("Sensors", ["编码器偏移、相序、角度校准", "观测器参数和估计角度"]),
                ("Protection", ["过压、欠压、过流、过温", "故障锁存与清除策略"]),
                ("Wizards", ["电阻/电感辨识", "编码器校准", "电流环整定"]),
            ],
            parent,
        )


class FocPage(PlaceholderWorkbenchPage):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(
            "FOC",
            "电流环、速度环、位置环、SVPWM 和观测器调试页。",
            [
                ("Id/Iq 电流环", "已映射", "PI gains", "ok"),
                ("速度环", "已映射", "PI gains", "ok"),
                ("观测器", "预留", "PLL / angle", "warning"),
            ],
            [
                ("Current Loop", ["Id/Iq Kp Ki", "电压限幅、解耦、采样延迟补偿"]),
                ("Speed / Position", ["速度 PI、位置 P", "加速度/减速度限制"]),
                ("SVPWM", ["duty_a / duty_b / duty_c", "调制比、死区、采样点"]),
                ("Observer", ["估计角度、编码器角度对比", "PLL 带宽和误差诊断"]),
            ],
            parent,
        )


class AppSettingsPage(PlaceholderWorkbenchPage):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(
            "应用设置",
            "控制模式、命令入口、安全策略和上位机行为配置。",
            [
                ("速度模式", "Mock 可用", "set_speed_target", "idle"),
                ("电流模式", "Mock 可用", "set_current_target", "idle"),
                ("位置模式", "Mock 可用", "set_position_target", "idle"),
            ],
            [
                ("Control Mode", ["release/debug/calibration", "速度/电流/位置目标选择"]),
                ("Command Policy", ["使能、停止、清故障", "运行中参数写入限制"]),
                ("Serial App", ["串口协议版本", "超时、重试、ACK/NACK"]),
                ("Safety", ["默认不自动使能", "真实硬件接入后增加确认弹窗"]),
            ],
            parent,
        )


class ControlTuningPage(QtWidgets.QWidget):
    """Teaching/research page for current, speed, and position loops."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.last_pi_suggestions = ()
        self.last_pi_validation = None
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("三环调参", "面向教学、科研和工程整定的电流环 / 速度环 / 位置环工作台。"))

        self.workflow_status: dict[str, KpiCard] = {}
        workflow_card = SectionCard("当前调参流程", "按专业上位机流程组织：辨识参数 -> 生成建议 -> 阶跃验证 -> 导出会话。")
        workflow_grid = QtWidgets.QGridLayout()
        workflow_grid.setSpacing(10)
        for index, (key, title, unit, state) in enumerate(
            [
                ("identify", "1. 参数辨识", "Rs / Ld / Lq", "idle"),
                ("suggest", "2. PI 建议", "Kp / Ki", "idle"),
                ("validate", "3. 阶跃验证", "Mock step", "idle"),
                ("export", "4. 报告归档", "report / session", "idle"),
            ]
        ):
            card = KpiCard(title, unit, state)
            self.workflow_status[key] = card
            workflow_grid.addWidget(card, 0, index)
        workflow_card.body.addLayout(workflow_grid)
        layout.addWidget(workflow_card)

        top = SectionCard("整定流程", "先用 Mock 建立工作流，后续接入 AxDr_L 后执行阶跃、扫频和安全限幅。")
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(12)
        cards = [
            WorkflowCard("电流环", "Id/Iq", ["Kp / Ki / 带宽 / 电流限幅", "预留阶跃响应、闭环带宽、相位裕度窗口"], ["阶跃测试", "扫频"]),
            WorkflowCard("速度环", "Speed", ["速度 Kp / Ki / 阻尼 / 前馈", "预留速度阶跃、负载扰动、超调分析"], ["阶跃测试", "负载扰动"]),
            WorkflowCard("位置环", "Position", ["位置 P/PI/PID、轨迹限制", "预留跟踪误差、稳态误差、定位重复性分析"], ["轨迹测试", "误差分析"]),
        ]
        for index, card in enumerate(cards):
            grid.addWidget(card, 0, index)
        top.body.addLayout(grid)
        layout.addWidget(top)

        table_card = SectionCard("参数预设窗口")
        table = QtWidgets.QTableWidget(5, 6)
        self.preset_table = table
        table.setHorizontalHeaderLabels(["对象", "Kp", "Ki", "Kd / FF", "限幅", "实验输出"])
        rows = [
            ["d轴电流环", "id_current_kp", "id_current_ki", "-", "current_limit", "Bode / Step"],
            ["q轴电流环", "iq_current_kp", "iq_current_ki", "-", "current_limit", "Bode / Step"],
            ["速度环", "speed_kp", "speed_ki", "speed_ff", "velocity_limit", "Overshoot / Settling"],
            ["位置环", "position_kp", "position_ki", "position_kd", "position_limit", "Tracking Error"],
            ["外部负载", "load_kp", "-", "friction_ff", "torque_limit", "Disturbance"],
        ]
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, column, item)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setDefaultSectionSize(28)
        table_card.body.addWidget(table)
        layout.addWidget(table_card)

        suggestion_card = SectionCard("电流环 PI 初值建议", "基于 Mock Rs/Ld/Lq 辨识结果生成，只作为教学和后续整定入口，不自动写入参数。")
        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(8)
        controls.addWidget(QtWidgets.QLabel("目标带宽"))
        self.current_bandwidth_spin = QtWidgets.QDoubleSpinBox()
        self.current_bandwidth_spin.setRange(20.0, 2000.0)
        self.current_bandwidth_spin.setDecimals(1)
        self.current_bandwidth_spin.setValue(350.0)
        self.current_bandwidth_spin.setSuffix(" Hz")
        controls.addWidget(self.current_bandwidth_spin)
        self.pi_button = QtWidgets.QPushButton("生成 Mock PI 建议")
        self.pi_button.clicked.connect(self.generate_mock_current_pi_suggestion)
        controls.addWidget(self.pi_button)
        self.pi_validate_button = QtWidgets.QPushButton("验证 PI 阶跃响应")
        self.pi_validate_button.clicked.connect(self.validate_mock_current_pi)
        controls.addWidget(self.pi_validate_button)
        self.pi_report_button = QtWidgets.QPushButton("导出调参报告")
        self.pi_report_button.clicked.connect(self.export_current_loop_tuning_report)
        controls.addWidget(self.pi_report_button)
        self.pi_session_button = QtWidgets.QPushButton("导出会话包")
        self.pi_session_button.clicked.connect(self.export_current_loop_tuning_session)
        controls.addWidget(self.pi_session_button)
        self.pi_status_label = QtWidgets.QLabel("状态：等待生成")
        self.pi_status_label.setObjectName("hintText")
        controls.addWidget(self.pi_status_label, 1)
        suggestion_card.body.addLayout(controls)

        self.pi_table = QtWidgets.QTableWidget(2, 7)
        self.pi_table.setHorizontalHeaderLabels(["轴", "Kp", "Ki", "Kp单位", "Ki单位", "目标带宽", "说明"])
        self.pi_table.horizontalHeader().setStretchLastSection(True)
        self.pi_table.verticalHeader().setDefaultSectionSize(28)
        for row, axis in enumerate(["d", "q"]):
            for column, value in enumerate([axis, "-", "-", "V/A", "V/(A*s)", "-", "待生成"]):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.pi_table.setItem(row, column, item)
        suggestion_card.body.addWidget(self.pi_table)

        validation_split = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.pi_validation_plot = pg.PlotWidget(title="Mock current-loop validation")
        self.pi_validation_plot.setBackground(COLORS["scope_bg"])
        self.pi_validation_plot.showGrid(x=True, y=True, alpha=0.18)
        self.pi_validation_plot.setLabel("bottom", "时间", "s")
        self.pi_validation_plot.setLabel("left", "Iq", "A")
        self.pi_validation_plot.addLegend(offset=(-12, 12))
        validation_split.addWidget(self.pi_validation_plot)

        self.pi_validation_table = QtWidgets.QTableWidget(4, 2)
        self.pi_validation_table.setHorizontalHeaderLabels(["指标", "数值"])
        self.pi_validation_table.horizontalHeader().setStretchLastSection(True)
        self.pi_validation_table.setMinimumWidth(280)
        for row, name in enumerate(["上升时间", "调节时间", "超调量", "稳态误差"]):
            for column, value in enumerate([name, "-"]):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.pi_validation_table.setItem(row, column, item)
        validation_split.addWidget(self.pi_validation_table)
        validation_split.setStretchFactor(0, 1)
        validation_split.setSizes([760, 300])
        suggestion_card.body.addWidget(validation_split, 1)
        layout.addWidget(suggestion_card)

        layout.addWidget(InfoBox("后续实现", "真实硬件阶段将从 commands/signals/parameters schema 生成实验任务，不把控制逻辑写死在 UI 里。"))
        layout.addStretch(1)
        self._set_workflow_state("identify", "待运行", "Mock 辨识", "idle")
        self._set_workflow_state("suggest", "待生成", "PI 初值", "idle")
        self._set_workflow_state("validate", "待验证", "阶跃响应", "idle")
        self._set_workflow_state("export", "待导出", "报告/会话", "idle")

    def generate_mock_current_pi_suggestion(self):
        rs_result = MockResistanceIdentification().run()
        l_result = MockInductanceIdentification().run()
        estimates = {
            estimate.key: float(estimate.value)
            for estimate in (*rs_result.estimates, *l_result.estimates)
            if isinstance(estimate.value, (float, int))
        }
        suggestions = suggest_current_loop_pi(
            resistance_ohm=estimates["phase_resistance"],
            d_inductance_h=estimates["d_inductance"],
            q_inductance_h=estimates["q_inductance"],
            target_bandwidth_hz=self.current_bandwidth_spin.value(),
        )
        self.last_pi_suggestions = suggestions
        self._set_workflow_state("identify", "完成", "Mock Rs/Ld/Lq", "ok")
        self._apply_pi_suggestions(suggestions)
        return suggestions

    def _apply_pi_suggestions(self, suggestions) -> None:
        for row, suggestion in enumerate(suggestions):
            values = [
                suggestion.axis,
                f"{suggestion.kp:.6g}",
                f"{suggestion.ki:.6g}",
                suggestion.unit_kp,
                suggestion.unit_ki,
                f"{suggestion.target_bandwidth_hz:.1f} Hz",
                suggestion.note,
            ]
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.pi_table.setItem(row, column, item)
        self.preset_table.item(0, 1).setText(f"{suggestions[0].kp:.6g}")
        self.preset_table.item(0, 2).setText(f"{suggestions[0].ki:.6g}")
        self.preset_table.item(1, 1).setText(f"{suggestions[1].kp:.6g}")
        self.preset_table.item(1, 2).setText(f"{suggestions[1].ki:.6g}")
        self.pi_status_label.setText("状态：已基于 Mock Rs/Ld/Lq 生成 PI 初值，真实写入仍禁用")
        self._set_workflow_state("suggest", "完成", f"{suggestions[1].target_bandwidth_hz:.1f} Hz", "ok")

    def validate_mock_current_pi(self):
        if not self.last_pi_suggestions:
            self.generate_mock_current_pi_suggestion()
        result = validate_current_loop_pi(self.last_pi_suggestions[1])
        self.last_pi_validation = result
        self._set_workflow_state("validate", "完成", "Mock step", "ok")
        self._apply_pi_validation(result)
        return result

    def export_current_loop_tuning_report(self, directory: str | None = None):
        if not self.last_pi_suggestions:
            self.generate_mock_current_pi_suggestion()
        if self.last_pi_validation is None:
            self.validate_mock_current_pi()
        if directory is None:
            directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选择调参报告导出目录")
            if not directory:
                self.pi_status_label.setText("状态：已取消调参报告导出")
                return None
        assert self.last_pi_validation is not None
        path = save_current_loop_tuning_report(self.last_pi_suggestions, self.last_pi_validation, directory)
        self.pi_status_label.setText(f"状态：调参报告已导出 {path}")
        self._set_workflow_state("export", "报告已导出", "Markdown", "ok")
        return path

    def export_current_loop_tuning_session(self, directory: str | None = None):
        if not self.last_pi_suggestions:
            self.generate_mock_current_pi_suggestion()
        if self.last_pi_validation is None:
            self.validate_mock_current_pi()
        if directory is None:
            directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选择实验会话包导出目录")
            if not directory:
                self.pi_status_label.setText("状态：已取消实验会话包导出")
                return {}
        assert self.last_pi_validation is not None
        artifacts = save_current_loop_tuning_session(self.last_pi_suggestions, self.last_pi_validation, directory)
        self.pi_status_label.setText(f"状态：实验会话包已导出 {artifacts['directory']}")
        self._set_workflow_state("export", "会话已导出", "session package", "ok")
        return artifacts

    def _apply_pi_validation(self, result) -> None:
        self.pi_validation_plot.clear()
        self.pi_validation_plot.plot(
            result.trace.time_s,
            result.trace.target,
            pen=pg.mkPen("#fbbf24", width=2.0),
            name="目标 Iq",
        )
        self.pi_validation_plot.plot(
            result.trace.time_s,
            result.trace.response,
            pen=pg.mkPen("#22d3ee", width=2.2),
            name="验证响应",
        )
        self.pi_validation_plot.enableAutoRange()
        metrics = result.metrics
        rows = [
            ("上升时间", self._format_seconds(metrics.rise_time_s)),
            ("调节时间", self._format_seconds(metrics.settling_time_s)),
            ("超调量", f"{metrics.overshoot_percent:.2f} %"),
            ("稳态误差", f"{metrics.steady_state_error:.4g} {result.trace.unit}"),
        ]
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.pi_validation_table.setItem(row, column, item)
        self.pi_status_label.setText(f"状态：PI Mock 阶跃验证完成，{result.summary}")

    def _format_seconds(self, value: float | None) -> str:
        return "--" if value is None else f"{value * 1000.0:.2f} ms"

    def _set_workflow_state(self, key: str, value: str, unit: str, state: str) -> None:
        card = self.workflow_status.get(key)
        if card is not None:
            card.set_value(value, unit, state)


class FilterDesignPage(QtWidgets.QWidget):
    """Filter and notch tuning placeholders for research workflows."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("滤波 / 陷波", "低通、陷波、观测器滤波和采样链路参数预设。"))

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(12)
        cards = [
            WorkflowCard("电流采样滤波", "LPF", ["采样频率、截止频率、延迟补偿", "用于解释滤波延迟对电流环相位的影响"], ["预览响应"]),
            WorkflowCard("速度估计滤波", "Speed", ["速度 LPF、微分噪声抑制、滑窗平均", "用于速度环整定和低速抖动分析"], ["噪声评估"]),
            WorkflowCard("机械谐振陷波", "Notch", ["中心频率、Q 值、衰减深度", "用于科研实验中的振动抑制和论文图表"], ["扫频识别"]),
            WorkflowCard("观测器滤波", "Observer", ["PLL 带宽、角度融合、估计误差窗口", "为无感观测器调试预留"], ["误差对比"]),
        ]
        for index, card in enumerate(cards):
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)

        preview = SectionCard("频域预览窗口")
        tabs = QtWidgets.QTabWidget()
        tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        tabs.addTab(self._demo_response_plot("低通幅相响应"), "LPF")
        tabs.addTab(self._demo_response_plot("陷波器幅相响应"), "Notch")
        tabs.addTab(self._demo_response_plot("观测器误差频谱"), "Observer")
        preview.body.addWidget(tabs)
        layout.addWidget(preview, 1)

    def _demo_response_plot(self, title: str) -> pg.PlotWidget:
        plot = pg.PlotWidget(title=title)
        plot.setBackground(COLORS["scope_bg"])
        plot.showGrid(x=True, y=True, alpha=0.18)
        plot.setLabel("bottom", "频率", "Hz")
        plot.setLabel("left", "幅值", "dB")
        plot.setMenuEnabled(False)
        x_values = [1 + index * 10 for index in range(200)]
        y_values = [-20 * math.log10(1 + (x / 800) ** 2) for x in x_values]
        plot.plot(x_values, y_values, pen=pg.mkPen("#2dd4bf", width=2.2))
        return plot


class TerminalPage(QtWidgets.QWidget):
    """Terminal layout following VESC Tool's command-console shape."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("Terminal", "协议调试、固件日志和命令行入口。当前仅为 Mock 框架。"))

        terminal = QtWidgets.QTextEdit()
        terminal.setReadOnly(True)
        terminal.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        terminal.setFont(QtGui.QFont("Consolas", 10))
        terminal.setPlainText(
            "eMotor-Studio Terminal\n"
            "----------------------------------------\n"
            "当前为 Mock 模式。\n"
            "Phase 7.2-A 后可在这里发送 ping / help / read_fault 等调试命令。\n"
        )
        layout.addWidget(terminal, 1)

        row = QtWidgets.QHBoxLayout()
        help_button = QtWidgets.QPushButton("帮助")
        help_button.setEnabled(False)
        command = QtWidgets.QLineEdit()
        command.setPlaceholderText("输入固件命令，真实串口终端待实现")
        command.setEnabled(False)
        send_button = QtWidgets.QPushButton("发送")
        send_button.setEnabled(False)
        clear_button = QtWidgets.QPushButton("清空")
        clear_button.clicked.connect(terminal.clear)
        row.addWidget(help_button)
        row.addWidget(command, 1)
        row.addWidget(send_button)
        row.addWidget(clear_button)
        layout.addLayout(row)


class SampledDataPage(QtWidgets.QWidget):
    """Triggered sampling framework similar to VESC Tool Sampled Data."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("采样数据", "高频触发采样、相电流/反电动势/滤波分析入口。当前只显示框架。"))

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        tabs = QtWidgets.QTabWidget()
        tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        tabs.addTab(self._plot_tab("相电流采样", ["PH A", "PH B", "PH C", "总电流", "电角度"]), "Current")
        tabs.addTab(self._plot_tab("反电动势 / 相电压", ["PH A", "PH B", "PH C", "Virtual GND", "Phase"]), "BEMF")
        tabs.addTab(self._filter_tab(), "Filter / FFT")
        splitter.addWidget(tabs)
        splitter.addWidget(self._sample_side_panel())
        splitter.setStretchFactor(0, 1)
        splitter.setSizes([860, 260])
        layout.addWidget(splitter, 1)

        bottom = SectionCard("采样控制")
        row = QtWidgets.QGridLayout()
        row.setHorizontalSpacing(8)
        row.setVerticalSpacing(8)
        for index, text in enumerate(["立即采样", "启动时采样", "启动触发", "故障触发", "停止采样", "保存 CSV", "加载 CSV"]):
            button = QtWidgets.QPushButton(text)
            button.setEnabled(False)
            row.addWidget(button, index // 4, index % 4)
        bottom.body.addLayout(row)
        bottom.body.addWidget(InfoBox("状态", "等待 Phase 7.x 固件采样协议。当前不会向开发板发送采样命令。"))
        layout.addWidget(bottom)

    def _plot_tab(self, title: str, channels: list[str]) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        plot = self._demo_plot(title)
        layout.addWidget(plot, 1)
        channel_row = QtWidgets.QHBoxLayout()
        for channel in channels:
            box = QtWidgets.QCheckBox(channel)
            box.setChecked(True)
            box.setEnabled(False)
            channel_row.addWidget(box)
        channel_row.addStretch(1)
        layout.addLayout(channel_row)
        return tab

    def _filter_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._demo_plot("滤波器响应"), 1)
        layout.addWidget(self._demo_plot("FFT / 频域分析"), 1)
        return tab

    def _sample_side_panel(self) -> QtWidgets.QWidget:
        panel = QtWidgets.QFrame()
        panel.setObjectName("sectionCard")
        panel.setMinimumWidth(250)
        panel.setMaximumWidth(300)
        layout = QtWidgets.QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        title = QtWidgets.QLabel("采样参数")
        title.setObjectName("sectionTitle")
        layout.addWidget(title)
        mode = QtWidgets.QComboBox()
        mode.addItems(["Time Plot", "FFT Plot", "Filter Plot"])
        mode.setEnabled(False)
        layout.addWidget(mode)
        for label, value, suffix in [
            ("采样点数", 1000, " samples"),
            ("降采样", 1, "x"),
            ("采样频率", 40000, " Hz"),
        ]:
            spin = QtWidgets.QSpinBox()
            spin.setRange(1, 200000)
            spin.setValue(value)
            spin.setPrefix(f"{label}: ")
            spin.setSuffix(suffix)
            spin.setEnabled(False)
            layout.addWidget(spin)
        for text in ["Raw", "Delay Comp", "Hamming", "Logscale"]:
            box = QtWidgets.QCheckBox(text)
            box.setEnabled(False)
            layout.addWidget(box)
        layout.addStretch(1)
        return panel

    def _demo_plot(self, title: str) -> pg.PlotWidget:
        pg.setConfigOptions(antialias=True, foreground="#d8dee9", background=COLORS["scope_bg"])
        plot = pg.PlotWidget(title=title)
        plot.setBackground(COLORS["scope_bg"])
        plot.showGrid(x=True, y=True, alpha=0.18)
        plot.getPlotItem().hideButtons()
        plot.setMenuEnabled(False)
        x_values = [index * 0.001 for index in range(500)]
        for offset, color in [(0.0, "#22d3ee"), (2.0, "#fbbf24"), (4.0, "#a78bfa")]:
            y_values = [math.sin(index * 0.05 + offset) for index in range(500)]
            plot.plot(x_values, y_values, pen=pg.mkPen(color, width=2.0))
        return plot


class DataAnalysisPage(PlaceholderWorkbenchPage):
    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(
            "数据分析",
            "日志、故障复盘、曲线对比和教学报告分析入口。",
            [
                ("CSV 记录", "可用", "Logger", "ok"),
                ("Markdown 报告", "可用", "Report", "ok"),
                ("故障复盘", "预留", "Fault timeline", "warning"),
            ],
            [
                ("Log Analysis", ["导入 CSV", "多通道曲线复盘", "关键事件标记"]),
                ("Experiment Plot", ["电流环/速度环阶跃响应", "超调、稳态误差和 settling time"]),
                ("Motor Analysis", ["参数辨识结果对比", "电机模型与实测波形校核"]),
                ("AI Debug", ["后续接入故障诊断知识库", "从日志和波形生成排查建议"]),
            ],
            parent,
        )


class ResearchWorkbenchPage(QtWidgets.QWidget):
    """Research workflows for paper-friendly motor experiments."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("实验工作台", "面向教学演示和论文实验的数据生成入口。"))

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(12)
        cards = [
            WorkflowCard("堵转 / 电流环实验", "Stall", ["自动设置安全限流，采集 Id/Iq、电压和温度", "用于估计电流环带宽、稳态误差和热漂移"], ["生成任务"]),
            WorkflowCard("速度阶跃实验", "Step", ["速度目标阶跃、负载扰动、超调和调节时间", "用于课程讲解和论文对比图"], ["生成任务"]),
            WorkflowCard("扫频实验", "Sweep", ["正弦扫频、chirp、PRBS 等激励预留", "用于伯德图、频响和机械共振分析"], ["生成任务"]),
            WorkflowCard("重复性实验", "Repeat", ["自动运行多轮相同实验并导出统计量", "用于科研数据可信度和工程验证"], ["生成任务"]),
        ]
        for index, card in enumerate(cards):
            grid.addWidget(card, index // 2, index % 2)
        layout.addLayout(grid)

        pipeline = SectionCard("实验数据流水线")
        steps = QtWidgets.QHBoxLayout()
        for title, unit, state in [
            ("1. 配置实验", "参数/限幅/安全状态", "idle"),
            ("2. 采集数据", "telemetry + event markers", "warning"),
            ("3. 自动分析", "指标 + 图表 + Markdown", "stop"),
            ("4. 导出论文素材", "CSV / PNG / 报告", "stop"),
        ]:
            card = KpiCard(title, unit, state)
            card.set_value("预留", unit, state)
            steps.addWidget(card)
        pipeline.body.addLayout(steps)
        layout.addWidget(pipeline)
        layout.addWidget(InfoBox("当前边界", "开发板不在身边时，先把实验任务结构、导出路径和报告入口设计好；真实执行等协议和硬件接入。"))
        layout.addStretch(1)


class ExperimentAnalysisPage(QtWidgets.QWidget):
    """Automatic analysis page for Mock and later hardware experiment data."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self._last_result = None
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("自动分析", "把实验数据转为可复现指标、图表和 Markdown 报告。"))

        setup = SectionCard("Mock 电流环阶跃实验", "当前不连接真实硬件。这里先跑通任务生成、数据分析、图表和报告入口。")
        setup_grid = QtWidgets.QGridLayout()
        setup_grid.setHorizontalSpacing(10)
        setup_grid.setVerticalSpacing(8)
        self.target_spin = QtWidgets.QDoubleSpinBox()
        self.target_spin.setRange(0.1, 80.0)
        self.target_spin.setDecimals(2)
        self.target_spin.setValue(5.0)
        self.target_spin.setSuffix(" A")
        self.duration_spin = QtWidgets.QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 5.0)
        self.duration_spin.setDecimals(2)
        self.duration_spin.setValue(0.5)
        self.duration_spin.setSuffix(" s")
        self.bandwidth_spin = QtWidgets.QDoubleSpinBox()
        self.bandwidth_spin.setRange(1.0, 500.0)
        self.bandwidth_spin.setDecimals(1)
        self.bandwidth_spin.setValue(42.0)
        self.bandwidth_spin.setSuffix(" Hz")
        self.damping_spin = QtWidgets.QDoubleSpinBox()
        self.damping_spin.setRange(0.2, 2.0)
        self.damping_spin.setDecimals(2)
        self.damping_spin.setValue(0.72)
        self.run_button = QtWidgets.QPushButton("运行 Mock 阶跃分析")
        self.run_button.clicked.connect(self.run_mock_current_step)
        self.export_button = QtWidgets.QPushButton("导出 CSV / 报告")
        self.export_button.clicked.connect(self.export_current_result)
        self.status_label = QtWidgets.QLabel("状态：等待运行")
        self.status_label.setObjectName("hintText")
        for column, (label, widget) in enumerate(
            [
                ("目标 Iq", self.target_spin),
                ("时长", self.duration_spin),
                ("假设带宽", self.bandwidth_spin),
                ("阻尼", self.damping_spin),
            ]
        ):
            setup_grid.addWidget(QtWidgets.QLabel(label), 0, column)
            setup_grid.addWidget(widget, 1, column)
        setup_grid.addWidget(self.run_button, 1, 4)
        setup_grid.addWidget(self.export_button, 1, 5)
        setup_grid.addWidget(self.status_label, 1, 6)
        setup_grid.setColumnStretch(6, 1)
        setup.body.addLayout(setup_grid)
        layout.addWidget(setup)

        kpi_row = QtWidgets.QHBoxLayout()
        kpi_row.setSpacing(12)
        self.metric_cards: dict[str, KpiCard] = {}
        for key, title, unit in [
            ("rise", "上升时间", "10% -> 90%"),
            ("settling", "调节时间", "2% 稳态带"),
            ("overshoot", "超调量", "peak - target"),
            ("error", "稳态误差", "final - target"),
        ]:
            card = KpiCard(title, unit, "idle")
            card.set_value("--", unit, "idle")
            self.metric_cards[key] = card
            kpi_row.addWidget(card)
        layout.addLayout(kpi_row)

        tabs = QtWidgets.QTabWidget()
        tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        tabs.addTab(self._step_response_tab(), "阶跃响应")
        tabs.addTab(self._analysis_table("电流环带宽扫描", ["频率", "幅值", "相位", "相干度", "备注"]), "带宽扫描")
        tabs.addTab(self._demo_response_plot("伯德图预览"), "伯德图")
        tabs.addTab(self._analysis_table("论文图表素材", ["图名", "数据源", "变量", "导出格式", "状态"]), "图表导出")
        layout.addWidget(tabs, 1)
        self.run_mock_current_step()

    def run_mock_current_step(self):
        experiment = CurrentLoopStepExperiment(
            target_current_a=self.target_spin.value(),
            duration_s=self.duration_spin.value(),
            natural_frequency_hz=self.bandwidth_spin.value(),
            damping_ratio=self.damping_spin.value(),
        )
        result = experiment.run()
        self._last_result = result
        self._apply_result(result)
        return result

    def export_current_result(self, directory: str | None = None) -> dict[str, object]:
        if self._last_result is None:
            self.run_mock_current_step()
        assert self._last_result is not None
        if directory is None:
            directory = QtWidgets.QFileDialog.getExistingDirectory(self, "选择实验导出目录")
            if not directory:
                self.status_label.setText("状态：已取消导出")
                return {}
        artifacts = save_experiment_artifacts(self._last_result, directory)
        png_path = artifacts["csv"].with_suffix(".png")
        self.response_plot.grab().save(str(png_path))
        artifacts["plot"] = png_path
        self.status_label.setText(f"状态：已导出 {artifacts['csv'].parent}")
        return artifacts

    def _apply_result(self, result) -> None:
        metrics = result.metrics
        self.metric_cards["rise"].set_value(self._format_seconds(metrics.rise_time_s), "10% -> 90%", "ok")
        self.metric_cards["settling"].set_value(self._format_seconds(metrics.settling_time_s), "2% 稳态带", "ok")
        overshoot_state = "warning" if metrics.overshoot_percent > 15.0 else "ok"
        self.metric_cards["overshoot"].set_value(f"{metrics.overshoot_percent:.2f} %", "peak - target", overshoot_state)
        error_state = "warning" if abs(metrics.steady_state_error) > abs(metrics.target_value) * 0.05 else "ok"
        self.metric_cards["error"].set_value(f"{metrics.steady_state_error:.4g} {result.trace.unit}", "final - target", error_state)

        self.response_plot.clear()
        self.response_plot.plot(
            result.trace.time_s,
            result.trace.target,
            pen=pg.mkPen("#fbbf24", width=2.0),
            name="目标 Iq",
        )
        self.response_plot.plot(
            result.trace.time_s,
            result.trace.response,
            pen=pg.mkPen("#22d3ee", width=2.4),
            name="反馈 Iq",
        )
        self.response_plot.enableAutoRange()
        self.status_label.setText(f"状态：已生成 {len(result.trace.time_s)} 点 Mock 数据，{result.summary}")

        rows = [
            ("目标电流", f"{metrics.target_value:.4g} {result.trace.unit}", "阶跃目标值"),
            ("最终值", f"{metrics.final_value:.4g} {result.trace.unit}", "末尾 10% 样本均值"),
            ("上升时间", self._format_seconds(metrics.rise_time_s), "10% 到 90%"),
            ("调节时间", self._format_seconds(metrics.settling_time_s), "进入并保持在 2% 误差带"),
            ("超调量", f"{metrics.overshoot_percent:.2f} %", "峰值相对目标值"),
            ("稳态误差", f"{metrics.steady_state_error:.4g} {result.trace.unit}", "最终值减目标值"),
        ]
        self.metric_table.setRowCount(len(rows))
        for row, values in enumerate(rows):
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.metric_table.setItem(row, column, item)
        self.report_preview.setPlainText(build_experiment_report(result))

    def _step_response_tab(self) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        plot_card = SectionCard("q轴电流环阶跃响应")
        self.response_plot = pg.PlotWidget(title="Mock Iq step response")
        self.response_plot.setBackground(COLORS["scope_bg"])
        self.response_plot.showGrid(x=True, y=True, alpha=0.18)
        self.response_plot.setLabel("bottom", "时间", "s")
        self.response_plot.setLabel("left", "电流", "A")
        self.response_plot.addLegend(offset=(-12, 12))
        self.response_plot.setMouseEnabled(x=True, y=True)
        plot_card.body.addWidget(self.response_plot, 1)
        layout.addWidget(plot_card, 2)

        side = QtWidgets.QVBoxLayout()
        metric_card = SectionCard("分析指标")
        self.metric_table = QtWidgets.QTableWidget(0, 3)
        self.metric_table.setHorizontalHeaderLabels(["指标", "数值", "说明"])
        self.metric_table.horizontalHeader().setStretchLastSection(True)
        self.metric_table.verticalHeader().setDefaultSectionSize(28)
        self.metric_table.setMinimumWidth(420)
        metric_card.body.addWidget(self.metric_table)
        side.addWidget(metric_card)

        report_card = SectionCard("Markdown 报告预览")
        self.report_preview = QtWidgets.QPlainTextEdit()
        self.report_preview.setReadOnly(True)
        self.report_preview.setMinimumHeight(220)
        self.report_preview.setFont(QtGui.QFont("Consolas", 9))
        report_card.body.addWidget(self.report_preview)
        side.addWidget(report_card, 1)
        layout.addLayout(side, 1)
        return widget

    def _format_seconds(self, value: float | None) -> str:
        return "--" if value is None else f"{value * 1000.0:.2f} ms"

    def _analysis_table(self, title: str, columns: list[str]) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        label = QtWidgets.QLabel(title)
        label.setObjectName("sectionTitle")
        table = QtWidgets.QTableWidget(4, len(columns))
        table.setHorizontalHeaderLabels(columns)
        table.horizontalHeader().setStretchLastSection(True)
        for row in range(table.rowCount()):
            for column, column_name in enumerate(columns):
                item = QtWidgets.QTableWidgetItem("待分析" if column == 0 else "-")
                item.setToolTip(column_name)
                table.setItem(row, column, item)
        layout.addWidget(label)
        layout.addWidget(table)
        return widget

    def _demo_response_plot(self, title: str) -> pg.PlotWidget:
        plot = pg.PlotWidget(title=title)
        plot.setBackground(COLORS["scope_bg"])
        plot.showGrid(x=True, y=True, alpha=0.18)
        plot.setLabel("bottom", "频率", "Hz")
        plot.setLabel("left", "幅值 / 相位")
        x_values = [1 + index * 8 for index in range(240)]
        magnitude = [-10 * math.log10(1 + (x / 600) ** 2) for x in x_values]
        phase = [-math.degrees(math.atan(x / 600)) for x in x_values]
        plot.plot(x_values, magnitude, pen=pg.mkPen("#2dd4bf", width=2.2), name="Magnitude")
        plot.plot(x_values, phase, pen=pg.mkPen("#fbbf24", width=2.0), name="Phase")
        return plot


class IdentificationPage(QtWidgets.QWidget):
    """Modular motor-parameter identification workbench."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.result_tables: dict[str, QtWidgets.QTableWidget] = {}
        self.module_plots: dict[str, pg.PlotWidget] = {}
        self.module_logs: dict[str, QtWidgets.QPlainTextEdit] = {}
        self.last_identification_results: dict[str, object] = {}
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("参数辨识", "按参数类型拆分辨识流程，每个模块都显示相关变量、拟合结果和安全边界。"))

        overview = SectionCard("辨识工作流", "当前仍为 Mock/框架模式。真实激励、采样和参数写入必须等协议、安全限制和硬件联调完成后再启用。")
        overview_grid = QtWidgets.QGridLayout()
        overview_grid.setSpacing(10)
        for index, (title, value, unit, state) in enumerate(
            [
                ("电气参数", "Rs / Ld / Lq", "分开辨识", "idle"),
                ("传感器参数", "电角度 / 相序", "独立校准", "warning"),
                ("机械参数", "J / B", "科研扩展", "stop"),
                ("观测器参数", "PLL / 误差", "后续接入", "stop"),
            ]
        ):
            card = KpiCard(title, unit, state)
            card.set_value(value, unit, state)
            overview_grid.addWidget(card, 0, index)
        overview.body.addLayout(overview_grid)
        layout.addWidget(overview)

        self.module_specs = self._identification_specs()
        self.module_tabs = QtWidgets.QTabWidget()
        self.module_tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        for spec in self.module_specs:
            self.module_tabs.addTab(self._build_module_tab(spec), spec["tab"])
        layout.addWidget(self.module_tabs, 1)

    def _identification_specs(self) -> list[dict[str, object]]:
        return [
            {
                "key": "resistance",
                "tab": "Rs 电阻",
                "title": "相电阻 Rs 辨识",
                "goal": "低幅值电流注入，拟合电压/电流关系，用于电流环初值和热模型。",
                "signals": ["phase_current", "current_q", "voltage_q", "bus_voltage", "temperature_mos"],
                "safety": ["电机保持静止或低速", "限制注入电流", "监控 MOS/线圈温度", "真实写入前需要人工确认"],
                "outputs": [
                    ("phase_resistance", "-", "ohm", "-", "待辨识"),
                    ("rs_temperature_coeff", "-", "%/degC", "-", "预留"),
                ],
                "plot": "step",
                "mock_enabled": True,
            },
            {
                "key": "inductance",
                "tab": "Ld / Lq 电感",
                "title": "d/q 轴电感辨识",
                "goal": "分别对 d/q 轴施加小信号阶跃，通过电流斜率估计 Ld/Lq。",
                "signals": ["current_d", "current_q", "voltage_d", "voltage_q", "electrical_angle"],
                "safety": ["先完成电角度和相序检查", "限制 Vd/Vq 阶跃幅值", "禁止长时间堵转大电流", "记录母线电压波动"],
                "outputs": [
                    ("d_inductance", "-", "H", "-", "待辨识"),
                    ("q_inductance", "-", "H", "-", "待辨识"),
                    ("current_loop_initial_bandwidth", "-", "Hz", "-", "建议值"),
                ],
                "plot": "current",
                "mock_enabled": True,
                "mock_action": "inductance",
            },
            {
                "key": "flux",
                "tab": "磁链 / Kt",
                "title": "磁链与转矩常数辨识",
                "goal": "结合速度、电压、电流和母线电压估计磁链，为 FOC 和观测器提供参数。",
                "signals": ["mechanical_speed", "bus_voltage", "phase_current", "voltage_q", "duty_a"],
                "safety": ["需要稳定转速区间", "限制最高转速", "记录空载/带载条件", "避免过压回灌"],
                "outputs": [
                    ("motor_flux", "-", "Wb", "-", "待辨识"),
                    ("torque_constant", "-", "N*m/A", "-", "待辨识"),
                ],
                "plot": "speed",
            },
            {
                "key": "angle",
                "tab": "电角度 / 相序",
                "title": "编码器零位、电角度和相序辨识",
                "goal": "校准 encoder offset、相序和电角度方向，避免 FOC 坐标系错误。",
                "signals": ["encoder_angle", "electrical_angle", "estimated_angle", "current_d", "current_q"],
                "safety": ["低电流锁轴", "确认转子可自由或安全定位", "相序错误时立即停止", "保存校准前后对比"],
                "outputs": [
                    ("encoder_electrical_offset", "-", "rad", "-", "待辨识"),
                    ("phase_order", "-", "enum", "-", "待辨识"),
                    ("angle_direction", "-", "enum", "-", "待确认"),
                ],
                "plot": "angle",
            },
            {
                "key": "mechanical",
                "tab": "惯量 / 摩擦",
                "title": "机械惯量与摩擦辨识",
                "goal": "通过速度阶跃、自由滑行或负载扰动估计惯量 J 和摩擦 B。",
                "signals": ["mechanical_speed", "speed_target", "current_q", "torque_estimate", "acceleration"],
                "safety": ["限制速度和加速度", "确认机械负载固定", "保留急停入口", "多轮重复验证"],
                "outputs": [
                    ("inertia", "-", "kg*m^2", "-", "待辨识"),
                    ("viscous_friction", "-", "N*m*s/rad", "-", "待辨识"),
                    ("coulomb_friction", "-", "N*m", "-", "预留"),
                ],
                "plot": "speed",
            },
            {
                "key": "observer",
                "tab": "观测器",
                "title": "无感观测器参数辨识",
                "goal": "对比估计角度和编码器角度，评估 PLL/观测器增益、低速误差和噪声。",
                "signals": ["estimated_angle", "encoder_angle", "observer_error", "mechanical_speed", "bus_voltage"],
                "safety": ["先完成编码器校准", "低速区间单独评估", "故障时停止实验", "不自动写入观测器增益"],
                "outputs": [
                    ("observer_pll_kp", "-", "-", "-", "建议值"),
                    ("observer_pll_ki", "-", "-", "-", "建议值"),
                    ("angle_error_rms", "-", "rad", "-", "待分析"),
                ],
                "plot": "angle",
            },
        ]

    def _build_module_tab(self, spec: dict[str, object]) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        splitter.addWidget(self._module_setup_panel(spec))
        splitter.addWidget(self._module_plot_panel(spec))
        splitter.addWidget(self._module_result_panel(spec))
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([300, 620, 360])
        layout.addWidget(splitter, 1)

        log = QtWidgets.QPlainTextEdit()
        log.setReadOnly(True)
        log.setMaximumHeight(92)
        log.setPlainText(
            "事件日志\n"
            "- 当前为框架预览，未向硬件发送激励。\n"
            "- 后续接入时，实验开始/停止、采样事件、故障、导出路径都会记录在这里。"
        )
        self.module_logs[str(spec["key"])] = log
        layout.addWidget(log)
        return tab

    def _module_setup_panel(self, spec: dict[str, object]) -> QtWidgets.QWidget:
        card = SectionCard("实验设置 / 安全边界", str(spec["goal"]))
        card.setMinimumWidth(280)
        card.setMaximumWidth(340)
        for text in spec["safety"]:
            label = QtWidgets.QLabel(f"- {text}")
            label.setObjectName("hintText")
            label.setWordWrap(True)
            card.body.addWidget(label)
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        for label, value, suffix in [
            ("注入幅值", 1.0, " A/V"),
            ("实验时长", 0.5, " s"),
            ("采样率", 2000.0, " Hz"),
        ]:
            spin = QtWidgets.QDoubleSpinBox()
            spin.setRange(0.0, 100000.0)
            spin.setDecimals(2)
            spin.setValue(value)
            spin.setSuffix(suffix)
            spin.setEnabled(False)
            form.addRow(label, spin)
        card.body.addLayout(form)
        row = QtWidgets.QHBoxLayout()
        for text in ["生成任务", "开始辨识", "停止", "导出"]:
            button = QtWidgets.QPushButton(text)
            button.setEnabled(False)
            row.addWidget(button)
        if spec.get("mock_enabled"):
            mock_button = QtWidgets.QPushButton("运行 Mock 辨识")
            if spec.get("mock_action") == "inductance":
                mock_button.clicked.connect(self.run_mock_inductance_identification)
            else:
                mock_button.clicked.connect(self.run_mock_resistance_identification)
            row.addWidget(mock_button)
        card.body.addLayout(row)
        card.body.addWidget(InfoBox("当前状态", "真实辨识需要协议、安全门限和硬件联调。本页仅定义专业工作流和数据窗口。"))
        card.body.addStretch(1)
        return card

    def _module_plot_panel(self, spec: dict[str, object]) -> QtWidgets.QWidget:
        card = SectionCard("相关变量预览", "辨识时必须看到关键变量变化，避免只输出一个黑盒结果。")
        plot = pg.PlotWidget(title=str(spec["title"]))
        plot.setBackground(COLORS["scope_bg"])
        plot.showGrid(x=True, y=True, alpha=0.18)
        plot.setLabel("bottom", "时间", "s")
        plot.setLabel("left", "归一化信号")
        plot.setMouseEnabled(x=True, y=True)
        plot.addLegend(offset=(-12, 12))
        self._populate_identification_plot(plot, str(spec["plot"]))
        self.module_plots[str(spec["key"])] = plot
        card.body.addWidget(plot, 1)

        signal_row = QtWidgets.QHBoxLayout()
        signal_row.setSpacing(8)
        for index, signal in enumerate(spec["signals"]):
            box = QtWidgets.QCheckBox(str(signal))
            box.setChecked(index < 3)
            box.setEnabled(False)
            signal_row.addWidget(box)
        signal_row.addStretch(1)
        card.body.addLayout(signal_row)
        return card

    def _module_result_panel(self, spec: dict[str, object]) -> QtWidgets.QWidget:
        card = SectionCard("拟合结果 / 写入建议")
        card.setMinimumWidth(330)
        table = QtWidgets.QTableWidget(len(spec["outputs"]), 5)
        table.setHorizontalHeaderLabels(["参数", "估计值", "单位", "置信度", "状态"])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setDefaultSectionSize(28)
        for row, values in enumerate(spec["outputs"]):
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                table.setItem(row, column, item)
        card.body.addWidget(table)
        self.result_tables[str(spec["key"])] = table
        card.body.addWidget(
            InfoBox(
                "写入原则",
                "真实硬件阶段只给出建议值。参数写入必须经过范围检查、运行状态检查和人工确认。",
            )
        )
        return card

    def _populate_identification_plot(self, plot: pg.PlotWidget, plot_kind: str) -> None:
        x_values = [index * 0.002 for index in range(500)]
        if plot_kind == "step":
            series = [
                ("电流反馈", [1.0 - math.exp(-index / 55.0) for index in range(500)], "#22d3ee"),
                ("注入电压", [0.0 if index < 20 else 1.0 for index in range(500)], "#fbbf24"),
            ]
        elif plot_kind == "current":
            series = [
                ("Id", [0.7 * math.sin(index * 0.035) for index in range(500)], "#38bdf8"),
                ("Iq", [0.7 * math.sin(index * 0.035 + 1.57) for index in range(500)], "#f472b6"),
                ("Vdq", [0.25 * math.sin(index * 0.07) for index in range(500)], "#a7f3d0"),
            ]
        elif plot_kind == "angle":
            series = [
                ("编码器角度", [math.sin(index * 0.025) for index in range(500)], "#fbbf24"),
                ("估计角度", [math.sin(index * 0.025 + 0.08) for index in range(500)], "#22d3ee"),
                ("角度误差", [0.08 * math.sin(index * 0.025) for index in range(500)], "#f87171"),
            ]
        else:
            series = [
                ("速度", [1.0 - math.exp(-index / 90.0) + 0.04 * math.sin(index * 0.05) for index in range(500)], "#22d3ee"),
                ("目标", [0.0 if index < 25 else 1.0 for index in range(500)], "#fbbf24"),
                ("Iq", [0.4 * math.exp(-index / 180.0) for index in range(500)], "#a78bfa"),
            ]
        for name, values, color in series:
            plot.plot(x_values, values, pen=pg.mkPen(color, width=2.0), name=name)

    def run_mock_resistance_identification(self):
        result = MockResistanceIdentification().run()
        self.last_identification_results["resistance"] = result
        self._apply_identification_result("resistance", result)
        return result

    def run_mock_inductance_identification(self):
        result = MockInductanceIdentification().run()
        self.last_identification_results["inductance"] = result
        self._apply_identification_result("inductance", result)
        return result

    def _apply_identification_result(self, module_key: str, result) -> None:
        table = self.result_tables[module_key]
        table.setRowCount(len(result.estimates))
        for row, estimate in enumerate(result.estimates):
            values = [
                estimate.key,
                self._format_estimate_value(estimate.value),
                estimate.unit,
                "--" if estimate.confidence is None else f"{estimate.confidence * 100.0:.1f}%",
                estimate.status,
            ]
            for column, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                if estimate.description:
                    item.setToolTip(estimate.description)
                table.setItem(row, column, item)

        plot = self.module_plots[module_key]
        plot.clear()
        colors = ["#22d3ee", "#fbbf24", "#a78bfa", "#f87171"]
        for index, (channel, values) in enumerate(result.trace.channels.items()):
            plot.plot(
                result.trace.time_s,
                values,
                pen=pg.mkPen(colors[index % len(colors)], width=2.0),
                name=f"{channel} ({result.trace.units.get(channel, '')})",
            )
        plot.enableAutoRange()
        self.module_logs[module_key].setPlainText(
            "事件日志\n"
            f"- {result.task.title}\n"
            f"- 样本数: {len(result.trace.time_s)}\n"
            f"- {result.summary}\n"
            "- 当前结果不会写入 AxDr_L，仅作为 Mock 辨识闭环预览。"
        )

    def _format_estimate_value(self, value: object) -> str:
        return f"{value:.6g}" if isinstance(value, float) else str(value)


class ObserverWorkbenchPage(QtWidgets.QWidget):
    """Sensorless observer and angle-estimation workbench placeholders."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("观测器", "无感观测器、估计角度、编码器角度和误差分析窗口。"))

        top = QtWidgets.QGridLayout()
        top.setSpacing(12)
        cards = [
            WorkflowCard("编码器 vs 观测器", "Angle", ["对比 encoder_angle、electrical_angle、estimated_angle", "预留角度误差 RMS、峰值和延迟估计"], ["开始对比"]),
            WorkflowCard("低速无感评估", "Low Speed", ["低速反电动势弱时的稳定性、噪声和漂移", "预留启动区间分析"], ["生成实验"]),
            WorkflowCard("PLL 参数整定", "PLL", ["PLL Kp/Ki、带宽、相位滞后和噪声抑制", "与滤波页共享频域工具"], ["整定向导"]),
            WorkflowCard("故障关联", "Fault", ["观测器失锁、编码器异常、过流联动", "用于工程诊断和课程案例"], ["查看案例"]),
        ]
        for index, card in enumerate(cards):
            top.addWidget(card, index // 2, index % 2)
        layout.addLayout(top)

        plot_card = SectionCard("角度误差预览")
        plot = pg.PlotWidget(title="estimated angle - encoder angle")
        plot.setBackground(COLORS["scope_bg"])
        plot.showGrid(x=True, y=True, alpha=0.18)
        plot.setLabel("bottom", "时间", "s")
        plot.setLabel("left", "误差", "rad")
        x_values = [index * 0.01 for index in range(500)]
        y_values = [0.05 * math.sin(index * 0.04) + 0.01 * math.sin(index * 0.37) for index in range(500)]
        plot.plot(x_values, y_values, pen=pg.mkPen("#2dd4bf", width=2.2))
        plot_card.body.addWidget(plot)
        layout.addWidget(plot_card, 1)
