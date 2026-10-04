import sys
from pathlib import Path
import signal

import rospy
from nav_msgs.msg import Odometry

from .PosePane import PosePane
from .NavigatePane import NavigationPane

from .CoordinateConversion import *
from .CustomUI import *

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QFrame, QPushButton
)
from PyQt5.QtCore import pyqtSignal, QObject,  QTimer



class LauncherPane(QFrame):
    def __init__(self, ros_setup_path: Path):
        super().__init__()
        self.ROS_SETUP_PATH = ros_setup_path

        self.cmd_vel = QPushButton("Inspect /cmd_vel")
        self.cmd_vel_p = None
        self.configure_button()

        initLayout("Launcher: ",
                   self.cmd_vel,
                   parent_widget=self)

    def configure_button(self):
        self.cmd_vel.clicked.connect(self.launch_cmd_vel)

    def launch_cmd_vel(self):
        ros_launch_msg_box(self.cmd_vel.text(), self.ROS_SETUP_PATH,
                           "rostopic echo /cmd_vel")
