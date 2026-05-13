"""Parameter page."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from emotor_studio.backend import BackendInterface
from emotor_studio.models import ParameterItem


class ParameterPage(QtWidgets.QWidget):
    def __init__(self, backend: BackendInterface, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.backend = backend
        self._parameters: dict[str, ParameterItem] = {}
        layout = QtWidgets.QVBoxLayout(self)
        toolbar = QtWidgets.QHBoxLayout()
        refresh = QtWidgets.QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        write_selected = QtWidgets.QPushButton("Write Selected")
        write_selected.clicked.connect(self.write_selected)
        self.status_label = QtWidgets.QLabel("Ready")
        toolbar.addWidget(refresh)
        toolbar.addWidget(write_selected)
        toolbar.addWidget(self.status_label, 1)
        layout.addLayout(toolbar)

        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Group", "Key", "Name", "Value", "Unit", "Range", "Description"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self) -> None:
        parameters = self.backend.read_parameters()
        parameters.sort(key=lambda item: (item.group, item.key))
        self._parameters = {item.key: item for item in parameters}
        self.table.setRowCount(len(parameters))
        for row, item in enumerate(parameters):
            range_text = ""
            if item.min_value is not None or item.max_value is not None:
                range_text = f"{item.min_value if item.min_value is not None else '-inf'}..{item.max_value if item.max_value is not None else 'inf'}"
            values = [
                item.group,
                item.key,
                item.name,
                str(item.value),
                item.unit,
                range_text,
                item.description,
            ]
            for column, value in enumerate(values):
                table_item = QtWidgets.QTableWidgetItem(value)
                if column != 3 or item.readonly:
                    table_item.setFlags(table_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                if column == 1:
                    table_item.setData(QtCore.Qt.ItemDataRole.UserRole, item.key)
                self.table.setItem(row, column, table_item)
        self.status_label.setText(f"Loaded {len(parameters)} parameters")

    def write_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            self.status_label.setText("Select one parameter row first")
            return
        key_item = self.table.item(row, 1)
        value_item = self.table.item(row, 3)
        if key_item is None or value_item is None:
            self.status_label.setText("Selected row is incomplete")
            return
        key = str(key_item.data(QtCore.Qt.ItemDataRole.UserRole) or key_item.text())
        parameter = self._parameters.get(key)
        if parameter is None:
            self.status_label.setText(f"Unknown parameter: {key}")
            return
        if parameter.readonly:
            self.status_label.setText(f"{key} is read-only")
            return
        try:
            parsed_value = self._parse_value(value_item.text(), parameter.value)
            updated = self.backend.write_parameter(key, parsed_value)
        except (KeyError, TypeError, ValueError) as exc:
            self.status_label.setText(f"Write failed: {exc}")
            return
        self._parameters[key] = updated
        value_item.setText(str(updated.value))
        self.status_label.setText(f"Wrote {key} = {updated.value}")

    @staticmethod
    def _parse_value(text: str, current_value: object) -> object:
        stripped = text.strip()
        if isinstance(current_value, bool):
            lowered = stripped.lower()
            if lowered in {"1", "true", "yes", "on"}:
                return True
            if lowered in {"0", "false", "no", "off"}:
                return False
            raise ValueError(f"Expected boolean value, got {text!r}")
        if isinstance(current_value, int) and not isinstance(current_value, bool):
            return int(stripped)
        if isinstance(current_value, float):
            return float(stripped)
        return stripped
