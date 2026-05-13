"""Main window for the eMotor-Studio skeleton."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from emotor_studio.backend import MockBackend
from emotor_studio.models import FaultEvent, TelemetrySample
from emotor_studio.pages import (
    CommandPage,
    DashboardPage,
    FaultPage,
    LoggerPage,
    ParameterPage,
    ReportPage,
    ScopePage,
)


class MainWindow(QtWidgets.QMainWindow):
    telemetry_received = QtCore.Signal(object)
    fault_received = QtCore.Signal(object)

    def __init__(self, backend: MockBackend | None = None) -> None:
        super().__init__()
        self.setWindowTitle("eMotor-Studio")
        self.resize(1180, 760)
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
        central = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(central)
        self.setCentralWidget(central)

        status_row = QtWidgets.QHBoxLayout()
        self.connection_label = QtWidgets.QLabel("Backend: Mock")
        self.mode_label = QtWidgets.QLabel("Mode: --")
        self.sample_label = QtWidgets.QLabel("RPM: --")
        status_row.addWidget(self.connection_label)
        status_row.addWidget(self.mode_label)
        status_row.addWidget(self.sample_label)
        status_row.addStretch(1)
        root.addLayout(status_row)

        body = QtWidgets.QHBoxLayout()
        root.addLayout(body, 1)

        self.nav = QtWidgets.QListWidget()
        self.nav.setFixedWidth(180)
        body.addWidget(self.nav)

        self.stack = QtWidgets.QStackedWidget()
        body.addWidget(self.stack, 1)

        self.dashboard_page = DashboardPage(self.backend)
        self.scope_page = ScopePage(self.backend.read_signal_schema())
        self.parameter_page = ParameterPage(self.backend)
        self.command_page = CommandPage(self.backend)
        self.fault_page = FaultPage(self.backend.read_fault_schema())
        self.logger_page = LoggerPage(self.backend.read_signal_schema())
        self.report_page = ReportPage(self.logger_page.samples)

        pages = [
            ("Dashboard", self.dashboard_page),
            ("Scope", self.scope_page),
            ("Parameter", self.parameter_page),
            ("Command", self.command_page),
            ("Fault", self.fault_page),
            ("Logger", self.logger_page),
            ("Report", self.report_page),
        ]
        for title, page in pages:
            self.nav.addItem(title)
            self.stack.addWidget(page)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)

    def _emit_telemetry(self, sample: TelemetrySample) -> None:
        self.telemetry_received.emit(sample)

    def _emit_fault(self, fault: FaultEvent) -> None:
        self.fault_received.emit(fault)

    def _on_telemetry(self, sample: TelemetrySample) -> None:
        self.mode_label.setText(f"State: {sample.run_state.value} / {sample.system_mode.value}")
        self.sample_label.setText(f"Speed: {sample.rpm:,.0f} rpm")
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
