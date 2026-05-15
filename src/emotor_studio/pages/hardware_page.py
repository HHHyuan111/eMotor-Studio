"""VESC-like connection page for eMotor-Studio."""

from __future__ import annotations

from PySide6 import QtWidgets

from emotor_studio.ui.components import InfoBox, KpiCard, PageHeader, SectionCard


class HardwarePage(QtWidgets.QWidget):
    """Connection strategy and transport selection page.

    The page mirrors VESC Tool's connection-oriented layout while keeping all
    real hardware controls disabled until Phase 7.2.
    """

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("硬件连接", "AxDr_L 通信入口。当前仍为 Mock 模式。"))

        summary = SectionCard("当前路线", "V1.1 串口优先，CAN 和 J-Link/RTT 作为后续扩展或调试辅助。")
        route_layout = QtWidgets.QGridLayout()
        route_layout.setHorizontalSpacing(10)
        route_layout.setVerticalSpacing(10)
        for title, value, unit, state in [
            ("Mock", "已启用", "当前默认后端", "ok"),
            ("USB CDC / Type-C COM", "优先", "若枚举为 COM 口", "idle"),
            ("J1 UART + USB-TTL", "备用", "Type-C 只供电时", "idle"),
            ("CAN", "后续", "多轴/工程化", "stop"),
            ("J-Link RTT", "辅助", "调试观察", "warning"),
        ]:
            card = KpiCard(title, unit, state)
            card.set_value(value, unit, state)
            card.setMaximumHeight(108)
            index = route_layout.count()
            route_layout.addWidget(card, index // 3, index % 3)
        summary.body.addLayout(route_layout)
        layout.addWidget(summary)

        tabs = QtWidgets.QTabWidget()
        tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        tabs.addTab(self._serial_tab(), "串口 / USB CDC")
        tabs.addTab(self._can_tab(), "CAN bus")
        tabs.addTab(self._tcp_tab(), "TCP / 调试桥")
        tabs.addTab(self._debug_tab(), "J-Link RTT")
        layout.addWidget(tabs, 1)

        layout.addWidget(
            InfoBox("本阶段边界", "当前不扫描端口、不打开串口、不执行 PING。Phase 7.2-A 后接入最小握手。")
        )

    def _serial_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        panel = SectionCard("串口 / USB CDC", "Type-C COM 优先；J1 UART + USB-TTL 作为备选。")
        row = QtWidgets.QGridLayout()
        row.setHorizontalSpacing(8)
        row.setVerticalSpacing(8)
        row.addWidget(QtWidgets.QLabel("端口"), 0, 0)
        port_box = QtWidgets.QComboBox()
        port_box.addItems(["Mock 虚拟端口", "COM 待扫描"])
        port_box.setEnabled(False)
        row.addWidget(port_box, 0, 1, 1, 2)
        baud = QtWidgets.QSpinBox()
        baud.setRange(9600, 3000000)
        baud.setValue(115200)
        baud.setSuffix(" bps")
        baud.setPrefix("Baud: ")
        baud.setEnabled(False)
        row.addWidget(baud, 0, 3)
        for column, text in enumerate(["刷新", "断开", "连接"], start=4):
            button = QtWidgets.QPushButton(text)
            button.setEnabled(False)
            row.addWidget(button, 0, column)
        panel.body.addLayout(row)
        panel.body.addWidget(InfoBox("协议状态", "AxDr_L 当前没有上位机协议。后续先实现 PING、固件信息、telemetry、参数读写。"))
        layout.addWidget(panel)
        layout.addStretch(1)
        return tab

    def _can_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        panel = SectionCard("CAN bus", "对齐 VESC Tool 的 CAN 节点发现思路，但 eMotor-Studio 放在 V1.2 / V2.0。")
        row = QtWidgets.QGridLayout()
        row.setHorizontalSpacing(8)
        row.setVerticalSpacing(8)
        interface_box = QtWidgets.QComboBox()
        interface_box.addItems(["SocketCAN / CANable 待实现", "PCAN / ZLG-CAN 待评估"])
        interface_box.setEnabled(False)
        node_box = QtWidgets.QComboBox()
        node_box.addItems(["Node ID 待扫描"])
        node_box.setEnabled(False)
        bitrate = QtWidgets.QSpinBox()
        bitrate.setRange(125, 1000)
        bitrate.setValue(500)
        bitrate.setSuffix(" kbit/s")
        bitrate.setEnabled(False)
        for column, (label, widget) in enumerate([("接口", interface_box), ("节点", node_box), ("波特率", bitrate)]):
            row.addWidget(QtWidgets.QLabel(label), 0, column * 2)
            row.addWidget(widget, 0, column * 2 + 1)
        scan_button = QtWidgets.QPushButton("扫描")
        scan_button.setEnabled(False)
        connect_button = QtWidgets.QPushButton("连接")
        connect_button.setEnabled(False)
        row.addWidget(scan_button, 1, 0)
        row.addWidget(connect_button, 1, 1)
        panel.body.addLayout(row)
        panel.body.addWidget(InfoBox("阶段定位", "CAN 更适合多轴、长线缆和工程部署，不作为 V1.1 第一落点。"))
        layout.addWidget(panel)
        layout.addStretch(1)
        return tab

    def _tcp_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        panel = SectionCard("TCP / 调试桥", "为后续仿真、远程调试或桥接工具预留，当前不实现。")
        grid = QtWidgets.QGridLayout()
        host = QtWidgets.QLineEdit("127.0.0.1")
        host.setEnabled(False)
        port = QtWidgets.QSpinBox()
        port.setRange(1, 65535)
        port.setValue(65102)
        port.setPrefix("Port: ")
        port.setEnabled(False)
        detected = QtWidgets.QComboBox()
        detected.addItem("未发现远程设备")
        detected.setEnabled(False)
        grid.addWidget(QtWidgets.QLabel("地址"), 0, 0)
        grid.addWidget(host, 0, 1)
        grid.addWidget(port, 0, 2)
        grid.addWidget(QtWidgets.QPushButton("连接（待实现）"), 0, 3)
        grid.addWidget(QtWidgets.QLabel("检测设备"), 1, 0)
        grid.addWidget(detected, 1, 1, 1, 2)
        grid.addWidget(QtWidgets.QPushButton("断开（待实现）"), 1, 3)
        for row in range(grid.rowCount()):
            for column in range(grid.columnCount()):
                widget = grid.itemAtPosition(row, column)
                if widget and isinstance(widget.widget(), QtWidgets.QPushButton):
                    widget.widget().setEnabled(False)
        panel.body.addLayout(grid)
        layout.addWidget(panel)
        layout.addStretch(1)
        return tab

    def _debug_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(12, 12, 12, 12)
        panel = SectionCard("J-Link / RTT", "调试辅助通道，不作为 eMotor-Studio V1.1 主通信。")
        panel.body.addWidget(
            InfoBox(
                "推荐用法",
                "SWD/J-Link 适合固件断点、变量观察、RTT 日志和疑难问题诊断。上位机主链路仍走同一套串口协议。",
            )
        )
        row = QtWidgets.QHBoxLayout()
        for text in ["打开 RTT Viewer", "读取调试日志", "连接 J-Link"]:
            button = QtWidgets.QPushButton(text)
            button.setEnabled(False)
            row.addWidget(button)
        row.addStretch(1)
        panel.body.addLayout(row)
        layout.addWidget(panel)
        layout.addStretch(1)
        return tab
