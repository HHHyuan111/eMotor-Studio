"""Scope page with a config-driven pyqtgraph plotting surface."""

from __future__ import annotations

from collections import deque
from typing import Any

from PySide6 import QtCore, QtWidgets
import pyqtgraph as pg

from emotor_studio.config import load_signals
from emotor_studio.models import TelemetrySample


class ScopePage(QtWidgets.QWidget):
    def __init__(
        self,
        signal_schema: list[dict[str, Any]] | None = None,
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._signal_schema = [signal for signal in (signal_schema or load_signals()) if signal.get("scope", False)]
        self._max_samples = 600
        self._time: deque[float] = deque(maxlen=self._max_samples)
        self._series: dict[str, deque[float]] = {}
        self._curves: dict[str, pg.PlotDataItem] = {}
        self._channel_items: dict[str, QtWidgets.QListWidgetItem] = {}
        self._t0: float | None = None

        layout = QtWidgets.QVBoxLayout(self)
        toolbar = QtWidgets.QHBoxLayout()
        self.pause_box = QtWidgets.QCheckBox("Pause")
        clear_button = QtWidgets.QPushButton("Clear")
        clear_button.clicked.connect(self.clear)
        self.window_spin = QtWidgets.QSpinBox()
        self.window_spin.setRange(100, 3000)
        self.window_spin.setSingleStep(100)
        self.window_spin.setValue(self._max_samples)
        self.window_spin.setSuffix(" samples")
        self.window_spin.valueChanged.connect(self._set_window)
        toolbar.addWidget(self.pause_box)
        toolbar.addWidget(clear_button)
        toolbar.addWidget(self.window_spin)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        content = QtWidgets.QHBoxLayout()
        layout.addLayout(content, 1)

        self.channel_list = QtWidgets.QListWidget()
        self.channel_list.setFixedWidth(260)
        self.channel_list.itemChanged.connect(self._sync_channel_visibility)
        content.addWidget(self.channel_list)

        pg.setConfigOptions(antialias=True)
        self.plot = pg.PlotWidget(title="AxDr_L Signal Scope")
        self.plot.setLabel("bottom", "Time", "s")
        self.plot.setLabel("left", "Signal Value")
        self.plot.addLegend()
        content.addWidget(self.plot, 1)

        self._build_channels()

    def clear(self) -> None:
        self._time.clear()
        for values in self._series.values():
            values.clear()
        self._t0 = None
        for curve in self._curves.values():
            curve.setData([], [])

    def update_telemetry(self, sample: TelemetrySample) -> None:
        if self.pause_box.isChecked():
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

    def _build_channels(self) -> None:
        default_channels = {
            "mechanical_speed",
            "speed_target_mechanical",
            "bus_voltage",
            "current_q",
            "current_d",
            "mos_temperature",
            "fault_word",
        }
        colors = [
            "#2f80ed",
            "#eb5757",
            "#27ae60",
            "#f2994a",
            "#9b51e0",
            "#00a3a3",
            "#828282",
            "#bb6bd9",
            "#219653",
            "#f2c94c",
        ]
        for index, signal in enumerate(self._signal_schema):
            name = str(signal["name"])
            display_name = str(signal.get("display_name") or name)
            unit = str(signal.get("unit") or "")
            label = f"{display_name} ({unit})" if unit else display_name
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, name)
            item.setFlags(item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(
                QtCore.Qt.CheckState.Checked
                if name in default_channels
                else QtCore.Qt.CheckState.Unchecked
            )
            self.channel_list.addItem(item)
            self._channel_items[name] = item
            self._series[name] = deque(maxlen=self._max_samples)
            pen = pg.mkPen(colors[index % len(colors)], width=2)
            curve = self.plot.plot(pen=pen, name=display_name)
            curve.setVisible(item.checkState() == QtCore.Qt.CheckState.Checked)
            self._curves[name] = curve

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
        if not checked:
            curve.setData([], [])
        else:
            curve.setData(list(self._time), list(self._series[name]))

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
