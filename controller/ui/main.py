#!/usr/bin/env python3
import sys
from pathlib import Path
from .PosePane import PosePane
from .NavigatePane import NavigationPane
import subprocess

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QScrollArea, QGroupBox, QButtonGroup, QFrame,
    QMessageBox
)
from PyQt5.QtCore import pyqtSignal, QObject, QProcess
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
        pose_frame = PosePane()
        main_layout.addWidget(pose_frame)

        # =====================================================================
        # 2. SCROLLABLE MIDDLE SECTION: Inputs & Controls
        # =====================================================================
        navigate_frame = NavigationPane(CONTROL_ROBOT_PATH)
        main_layout.addWidget(navigate_frame)
    


def launch_ros_endpoint():
    reply = QMessageBox.question(
        None,
        "Start ROS TCP Endpoint",
        "Do you want to start the ROS TCP endpoint?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.No
    )

    if reply == QMessageBox.Yes:
        command = f"""
                source {str(ROS_SETUP_PATH)}
                roslaunch ros_tcp_endpoint endpoint.launch
            """

        subprocess.Popen([
            "gnome-terminal",
            "--",
            "bash",
            "-c",
            command
        ])


        





if __name__ == "__main__":
    app = QApplication(sys.argv)

    launch_ros_endpoint()

    window = RobotControllerUI()
    window.show()

    sys.exit(app.exec_())