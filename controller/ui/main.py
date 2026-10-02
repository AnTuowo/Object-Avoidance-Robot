#!/usr/bin/env python3
import sys
from pathlib import Path
import subprocess
from .CoordinatePane import CoordinatePane
from .NavigatePane import StatusLabel

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, 
    QScrollArea, QGroupBox
)
from PyQt5.QtCore import pyqtSignal, QObject, QProcess, Qt
from PyQt5.QtGui import QDoubleValidator


# ------- EXECUTION DIR -------
THIS_FILE_DIR = Path(__file__).resolve().parent
REPO_DIR = THIS_FILE_DIR.parent.parent
ROS_SETUP_PATH = REPO_DIR / "catkin_ws" / "devel" / "setup.bash"
CONTROL_ROBOT_PATH = REPO_DIR / "catkin_ws" / "src" / "ros_packages" / "unity_robotics_demo" / "scripts" / "milestone1_controller.py"



# -------
# Signals must be defined on an object inheriting from QObject
class RosBridgeSignals(QObject):
    # Sends: pos_x, pos_y, pos_z, ros_yaw (radians)
    odom_received = pyqtSignal(float, float, float, float)


class RobotControllerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.process = None

    def init_ui(self):
        self.setWindowTitle("Robot Controller")
        self.resize(450, 600)

        main_layout = QVBoxLayout(self)

        # =====================================================================
        # 1. TOP FIXED SECTION: Display & System Selectors
        # =====================================================================
        top_frame = CoordinatePane()
        main_layout.addWidget(top_frame)

        # =====================================================================
        # 2. SCROLLABLE MIDDLE SECTION: Inputs & Controls
        # =====================================================================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

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
        layout_y = QHBoxLayout()
        layout_y.addWidget(QLabel("Y: "))
        self.input_y = QLineEdit()
        self.input_y.setPlaceholderText("Enter float...")
        self.input_y.setValidator(validator)
        self.input_y.textChanged.connect(self.validate_inputs)
        layout_y.addWidget(self.input_y)
        input_group_layout.addLayout(layout_y)

        # Start Button
        button_group = QHBoxLayout()
        self.btn_start = QPushButton("Start")
        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.on_start_clicked)
        button_group.addWidget(self.btn_start)

        # Status
        self.status_icon = StatusLabel()
        button_group.addWidget(self.status_icon)

        input_group_layout.addLayout(button_group)


        scroll_layout.addWidget(input_group)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)



    # =========================================================================
    # Validation & Actions
    # =========================================================================
    def validate_inputs(self):
        txt_x = self.input_x.text().strip()
        txt_y = self.input_y.text().strip()

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
        val_x = float(self.input_x.text().strip())
        val_y = float(self.input_y.text().strip())

        self.on_process_start()
        print(f"Executing script with target parameters -> X: {val_x}, Y: {val_y}")
        self.process = QProcess(self)
        self.process.finished.connect(self.on_process_finish)
        self.process.start("python3", [str(CONTROL_ROBOT_PATH), str(val_x), str(val_y)])
        #subprocess.Popen(["python3", CONTROL_ROBOT_PATH, str(val_x), str(val_y)])


    def on_process_start(self):
        self.status_icon.running_state()
        self.btn_start.setEnabled(False)
    def on_process_finish(self):
        self.status_icon.success_state()
        self.btn_start.setEnabled(True)


        





if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotControllerUI()
    window.show()

    sys.exit(app.exec_())