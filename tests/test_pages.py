import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from emotor_studio.backend import MockBackend
from emotor_studio.pages import (
    CommandPage,
    ControlTuningPage,
    FaultPage,
    IdentificationPage,
    LoggerPage,
    ParameterPage,
    ReportPage,
    ScopePage,
)


def _app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_scope_page_builds_axdr_l_channels() -> None:
    _app()
    backend = MockBackend()

    page = ScopePage(backend.read_signal_schema())

    assert page.channel_list.count() > 0
    assert "mechanical_speed" in page._channel_items
    assert page.preset_combo.count() >= 5


def test_scope_page_applies_presets_and_filters_channels() -> None:
    _app()
    backend = MockBackend()

    page = ScopePage(backend.read_signal_schema())
    page._apply_channel_preset("电流环")

    assert page._channel_items["current_q"].checkState().name == "Checked"
    assert page._channel_items["mechanical_speed"].checkState().name == "Unchecked"

    page.search_box.setText("母线")

    visible = [
        page.channel_list.item(index).text()
        for index in range(page.channel_list.count())
        if not page.channel_list.item(index).isHidden()
    ]
    assert visible
    assert all("母线" in label or "bus" in label.lower() for label in visible)


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


def test_parameter_page_filters_writable_parameters() -> None:
    _app()
    backend = MockBackend()
    page = ParameterPage(backend)

    total_rows = page.table.rowCount()
    page.writable_only.setChecked(True)

    assert page.table.rowCount() <= total_rows
    assert page.total_card.value_label.text() == str(len(page._all_parameters))
    assert page.editable_card.value_label.text().isdigit()


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

    assert "# eMotor-Studio" in report
    assert "- Samples: 2" in report
    assert "| rpm | 100.000 | 150.000 | 200.000 |" in report


def test_identification_page_exposes_modular_workflows() -> None:
    _app()

    page = IdentificationPage()

    assert page.module_tabs.count() == 6
    assert page.module_tabs.tabText(0) == "Rs 电阻"
    assert "inductance" in page.result_tables
    assert page.result_tables["angle"].rowCount() == 3


def test_identification_page_runs_mock_resistance_identification() -> None:
    _app()

    page = IdentificationPage()
    result = page.run_mock_resistance_identification()

    assert result.task.module == "resistance"
    assert "resistance" in page.last_identification_results
    assert page.result_tables["resistance"].item(0, 0).text() == "phase_resistance"
    assert page.result_tables["resistance"].item(0, 4).text() == "suggested"


def test_identification_page_runs_mock_inductance_identification() -> None:
    _app()

    page = IdentificationPage()
    result = page.run_mock_inductance_identification()

    assert result.task.module == "inductance"
    assert "inductance" in page.last_identification_results
    assert page.result_tables["inductance"].item(0, 0).text() == "d_inductance"
    assert page.result_tables["inductance"].item(1, 0).text() == "q_inductance"


def test_control_tuning_page_generates_mock_pi_suggestions() -> None:
    _app()

    page = ControlTuningPage()
    suggestions = page.generate_mock_current_pi_suggestion()

    assert len(suggestions) == 2
    assert page.pi_table.item(0, 0).text() == "d"
    assert page.pi_table.item(1, 0).text() == "q"
    assert page.preset_table.item(0, 1).text() != "id_current_kp"
    assert "Mock Rs/Ld/Lq" in page.pi_status_label.text()
    assert page.workflow_status["identify"].value_label.text() == "完成"
    assert page.workflow_status["suggest"].value_label.text() == "完成"


def test_control_tuning_page_validates_mock_pi_step_response() -> None:
    _app()

    page = ControlTuningPage()
    result = page.validate_mock_current_pi()

    assert result.metrics.rise_time_s is not None
    assert page.pi_validation_table.item(0, 1).text().endswith("ms")
    assert page.last_pi_validation is result
    assert page.workflow_status["validate"].value_label.text() == "完成"


def test_control_tuning_page_exports_tuning_report(tmp_path) -> None:
    _app()

    page = ControlTuningPage()
    path = page.export_current_loop_tuning_report(str(tmp_path))

    assert path is not None
    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("# eMotor-Studio Current Loop Tuning Report")
    assert str(path) in page.pi_status_label.text()


def test_control_tuning_page_exports_tuning_session(tmp_path) -> None:
    _app()

    page = ControlTuningPage()
    artifacts = page.export_current_loop_tuning_session(str(tmp_path))

    assert artifacts["directory"].is_dir()
    assert artifacts["manifest"].exists()
    assert artifacts["validation_trace"].exists()
    assert str(artifacts["directory"]) in page.pi_status_label.text()
