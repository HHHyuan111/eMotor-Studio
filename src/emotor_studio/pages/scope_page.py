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
        self._max_samples = 6000
        self._visible_window_seconds = 30.0
        self._time: deque[float] = deque(maxlen=self._max_samples)
        self._series: dict[str, deque[float]] = {}
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._fixed_curves: dict[str, tuple[pg.PlotDataItem, str]] = {}
        self._curve_colors: dict[str, str] = {}
        self._fixed_curve_colors: dict[str, str] = {}
        self._fixed_plots: list[pg.PlotWidget] = []
        self._all_plots: list[pg.PlotWidget] = []
        self._plot_channels: dict[pg.PlotWidget, list[str]] = {}
        self._plot_cursor_lines: dict[pg.PlotWidget, dict[str, pg.InfiniteLine]] = {}
        self._channel_items: dict[str, QtWidgets.QListWidgetItem] = {}
        self._t0: float | None = None
        self._view_locked = True
        self._mouse_proxy: pg.SignalProxy | None = None
        self._drag_plot: pg.PlotWidget | None = None
        self._drag_origin_x: float | None = None
        self._drag_origin_range: tuple[float, float] | None = None
        self._cursor_a_index: int | None = None
        self._cursor_b_index: int | None = None
        self._current_cursor_index: int | None = None
        self._current_x_range: tuple[float, float] | None = None
        self._cursor_syncing = False
        self._highlighted_channel: str | None = None

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        root.addWidget(PageHeader("实时波形", "配置驱动的工程示波器：暂停后拖动查看历史，滚轮缩放横轴，右键打开中文菜单。"))

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setTabShape(QtWidgets.QTabWidget.TabShape.Triangular)
        work_area = QtWidgets.QWidget()
        work_layout = QtWidgets.QHBoxLayout(work_area)
        work_layout.setContentsMargins(0, 0, 0, 0)
        work_layout.setSpacing(12)
        work_layout.addWidget(self.tabs, 1)
        self.measurement_panel = self._build_measurement_panel()
        work_layout.addWidget(self.measurement_panel)
        root.addWidget(work_area, 1)

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

        plot_panel = SectionCard("曲线区", "滚轮缩放横轴，暂停/手动模式可拖动历史数据。")
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
        self.cursor_a_line = pg.InfiniteLine(
            angle=90,
            movable=True,
            pen=pg.mkPen("#E7B75F", width=1.2, style=QtCore.Qt.PenStyle.DashLine),
        )
        self.cursor_b_line = pg.InfiniteLine(
            angle=90,
            movable=True,
            pen=pg.mkPen("#E58282", width=1.2, style=QtCore.Qt.PenStyle.DashLine),
        )
        self.cursor_line.setVisible(False)
        self.cursor_a_line.setVisible(False)
        self.cursor_b_line.setVisible(False)
        self.plot.addItem(self.cursor_line, ignoreBounds=True)
        self.plot.addItem(self.cursor_a_line, ignoreBounds=True)
        self.plot.addItem(self.cursor_b_line, ignoreBounds=True)
        self._plot_cursor_lines[self.plot] = {
            "hover": self.cursor_line,
            "a": self.cursor_a_line,
            "b": self.cursor_b_line,
        }
        self.plot.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.plot.customContextMenuRequested.connect(self._show_context_menu)
        self._register_plot(self.plot, fixed=False)
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
        self.tabs.currentChanged.connect(lambda _index: self._refresh_measurement_panel())

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
        export_view_button = QtWidgets.QPushButton("导出视图")
        export_view_button.setProperty("variant", "ghost")
        export_view_button.clicked.connect(self._choose_export_view_path)
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
        zoom_in_button.clicked.connect(lambda: self._zoom_current_x(0.7))
        zoom_out_button = QtWidgets.QPushButton("横轴缩小")
        zoom_out_button.setProperty("variant", "ghost")
        zoom_out_button.clicked.connect(lambda: self._zoom_current_x(1.4))
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
        self.window_spin.setRange(300, 60000)
        self.window_spin.setSingleStep(300)
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
            export_view_button,
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

    def _build_measurement_panel(self) -> SectionCard:
        panel = SectionCard("测量", "拖动 A/B 游标可吸附采样点")
        panel.setMinimumWidth(260)
        panel.setMaximumWidth(320)

        cursor_grid = QtWidgets.QGridLayout()
        cursor_grid.setHorizontalSpacing(8)
        cursor_grid.setVerticalSpacing(6)
        self.cursor_a_label = QtWidgets.QLabel("A：--")
        self.cursor_a_label.setObjectName("hintText")
        self.cursor_b_label = QtWidgets.QLabel("B：--")
        self.cursor_b_label.setObjectName("hintText")
        self.cursor_delta_label = QtWidgets.QLabel("Δt：--")
        self.cursor_delta_label.setObjectName("hintText")
        set_a = QtWidgets.QPushButton("设为 A")
        set_a.setProperty("variant", "ghost")
        set_a.clicked.connect(self._set_cursor_a_from_current)
        set_b = QtWidgets.QPushButton("设为 B")
        set_b.setProperty("variant", "ghost")
        set_b.clicked.connect(self._set_cursor_b_from_current)
        cursor_grid.addWidget(self.cursor_a_label, 0, 0)
        cursor_grid.addWidget(set_a, 0, 1)
        cursor_grid.addWidget(self.cursor_b_label, 1, 0)
        cursor_grid.addWidget(set_b, 1, 1)
        cursor_grid.addWidget(self.cursor_delta_label, 2, 0, 1, 2)
        panel.body.addLayout(cursor_grid)

        self.measure_table = QtWidgets.QTableWidget(0, 3)
        self.measure_table.setHorizontalHeaderLabels(["通道", "A 值", "B-A"])
        self.measure_table.horizontalHeader().setStretchLastSection(True)
        self.measure_table.setAlternatingRowColors(True)
        self.measure_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.measure_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.measure_table.verticalHeader().setDefaultSectionSize(28)
        self.measure_table.itemSelectionChanged.connect(self._highlight_selected_measurement_row)
        panel.body.addWidget(self.measure_table, 1)

        self.highlight_label = QtWidgets.QLabel("高亮：--")
        self.highlight_label.setObjectName("hintText")
        panel.body.addWidget(self.highlight_label)
        self.view_range_label = QtWidgets.QLabel("视图：--")
        self.view_range_label.setObjectName("hintText")
        self.view_range_label.setWordWrap(True)
        panel.body.addWidget(self.view_range_label)
        return panel

    def _build_rt_tabs(self) -> None:
        tab_specs = [
            (
                "电流",
                "电流 (A)",
                [
                    ("phase_current_a", "A相电流", "#61A5FA"),
                    ("phase_current_b", "B相电流", "#E7B75F"),
                    ("phase_current_c", "C相电流", "#9D8DF1"),
                    ("current_q", "q轴电流", "#4EC9A8"),
                    ("current_d", "d轴电流", "#E58282"),
                ],
            ),
            (
                "温度",
                "温度 (degC)",
                [
                    ("mos_temperature", "MOS温度", "#E79A54"),
                    ("coil_temperature", "线圈温度", "#8ABF6A"),
                ],
            ),
            (
                "转速",
                "速度 (rad/s)",
                [
                    ("mechanical_speed", "实际转速", "#6EA8FE"),
                    ("speed_target_mechanical", "目标转速", "#4EC9A8"),
                    ("rotor_speed_filtered", "滤波转速", "#E7B75F"),
                ],
            ),
            (
                "FOC",
                "FOC 变量",
                [
                    ("current_q", "Iq", "#4EC9A8"),
                    ("current_d", "Id", "#E58282"),
                    ("voltage_q", "Vq", "#61A5FA"),
                    ("voltage_d", "Vd", "#9D8DF1"),
                ],
            ),
        ]
        for title, left_label, channels in tab_specs:
            tab, plot = self._make_plot_tab(f"{title}实时数据", left_label)
            for signal_name, curve_name, color in channels:
                curve = plot.plot(name=curve_name, pen=pg.mkPen(color, width=2.15))
                curve_key = f"{title}:{signal_name}"
                self._fixed_curves[curve_key] = (curve, signal_name)
                self._fixed_curve_colors[curve_key] = color
                self._plot_channels.setdefault(plot, []).append(signal_name)
            self.tabs.addTab(tab, title)
        self.tabs.addTab(self._rotor_position_tab(), "转子位置")

    def _make_plot_tab(self, title: str, left_label: str) -> tuple[QtWidgets.QWidget, pg.PlotWidget]:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        plot = self._make_plot(title, left_label)
        legend = plot.addLegend(offset=(-12, 12))
        legend.setParentItem(plot.getPlotItem())
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
        self._register_plot(plot, fixed=True)
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
            ("electrical_angle", "电角度", "#61A5FA"),
            ("encoder_angle", "编码器角度", "#E7B75F"),
            ("mechanical_position_multi", "机械位置", "#4EC9A8"),
        ]:
            curve = plot.plot(name=curve_name, pen=pg.mkPen(color, width=2.15))
            curve_key = f"position:{signal_name}"
            self._fixed_curves[curve_key] = (curve, signal_name)
            self._fixed_curve_colors[curve_key] = color
            self._plot_channels.setdefault(plot, []).append(signal_name)
        legend = plot.addLegend(offset=(-12, 12))
        legend.setParentItem(plot.getPlotItem())
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
        self._set_plot_cursor_visibility("hover", False)
        self._set_plot_cursor_visibility("a", False)
        self._set_plot_cursor_visibility("b", False)
        self._cursor_a_index = None
        self._cursor_b_index = None
        self._current_cursor_index = None
        self._set_highlighted_channel(None)
        self.cursor_label.setText("光标：--")
        self._refresh_measurement_panel()
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
                self._refresh_custom_curve(name, x_values)
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
        selected = self._active_measure_channels()
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

    def export_view_csv(self, path: str | Path) -> Path:
        export_path = Path(path)
        export_path.parent.mkdir(parents=True, exist_ok=True)
        left, right = self._current_view_range()
        selected = self._active_measure_channels()
        with export_path.open("w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["time_s", *selected])
            for index, timestamp in self._indices_in_range(left, right):
                row = [timestamp]
                for name in selected:
                    values = list(self._series[name])
                    row.append(values[index] if index < len(values) else "")
                writer.writerow(row)
        return export_path

    def eventFilter(self, watched: QtCore.QObject, event: QtCore.QEvent) -> bool:
        plot = self._plot_for_viewport(watched)
        if plot is not None:
            if event.type() == QtCore.QEvent.Type.MouseButtonPress:
                mouse_event = event
                if mouse_event.button() == QtCore.Qt.MouseButton.RightButton:
                    self._update_cursor_from_event(plot, mouse_event)
                    self._show_context_menu_global(self._event_global_pos(mouse_event))
                    return True
                if mouse_event.button() == QtCore.Qt.MouseButton.LeftButton and self._is_near_cursor_line(plot, mouse_event):
                    return False
                if mouse_event.button() == QtCore.Qt.MouseButton.LeftButton and self._allow_manual_x_interaction():
                    self._start_x_drag(plot, mouse_event)
                    return True
            if event.type() == QtCore.QEvent.Type.MouseMove:
                self._update_cursor_from_event(plot, event)
                if self._drag_plot is plot:
                    self._drag_x_view(plot, event)
                    return True
            if event.type() == QtCore.QEvent.Type.MouseButtonRelease and self._drag_plot is plot:
                self._end_x_drag()
                return True
            if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
                self._fit_recent_view()
                return True
            if event.type() == QtCore.QEvent.Type.Wheel:
                wheel_event = event
                delta = wheel_event.angleDelta().y() if hasattr(wheel_event, "angleDelta") else 0
                self._zoom_x_at(plot, 0.82 if delta > 0 else 1.22, wheel_event)
                return True
        return super().eventFilter(watched, event)

    def _register_plot(self, plot: pg.PlotWidget, fixed: bool) -> None:
        plot.viewport().installEventFilter(self)
        if plot not in self._all_plots:
            self._all_plots.append(plot)
        if fixed and plot not in self._fixed_plots:
            self._fixed_plots.append(plot)
        self._plot_channels.setdefault(plot, [])
        if plot not in self._plot_cursor_lines:
            hover = pg.InfiniteLine(
                angle=90,
                movable=False,
                pen=pg.mkPen("#94a3b8", width=1, style=QtCore.Qt.PenStyle.DashLine),
            )
            cursor_a = pg.InfiniteLine(
                angle=90,
                movable=True,
                pen=pg.mkPen("#E7B75F", width=1.2, style=QtCore.Qt.PenStyle.DashLine),
            )
            cursor_b = pg.InfiniteLine(
                angle=90,
                movable=True,
                pen=pg.mkPen("#E58282", width=1.2, style=QtCore.Qt.PenStyle.DashLine),
            )
            for line in [hover, cursor_a, cursor_b]:
                line.setVisible(False)
                plot.addItem(line, ignoreBounds=True)
            self._plot_cursor_lines[plot] = {"hover": hover, "a": cursor_a, "b": cursor_b}
        self._configure_cursor_lines(plot)

    def _configure_cursor_lines(self, plot: pg.PlotWidget) -> None:
        for key in ["a", "b"]:
            line = self._plot_cursor_lines[plot][key]
            line.setMovable(True)
            line.setHoverPen(pg.mkPen("#DDE5EF", width=1.6, style=QtCore.Qt.PenStyle.DashLine))
            line.sigPositionChangeFinished.connect(
                lambda moved_line, cursor_key=key: self._snap_dragged_cursor(cursor_key, moved_line)
            )

    def _plot_for_viewport(self, watched: QtCore.QObject) -> pg.PlotWidget | None:
        for plot in self._all_plots:
            if watched is plot.viewport():
                return plot
        return None

    def _build_channels(self) -> None:
        default_channels = self._PRESETS["默认"]
        colors = [
            "#6EA8FE",
            "#E7B75F",
            "#4EC9A8",
            "#E58282",
            "#9D8DF1",
            "#8ABF6A",
            "#6FC7D9",
            "#DDE5EF",
            "#D69A72",
            "#8AA9C8",
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
            curve = self.plot.plot(pen=pg.mkPen(color, width=2.25))
            curve.setVisible(item.checkState() == QtCore.Qt.CheckState.Checked)
            self._curves[name] = curve
            self._curve_colors[name] = color
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
        if checked:
            self._refresh_custom_curve(name)
        else:
            curve.setData([], [])
        self._update_status_labels()

    def _refresh_custom_curve(self, name: str, x_values: list[float] | None = None) -> None:
        curve = self._curves.get(name)
        if curve is None:
            return
        x_data = x_values if x_values is not None else list(self._time)
        y_data = list(self._series[name])
        curve.setData(x_data, y_data)

    def _choose_export_path(self) -> None:
        path, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "导出示波器数据",
            "emotor_scope.csv",
            "CSV Files (*.csv)",
        )
        if path:
            self.export_csv(path)

    def _choose_export_view_path(self) -> None:
        path, _selected_filter = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "导出当前视图数据",
            "emotor_scope_view.csv",
            "CSV Files (*.csv)",
        )
        if path:
            self.export_view_csv(path)

    def _show_context_menu(self, position: QtCore.QPoint) -> None:
        self._show_context_menu_global(self.plot.mapToGlobal(position))

    def _show_context_menu_global(self, position: QtCore.QPoint) -> None:
        menu = QtWidgets.QMenu(self)
        pause_action = menu.addAction("继续采样" if self.pause_box.isChecked() else "暂停采样")
        clear_action = menu.addAction("清空曲线")
        export_action = menu.addAction("导出 CSV")
        export_view_action = menu.addAction("导出当前视图")
        menu.addSeparator()
        cursor_a_action = menu.addAction("当前光标设为 A")
        cursor_b_action = menu.addAction("当前光标设为 B")
        clear_cursor_action = menu.addAction("清除 A/B 游标")
        clear_highlight_action = menu.addAction("清除曲线高亮")
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
        elif action == export_view_action:
            self._choose_export_view_path()
        elif action == cursor_a_action:
            self._set_cursor_a_from_current()
        elif action == cursor_b_action:
            self._set_cursor_b_from_current()
        elif action == clear_cursor_action:
            self._clear_cursors()
        elif action == clear_highlight_action:
            self._set_highlighted_channel(None)
        elif action == zoom_in_action:
            self._zoom_current_x(0.7)
        elif action == zoom_out_action:
            self._zoom_current_x(1.4)
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
        history = f"{len(self._time)} / {self._max_samples} 点"
        window = f"{self._visible_window_seconds:.1f} s"
        self.status_label.setText(f"采样状态：{state} / {mode} / 历史 {history} / 窗口 {window}")
        self.channel_count_label.setText(f"已选通道：{len(self._selected_channels())}")
        self._refresh_measurement_panel()

    def _set_time_window(self, value: float) -> None:
        self._visible_window_seconds = value
        self._fit_recent_view()

    def _zoom_time(self, factor: float) -> None:
        self.time_window.setValue(min(max(self.time_window.value() * factor, 2.0), 600.0))

    def _zoom_current_x(self, factor: float) -> None:
        left, right = self._current_view_range()
        center = (left + right) / 2.0
        width = min(max((right - left) * factor, 1.0), 3600.0)
        new_left = max(0.0, center - width / 2.0)
        self._set_all_x_ranges(new_left, new_left + width)
        self._visible_window_seconds = width
        self.time_window.blockSignals(True)
        self.time_window.setValue(min(max(width, 2.0), 600.0))
        self.time_window.blockSignals(False)
        self._view_locked = False
        self.lock_box.setChecked(False)
        self._auto_range_y()
        self._update_status_labels()

    def _zoom_x_at(self, plot: pg.PlotWidget, factor: float, event: QtCore.QEvent) -> None:
        view_box = plot.getViewBox()
        current_left, current_right = view_box.viewRange()[0]
        width = max(current_right - current_left, 1.0)
        new_width = min(max(width * factor, 1.0), 3600.0)
        position = event.position().toPoint() if hasattr(event, "position") else event.pos()
        scene_pos = plot.mapToScene(position)
        try:
            anchor_x = view_box.mapSceneToView(scene_pos).x()
        except Exception:
            anchor_x = (current_left + current_right) / 2.0
        ratio = 0.5 if current_right == current_left else (anchor_x - current_left) / width
        ratio = min(max(ratio, 0.0), 1.0)
        left = max(0.0, anchor_x - new_width * ratio)
        right = left + new_width
        self._set_all_x_ranges(left, right)
        self._visible_window_seconds = new_width
        self.time_window.blockSignals(True)
        self.time_window.setValue(min(max(new_width, 2.0), 600.0))
        self.time_window.blockSignals(False)
        self._view_locked = False
        self.lock_box.setChecked(False)
        self._auto_range_y()
        self._update_status_labels()

    def _start_x_drag(self, plot: pg.PlotWidget, event: QtCore.QEvent) -> None:
        self._drag_plot = plot
        self._drag_origin_range = tuple(plot.getViewBox().viewRange()[0])
        position = event.position().toPoint() if hasattr(event, "position") else event.pos()
        scene_pos = plot.mapToScene(position)
        self._drag_origin_x = plot.getViewBox().mapSceneToView(scene_pos).x()
        plot.viewport().setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

    def _drag_x_view(self, plot: pg.PlotWidget, event: QtCore.QEvent) -> None:
        if self._drag_origin_x is None or self._drag_origin_range is None:
            return
        position = event.position().toPoint() if hasattr(event, "position") else event.pos()
        scene_pos = plot.mapToScene(position)
        current_x = plot.getViewBox().mapSceneToView(scene_pos).x()
        delta = self._drag_origin_x - current_x
        left, right = self._drag_origin_range
        width = right - left
        new_left = max(0.0, left + delta)
        self._set_all_x_ranges(new_left, new_left + width)

    def _update_cursor_from_event(self, plot: pg.PlotWidget, event: QtCore.QEvent) -> None:
        if not self._time:
            self._set_plot_cursor_visibility("hover", False)
            self.cursor_label.setText("光标：--")
            return
        position = event.position().toPoint() if hasattr(event, "position") else event.pos()
        scene_pos = plot.mapToScene(position)
        try:
            x_value = plot.getViewBox().mapSceneToView(scene_pos).x()
        except Exception:
            return
        self._update_cursor_readout(x_value)

    def _end_x_drag(self) -> None:
        if self._drag_plot is not None:
            self._drag_plot.viewport().unsetCursor()
        self._drag_plot = None
        self._drag_origin_x = None
        self._drag_origin_range = None

    def _fit_recent_view(self) -> None:
        if self._time:
            self._apply_recent_x_range(list(self._time)[-1])
        self._auto_range_y()

    def _fit_all_view(self) -> None:
        if not self._time:
            return
        values = list(self._time)
        self._set_all_x_ranges(values[0], max(values[-1], values[0] + 1.0), padding=0.02)
        self._auto_range_y()

    def _auto_range_y(self) -> None:
        self.plot.enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)
        for plot in self._fixed_plots:
            plot.enableAutoRange(axis=pg.ViewBox.YAxis, enable=True)

    def _allow_manual_x_interaction(self) -> bool:
        return self.pause_box.isChecked() or not self._view_locked

    def _update_plot_interaction(self) -> None:
        manual = self._allow_manual_x_interaction()
        for plot in self._all_plots:
            plot.getViewBox().setMouseEnabled(x=False, y=False)
            plot.viewport().setCursor(QtCore.Qt.CursorShape.OpenHandCursor if manual else QtCore.Qt.CursorShape.ArrowCursor)

    def _apply_recent_x_range(self, latest_time: float) -> None:
        left = max(0.0, latest_time - self._visible_window_seconds)
        right = max(self._visible_window_seconds, latest_time)
        self._set_all_x_ranges(left, right, padding=0.01)

    def _set_all_x_ranges(self, left: float, right: float, padding: float = 0.0) -> None:
        self._current_x_range = (float(left), float(right))
        for plot in self._all_plots:
            plot.setXRange(left, right, padding=padding)
        self._refresh_measurement_panel()

    def _current_view_range(self) -> tuple[float, float]:
        if self._current_x_range is not None:
            return self._current_x_range
        if self._all_plots:
            plot = self._active_plot() if hasattr(self, "tabs") else self._all_plots[0]
            left, right = plot.getViewBox().viewRange()[0]
            return float(left), float(right)
        return 0.0, 0.0

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
            self._set_plot_cursor_visibility("hover", False)
            return
        times = list(self._time)
        index = min(range(len(times)), key=lambda item: abs(times[item] - x_value))
        timestamp = times[index]
        self._set_plot_cursor_position("hover", timestamp)
        self._cursor_a_index = index if self._cursor_a_index is None else self._cursor_a_index
        pieces = []
        for name in self._active_measure_channels()[:4]:
            values = list(self._series.get(name, []))
            if index < len(values):
                pieces.append(f"{self._short_channel_label(name)} {values[index]:.4g}")
        suffix = " | ".join(pieces) if pieces else "未选择通道"
        self.cursor_label.setText(f"光标：{timestamp:.2f}s | {suffix}")
        self._current_cursor_index = index
        self._refresh_measurement_panel()

    def _set_cursor_a_from_current(self) -> None:
        self._cursor_a_index = self._nearest_visible_index()
        self._refresh_measurement_panel(self._active_plot())

    def _set_cursor_b_from_current(self) -> None:
        self._cursor_b_index = self._nearest_visible_index()
        self._refresh_measurement_panel(self._active_plot())

    def _clear_cursors(self) -> None:
        self._cursor_a_index = None
        self._cursor_b_index = None
        self._set_plot_cursor_visibility("a", False)
        self._set_plot_cursor_visibility("b", False)
        self._refresh_measurement_panel(self._active_plot())

    def _snap_dragged_cursor(self, key: str, line: pg.InfiniteLine) -> None:
        if self._cursor_syncing or not self._time:
            return
        index = self._nearest_index_for_time(float(line.value()))
        if key == "a":
            self._cursor_a_index = index
        elif key == "b":
            self._cursor_b_index = index
        times = list(self._time)
        self._set_plot_cursor_position(key, times[index])
        self._refresh_measurement_panel(self._active_plot())

    def _nearest_visible_index(self) -> int | None:
        if not self._time:
            return None
        if hasattr(self, "_current_cursor_index"):
            index = int(self._current_cursor_index)
            return min(max(index, 0), len(self._time) - 1)
        left, right = self._current_view_range()
        midpoint = (left + right) / 2.0
        times = list(self._time)
        return min(range(len(times)), key=lambda item: abs(times[item] - midpoint))

    def _nearest_index_for_time(self, x_value: float) -> int:
        times = list(self._time)
        return min(range(len(times)), key=lambda item: abs(times[item] - x_value))

    def _refresh_measurement_panel(self, plot: pg.PlotWidget | None = None) -> None:
        if not hasattr(self, "measure_table"):
            return
        plot = plot or self._active_plot()
        times = list(self._time)
        left, right = self._current_view_range()
        self.view_range_label.setText(f"视图：{left:.2f}s .. {right:.2f}s")
        self.cursor_a_label.setText(self._cursor_label("A", self._cursor_a_index, times))
        self.cursor_b_label.setText(self._cursor_label("B", self._cursor_b_index, times))
        if self._cursor_a_index is not None and self._cursor_b_index is not None and times:
            delta = times[self._cursor_b_index] - times[self._cursor_a_index]
            self.cursor_delta_label.setText(f"Δt：{delta:.4g} s")
        else:
            self.cursor_delta_label.setText("Δt：--")

        self.measure_table.setRowCount(0)
        if self._cursor_a_index is None or not times:
            return
        a_index = self._cursor_a_index
        b_index = self._cursor_b_index
        for name in self._active_measure_channels(plot)[:10]:
            values = list(self._series.get(name, []))
            if a_index >= len(values):
                continue
            row = self.measure_table.rowCount()
            self.measure_table.insertRow(row)
            self.measure_table.setVerticalHeaderItem(row, QtWidgets.QTableWidgetItem(""))
            a_value = values[a_index]
            delta_text = "--"
            if b_index is not None and b_index < len(values):
                delta_text = f"{values[b_index] - a_value:.6g}"
            for column, value in enumerate([self._short_channel_label(name), f"{a_value:.6g}", delta_text]):
                item = QtWidgets.QTableWidgetItem(value)
                item.setData(QtCore.Qt.ItemDataRole.UserRole, name)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.measure_table.setItem(row, column, item)

    def _cursor_label(self, name: str, index: int | None, times: list[float]) -> str:
        if index is None or not times:
            self._set_cursor_line_visibility(name, False)
            return f"{name}：--"
        index = min(max(index, 0), len(times) - 1)
        self._set_cursor_line_position(name, times[index])
        return f"{name}：{times[index]:.4g} s"

    def _active_plot(self) -> pg.PlotWidget:
        current = self.tabs.currentWidget()
        for plot in self._all_plots:
            widget: QtWidgets.QWidget | None = plot
            while widget is not None:
                if widget is current:
                    return plot
                widget = widget.parentWidget()
        return self.plot

    def _active_measure_channels(self, plot: pg.PlotWidget | None = None) -> list[str]:
        active_plot = plot or self._active_plot()
        channels = self._plot_channels.get(active_plot, [])
        if channels:
            return channels
        return self._selected_channels()

    def _set_cursor_line_position(self, cursor_name: str, value: float) -> None:
        key = "a" if cursor_name == "A" else "b"
        self._set_plot_cursor_position(key, value)

    def _set_cursor_line_visibility(self, cursor_name: str, visible: bool) -> None:
        key = "a" if cursor_name == "A" else "b"
        self._set_plot_cursor_visibility(key, visible)

    def _set_plot_cursor_position(self, key: str, value: float) -> None:
        self._cursor_syncing = True
        for lines in self._plot_cursor_lines.values():
            line = lines[key]
            line.setPos(value)
            line.setVisible(True)
        self._cursor_syncing = False

    def _set_plot_cursor_visibility(self, key: str, visible: bool) -> None:
        for lines in self._plot_cursor_lines.values():
            lines[key].setVisible(visible)

    def _is_near_cursor_line(self, plot: pg.PlotWidget, event: QtCore.QEvent) -> bool:
        if not self._time:
            return False
        position = event.position().toPoint() if hasattr(event, "position") else event.pos()
        scene_pos = plot.mapToScene(position)
        try:
            x_value = plot.getViewBox().mapSceneToView(scene_pos).x()
        except Exception:
            return False
        times = list(self._time)
        left, right = plot.getViewBox().viewRange()[0]
        tolerance = max((right - left) * 0.01, 0.05)
        candidates = []
        if self._cursor_a_index is not None:
            candidates.append(times[min(self._cursor_a_index, len(times) - 1)])
        if self._cursor_b_index is not None:
            candidates.append(times[min(self._cursor_b_index, len(times) - 1)])
        return any(abs(x_value - candidate) <= tolerance for candidate in candidates)

    def _highlight_selected_measurement_row(self) -> None:
        items = self.measure_table.selectedItems()
        if not items:
            return
        name = items[0].data(QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(name, str):
            self._set_highlighted_channel(name)

    def _set_highlighted_channel(self, name: str | None) -> None:
        self._highlighted_channel = name
        for channel_name, curve in self._curves.items():
            color = self._curve_colors.get(channel_name, "#DDE5EF")
            width = 3.2 if name == channel_name else 2.25
            alpha = 255 if name in (None, channel_name) else 120
            curve.setPen(pg.mkPen(QtGui.QColor(color).lighter(115) if name == channel_name else QtGui.QColor(color).darker(105), width=width))
            curve.setOpacity(alpha / 255)
        for curve_key, (curve, channel_name) in self._fixed_curves.items():
            color = self._fixed_curve_colors.get(curve_key, "#DDE5EF")
            width = 3.2 if name == channel_name else 2.15
            qcolor = QtGui.QColor(color).lighter(115) if name == channel_name else QtGui.QColor(color).darker(105)
            curve.setPen(pg.mkPen(qcolor, width=width))
            curve.setOpacity(1.0 if name in (None, channel_name) else 0.45)
        self.highlight_label.setText(f"高亮：{self._short_channel_label(name)}" if name else "高亮：--")

    def _indices_in_range(self, left: float, right: float) -> list[tuple[int, float]]:
        return [
            (index, timestamp)
            for index, timestamp in enumerate(self._time)
            if left <= timestamp <= right
        ]

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
