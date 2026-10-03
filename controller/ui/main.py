#!/usr/bin/env python3
import sys
from pathlib import Path
import signal
import subprocess

from .PosePane import PosePane
from .NavigatePane import NavigationPane

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QMessageBox, QFrame
)
from PyQt5.QtCore import pyqtSignal, QObject,  QTimer


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

        pose_frame = PosePane()
        pose_frame.setFrameShape(QFrame.Box)
        pose_frame.setFrameShadow(QFrame.Raised)
        pose_frame.setLineWidth(2)
        main_layout.addWidget(pose_frame)

        navigate_frame = NavigationPane(CONTROL_ROBOT_PATH)
        navigate_frame.setFrameShape(QFrame.Box)
        navigate_frame.setFrameShadow(QFrame.Raised)
        navigate_frame.setLineWidth(2)
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
    # 1. Allow Python to exit on SIGINT
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    
    # 2. Add a periodic timer to wake up Python's interpreter
    timer = QTimer()
    timer.start(500)  # Fires every 500ms
    timer.timeout.connect(lambda: None)  # Dummy callback keeps Python responsive to signal

    launch_ros_endpoint()

    window = RobotControllerUI()
    window.show()

    sys.exit(app.exec_())