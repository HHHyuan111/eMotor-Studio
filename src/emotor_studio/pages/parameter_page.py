"""Parameter configuration page."""

from __future__ import annotations

from PySide6 import QtCore, QtWidgets

from emotor_studio.backend import BackendInterface
from emotor_studio.models import ParameterItem
from emotor_studio.ui.components import InfoBox, KpiCard, PageHeader, SectionCard


class ParameterPage(QtWidgets.QWidget):
    def __init__(self, backend: BackendInterface, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.backend = backend
        self._parameters: dict[str, ParameterItem] = {}
        self._all_parameters: list[ParameterItem] = []

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        layout.addWidget(PageHeader("参数配置", "按 AxDr_L 控制对象组织的 Mock 参数表，真实固件写入将在后续阶段接入。"))

        summary_card = SectionCard("参数概览", "先看参数规模、分组和可写状态，再进入搜索和写入。")
        summary_grid = QtWidgets.QGridLayout()
        summary_grid.setSpacing(10)
        self.total_card = KpiCard("参数总数", "schema items", "idle")
        self.editable_card = KpiCard("可写参数", "Mock writeable", "ok")
        self.readonly_card = KpiCard("只读参数", "protected", "warning")
        self.group_card = KpiCard("分组数量", "groups", "idle")
        for index, card in enumerate([self.total_card, self.editable_card, self.readonly_card, self.group_card]):
            summary_grid.addWidget(card, 0, index)
        summary_card.body.addLayout(summary_grid)
        layout.addWidget(summary_card)

        toolbar_card = SectionCard("操作栏")
        toolbar = QtWidgets.QHBoxLayout()
        toolbar.setSpacing(8)
        self.group_filter = QtWidgets.QComboBox()
        self.group_filter.setMinimumWidth(160)
        self.group_filter.currentTextChanged.connect(lambda _text: self._populate_table())
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setPlaceholderText("搜索参数名 / 显示名 / 说明")
        self.search_edit.textChanged.connect(lambda _text: self._populate_table())
        self.writable_only = QtWidgets.QCheckBox("仅显示可写")
        self.writable_only.toggled.connect(lambda _checked: self._populate_table())
        refresh = QtWidgets.QPushButton("读取参数")
        refresh.clicked.connect(self.refresh)
        write_selected = QtWidgets.QPushButton("写入参数")
        write_selected.setProperty("variant", "primary")
        write_selected.clicked.connect(self.write_selected)
        save_button = QtWidgets.QPushButton("保存配置")
        save_button.setProperty("variant", "ghost")
        save_button.clicked.connect(lambda: self.status_label.setText("状态：保存配置待实现"))
        load_button = QtWidgets.QPushButton("加载配置")
        load_button.setProperty("variant", "ghost")
        load_button.clicked.connect(lambda: self.status_label.setText("状态：加载配置待实现"))
        toolbar.addWidget(QtWidgets.QLabel("分组"))
        toolbar.addWidget(self.group_filter)
        toolbar.addWidget(self.search_edit, 1)
        toolbar.addWidget(self.writable_only)
        toolbar.addWidget(refresh)
        toolbar.addWidget(write_selected)
        toolbar.addWidget(save_button)
        toolbar.addWidget(load_button)
        toolbar_card.body.addLayout(toolbar)
        layout.addWidget(toolbar_card)

        content = QtWidgets.QHBoxLayout()
        content.setSpacing(12)
        layout.addLayout(content, 1)

        table_card = SectionCard("参数表")
        self.table = QtWidgets.QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["分组", "参数名", "显示名", "当前值", "单位", "最小值", "最大值", "说明"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setDefaultSectionSize(30)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.table.itemSelectionChanged.connect(self._update_detail_panel)
        self.table.setColumnWidth(0, 118)
        self.table.setColumnWidth(1, 170)
        self.table.setColumnWidth(2, 170)
        self.table.setColumnWidth(3, 130)
        self.table.setColumnWidth(4, 90)
        self.table.setColumnWidth(5, 90)
        self.table.setColumnWidth(6, 90)
        table_card.body.addWidget(self.table)
        content.addWidget(table_card, 1)

        detail_card = SectionCard("参数说明", "选中一行查看参数含义和写入安全提示。")
        detail_card.setMinimumWidth(300)
        detail_card.setMaximumWidth(340)
        self.detail_title = QtWidgets.QLabel("未选择参数")
        self.detail_title.setObjectName("sectionTitle")
        self.detail_body = QtWidgets.QLabel("请选择左侧参数。")
        self.detail_body.setObjectName("infoBody")
        self.detail_body.setWordWrap(True)
        self.detail_meta = QtWidgets.QLabel("只读：--\n运行中写入：后续固件协议确认")
        self.detail_meta.setObjectName("hintText")
        self.status_label = QtWidgets.QLabel("状态：就绪")
        self.status_label.setObjectName("hintText")
        detail_card.body.addWidget(self.detail_title)
        detail_card.body.addWidget(self.detail_body)
        detail_card.body.addWidget(self.detail_meta)
        detail_card.body.addWidget(InfoBox("安全提示", "当前写入只作用于 MockBackend。真实硬件阶段需要由固件协议声明哪些参数允许运行中修改。"))
        detail_card.body.addStretch(1)
        detail_card.body.addWidget(self.status_label)
        content.addWidget(detail_card)

        self.refresh()

    def refresh(self) -> None:
        parameters = self.backend.read_parameters()
        parameters.sort(key=lambda item: (item.group, item.key))
        self._all_parameters = parameters
        self._parameters = {item.key: item for item in parameters}
        current_group = self.group_filter.currentText()
        groups = ["全部", *sorted({item.group for item in parameters})]
        self.group_filter.blockSignals(True)
        self.group_filter.clear()
        self.group_filter.addItems(groups)
        if current_group in groups:
            self.group_filter.setCurrentText(current_group)
        self.group_filter.blockSignals(False)
        self._populate_table()
        self._update_summary_cards()
        self.status_label.setText(f"状态：已读取 {len(parameters)} 个参数")

    def write_selected(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            self.status_label.setText("状态：请先选择一个参数")
            return
        key_item = self.table.item(row, 1)
        value_item = self.table.item(row, 3)
        if key_item is None or value_item is None:
            self.status_label.setText("状态：选中行信息不完整")
            return
        key = str(key_item.data(QtCore.Qt.ItemDataRole.UserRole) or key_item.text())
        parameter = self._parameters.get(key)
        if parameter is None:
            self.status_label.setText(f"状态：未知参数 {key}")
            return
        if parameter.readonly:
            self.status_label.setText(f"状态：{key} 是只读参数")
            return
        try:
            parsed_value = self._parse_value(value_item.text(), parameter.value)
            updated = self.backend.write_parameter(key, parsed_value)
        except (KeyError, TypeError, ValueError) as exc:
            self.status_label.setText(f"状态：写入失败 {exc}")
            return
        self._parameters[key] = updated
        value_item.setText(str(updated.value))
        self.status_label.setText(f"状态：已写入 {key} = {updated.value}")
        self._update_detail_panel()

    def _populate_table(self) -> None:
        group = self.group_filter.currentText() or "全部"
        keyword = self.search_edit.text().strip().lower()
        writable_only = self.writable_only.isChecked()
        parameters = [
            item
            for item in self._all_parameters
            if (group == "全部" or item.group == group)
            and (not writable_only or not item.readonly)
            and (
                not keyword
                or keyword in item.key.lower()
                or keyword in item.name.lower()
                or keyword in item.description.lower()
            )
        ]
        self.table.setRowCount(len(parameters))
        for row, item in enumerate(parameters):
            name_text = f"{item.name}（只读）" if item.readonly else item.name
            values = [
                item.group,
                item.key,
                name_text,
                str(item.value),
                item.unit,
                "" if item.min_value is None else str(item.min_value),
                "" if item.max_value is None else str(item.max_value),
                item.description,
            ]
            for column, value in enumerate(values):
                table_item = QtWidgets.QTableWidgetItem(value)
                if column != 3 or item.readonly:
                    table_item.setFlags(table_item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                if column == 1:
                    table_item.setData(QtCore.Qt.ItemDataRole.UserRole, item.key)
                if item.readonly:
                    table_item.setToolTip("只读参数")
                self.table.setItem(row, column, table_item)
        self.table.resizeRowsToContents()
        self.status_label.setText(f"状态：显示 {len(parameters)} / {len(self._all_parameters)} 个参数")
        self._update_detail_panel()

    def _update_summary_cards(self) -> None:
        total = len(self._all_parameters)
        readonly = sum(1 for item in self._all_parameters if item.readonly)
        editable = total - readonly
        groups = len({item.group for item in self._all_parameters})
        self.total_card.set_value(str(total), "items", "idle")
        self.editable_card.set_value(str(editable), "可写", "ok")
        self.readonly_card.set_value(str(readonly), "只读", "warning" if readonly else "ok")
        self.group_card.set_value(str(groups), "groups", "idle")

    def _update_detail_panel(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            self.detail_title.setText("未选择参数")
            self.detail_body.setText("请选择左侧参数。")
            self.detail_meta.setText("只读：--\n运行中写入：后续固件协议确认")
            return
        key_item = self.table.item(row, 1)
        key = key_item.data(QtCore.Qt.ItemDataRole.UserRole) if key_item else None
        parameter = self._parameters.get(str(key))
        if parameter is None:
            return
        self.detail_title.setText(parameter.name)
        self.detail_body.setText(parameter.description or "暂无说明。")
        readonly = "是" if parameter.readonly else "否"
        limits = f"{parameter.min_value} .. {parameter.max_value}" if parameter.min_value is not None or parameter.max_value is not None else "未限定"
        self.detail_meta.setText(
            f"参数名：{parameter.key}\n"
            f"分组：{parameter.group}\n"
            f"单位：{parameter.unit or '-'}\n"
            f"范围：{limits}\n"
            f"只读：{readonly}\n"
            "运行中写入：后续固件协议确认"
        )

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
