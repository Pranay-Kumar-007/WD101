# device_details_widget.py

import sys
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import (
    QWidget, QGroupBox, QRadioButton, QStackedLayout,
    QFormLayout, QVBoxLayout, QHBoxLayout, QLineEdit,
    QLabel, QPushButton, QComboBox, QMessageBox,
    QDateTimeEdit, QAction, QCalendarWidget,
)
from PyQt5.QtGui import QPixmap, QPainter, QFont, QIcon


class DeviceDetailsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        self.date_edit = None

        size = 20
        self.pix = QPixmap(size, size)
        self.pix.fill(Qt.transparent)
        p = QPainter(self.pix)
        f = QFont()
        f.setPointSize(14)
        p.setFont(f)
        p.drawText(self.pix.rect(), Qt.AlignCenter, "\u25A0")
        p.end()

        group = QGroupBox("Utilities")
        gbox = QVBoxLayout(group)
        self.stack = QStackedLayout()

        self.options = [
            ("Task UI 1", [
                ("Dropdown Option 1:", QComboBox()),
                ("Dropdown Option 2:", QComboBox()),
                ("Dropdown Option 3:", QComboBox()),
            ]),
            ("Task UI 2", [
                ("Temp1:", QLineEdit()),
                ("Temp2:", QLineEdit()),
            ]),
            ("Task UI 3", [
                ("Site ID:", QLineEdit()),
                ("Comments:", QLineEdit()),
            ]),
            ("Task UI 4", [
                ("Site ID:", QLineEdit()),
                ("Comments:", QLineEdit()),
            ]),
        ]

        for idx, (label, fields) in enumerate(self.options):
            rb = QRadioButton(label)
            rb.toggled.connect(
                lambda chk, i=idx: chk and self.stack.setCurrentIndex(i)
            )
            gbox.addWidget(rb)

            page = QWidget()
            form = QFormLayout(page)
            for text, widget in fields:
                if "Dropdown Option" in text:
                    widget.addItems(["Option A", "Option B", "Option C"])
                    layout.addWidget(widget)
                    if text == "Dropdown Option 1:":
                        widget.setObjectName("myCombo")
                    if text == "Dropdown Option 2:":
                        widget.setObjectName("combo2")
                    if text == "Dropdown Option 3:":
                        widget.setObjectName("combo3")
                form.addRow(QLabel(text), widget)
            self.stack.addWidget(page)

        group.findChildren(QRadioButton)[0].setChecked(True)

        layout.addWidget(group)
        layout.addLayout(self.stack)

        self._build_date_section(layout)
        self._build_action_buttons(layout)

    def _build_date_section(self, parent_layout):
        date_group = QGroupBox("Schedule")
        date_layout = QFormLayout(date_group)

        self.date_edit = QDateTimeEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDateTime(QDateTime.currentDateTime())
        self.date_edit.setDisplayFormat("dd-MM-yyyy HH:mm")
        date_layout.addRow(QLabel("Start Time:"), self.date_edit)

        parent_layout.addWidget(date_group)

    def _build_action_buttons(self, parent_layout):
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_send = QPushButton("Send Email")
        self.btn_submit = QPushButton("Submit")
        self.btn_next = QPushButton("Next")

        self.btn_send.setMinimumWidth(120)
        self.btn_submit.setMinimumWidth(120)
        self.btn_next.setMinimumWidth(180)

        self.btn_send.clicked.connect(self._on_send)
        self.btn_submit.clicked.connect(self._on_submit)
        self.btn_next.clicked.connect(self._on_next)

        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_send)
        btn_layout.addWidget(self.btn_submit)
        btn_layout.addWidget(self.btn_next)

        parent_layout.addStretch()
        parent_layout.addLayout(btn_layout)

    def _on_send(self):
        QMessageBox.information(self, "Send", "Email action triggered.")

    def _on_submit(self):
        QMessageBox.information(self, "Submit", "Submit action triggered.")

    def _on_next(self):
        QMessageBox.information(self, "Next", "Next action triggered.")
