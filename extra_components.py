# extra_components_widget.py

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGroupBox, QLabel, QLineEdit, QTextEdit, QPlainTextEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QPushButton, QToolButton, QToolBar, QAction,
)
from PyQt5.QtGui import QIcon


class ExtraComponentsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(16)

        self._build_toolbar(layout)
        self._build_text_inputs(layout)
        self._build_numeric_inputs(layout)
        self._build_toggles(layout)
        self._build_actions(layout)

    def _build_toolbar(self, parent_layout):
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setMovable(False)

        self.tb_new = QToolButton()
        self.tb_new.setText("New")
        self.tb_new.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.tb_open = QToolButton()
        self.tb_open.setText("Open")
        self.tb_open.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.tb_save = QToolButton()
        self.tb_save.setText("Save")
        self.tb_save.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.tb_refresh = QToolButton()
        self.tb_refresh.setText("Refresh")
        self.tb_refresh.setCheckable(True)
        self.tb_refresh.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.toolbar.addWidget(self.tb_new)
        self.toolbar.addWidget(self.tb_open)
        self.toolbar.addSeparator()
        self.toolbar.addWidget(self.tb_save)
        self.toolbar.addWidget(self.tb_refresh)

        parent_layout.addWidget(self.toolbar)

    def _build_text_inputs(self, parent_layout):
        group = QGroupBox("Text Inputs")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.line_hostname = QLineEdit()
        self.line_hostname.setPlaceholderText("Enter hostname...")
        form.addRow(QLabel("Hostname:"), self.line_hostname)

        self.line_site_id = QLineEdit()
        self.line_site_id.setPlaceholderText("Enter site ID...")
        form.addRow(QLabel("Site ID:"), self.line_site_id)

        self.text_notes = QTextEdit()
        self.text_notes.setPlaceholderText("Enter rich text notes...")
        self.text_notes.setMaximumHeight(120)
        form.addRow(QLabel("Notes:"), self.text_notes)

        self.plain_log = QPlainTextEdit()
        self.plain_log.setPlaceholderText("Log output appears here...")
        self.plain_log.setMaximumHeight(100)
        self.plain_log.setReadOnly(True)
        form.addRow(QLabel("Log:"), self.plain_log)

        parent_layout.addWidget(group)

    def _build_numeric_inputs(self, parent_layout):
        group = QGroupBox("Numeric Inputs")
        form = QFormLayout(group)
        form.setSpacing(10)

        self.spin_retries = QSpinBox()
        self.spin_retries.setRange(0, 100)
        self.spin_retries.setValue(3)
        self.spin_retries.setSuffix(" retries")
        form.addRow(QLabel("Max Retries:"), self.spin_retries)

        self.dspin_threshold = QDoubleSpinBox()
        self.dspin_threshold.setRange(0.0, 100.0)
        self.dspin_threshold.setValue(95.5)
        self.dspin_threshold.setSuffix(" %")
        self.dspin_threshold.setDecimals(1)
        self.dspin_threshold.setSingleStep(0.5)
        form.addRow(QLabel("Threshold:"), self.dspin_threshold)

        self.combo_priority = QComboBox()
        self.combo_priority.addItems(["Low", "Medium", "High", "Critical"])
        self.combo_priority.setCurrentIndex(1)
        form.addRow(QLabel("Priority:"), self.combo_priority)

        parent_layout.addWidget(group)

    def _build_toggles(self, parent_layout):
        group = QGroupBox("Options")
        vbox = QVBoxLayout(group)
        vbox.setSpacing(8)

        self.chk_auto_refresh = QCheckBox("Enable auto-refresh")
        self.chk_auto_refresh.setChecked(True)
        vbox.addWidget(self.chk_auto_refresh)

        self.chk_notifications = QCheckBox("Send notifications")
        vbox.addWidget(self.chk_notifications)

        self.chk_verbose = QCheckBox("Verbose logging")
        vbox.addWidget(self.chk_verbose)

        self.chk_disabled_demo = QCheckBox("Disabled option (demo)")
        self.chk_disabled_demo.setEnabled(False)
        vbox.addWidget(self.chk_disabled_demo)

        parent_layout.addWidget(group)

    def _build_actions(self, parent_layout):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_apply = QPushButton("Apply")
        self.btn_apply.setMinimumWidth(100)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setProperty("secondary", True)
        self.btn_reset.setMinimumWidth(100)

        self.btn_delete = QPushButton("Delete")
        self.btn_delete.setProperty("danger", True)
        self.btn_delete.setMinimumWidth(100)

        self.btn_disabled_demo = QPushButton("Disabled (demo)")
        self.btn_disabled_demo.setEnabled(False)
        self.btn_disabled_demo.setMinimumWidth(100)

        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_reset.clicked.connect(self._on_reset)
        self.btn_delete.clicked.connect(self._on_delete)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_disabled_demo)
        btn_layout.addWidget(self.btn_apply)

        parent_layout.addStretch()
        parent_layout.addLayout(btn_layout)

    def _on_apply(self):
        self.plain_log.appendPlainText(
            f"Applied: retries={self.spin_retries.value()}, "
            f"threshold={self.dspin_threshold.value()}%, "
            f"priority={self.combo_priority.currentText()}"
        )

    def _on_reset(self):
        self.line_hostname.clear()
        self.line_site_id.clear()
        self.text_notes.clear()
        self.spin_retries.setValue(3)
        self.dspin_threshold.setValue(95.5)
        self.combo_priority.setCurrentIndex(1)
        self.chk_auto_refresh.setChecked(True)
        self.chk_notifications.setChecked(False)
        self.chk_verbose.setChecked(False)
        self.plain_log.appendPlainText("Settings reset to defaults.")

    def _on_delete(self):
        self.plain_log.appendPlainText("Delete action triggered.")
