import sys
from pathlib import Path
from .PosePane import PosePane
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QScrollArea, QGroupBox, QButtonGroup, QFrame,
    QMessageBox
)
from PyQt5.QtCore import pyqtSignal, QObject, QProcess
from PyQt5.QtGui import QDoubleValidator
from .CoordinateConversion import *
from .ProcessManager import *



class NavigationPane(QFrame):
    def __init__(self, control_script_path: Path):
        super().__init__()
        self.init_ui()
        self.control_script_path = str(control_script_path)
        self.process = QProcess()

    def init_ui(self):
        self_layout = QVBoxLayout(self)
        # Pose system Selector Checkbox
        unit_layout = QHBoxLayout()
        self.chk_unity = QCheckBox("Unity")
        self.chk_ros = QCheckBox("Ros")
        angle_option = QButtonGroup(self)
        angle_option.setExclusive(True)
        angle_option.addButton(self.chk_ros)
        angle_option.addButton(self.chk_unity)
        self.chk_ros.setChecked(True)
        unit_layout.addWidget(QLabel("Pos System: "))
        unit_layout.addWidget(self.chk_ros)
        unit_layout.addWidget(self.chk_unity)
        self_layout.addLayout(unit_layout)

        # Input Group Box
        input_group = QGroupBox("Target Navigation")
        input_group_layout = QVBoxLayout(input_group)
        
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)

        # X Input
        layout_x = QHBoxLayout()
        layout_x.addWidget(QLabel("X: "))
        self.input_x = QLineEdit()
        self.input_x.setPlaceholderText("Enter float...")
        self.input_x.setValidator(validator)
        self.input_x.textChanged.connect(self.validate_inputs)
        layout_x.addWidget(self.input_x)
        input_group_layout.addLayout(layout_x)

        # Y Input
        layout_y_z = QHBoxLayout()
        layout_y_z.addWidget(QLabel("Y(Ros) / Z(Unity): "))
        self.input_y_z = QLineEdit()
        self.input_y_z.setPlaceholderText("Enter float...")
        self.input_y_z.setValidator(validator)
        self.input_y_z.textChanged.connect(self.validate_inputs)
        layout_y_z.addWidget(self.input_y_z)
        input_group_layout.addLayout(layout_y_z)


        # Start Button
        button_group = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.on_start_clicked)
        button_group.addWidget(self.btn_start)

        # Cancel Button
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.hide()
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)
        button_group.addWidget(self.btn_cancel)

        # Status
        self.status_icon = StatusLabel()
        button_group.addWidget(self.status_icon)

        input_group_layout.addLayout(button_group)
        self_layout.addWidget(input_group)

    def validate_inputs(self):
        txt_x = self.input_x.text().strip()
        txt_y = self.input_y_z.text().strip()

        if not txt_x or not txt_y:
            self.btn_start.setEnabled(False)
            return

        try:
            float(txt_x)
            float(txt_y)
            self.btn_start.setEnabled(True)
        except ValueError:
            self.btn_start.setEnabled(False)

    def on_start_clicked(self):
        if self.btn_start.text() == "Start":
            val_x = float(self.input_x.text().strip())
            val_y = float(self.input_y_z.text().strip())

            if self.chk_unity.isChecked():
                val_x, val_y, _, _ = unity_to_ros(val_x, None, val_y, None)

            self.on_process_start()
            print(f"Executing script with target ROS parameters -> X: {val_x}, Y: {val_y}")
            self.process = QProcess(self)
            self.process.finished.connect(self.on_process_finish)
            self.process.start("python3", [self.control_script_path, str(val_x), str(val_y)])

            self.btn_cancel.show()
        elif self.btn_start.text() == "Pause":
            pause_process(self.process)
            self.btn_start.setText("Resume")
        elif self.btn_start.text() == "Resume":
            resume_process(self.process)
            self.btn_start.setText("Pause")
        


    def on_process_start(self):
        self.status_icon.running_state()
        self.btn_start.setText("Pause")
    def on_process_finish(self):
        self.status_icon.success_state()
        self.btn_start.setText("Start")
        self.btn_cancel.hide()


    def on_cancel_clicked(self):
        self.btn_cancel.hide()
        cancel_process(self.process)
        







class StatusLabel(QPushButton):
    def __init__(self):
        super().__init__()
        self.hide()
        self.clicked.connect(self.hide)
        self.style_format_str = """
            QPushButton {
                background-color: %s;
                color: %s;
                border: 2px solid %s;
                border-radius: 50px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: gainsboro;
            }
        """
    def running_state(self):
        self.show()
        self.setEnabled(False)
        self.setText("Running")
        self.setStyleSheet(self.style_format_str % ("LemonChiffon", "Gold", "Gold"))
    def success_state(self):
        self.show()
        self.setEnabled(True)
        self.setText("Done  [x]")
        self.setStyleSheet(self.style_format_str % ("HoneyDew", "SpringGreen", "SpringGreen"))
    def fail_state(self):
        self.show()
        self.setEnabled(True)
        self.setText("Failed  [x]")
        self.setStyleSheet(self.style_format_str % ("LightPink", "Red", "Red"))