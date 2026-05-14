import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets

from emotor_studio.models import ExperimentTrace
from emotor_studio.pages import ExperimentAnalysisPage
from emotor_studio.services import (
    CurrentLoopStepExperiment,
    MockInductanceIdentification,
    MockResistanceIdentification,
    build_current_loop_session_manifest,
    build_current_loop_tuning_report,
    build_experiment_csv,
    build_experiment_report,
    build_pi_suggestions_csv,
    build_validation_metrics_payload,
    build_validation_trace_csv,
    save_current_loop_tuning_report,
    save_current_loop_tuning_session,
    save_experiment_artifacts,
    suggest_current_loop_pi,
    validate_current_loop_pi,
)
from emotor_studio.services.experiments import analyze_step_response


def _app() -> QtWidgets.QApplication:
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def test_current_loop_step_experiment_generates_metrics() -> None:
    result = CurrentLoopStepExperiment().run()

    assert result.task.name == "mock_current_loop_step"
    assert len(result.trace.time_s) == len(result.trace.response) == len(result.trace.target)
    assert result.metrics.rise_time_s is not None
    assert result.metrics.settling_time_s is not None
    assert result.metrics.overshoot_percent >= 0.0
    assert abs(result.metrics.steady_state_error) < 0.05


def test_step_response_analysis_known_trace() -> None:
    trace = ExperimentTrace(
        time_s=(0.0, 0.1, 0.2, 0.3, 0.4),
        target=(1.0, 1.0, 1.0, 1.0, 1.0),
        response=(0.0, 0.2, 0.9, 1.0, 1.0),
        unit="A",
    )

    metrics = analyze_step_response(trace)

    assert metrics.target_value == 1.0
    assert metrics.rise_time_s == 0.1
    assert metrics.settling_time_s == 0.3
    assert metrics.overshoot_percent == 0.0


def test_experiment_report_contains_research_metrics() -> None:
    result = CurrentLoopStepExperiment().run()

    report = build_experiment_report(result)

    assert "# Mock q轴电流环阶跃响应" in report
    assert "Rise time" in report
    assert "Overshoot" in report
    assert "Steady-state error" in report


def test_experiment_csv_and_artifacts_are_exportable(tmp_path) -> None:
    result = CurrentLoopStepExperiment().run()

    csv_text = build_experiment_csv(result)
    artifacts = save_experiment_artifacts(result, tmp_path)

    assert csv_text.startswith("time_s,target,response,unit")
    assert artifacts["csv"].read_text(encoding="utf-8").startswith("time_s,target,response,unit")
    assert artifacts["report"].read_text(encoding="utf-8").startswith("# Mock q轴电流环阶跃响应")


def test_experiment_analysis_page_runs_mock_step() -> None:
    _app()
    page = ExperimentAnalysisPage()

    result = page.run_mock_current_step()

    assert page.metric_table.rowCount() == 6
    assert page.report_preview.toPlainText().startswith("# Mock q轴电流环阶跃响应")
    assert result.metrics.rise_time_s is not None


def test_experiment_analysis_page_exports_artifacts(tmp_path) -> None:
    _app()
    page = ExperimentAnalysisPage()

    artifacts = page.export_current_result(str(tmp_path))

    assert artifacts["csv"].exists()
    assert artifacts["report"].exists()
    assert artifacts["plot"].exists()


def test_mock_resistance_identification_estimates_rs() -> None:
    result = MockResistanceIdentification(true_resistance_ohm=0.185).run()
    estimates = {estimate.key: estimate for estimate in result.estimates}

    assert result.task.module == "resistance"
    assert "phase_current" in result.trace.channels
    assert abs(float(estimates["phase_resistance"].value) - 0.185) < 0.005
    assert estimates["phase_resistance"].confidence is not None


def test_mock_inductance_identification_estimates_ld_lq() -> None:
    result = MockInductanceIdentification(true_ld_h=0.00021, true_lq_h=0.00026).run()
    estimates = {estimate.key: estimate for estimate in result.estimates}

    assert result.task.module == "inductance"
    assert "current_d" in result.trace.channels
    assert "current_q" in result.trace.channels
    assert abs(float(estimates["d_inductance"].value) - 0.00021) < 0.00001
    assert abs(float(estimates["q_inductance"].value) - 0.00026) < 0.00001
    assert float(estimates["current_loop_initial_bandwidth"].value) > 50.0


def test_current_loop_pi_suggestion_uses_rs_and_inductance() -> None:
    d_axis, q_axis = suggest_current_loop_pi(
        resistance_ohm=0.185,
        d_inductance_h=0.00021,
        q_inductance_h=0.00026,
        target_bandwidth_hz=350.0,
    )

    assert d_axis.axis == "d"
    assert q_axis.axis == "q"
    assert d_axis.kp > 0.0
    assert q_axis.kp > d_axis.kp
    assert d_axis.ki == q_axis.ki
    assert "真实硬件写入前" in d_axis.note


def test_current_loop_pi_validation_returns_step_metrics() -> None:
    _, q_axis = suggest_current_loop_pi(
        resistance_ohm=0.185,
        d_inductance_h=0.00021,
        q_inductance_h=0.00026,
        target_bandwidth_hz=350.0,
    )

    result = validate_current_loop_pi(q_axis)

    assert result.metrics.rise_time_s is not None
    assert result.metrics.settling_time_s is not None
    assert result.metrics.overshoot_percent >= 0.0
    assert result.trace.unit == "A"


def test_current_loop_tuning_report_is_exportable(tmp_path) -> None:
    suggestions = suggest_current_loop_pi(
        resistance_ohm=0.185,
        d_inductance_h=0.00021,
        q_inductance_h=0.00026,
        target_bandwidth_hz=350.0,
    )
    validation = validate_current_loop_pi(suggestions[1])

    report = build_current_loop_tuning_report(suggestions, validation)
    path = save_current_loop_tuning_report(suggestions, validation, tmp_path)

    assert "# eMotor-Studio Current Loop Tuning Report" in report
    assert "Mock Step Validation" in report
    assert path.read_text(encoding="utf-8").startswith("# eMotor-Studio Current Loop Tuning Report")


def test_current_loop_tuning_session_package_is_exportable(tmp_path) -> None:
    suggestions = suggest_current_loop_pi(
        resistance_ohm=0.185,
        d_inductance_h=0.00021,
        q_inductance_h=0.00026,
        target_bandwidth_hz=350.0,
    )
    validation = validate_current_loop_pi(suggestions[1])

    manifest = build_current_loop_session_manifest(suggestions, validation, "test_session")
    pi_csv = build_pi_suggestions_csv(suggestions)
    trace_csv = build_validation_trace_csv(validation)
    metrics = build_validation_metrics_payload(validation)
    artifacts = save_current_loop_tuning_session(suggestions, validation, tmp_path, "test_session")

    assert manifest["schema_version"] == "emotor_studio_session_v0"
    assert manifest["session_type"] == "current_loop_tuning"
    assert pi_csv.startswith("axis,kp,ki")
    assert trace_csv.startswith("time_s,target,response,unit")
    assert metrics["metrics"]["rise_time_s"] is not None
    assert artifacts["directory"].is_dir()
    assert artifacts["manifest"].exists()
    assert artifacts["report"].exists()
    assert artifacts["pi_suggestions"].exists()
    assert artifacts["validation_trace"].exists()
    assert artifacts["validation_metrics"].exists()
    assert artifacts["config_snapshot"].exists()
    assert artifacts["safety_notes"].exists()
