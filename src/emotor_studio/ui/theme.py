"""Shared visual design system for eMotor-Studio."""

from __future__ import annotations


COLORS = {
    "window": "#e8edf3",
    "workspace": "#f3f6fa",
    "sidebar": "#182230",
    "sidebar_panel": "#253247",
    "card": "#ffffff",
    "card_soft": "#f7f9fc",
    "border": "#d5dde8",
    "border_strong": "#aebdce",
    "text": "#182436",
    "muted": "#697789",
    "primary": "#315f85",
    "primary_hover": "#264c6a",
    "primary_soft": "#e7eef6",
    "danger": "#c93d3d",
    "danger_hover": "#a83333",
    "ok": "#23825f",
    "idle": "#446b9f",
    "stop": "#6b7888",
    "fault": "#c93d3d",
    "warning": "#b7791f",
    "scope_bg": "#0c1118",
    "scope_grid": "#263342",
}

SPACING = {
    "page": 16,
    "card": 14,
    "section": 12,
    "button": 8,
    "table_row": 30,
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
}}

QLabel#appTitle {{
    color: #ffffff;
    font-size: 19px;
    font-weight: 700;
}}

QLabel#appSubtitle {{
    color: #a9b6c8;
    font-size: 12px;
}}

QLabel#navGroup {{
    color: #7f8ea3;
    font-size: 11px;
    font-weight: 700;
    padding: 14px 8px 4px 8px;
}}

QListWidget#navList {{
    background: {COLORS["sidebar"]};
    border: none;
    color: #d9e2ef;
    outline: 0;
    font-size: 13px;
}}

QListWidget#navList::item {{
    min-height: 30px;
    padding: 5px 10px;
    border-left: 3px solid transparent;
    border-radius: 4px;
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

QWidget#topBar {{
    background: #ffffff;
    border-bottom: 1px solid {COLORS["border"]};
}}

QWidget#workbenchToolBar {{
    background: #f4f7fb;
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
    color: {COLORS["text"]};
    font-size: 18px;
    font-weight: 700;
}}

QLabel#pageSubtitle {{
    color: {COLORS["muted"]};
    font-size: 12px;
}}

QFrame#sectionCard {{
    background: {COLORS["card"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 8px;
}}

QFrame#workflowCard {{
    background: #ffffff;
    border: 1px solid {COLORS["border"]};
    border-left: 4px solid {COLORS["primary"]};
    border-radius: 8px;
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
    color: #233247;
    font-size: 13px;
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
    border-radius: 7px;
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
    color: {COLORS["text"]};
    font-size: 19px;
    font-weight: 750;
}}

QLabel#kpiUnit {{
    color: {COLORS["muted"]};
    font-size: 12px;
}}

QFrame#infoBox {{
    background: {COLORS["card_soft"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 7px;
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
    background: #f3f6fa;
    border: 1px solid {COLORS["border"]};
    border-radius: 5px;
    padding: 4px 8px;
    color: {COLORS["muted"]};
}}

QLabel[state="ok"] {{
    background: #e9f4ef;
    border-color: #b4d7ca;
    color: #1f6d52;
}}

QLabel[state="idle"] {{
    background: #edf3fb;
    border-color: #bacbe1;
    color: #365d90;
}}

QLabel[state="stop"], QLabel[state="muted"] {{
    background: #f1f4f8;
    border-color: {COLORS["border"]};
    color: {COLORS["muted"]};
}}

QLabel[state="fault"] {{
    background: #faeeee;
    border-color: #e4b8b8;
    color: #9d3030;
}}

QLabel[state="warning"] {{
    background: #fbf4e8;
    border-color: #e4c68d;
    color: #8c5b13;
}}

QPushButton {{
    background: #ffffff;
    border: 1px solid {COLORS["border_strong"]};
    border-radius: 6px;
    padding: 5px 10px;
    min-height: 23px;
}}

QPushButton:hover {{
    background: #f1f5fa;
    border-color: #8ea6bf;
}}

QPushButton:disabled {{
    background: #eef2f7;
    color: #94a3b8;
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
    background: #fbf4e8;
    border-color: #d8b670;
    color: #755015;
}}

QPushButton[variant="ghost"] {{
    background: #f8fafc;
    color: #31445b;
}}

QToolButton#toolStripButton {{
    background: #ffffff;
    border: 1px solid {COLORS["border_strong"]};
    border-radius: 5px;
    padding: 5px 8px;
    color: #26364b;
}}

QToolButton#toolStripButton:hover {{
    background: #eef3f8;
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
    background: #ffffff;
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
    border-radius: 7px;
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
    background: #ffffff;
    border: 1px solid {COLORS["border"]};
    gridline-color: #e4e9f0;
    selection-background-color: #dceafe;
    alternate-background-color: #f8fafc;
}}

QTableWidget::item {{
    padding: 2px 5px;
}}

QHeaderView::section {{
    background: #eef2f6;
    border: none;
    border-right: 1px solid {COLORS["border"]};
    padding: 5px;
    font-weight: 700;
}}

QLineEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background: #ffffff;
    border: 1px solid {COLORS["border_strong"]};
    border-radius: 5px;
    padding: 4px 6px;
}}

QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS["primary"]};
}}

QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    background: {COLORS["card"]};
}}

QTabBar::tab {{
    background: #edf1f6;
    padding: 6px 11px;
    border: 1px solid {COLORS["border"]};
    border-bottom: none;
}}

QTabBar::tab:selected {{
    background: #ffffff;
    color: {COLORS["primary"]};
}}

QListWidget#scopeChannelList {{
    background: #ffffff;
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    outline: 0;
}}

QListWidget#deviceList {{
    background: #0d1621;
    border: 1px solid #253245;
    border-radius: 5px;
    color: #cbd5e1;
    outline: 0;
}}

QListWidget#deviceList::item {{
    min-height: 26px;
    padding: 4px 6px;
}}

QListWidget#scopeChannelList::item {{
    min-height: 29px;
    padding: 3px 6px;
}}

QListWidget#scopeChannelList::item:selected {{
    background: {COLORS["primary_soft"]};
    color: {COLORS["text"]};
}}

QMenu {{
    background: #ffffff;
    border: 1px solid #cbd5e1;
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
"""
