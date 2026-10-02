import math
import rospy
from nav_msgs.msg import Odometry
from .CoordinateConversion import *

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, 
    QCheckBox, QFrame, QButtonGroup
)
from PyQt5.QtCore import pyqtSignal, QObject

# Signals must be defined on an object inheriting from QObject
class RosBridgeSignals(QObject):
    # Sends: pos_x, pos_y, pos_z, ros_yaw (radians)
    odom_received = pyqtSignal(float, float, float, float)


class CoordinatePane(QFrame):
    def __init__(self):
        super().__init__()
        # self.current_ros_pose = (None, None, None, None) # x, y, z, yaw
        self.signals = RosBridgeSignals()
        self.signals.odom_received.connect(self.update_odom_display)

        self.init_ui()
        self.init_ros()


    def init_ros(self):
        rospy.init_node("robot_controller_gui", anonymous=True, disable_signals=True)
        rospy.Subscriber("/odom", Odometry, self.odom_callback)

    def init_ui(self):
        top_layout = QVBoxLayout(self)

        # Coordinate System Selector Checkboxes
        coor_sys_layout = QHBoxLayout()
        self.chk_ros = QCheckBox("ROS Coordinates")
        self.chk_unity = QCheckBox("Unity Coordinates")
        self.chk_ros.setChecked(True)
        self.chk_unity.setChecked(True)

        coor_sys_layout.addWidget(QLabel("Coordinate System: "))
        coor_sys_layout.addWidget(self.chk_ros)
        coor_sys_layout.addWidget(self.chk_unity)


        # Unit Selector Checkbox
        unit_layout = QHBoxLayout()
        self.chk_rad = QCheckBox("Rad")
        self.chk_deg = QCheckBox("Degree")
        self.angle_option = QButtonGroup(self)
        self.angle_option.setExclusive(True)
        self.angle_option.addButton(self.chk_deg)
        self.angle_option.addButton(self.chk_rad)
        self.chk_deg.setChecked(True)

        unit_layout.addWidget(QLabel("Angle unit: "))
        unit_layout.addWidget(self.chk_deg)
        unit_layout.addWidget(self.chk_rad)


        top_layout.addLayout(coor_sys_layout)
        top_layout.addLayout(unit_layout)

        # self.chk_ros.stateChanged.connect(self.update_odom_display)
        # self.chk_unity.stateChanged.connect(self.update_odom_display)

        # Labels for Position and Yaw Display
        self.lbl_ros_coords = QLabel("ROS (x, y, z | yaw): N/A")
        self.lbl_unity_coords = QLabel("Unity (x, y, z | yaw): N/A")

        top_layout.addWidget(self.lbl_ros_coords)
        top_layout.addWidget(self.lbl_unity_coords)






    def odom_callback(self, msg):
        pos = msg.pose.pose.position
        ori = msg.pose.pose.orientation

        ros_yaw_rad = yaw_from_quat(x=ori.x, y=ori.y, z=ori.z, w=ori.w)

        # Safely send parameters across threads via Qt Signal
        self.signals.odom_received.emit(pos.x, pos.y, pos.z, ros_yaw_rad)


    def update_odom_display(self, x=None, y=None, z=None, ros_yaw_rad=None):
        # print(f"x: {x}, y: {y}, z: {z}, yaw: {ros_yaw_rad}")
        if x is None or y is None or z is None or ros_yaw_rad is None:
            self.lbl_ros_coords.setText("ROS (x, y, z | yaw): N/A")
            self.lbl_unity_coords.setText("Unity (x, y, z | yaw): N/A")
        else:
            if self.chk_deg.isChecked():
                ros_yaw_rad = math.degrees(ros_yaw_rad)
            # self.current_ros_pose = (x, y, z, ros_yaw_rad)
            # rx, ry, rz, ryaw = self.current_ros_pose
            rx, ry, rz, ryaw = (x, y, z, ros_yaw_rad)
            self.lbl_ros_coords.setText(
                    f"ROS (x, y, z, yaw): ({rx:.2f}, {ry:.2f}, {rz:.2f})\n" 
                    f"\tYaw (Z-Rot): {ryaw:.1f})"
                )
            ux, uy, uz, uyaw = ros_to_unity(x, y, z, ros_yaw_rad)
            self.lbl_unity_coords.setText(
                    f"Unity (x, y, z): ({ux:.2f}, {uy:.2f}, {uz:.2f})\n"
                    f"\tYaw (Y-Rot): {uyaw:.1f}"
                )

        # 1. Display ROS Coordinates and Yaw (Radians + Degrees)
        if self.chk_ros.isChecked():
            self.lbl_ros_coords.show()
        else:
            self.lbl_ros_coords.hide()

        # 2. Display Unity Coordinates and Yaw (Euler Degrees [0, 360))
        if self.chk_unity.isChecked():
            
            self.lbl_unity_coords.show()
        else:
            self.lbl_unity_coords.hide()