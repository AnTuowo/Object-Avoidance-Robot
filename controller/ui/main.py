#!/usr/bin/env python3
import sys
from pathlib import Path
import signal
import subprocess

import rospy
from nav_msgs.msg import Odometry

from .PosePane import PosePane
from .NavigatePane import NavigationPane
from .CoordinateConversion import *

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QMessageBox, QFrame, QAction
)
from PyQt5.QtCore import pyqtSignal, QObject,  QTimer


# ------- EXECUTION DIR -------
THIS_FILE_DIR = Path(__file__).resolve().parent
REPO_DIR = THIS_FILE_DIR.parent.parent
ROS_SETUP_PATH = REPO_DIR / "catkin_ws" / "devel" / "setup.bash"
CONTROL_ROBOT_PATH = REPO_DIR / "catkin_ws" / "src" / "ros_packages" / "unity_robotics_demo" / "scripts" / "milestone1_controller.py"
# /home/tranhuynh/Documents/WS26_Project_Robot_Avoidance/Object-Avoidance-Robot/catkin_ws/devel/setup.bash


# -------
# Signals must be defined on an object inheriting from QObject
class RosBridgeSignals(QObject):
    # Sends: pos_x, pos_y, pos_z, ros_yaw (radians)
    odom_received = pyqtSignal(float, float, float, float)


class RobotControllerUI(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = RosBridgeSignals()
        self.process = None

        self.init_ros()
        self.init_ui()
        self.signals.odom_received.connect(self.pose_frame.update_odom_display)

    def init_ui(self):
        self.setWindowTitle("Robot Controller")
        self.resize(450, 600)

        self.connection_state = QAction(checkable=True)
        self.connection_state.setChecked(False)
        print(f"Check state: {self.connection_state.isChecked()}")
        self.connection_state.toggled.connect(self.on_connect_state_change)

        main_layout = QVBoxLayout(self)

        self.pose_frame = PosePane(connection_state=self.connection_state)
        self.pose_frame.setFrameShape(QFrame.Box)
        self.pose_frame.setFrameShadow(QFrame.Raised)
        self.pose_frame.setLineWidth(2)
        main_layout.addWidget(self.pose_frame)

        self.navigate_frame = NavigationPane(connection_state=self.connection_state,
                                             control_script_path=CONTROL_ROBOT_PATH)
        self.navigate_frame.setFrameShape(QFrame.Box)
        self.navigate_frame.setFrameShadow(QFrame.Raised)
        self.navigate_frame.setLineWidth(2)
        main_layout.addWidget(self.navigate_frame)

    def init_ros(self):
        rospy.init_node("robot_controller_gui", anonymous=True, disable_signals=True)
        rospy.Subscriber("/odom", Odometry, self.odom_callback)

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        ori = msg.pose.pose.orientation

        ros_yaw_rad = yaw_from_quat(x=ori.x, y=ori.y, z=ori.z, w=ori.w)
        # Safely send parameters across threads via Qt Signal
        self.signals.odom_received.emit(pos.x, pos.y, pos.z, ros_yaw_rad)


    def on_connect_state_change(self):
        self.navigate_frame.btn_start.setEnabled(self.connection_state.isChecked())



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