"""Shared visual design system for eMotor-Studio."""

from __future__ import annotations


COLORS = {
    "window": "#d8e0e8",
    "workspace": "#edf2f6",
    "sidebar": "#101923",
    "sidebar_panel": "#1f3043",
    "sidebar_hover": "#172434",
    "card": "#fbfcfd",
    "card_soft": "#f4f7fa",
    "surface_alt": "#e9eff5",
    "border": "#d6dee8",
    "border_strong": "#b7c4d2",
    "text": "#111827",
    "text_strong": "#0b1220",
    "muted": "#64748b",
    "subtle": "#8a97a8",
    "primary": "#24758f",
    "primary_hover": "#1a5d74",
    "primary_soft": "#e5f3f6",
    "danger": "#b8322b",
    "danger_hover": "#92251f",
    "ok": "#28765f",
    "idle": "#3e658f",
    "stop": "#667085",
    "fault": "#b8322b",
    "warning": "#9b6516",
    "scope_bg": "#071018",
    "scope_panel": "#0c1720",
    "scope_grid": "#273847",
}

SPACING = {
    "page": 18,
    "card": 16,
    "section": 12,
    "button": 8,
    "table_row": 32,
}

APP_STYLE = f"""
QMainWindow {{
    background: {COLORS["window"]};
}}

QWidget {{
    color: {COLORS["text"]};
    font-family: "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
    font-size: 12px;
}}

QWidget#sidebar {{
    background: {COLORS["sidebar"]};
    border-right: 1px solid #243348;
}}

QLabel#appTitle {{
    color: #ffffff;
    font-size: 19px;
    font-weight: 700;
}}

QLabel#appSubtitle {{
    color: #a9b7c9;
    font-size: 12px;
}}

QLabel#navGroup {{
    color: #7f91a8;
    font-size: 11px;
    font-weight: 700;
    padding: 15px 8px 5px 8px;
}}

QListWidget#navList {{
    background: {COLORS["sidebar"]};
    border: none;
    color: #d9e3f0;
    outline: 0;
    font-size: 13px;
}}

QListWidget#navList::item {{
    min-height: 31px;
    padding: 5px 10px;
    border-left: 3px solid transparent;
    border-radius: 7px;
}}

QListWidget#navList::item:disabled {{
    color: #7f8ea3;
    font-size: 11px;
    font-weight: 700;
    padding-top: 14px;
    min-height: 24px;
    background: {COLORS["sidebar"]};
}}

QListWidget#navList::item:selected {{
    background: {COLORS["sidebar_panel"]};
    color: #ffffff;
    border-left: 3px solid {COLORS["primary"]};
}}

QListWidget#navList::item:hover {{
    background: {COLORS["sidebar_hover"]};
}}

QWidget#topBar {{
    background: #fcfdff;
    border-bottom: 1px solid {COLORS["border"]};
}}

QWidget#workbenchToolBar {{
    background: #f7f9fc;
    border-bottom: 1px solid {COLORS["border"]};
}}

QWidget#pageContainer {{
    background: {COLORS["workspace"]};
}}

QScrollArea#pageScrollArea {{
    background: {COLORS["workspace"]};
    border: none;
}}

QScrollArea#pageScrollArea > QWidget > QWidget {{
    background: {COLORS["workspace"]};
}}

QLabel#pageTitle {{
    color: {COLORS["text_strong"]};
    font-size: 19px;
    font-weight: 700;
}}

QLabel#pageSubtitle {{
    color: {COLORS["muted"]};
    font-size: 12px;
}}

QFrame#sectionCard {{
    background: {COLORS["card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 9px;
}}

QFrame#workflowCard {{
    background: {COLORS["card"]};
    border: 1px solid {COLORS["border"]};
    border-left: 4px solid {COLORS["primary"]};
    border-radius: 9px;
}}

QLabel#workflowTitle {{
    color: {COLORS["text"]};
    font-size: 14px;
    font-weight: 750;
}}

QLabel#workflowTag {{
    color: {COLORS["primary_hover"]};
    background: {COLORS["primary_soft"]};
    border: 1px solid #bdcddd;
    border-radius: 4px;
    padding: 2px 6px;
}}

QLabel#sectionTitle {{
    color: {COLORS["text_strong"]};
    font-size: 14px;
    font-weight: 700;
}}

QLabel#sectionSubtitle {{
    color: {COLORS["muted"]};
    font-size: 12px;
}}

QFrame#kpiCard {{
    background: {COLORS["card"]};
    border: 1px solid {COLORS["border"]};
    border-left: 4px solid #94a3b8;
    border-radius: 9px;
}}

QFrame#kpiCard[state="ok"] {{
    border-left-color: {COLORS["ok"]};
}}

QFrame#kpiCard[state="idle"] {{
    border-left-color: {COLORS["idle"]};
}}

QFrame#kpiCard[state="stop"] {{
    border-left-color: {COLORS["stop"]};
}}

QFrame#kpiCard[state="fault"] {{
    border-left-color: {COLORS["fault"]};
}}

QFrame#kpiCard[state="warning"] {{
    border-left-color: {COLORS["warning"]};
}}

QLabel#kpiTitle {{
    color: {COLORS["muted"]};
    font-size: 12px;
    font-weight: 600;
}}

QLabel#kpiValue {{
    color: {COLORS["text_strong"]};
    font-size: 20px;
    font-weight: 750;
}}

QLabel#kpiUnit {{
    color: {COLORS["muted"]};
    font-size: 12px;
}}

QFrame#infoBox {{
    background: {COLORS["card_soft"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 9px;
}}

QLabel#infoTitle {{
    color: {COLORS["text"]};
    font-size: 13px;
    font-weight: 700;
}}

QLabel#infoBody, QLabel#hintText {{
    color: {COLORS["muted"]};
    font-size: 12px;
}}

QLabel[role="statusChip"] {{
    background: #f6f8fb;
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 4px 10px;
    color: {COLORS["muted"]};
    font-weight: 600;
}}

QLabel[state="ok"] {{
    background: #e8f5ef;
    border-color: #acd8c6;
    color: #17604a;
}}

QLabel[state="idle"] {{
    background: #eaf2fb;
    border-color: #b5cae4;
    color: #28537e;
}}

QLabel[state="stop"], QLabel[state="muted"] {{
    background: #f3f6f9;
    border-color: {COLORS["border"]};
    color: {COLORS["muted"]};
}}

QLabel[state="fault"] {{
    background: #fff0ee;
    border-color: #f1b8b2;
    color: #9a241a;
}}

QLabel[state="warning"] {{
    background: #fff6e6;
    border-color: #eac47a;
    color: #81510b;
}}

QPushButton {{
    background: #fcfdff;
    border: 1px solid {COLORS["border_strong"]};
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 26px;
}}

QPushButton:hover {{
    background: #f3f7fb;
    border-color: #839bb6;
}}

QPushButton:pressed {{
    background: #e8f0f6;
}}

QPushButton:disabled {{
    background: #eef2f6;
    border-color: #d8e0ea;
    color: #9aa8b8;
}}

QPushButton[variant="primary"] {{
    background: {COLORS["primary"]};
    border-color: {COLORS["primary"]};
    color: #ffffff;
}}

QPushButton[variant="primary"]:hover {{
    background: {COLORS["primary_hover"]};
}}

QPushButton[variant="danger"] {{
    background: {COLORS["danger"]};
    border-color: {COLORS["danger"]};
    color: #ffffff;
}}

QPushButton[variant="danger"]:hover {{
    background: {COLORS["danger_hover"]};
}}

QPushButton[variant="warning"] {{
    background: #fff6e6;
    border-color: #d8a84b;
    color: #77480a;
}}

QPushButton[variant="ghost"] {{
    background: #f8fafc;
    color: #26384f;
}}

QPushButton[variant="ghost"]:hover {{
    background: #edf5f8;
    border-color: #a8bdcc;
}}

QToolButton#toolStripButton {{
    background: #fbfcfe;
    border: 1px solid {COLORS["border_strong"]};
    border-radius: 7px;
    padding: 6px 10px;
    color: #26364b;
}}

QToolButton#toolStripButton:hover {{
    background: #eef4f8;
    border-color: #91a9c2;
}}

QToolButton#toolStripButton:checked {{
    background: {COLORS["primary_soft"]};
    border-color: {COLORS["primary"]};
    color: {COLORS["primary_hover"]};
}}

QToolButton#toolStripButton:disabled {{
    background: #eef2f7;
    color: #94a3b8;
}}

QFrame#commandStrip {{
    background: #fbfcfe;
    border-top: 1px solid {COLORS["border"]};
}}

QDoubleSpinBox#stripSpin {{
    font-family: "Consolas", "Microsoft YaHei UI", monospace;
    min-width: 92px;
}}

QPushButton#stripButton {{
    min-height: 22px;
    padding: 4px 8px;
}}

QPushButton#stripStopButton {{
    background: #dc2626;
    border-color: #dc2626;
    color: #ffffff;
    font-weight: 800;
    min-width: 72px;
}}

QProgressBar#stripBar {{
    min-width: 130px;
    height: 18px;
    text-align: center;
}}

QGroupBox {{
    background: {COLORS["card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 10px;
    margin-top: 12px;
    padding: 12px 10px 10px 10px;
    font-weight: 700;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
    color: #31445b;
}}

QTableWidget {{
    background: {COLORS["card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 9px;
    gridline-color: #e6edf3;
    selection-background-color: #d9edf3;
    alternate-background-color: #f7f9fc;
}}

QTableWidget::item {{
    padding: 3px 6px;
}}

QHeaderView::section {{
    background: #edf2f7;
    border: none;
    border-right: 1px solid {COLORS["border"]};
    padding: 7px;
    font-weight: 700;
    color: {COLORS["text_strong"]};
}}

QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: #fcfdff;
    border: 1px solid {COLORS["border_strong"]};
    border-radius: 8px;
    padding: 5px 7px;
}}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS["primary"]};
}}

QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    background: {COLORS["card"]};
    border-radius: 9px;
}}

QTabBar::tab {{
    background: #e7edf4;
    padding: 7px 14px;
    border: 1px solid {COLORS["border"]};
    border-bottom: none;
    color: {COLORS["muted"]};
}}

QTabBar::tab:hover {{
    background: #f1f5f9;
    color: {COLORS["text"]};
}}

QTabBar::tab:selected {{
    background: {COLORS["card"]};
    color: {COLORS["primary"]};
    font-weight: 700;
}}

QListWidget#scopeChannelList {{
    background: #f8fafc;
    border: 1px solid {COLORS["border"]};
    border-radius: 9px;
    outline: 0;
}}

QListWidget#deviceList {{
    background: #0c151f;
    border: 1px solid #253245;
    border-radius: 8px;
    color: #cbd5e1;
    outline: 0;
}}

QListWidget#deviceList::item {{
    min-height: 26px;
    padding: 4px 6px;
}}

QListWidget#scopeChannelList::item {{
    min-height: 30px;
    padding: 4px 7px;
}}

QListWidget#scopeChannelList::item:selected {{
    background: {COLORS["primary_soft"]};
    color: {COLORS["text"]};
}}

QMenu {{
    background: #fcfdff;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 4px;
}}

QMenu::item {{
    padding: 6px 24px;
}}

QMenu::item:selected {{
    background: {COLORS["primary_soft"]};
}}

QProgressBar {{
    background: #eef2f7;
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    height: 9px;
}}

QProgressBar::chunk {{
    background: {COLORS["primary"]};
    border-radius: 3px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 11px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: #bdc9d6;
    border-radius: 5px;
    min-height: 32px;
}}

QScrollBar::handle:vertical:hover {{
    background: #9dadbd;
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 11px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background: #bdc9d6;
    border-radius: 5px;
    min-width: 32px;
}}

QScrollBar::handle:horizontal:hover {{
    background: #9dadbd;
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}
"""
