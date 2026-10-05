#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path
import signal

import rospy
from nav_msgs.msg import Odometry

from .PosePane import PosePane
from .NavigatePane import NavigationPane
from .LauncherPane import LauncherPane
from .CoordinateConversion import *
from .CustomUI import *

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QFrame, QPushButton
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
    ODOM_TIMEOUT_MS = 500  # 500 ms

    def __init__(self):
        super().__init__()
        self.signals = RosBridgeSignals()
        self.process = None
        self.robot_connected = False

        # Timer used to detect loss of /odom messages
        self.odom_timeout_timer = QTimer(self)
        self.odom_timeout_timer.setSingleShot(True)
        self.odom_timeout_timer.timeout.connect(self.odom_timeout)

        self.init_ros()
        self.init_ui()
        self.signals.odom_received.connect(self.on_odom_arrive)


    # ------------------ UI SECTION ------------------
    def init_ui(self):
        self.setWindowTitle("Robot Controller")
        self.resize(450, 600)

        self.launcher_frame = LauncherPane(ROS_SETUP_PATH)
        self.launcher_frame.setFrameShape(QFrame.Box)
        self.launcher_frame.setFrameShadow(QFrame.Raised)
        self.launcher_frame.setLineWidth(2)

        self.pose_frame = PosePane()
        self.pose_frame.setFrameShape(QFrame.Box)
        self.pose_frame.setFrameShadow(QFrame.Raised)
        self.pose_frame.setLineWidth(2)

        self.navigate_frame = NavigationPane(control_script_path=CONTROL_ROBOT_PATH)
        self.navigate_frame.setFrameShape(QFrame.Box)
        self.navigate_frame.setFrameShadow(QFrame.Raised)
        self.navigate_frame.setLineWidth(2)

        initLayout(self.launcher_frame,
                   self.pose_frame,
                   self.navigate_frame,
                   layout_class=QVBoxLayout,
                   stretch_factor=(0, 0, 1),
                   parent_widget=self)


    # ------------------ ROS SECTION ------------------
    def init_ros(self):
        rospy.init_node("robot_controller_gui", anonymous=True, disable_signals=True)
        rospy.Subscriber("/odom", Odometry, self.odom_callback)

    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        ori = msg.pose.pose.orientation

        ros_yaw_rad = yaw_from_quat(x=ori.x, y=ori.y, z=ori.z, w=ori.w)
        # Safely send parameters across threads via Qt Signal
        self.signals.odom_received.emit(pos.x, pos.y, pos.z, ros_yaw_rad)

    def on_odom_arrive(self, x, y, z, ros_yaw_rad):
        self.pose_frame.update_odom_display(x, y, z, ros_yaw_rad)
        self.navigate_frame.update_dist_err(x, y, ros_yaw_rad)
        if self.navigate_frame.robot_connected is not True:
            self.navigate_frame.state_toggle()

        self.odom_timeout_timer.start(self.ODOM_TIMEOUT_MS)

    def odom_timeout(self):
        self.pose_frame.update_odom_display()
        self.navigate_frame.state_toggle()


        


if __name__ == "__main__":
    # 1. Allow Python to exit on SIGINT
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    
    # 2. Add a periodic timer to wake up Python's interpreter
    timer = QTimer()
    timer.start(500)  # Fires every 500ms
    timer.timeout.connect(lambda: None)  # Dummy callback keeps Python responsive to signal

    p = ros_launch_msg_box("ROS TCP Endpoint", ROS_SETUP_PATH, 
                       "roslaunch ros_tcp_endpoint endpoint.launch")
    time.sleep(1.2)
    def cleanup():
        # Ensure process exists and has a valid PID before signaling
            if 'p' in globals() and p is not None and p.poll() is None:
                try:
                    os.killpg(os.getpgid(p.pid), signal.SIGINT)
                except (ProcessLookupError, OSError):
                    pass
    app.aboutToQuit.connect(cleanup)

    window = RobotControllerUI()
    window.show()

    sys.exit(app.exec_())