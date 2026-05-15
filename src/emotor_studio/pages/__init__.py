"""UI pages for eMotor-Studio."""

from .command_page import CommandPage
from .dashboard_page import DashboardPage
from .fault_page import FaultPage
from .hardware_page import HardwarePage
from .logger_page import LoggerPage
from .parameter_page import ParameterPage
from .report_page import ReportPage
from .scope_page import ScopePage
from .vesc_like_pages import (
    AppSettingsPage,
    ControlTuningPage,
    DataAnalysisPage,
    ExperimentAnalysisPage,
    FirmwarePage,
    FilterDesignPage,
    FocPage,
    IdentificationPage,
    MotorSettingsPage,
    ObserverWorkbenchPage,
    ResearchWorkbenchPage,
    SampledDataPage,
    SystemToolsPage,
    TerminalPage,
)

__all__ = [
    "AppSettingsPage",
    "CommandPage",
    "ControlTuningPage",
    "DashboardPage",
    "DataAnalysisPage",
    "ExperimentAnalysisPage",
    "FaultPage",
    "FirmwarePage",
    "FilterDesignPage",
    "FocPage",
    "HardwarePage",
    "IdentificationPage",
    "LoggerPage",
    "MotorSettingsPage",
    "ObserverWorkbenchPage",
    "ParameterPage",
    "ReportPage",
    "ResearchWorkbenchPage",
    "SampledDataPage",
    "ScopePage",
    "SystemToolsPage",
    "TerminalPage",
]
