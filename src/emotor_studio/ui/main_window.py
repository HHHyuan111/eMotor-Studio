"""Main window for the eMotor-Studio workbench."""

from __future__ import annotations

from datetime import datetime

from PySide6 import QtCore, QtWidgets

from emotor_studio.backend import MockBackend
from emotor_studio.models import FaultEvent, TelemetrySample
from emotor_studio.pages import (
    AppSettingsPage,
    CommandPage,
    ControlTuningPage,
    DashboardPage,
    DataAnalysisPage,
    ExperimentAnalysisPage,
    FaultPage,
    FirmwarePage,
    FilterDesignPage,
    FocPage,
    HardwarePage,
    IdentificationPage,
    LoggerPage,
    MotorSettingsPage,
    ObserverWorkbenchPage,
    ParameterPage,
    ReportPage,
    ResearchWorkbenchPage,
    SampledDataPage,
    ScopePage,
    SystemToolsPage,
    TerminalPage,
)
from emotor_studio.ui.components import PageScrollArea, StatusChip
from emotor_studio.ui.theme import APP_STYLE


class MainWindow(QtWidgets.QMainWindow):
    telemetry_received = QtCore.Signal(object)
    fault_received = QtCore.Signal(object)

    def __init__(self, backend: MockBackend | None = None) -> None:
        super().__init__()
        self.setWindowTitle("eMotor-Studio")
        self.resize(1600, 940)
        self.setMinimumSize(1120, 740)
        self.backend = backend or MockBackend()
        self.backend.add_telemetry_callback(self._emit_telemetry)
        self.backend.add_fault_callback(self._emit_fault)
        self.telemetry_received.connect(self._on_telemetry)
        self.fault_received.connect(self._on_fault)
        self._build_ui()
        self.backend.connect()
        self.backend.start()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.backend.tick(0.05))
        self.timer.start(50)

    def _build_ui(self) -> None:
        self.setStyleSheet(APP_STYLE)
        self._build_menus()
        central = QtWidgets.QWidget()
        root = QtWidgets.QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.setCentralWidget(central)
        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_workspace(), 1)

    def _build_menus(self) -> None:
        menu_bar = self.menuBar()
        menu_specs = [
            ("文件", ["打开配置", "保存配置", "导出当前数据", "退出"]),
            ("编辑", ["首选项", "重置窗口布局"]),
            ("配置备份", ["备份电机配置", "备份应用配置", "恢复配置"]),
            ("向导", ["FOC 设置向导", "电机参数辨识", "应用设置向导"]),
            ("终端", ["显示帮助", "打印故障", "打印线程", "清空终端"]),
            ("开发者", ["CAN 工具", "调试控制台", "SWD Programmer", "脚本工具"]),
            ("帮助", ["项目说明", "安全提示", "关于 eMotor-Studio"]),
        ]
        for menu_title, action_titles in menu_specs:
            menu = menu_bar.addMenu(menu_title)
            for action_title in action_titles:
                action = menu.addAction(action_title)
                action.setEnabled(action_title == "退出")
                if action_title == "退出":
                    action.triggered.connect(self.close)

    def _build_sidebar(self) -> QtWidgets.QWidget:
        sidebar = QtWidgets.QWidget()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(244)
        sidebar_layout = QtWidgets.QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.setSpacing(7)

        title = QtWidgets.QLabel("eMotor-Studio")
        title.setObjectName("appTitle")
        subtitle = QtWidgets.QLabel("教学 · 科研 · 工程电机控制平台")
        subtitle.setObjectName("appSubtitle")
        sidebar_layout.addWidget(title)
        sidebar_layout.addWidget(subtitle)
        sidebar_layout.addSpacing(10)

        self.nav = QtWidgets.QListWidget()
        self.nav.setObjectName("navList")
        self.nav.setFixedWidth(212)
        sidebar_layout.addWidget(self.nav, 5)

        device_title = QtWidgets.QLabel("当前目标")
        device_title.setObjectName("appSubtitle")
        sidebar_layout.addWidget(device_title)
        self.device_list = QtWidgets.QListWidget()
        self.device_list.setObjectName("deviceList")
        self.device_list.addItems(["Mock 仿真", "AxDr_L 硬件待接入"])
        self.device_list.setFixedHeight(62)
        sidebar_layout.addWidget(self.device_list)
        scan_button = QtWidgets.QPushButton("硬件扫描（待实现）")
        scan_button.setEnabled(False)
        sidebar_layout.addWidget(scan_button)

        footer = QtWidgets.QLabel("Mock 可运行 / AxDr_L 对齐")
        footer.setObjectName("appSubtitle")
        sidebar_layout.addWidget(footer)
        return sidebar

    def _build_workspace(self) -> QtWidgets.QWidget:
        workspace = QtWidgets.QWidget()
        workspace.setObjectName("pageContainer")
        workspace_layout = QtWidgets.QVBoxLayout(workspace)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        top_bar = QtWidgets.QScrollArea()
        top_bar.setObjectName("topBar")
        top_bar.setWidgetResizable(True)
        top_bar.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        top_bar.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        top_bar.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        top_content = QtWidgets.QWidget()
        top_bar.setWidget(top_content)
        top_bar.setFixedHeight(52)
        status_row = QtWidgets.QHBoxLayout(top_content)
        status_row.setContentsMargins(18, 10, 18, 10)
        status_row.setSpacing(9)
        self.backend_label = StatusChip("当前后端：Mock")
        self.connection_label = StatusChip("连接状态：已连接", "ok")
        self.mode_label = StatusChip("运行状态：--")
        self.fault_label = StatusChip("故障状态：无故障", "ok")
        self.strategy_label = StatusChip("通信策略：串口优先")
        self.session_label = StatusChip(f"会话：{datetime.now().strftime('%H:%M')}")
        for widget in [
            self.backend_label,
            self.connection_label,
            self.mode_label,
            self.fault_label,
            self.strategy_label,
            self.session_label,
        ]:
            status_row.addWidget(widget)
        status_row.addStretch(1)
        workspace_layout.addWidget(top_bar)

        self.stack = QtWidgets.QStackedWidget()
        workspace_layout.addWidget(self.stack, 1)

        self.dashboard_page = DashboardPage(self.backend)
        self.hardware_page = HardwarePage()
        self.firmware_page = FirmwarePage()
        self.motor_settings_page = MotorSettingsPage()
        self.control_tuning_page = ControlTuningPage()
        self.filter_design_page = FilterDesignPage()
        self.parameter_page = ParameterPage(self.backend)
        self.foc_page = FocPage()
        self.app_settings_page = AppSettingsPage()
        self.command_page = CommandPage(self.backend)
        self.scope_page = ScopePage(self.backend.read_signal_schema())
        self.sampled_data_page = SampledDataPage()
        self.research_page = ResearchWorkbenchPage()
        self.experiment_page = ExperimentAnalysisPage()
        self.identification_page = IdentificationPage()
        self.observer_page = ObserverWorkbenchPage()
        self.data_analysis_page = DataAnalysisPage()
        self.fault_page = FaultPage(self.backend.read_fault_schema())
        self.logger_page = LoggerPage(self.backend.read_signal_schema())
        self.report_page = ReportPage(self.logger_page.samples)
        self.terminal_page = TerminalPage()
        self.system_tools_page = SystemToolsPage(
            [
                ("电机设置", self.motor_settings_page),
                ("FOC", self.foc_page),
                ("滤波 / 陷波", self.filter_design_page),
                ("应用设置", self.app_settings_page),
                ("观测器", self.observer_page),
                ("数据分析", self.data_analysis_page),
                ("固件", self.firmware_page),
                ("Terminal", self.terminal_page),
            ]
        )

        self._add_nav_group("总览")
        self._add_page("仪表盘", self.dashboard_page)
        self._add_page("连接", self.hardware_page)
        self._add_nav_group("实时调试")
        self._add_page("波形", self.scope_page)
        self._add_page("采样", self.sampled_data_page)
        self._add_page("记录", self.logger_page)
        self._add_nav_group("控制调参")
        self._add_page("命令", self.command_page)
        self._add_page("参数", self.parameter_page)
        self._add_page("三环", self.control_tuning_page)
        self._add_nav_group("科研工程")
        self._add_page("实验", self.research_page)
        self._add_page("分析", self.experiment_page)
        self._add_page("辨识", self.identification_page)
        self._add_nav_group("诊断输出")
        self._add_page("故障", self.fault_page)
        self._add_page("报告", self.report_page)
        self._add_nav_group("系统")
        self._add_page("工具", self.system_tools_page)

        self.nav.currentRowChanged.connect(self._on_nav_changed)
        first_page_row = self._first_page_row()
        self.nav.setCurrentRow(first_page_row)
        self._on_nav_changed(first_page_row)
        return workspace

    def _add_nav_group(self, title: str) -> None:
        item = QtWidgets.QListWidgetItem(title)
        item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, None)
        self.nav.addItem(item)

    def _add_page(self, title: str, page: QtWidgets.QWidget) -> None:
        stack_index = self.stack.addWidget(PageScrollArea(page))
        item = QtWidgets.QListWidgetItem(f"  {title}")
        item.setData(QtCore.Qt.ItemDataRole.UserRole, stack_index)
        self.nav.addItem(item)

    def _first_page_row(self) -> int:
        for row in range(self.nav.count()):
            if self.nav.item(row).data(QtCore.Qt.ItemDataRole.UserRole) is not None:
                return row
        return 0

    def _on_nav_changed(self, row: int) -> None:
        if row < 0:
            return
        item = self.nav.item(row)
        stack_index = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if stack_index is None:
            self.nav.setCurrentRow(self._first_page_row())
            return
        self.stack.setCurrentIndex(int(stack_index))

    def _emit_telemetry(self, sample: TelemetrySample) -> None:
        self.telemetry_received.emit(sample)

    def _emit_fault(self, fault: FaultEvent) -> None:
        self.fault_received.emit(fault)

    def _on_telemetry(self, sample: TelemetrySample) -> None:
        self.connection_label.setText("连接状态：已连接")
        self.connection_label.set_state("ok")
        run_state = sample.run_state.value
        self.mode_label.setText(f"运行状态：{self._run_state_text(run_state)} / {sample.system_mode.value}")
        self.mode_label.set_state("fault" if sample.faults else ("ok" if run_state == "runing" else "idle"))
        if sample.faults:
            self.fault_label.setText(f"故障状态：{', '.join(sample.faults)}")
            self.fault_label.set_state("fault")
        else:
            self.fault_label.setText("故障状态：无故障")
            self.fault_label.set_state("ok")
        self.session_label.setText(f"转速：{sample.rpm:,.0f} rpm")
        self.dashboard_page.update_telemetry(sample)
        self.scope_page.update_telemetry(sample)
        self.fault_page.update_telemetry(sample)
        self.logger_page.update_telemetry(sample)

    def _on_fault(self, fault: FaultEvent) -> None:
        self.fault_page.add_fault(fault)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.timer.stop()
        self.backend.disconnect()
        super().closeEvent(event)

    @staticmethod
    def _run_state_text(value: str) -> str:
        return {
            "runing": "运行",
            "stop": "停止",
            "fault": "故障",
            "prech": "预充",
        }.get(value, value)
