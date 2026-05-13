import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from emotor_studio.backend import MockBackend
from emotor_studio.pages import CommandPage, FaultPage, LoggerPage, ParameterPage, ReportPage, ScopePage


def _app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_scope_page_builds_axdr_l_channels() -> None:
    _app()
    backend = MockBackend()

    page = ScopePage(backend.read_signal_schema())

    assert page.channel_list.count() > 0
    assert "mechanical_speed" in page._channel_items


def test_parameter_page_writes_selected_value() -> None:
    _app()
    backend = MockBackend()
    page = ParameterPage(backend)
    row = next(
        index
        for index in range(page.table.rowCount())
        if page.table.item(index, 1).text() == "position_kp"
    )
    page.table.setCurrentCell(row, 3)
    page.table.item(row, 3).setText("2.5")

    page.write_selected()

    parameters = {item.key: item for item in backend.read_parameters()}
    assert parameters["position_kp"].value == 2.5


def test_command_page_uses_command_schema() -> None:
    _app()
    backend = MockBackend()

    page = CommandPage(backend)

    assert page.command_combo.count() > 0
    assert any(
        page.command_combo.itemData(index)["name"] == "set_speed_target"
        for index in range(page.command_combo.count())
    )


def test_fault_page_decodes_fault_word() -> None:
    _app()
    backend = MockBackend()
    page = FaultPage(backend.read_fault_schema())
    fault = backend.inject_fault(code="ov_tmos")
    sample = backend.tick()

    page.add_fault(fault)
    page.update_telemetry(sample)

    assert page.active_table.rowCount() == 1
    assert page.active_table.item(0, 1).text() == "ov_tmos"
    assert page.table.rowCount() == 1


def test_logger_page_records_and_exports_csv(tmp_path) -> None:
    _app()
    backend = MockBackend()
    page = LoggerPage(backend.read_signal_schema())
    backend.start()

    page.update_telemetry(backend.tick())
    export_path = page.export_csv(tmp_path / "telemetry.csv")

    assert len(page.samples) == 1
    assert export_path.read_text(encoding="utf-8").startswith("timestamp,rpm,target_rpm")


def test_report_page_builds_markdown_from_samples() -> None:
    _app()
    samples = [
        {
            "timestamp": 10.0,
            "rpm": 100.0,
            "target_rpm": 120.0,
            "mechanical_speed": 10.0,
            "bus_voltage": 24.0,
            "current_q": 1.0,
        },
        {
            "timestamp": 11.0,
            "rpm": 200.0,
            "target_rpm": 220.0,
            "mechanical_speed": 20.0,
            "bus_voltage": 25.0,
            "current_q": 2.0,
        },
    ]
    page = ReportPage(lambda: samples)

    report = page.build_report()

    assert "# eMotor-Studio Session Report" in report
    assert "- Samples: 2" in report
    assert "| rpm | 100.000 | 150.000 | 200.000 |" in report
