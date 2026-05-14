"""Scope page with a signal sidebar, large plot area, and bottom control bar."""

from __future__ import annotations

from collections import deque
import csv
from pathlib import Path
from typing import Any

from PySide6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from emotor_studio.config import load_signals
from emotor_studio.models import TelemetrySample
from emotor_studio.ui.components import PageHeader, SectionCard
from emotor_studio.ui.theme import COLORS


class ScopePage(QtWidgets.QWidget):
    _CHINESE_SIGNAL_NAMES = {
        "bus_voltage": "母线电压",
        "bus_current": "母线电流",
        "phase_current_a": "A相电流",
        "phase_current_b": "B相电流",
        "phase_current_c": "C相电流",
        "current_d": "d轴电流",
        "current_q": "q轴电流",
        "current_abs": "电流幅值",
        "voltage_d": "d轴电压",
        "voltage_q": "q轴电压",
        "electrical_angle": "电角度",
        "encoder_angle": "编码器角度",
        "mechanical_position_multi": "机械位置",
        "rotor_speed_filtered": "滤波转速",
        "mechanical_speed": "机械转速",
        "speed_target_mechanical": "目标转速",
        "current_target_d": "d轴电流给定",
        "current_target_q": "q轴电流给定",
        "position_target_mechanical": "位置给定",
        "duty_a": "A相占空比",
        "duty_b": "B相占空比",
        "duty_c": "C相占空比",
        "mos_temperature": "MOS温度",
        "coil_temperature": "线圈温度",
        "fault_word": "故障字",
    }
    _PRESETS = {
        "默认": {"mechanical_speed", "speed_target_mechanical", "bus_voltage", "current_q", "current_d", "mos_temperature"},
        "电流环": {"current_q", "current_d", "current_target_q", "current_target_d", "voltage_q", "voltage_d"},
        "速度环": {"mechanical_speed", "speed_target_mechanical", "rotor_speed_filtered", "bus_voltage", "bus_current"},
        "角度/位置": {"electrical_angle", "encoder_angle", "mechanical_position_multi", "position_target_mechanical"},
        "温度/保护": {"mos_temperature", "coil_temperature", "bus_voltage", "bus_current", "fault_word"},
        "PWM": {"duty_a", "duty_b", "duty_c", "bus_voltage", "current_abs"},
    }

    def __init__(
        self,
        signal_schema: list[dict[str, Any]] | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._signal_schema = [signal for signal in (signal_schema or load_signals()) if signal.get("scope", False)]
        self._max_samples = 600
        self._visible_window_seconds = 30.0
        self._time: deque[float] = deque(maxlen=self._max_samples)
        self._series: dict[str, deque[float]] = {}
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._fixed_curves: dict[str, tuple[pg.PlotDataItem, str]] = {}
        self._fixed_plots: list[pg.PlotWidget] = []
        self._channel_items: dict[str, QtWidgets.QListWidgetItem] = {}
        self._t0: float | None = None
        self._view_locked = True
        self._mouse_proxy: pg.SignalProxy | None = None

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        root.addWidget(PageHeader("实时波形", "配置驱动的工程示波器：暂停后拖动查看历史，滚轮缩放横轴，右键打开中文菜单。"))

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        root.addWidget(self.tabs, 1)

        self._build_rt_tabs()

        custom_tab = QtWidgets.QWidget()
        body = QtWidgets.QHBoxLayout(custom_tab)
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(12)

        signal_panel = SectionCard("信号通道", "按调试目标选择 AxDr_L 映射信号，避免所有变量一次性堆到曲线上。")
        signal_panel.setMinimumWidth(260)
        signal_panel.setMaximumWidth(320)
        preset_row = QtWidgets.QHBoxLayout()
        preset_row.setSpacing(6)
        preset_row.addWidget(QtWidgets.QLabel("预设"))
        self.preset_combo = QtWidgets.QComboBox()
        self.preset_combo.addItems(self._PRESETS.keys())
        self.preset_combo.currentTextChanged.connect(self._apply_channel_preset)
        preset_row.addWidget(self.preset_combo, 1)
        signal_panel.body.addLayout(preset_row)
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText("搜索信号 / 单位 / 说明")
        self.search_box.textChanged.connect(self._filter_channels)
        signal_panel.body.addWidget(self.search_box)
        select_row = QtWidgets.QHBoxLayout()
        select_row.setSpacing(6)
        select_all = QtWidgets.QPushButton("全选")
        select_all.setProperty("variant", "ghost")
        select_all.clicked.connect(lambda: self._set_all_visible_channels(True))
        select_none = QtWidgets.QPushButton("清空选择")
        select_none.setProperty("variant", "ghost")
        select_none.clicked.connect(lambda: self._set_all_visible_channels(False))
        select_row.addWidget(select_all)
        select_row.addWidget(select_none)
        signal_panel.body.addLayout(select_row)
        self.channel_list = QtWidgets.QListWidget()
        self.channel_list.setObjectName("scopeChannelList")
        self.channel_list.itemChanged.connect(self._sync_channel_visibility)
        signal_panel.body.addWidget(self.channel_list, 1)
        body.addWidget(signal_panel)

        plot_panel = SectionCard("曲线区", "亮色曲线用于关键变量；暂停后进入人工查看模式。")
        pg.setConfigOptions(antialias=True, foreground="#d8dee9", background=COLORS["scope_bg"])
        self.plot = pg.PlotWidget(title="自定义实时示波器")
        self.plot.setMenuEnabled(False)
        self.plot.setBackground(COLORS["scope_bg"])
        self.plot.setLabel("bottom", "时间", "s")
        self.plot.setLabel("left", "信号值")
        self.plot.showGrid(x=True, y=True, alpha=0.18)
        self.plot.getPlotItem().hideButtons()
        self.cursor_line = pg.InfiniteLine(
            angle=90,
            movable=False,
            pen=pg.mkPen("#94a3b8", width=1, style=QtCore.Qt.PenStyle.DashLine),
        )
        self.cursor_line.setVisible(False)
        self.plot.addItem(self.cursor_line, ignoreBounds=True)
        self.plot.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.plot.customContextMenuRequested.connect(self._show_context_menu)
        self.plot.viewport().installEventFilter(self)
        self._mouse_proxy = pg.SignalProxy(
            self.plot.scene().sigMouseMoved,
            rateLimit=30,
            slot=self._on_mouse_moved,
        )
        view_box = self.plot.getViewBox()
        view_box.setMouseMode(pg.ViewBox.PanMode)
        view_box.setMouseEnabled(x=False, y=False)
        view_box.setDefaultPadding(0.03)
        view_box.setLimits(xMin=0.0, minXRange=1.0, maxXRange=3600.0)
        plot_panel.body.addWidget(self.plot, 1)
        body.addWidget(plot_panel, 1)
        self.tabs.addTab(custom_tab, "自定义通道")

        controls = SectionCard("示波器控制")
        control_row = QtWidgets.QHBoxLayout()
        control_row.setSpacing(8)
        self.pause_box = QtWidgets.QCheckBox("暂停")
        self.pause_box.toggled.connect(self._set_paused)
        clear_button = QtWidgets.QPushButton("清空")
        clear_button.setProperty("variant", "ghost")
        clear_button.clicked.connect(self.clear)
        export_button = QtWidgets.QPushButton("导出 CSV")
        export_button.setProperty("variant", "ghost")
        export_button.clicked.connect(self._choose_export_path)
        self.lock_box = QtWidgets.QCheckBox("跟随实时")
        self.lock_box.setChecked(True)
        self.lock_box.toggled.connect(self._set_view_locked)
        self.time_window = QtWidgets.QDoubleSpinBox()
        self.time_window.setRange(2.0, 600.0)
        self.time_window.setDecimals(1)
        self.time_window.setSingleStep(5.0)
        self.time_window.setValue(self._visible_window_seconds)
        self.time_window.setSuffix(" s")
        self.time_window.valueChanged.connect(self._set_time_window)
        zoom_in_button = QtWidgets.QPushButton("横轴放大")
        zoom_in_button.setProperty("variant", "ghost")
        zoom_in_button.clicked.connect(lambda: self._zoom_time(0.5))
        zoom_out_button = QtWidgets.QPushButton("横轴缩小")
        zoom_out_button.setProperty("variant", "ghost")
        zoom_out_button.clicked.connect(lambda: self._zoom_time(2.0))
        fit_button = QtWidgets.QPushButton("适应窗口")
        fit_button.setProperty("variant", "ghost")
        fit_button.clicked.connect(self._fit_recent_view)
        show_all_button = QtWidgets.QPushButton("全部历史")
        show_all_button.setProperty("variant", "ghost")
        show_all_button.clicked.connect(self._fit_all_view)
        y_auto_button = QtWidgets.QPushButton("Y轴自适应")
        y_auto_button.setProperty("variant", "ghost")
        y_auto_button.clicked.connect(self._auto_range_y)
        self.window_spin = QtWidgets.QSpinBox()
        self.window_spin.setRange(100, 3000)
        self.window_spin.setSingleStep(100)
        self.window_spin.setValue(self._max_samples)
        self.window_spin.setSuffix(" 点")
        self.window_spin.valueChanged.connect(self._set_window)
        self.status_label = QtWidgets.QLabel("采样状态：运行中")
        self.status_label.setObjectName("hintText")
        self.channel_count_label = QtWidgets.QLabel("已选通道：0")
        self.channel_count_label.setObjectName("hintText")
        left_controls = [
            self.pause_box,
            clear_button,
            export_button,
            self.lock_box,
            QtWidgets.QLabel("时间窗"),
            self.time_window,
            zoom_in_button,
            zoom_out_button,
            fit_button,
            show_all_button,
            y_auto_button,
            QtWidgets.QLabel("缓存"),
            self.window_spin,
        ]
        for widget in left_controls:
            control_row.addWidget(widget)
        control_row.addStretch(1)
        self.cursor_label = QtWidgets.QLabel("光标：--")
        self.cursor_label.setObjectName("hintText")
        control_row.addWidget(self.cursor_label)
        control_row.addWidget(self.status_label)
        control_row.addWidget(self.channel_count_label)
        controls.body.addLayout(control_row)
        root.addWidget(controls)

        self._build_channels()
        self._update_status_labels()

    def _build_rt_tabs(self) -> None:
        tab_specs = [
            (
                "电流",
                "电流 (A)",
                [
                    ("phase_current_a", "A相电流", "#22d3ee"),
                    ("phase_current_b", "B相电流", "#fbbf24"),
                    ("phase_current_c", "C相电流", "#a78bfa"),
                    ("current_q", "q轴电流", "#34d399"),
                    ("current_d", "d轴电流", "#fb7185"),
                ],
            ),
            (
                "温度",
                "温度 (degC)",
                [
                    ("mos_temperature", "MOS温度", "#f97316"),
                    ("coil_temperature", "线圈温度", "#84cc16"),
                ],
            ),
            (
                "转速",
                "速度 (rad/s)",
                [
                    ("mechanical_speed", "实际转速", "#60a5fa"),
                    ("speed_target_mechanical", "目标转速", "#34d399"),
                    ("rotor_speed_filtered", "滤波转速", "#fbbf24"),
                ],
            ),
            (
                "FOC",
                "FOC 变量",
                [
                    ("current_q", "Iq", "#34d399"),
                    ("current_d", "Id", "#fb7185"),
                    ("voltage_q", "Vq", "#22d3ee"),
                    ("voltage_d", "Vd", "#a78bfa"),
                ],
            ),
        ]
        for title, left_label, channels in tab_specs:
            tab, plot = self._make_plot_tab(f"{title}实时数据", left_label)
            for signal_name, curve_name, color in channels:
                curve = plot.plot(name=curve_name, pen=pg.mkPen(color, width=2.3))
                self._fixed_curves[f"{title}:{signal_name}"] = (curve, signal_name)
            self.tabs.addTab(tab, title)
        self.tabs.addTab(self._rotor_position_tab(), "转子位置")

    def _make_plot_tab(self, title: str, left_label: str) -> tuple[QtWidgets.QWidget, pg.PlotWidget]:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        plot = self._make_plot(title, left_label)
        plot.addLegend(offset=(10, 10))
        layout.addWidget(plot, 1)
        hint = QtWidgets.QLabel("按 VESC Realtime Data 的分类思路组织：电流、温度、转速、FOC、转子位置。")
        hint.setObjectName("hintText")
        layout.addWidget(hint)
        return tab, plot

    def _make_plot(self, title: str, left_label: str) -> pg.PlotWidget:
        pg.setConfigOptions(antialias=True, foreground="#d8dee9", background=COLORS["scope_bg"])
        plot = pg.PlotWidget(title=title)
        plot.setMenuEnabled(False)
        plot.setBackground(COLORS["scope_bg"])
        plot.setLabel("bottom", "时间", "s")
        plot.setLabel("left", left_label)
        plot.showGrid(x=True, y=True, alpha=0.18)
        plot.getPlotItem().hideButtons()
        view_box = plot.getViewBox()
        view_box.setMouseMode(pg.ViewBox.PanMode)
        view_box.setDefaultPadding(0.03)
        view_box.setLimits(xMin=0.0, minXRange=1.0, maxXRange=3600.0)
        self._fixed_plots.append(plot)
        return plot

    def _rotor_position_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        left = QtWidgets.QVBoxLayout()
        self.position_bar = QtWidgets.QProgressBar()
        self.position_bar.setRange(0, 359)
        self.position_bar.setFormat("%v deg")
        left.addWidget(self.position_bar)
        plot = self._make_plot("转子位置 / 角度", "角度 (rad)")
        for signal_name, curve_name, color in [
            ("electrical_angle", "电角度", "#22d3ee"),
            ("encoder_angle", "编码器角度", "#fbbf24"),
            ("mechanical_position_multi", "机械位置", "#34d399"),
        ]:
            curve = plot.plot(name=curve_name, pen=pg.mkPen(color, width=2.3))
            self._fixed_curves[f"position:{signal_name}"] = (curve, signal_name)
        plot.addLegend(offset=(10, 10))
        left.addWidget(plot, 1)
        layout.addLayout(left, 1)
        side = QtWidgets.QVBoxLayout()
        for text in ["电感检测", "编码器", "观测器", "PID位置", "观测器 vs 编码器", "PID误差", "停止"]:
            button = QtWidgets.QPushButton(text)
            button.setEnabled(False)
            side.addWidget(button)
        side.addStretch(1)
        layout.addLayout(side)
        return tab

    def clear(self) -> None:
        self._time.clear()
        for values in self._series.values():
            values.clear()
        self._t0 = None
        for curve in self._curves.values():
            curve.setData([], [])
        for curve, _signal_name in self._fixed_curves.values():
            curve.setData([], [])
        self.cursor_line.setVisible(False)
        self.cursor_label.setText("光标：--")
        self._update_status_labels()

    def update_telemetry(self, sample: TelemetrySample) -> None:
        if self.pause_box.isChecked():
            self._update_status_labels()
            return
        if self._t0 is None:
            self._t0 = sample.timestamp
        self._time.append(sample.timestamp - self._t0)
        x_values = list(self._time)
        for signal in self._signal_schema:
            name = str(signal["name"])
            value = self._numeric_signal(sample, name)
            self._series[name].append(value)
            if self._channel_items[name].checkState() == QtCore.Qt.CheckState.Checked:
                self._curves[name].setData(x_values, list(self._series[name]))
        for curve, signal_name in self._fixed_curves.values():
            if signal_name in self._series:
                curve.setData(x_values, list(self._series[signal_name]))
        self._update_position_bar(sample)
        if self._view_locked and not self.pause_box.isChecked() and x_values:
            self._apply_recent_x_range(x_values[-1])
            self._auto_range_y()
        self._update_status_labels()

    def export_csv(self, path: str | Path) -> Path:
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        selected = self._selected_channels()
        with export_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["time_s", *selected])
            for index, timestamp in enumerate(self._time):
                row = [timestamp]
                for name in selected:
                    values = list(self._series[name])
                    row.append(values[index] if index < len(values) else "")
                writer.writerow(row)
        return export_path

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        if watched is self.plot.viewport():
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                mouse_event = event
                if mouse_event.button() == QtCore.Qt.MouseButton.RightButton:
                    self._show_context_menu_global(self._event_global_pos(mouse_event))
                    return True
            if event.type() == QtCore.QEvent.Type.Wheel and not self._allow_manual_x_interaction():
                wheel_event = event
                delta = wheel_event.angleDelta().y() if hasattr(wheel_event, "angleDelta") else 0
                self._zoom_time(0.85 if delta > 0 else 1.18)
                return True
        return super().eventFilter(watched, event)

    def _build_channels(self) -> None:
        default_channels = self._PRESETS["默认"]
        colors = [
            "#62a8ff",
            "#f4c15d",
            "#5fd6b3",
            "#d98989",
            "#b8a1ff",
            "#a7d46f",
            "#63d4e8",
            "#e5e7eb",
            "#f28f61",
            "#8fb3d9",
        ]
        for index, signal in enumerate(self._signal_schema):
            name = str(signal["name"])
            color = colors[index % len(colors)]
            item = QtWidgets.QListWidgetItem(self._channel_label(signal))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, name)
            item.setData(QtCore.Qt.ItemDataRole.DecorationRole, QtGui.QColor(color))
            item.setToolTip(str(signal.get("description") or name))
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.CheckState.Checked if name in default_channels else QtCore.Qt.CheckState.Unchecked)
            self.channel_list.addItem(item)
            self._channel_items[name] = item
            self._series[name] = deque(maxlen=self._max_samples)
            curve = self.plot.plot(pen=pg.mkPen(color, width=2.6))
            curve.setVisible(item.checkState() == QtCore.Qt.CheckState.Checked)
            self._curves[name] = curve
        self._update_status_labels()

    def _apply_channel_preset(self, preset_name: str) -> None:
        selected = self._PRESETS.get(preset_name, set())
        for name, item in self._channel_items.items():
            item.setCheckState(QtCore.Qt.CheckState.Checked if name in selected else QtCore.Qt.CheckState.Unchecked)
        self._update_status_labels()

    def _filter_channels(self, text: str) -> None:
        query = text.strip().lower()
        for index in range(self.channel_list.count()):
            item = self.channel_list.item(index)
            name = str(item.data(QtCore.Qt.ItemDataRole.UserRole))
            haystack = f"{item.text()} {item.toolTip()} {name}".lower()
            item.setHidden(bool(query) and query not in haystack)

    def _set_all_visible_channels(self, checked: bool) -> None:
        state = QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked
        for index in range(self.channel_list.count()):
            item = self.channel_list.item(index)
            if not item.isHidden():
                item.setCheckState(state)
        self._update_status_labels()

    def _set_window(self, value: int) -> None:
        self._max_samples = value
        self._time = deque(self._time, maxlen=self._max_samples)
        for name, series in list(self._series.items()):
            self._series[name] = deque(series, maxlen=self._max_samples)

    def _sync_channel_visibility(self, item: QtWidgets.QListWidgetItem) -> None:
        name = str(item.data(QtCore.Qt.ItemDataRole.UserRole))
        curve = self._curves.get(name)
        if curve is None:
            return
        checked = item.checkState() == QtCore.Qt.CheckState.Checked
        curve.setVisible(checked)
        curve.setData(list(self._time), list(self._series[name])) if checked else curve.setData([], [])
        self._update_status_labels()

    def _choose_export_path(self) -> None:
        path, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "导出示波器数据",
            "emotor_scope.csv",
            "CSV Files (*.csv)",
        )
        if path:
            self.export_csv(path)

    def _show_context_menu(self, position: QtCore.QPoint) -> None:
        self._show_context_menu_global(self.plot.mapToGlobal(position))

    def _show_context_menu_global(self, position: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        pause_action = menu.addAction("继续采样" if self.pause_box.isChecked() else "暂停采样")
        clear_action = menu.addAction("清空曲线")
        export_action = menu.addAction("导出 CSV")
        menu.addSeparator()
        zoom_in_action = menu.addAction("横轴放大")
        zoom_out_action = menu.addAction("横轴缩小")
        fit_action = menu.addAction("适应最近窗口")
        all_action = menu.addAction("显示全部历史")
        menu.addSeparator()
        lock_action = menu.addAction("手动查看" if self.lock_box.isChecked() else "跟随实时")
        auto_action = menu.addAction("自动缩放 Y 轴")
        action = menu.exec(position)
        if action == pause_action:
            self.pause_box.setChecked(not self.pause_box.isChecked())
        elif action == clear_action:
            self.clear()
        elif action == export_action:
            self._choose_export_path()
        elif action == zoom_in_action:
            self._zoom_time(0.5)
        elif action == zoom_out_action:
            self._zoom_time(2.0)
        elif action == fit_action:
            self._fit_recent_view()
        elif action == all_action:
            self._fit_all_view()
        elif action == lock_action:
            self.lock_box.setChecked(not self.lock_box.isChecked())
        elif action == auto_action:
            self._auto_range_y()

    def _event_global_pos(self, event: QtCore.QEvent) -> QtCore.QPoint:
        if hasattr(event, "globalPosition"):
            return event.globalPosition().toPoint()
        if hasattr(event, "globalPos"):
            return event.globalPos()
        return self.plot.mapToGlobal(QtCore.QPoint(0, 0))

    def _set_view_locked(self, locked: bool) -> None:
        self._view_locked = locked
        self._update_plot_interaction()
        if locked and not self.pause_box.isChecked():
            self._fit_recent_view()
        self._update_status_labels()

    def _set_paused(self, paused: bool) -> None:
        self._update_plot_interaction()
        if not paused and self._view_locked:
            self._fit_recent_view()
        self._update_status_labels()

    def _selected_channels(self) -> list[str]:
        return [
            name
            for name, item in self._channel_items.items()
            if item.checkState() == QtCore.Qt.CheckState.Checked
        ]

    def _update_status_labels(self) -> None:
        state = "已暂停" if self.pause_box.isChecked() else "运行中"
        if self.pause_box.isChecked():
            mode = "暂停查看：可左键拖动 / 滚轮缩放横轴"
        else:
            mode = "实时跟随" if self._view_locked else "手动查看"
        self.status_label.setText(f"采样状态：{state} / {mode}")
        self.channel_count_label.setText(f"已选通道：{len(self._selected_channels())}")

    def _set_time_window(self, value: float) -> None:
        self._visible_window_seconds = value
        self._fit_recent_view()

    def _zoom_time(self, factor: float) -> None:
        self.time_window.setValue(min(max(self.time_window.value() * factor, 2.0), 600.0))

    def _fit_recent_view(self) -> None:
        if self._time:
            self._apply_recent_x_range(list(self._time)[-1])
        self._auto_range_y()

    def _fit_all_view(self) -> None:
        if not self._time:
            return
        values = list(self._time)
        self.plot.setXRange(values[0], max(values[-1], values[0] + 1.0), padding=0.02)
        for plot in self._fixed_plots:
            plot.setXRange(values[0], max(values[-1], values[0] + 1.0), padding=0.02)
        self._auto_range_y()

    def _auto_range_y(self) -> None:
        self.plot.enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)
        for plot in self._fixed_plots:
            plot.enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)

    def _allow_manual_x_interaction(self) -> bool:
        return self.pause_box.isChecked() or not self._view_locked

    def _update_plot_interaction(self) -> None:
        manual = self._allow_manual_x_interaction()
        self.plot.getViewBox().setMouseEnabled(x=manual, y=False)

    def _apply_recent_x_range(self, latest_time: float) -> None:
        left = max(0.0, latest_time - self._visible_window_seconds)
        right = max(self._visible_window_seconds, latest_time)
        self.plot.setXRange(left, right, padding=0.01)
        for plot in self._fixed_plots:
            plot.setXRange(left, right, padding=0.01)

    def _update_position_bar(self, sample: TelemetrySample) -> None:
        if not hasattr(self, "position_bar"):
            return
        angle = self._numeric_signal(sample, "electrical_angle")
        degrees = int((angle % 6.283185307179586) / 6.283185307179586 * 359)
        self.position_bar.setValue(degrees)

    def _on_mouse_moved(self, event: tuple[QtCore.QPointF]) -> None:
        if not event:
            return
        scene_pos = event[0]
        if not self.plot.sceneBoundingRect().contains(scene_pos):
            return
        view_pos = self.plot.getViewBox().mapSceneToView(scene_pos)
        self._update_cursor_readout(view_pos.x())

    def _update_cursor_readout(self, x_value: float) -> None:
        if not self._time:
            self.cursor_label.setText("光标：--")
            self.cursor_line.setVisible(False)
            return
        times = list(self._time)
        index = min(range(len(times)), key=lambda item: abs(times[item] - x_value))
        timestamp = times[index]
        self.cursor_line.setPos(timestamp)
        self.cursor_line.setVisible(True)
        pieces = []
        for name in self._selected_channels()[:4]:
            values = list(self._series.get(name, []))
            if index < len(values):
                pieces.append(f"{self._short_channel_label(name)} {values[index]:.4g}")
        suffix = " | ".join(pieces) if pieces else "未选择通道"
        self.cursor_label.setText(f"光标：{timestamp:.2f}s | {suffix}")

    def _short_channel_label(self, name: str) -> str:
        for signal in self._signal_schema:
            if str(signal["name"]) == name:
                return self._CHINESE_SIGNAL_NAMES.get(name, str(signal.get("display_name") or name))
        return name

    def _channel_label(self, signal: dict[str, Any]) -> str:
        name = str(signal["name"])
        display_name = self._CHINESE_SIGNAL_NAMES.get(name, str(signal.get("display_name") or name))
        unit = str(signal.get("unit") or "")
        return f"{display_name} ({unit})" if unit else display_name

    @staticmethod
    def _numeric_signal(sample: TelemetrySample, name: str) -> float:
        if name == "rpm":
            return sample.rpm
        if name == "target_rpm":
            return sample.target_rpm
        value = sample.signals.get(name)
        if isinstance(value, (int, float)):
            return float(value)
        return 0.0
