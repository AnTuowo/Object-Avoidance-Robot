import math
import rospy
from nav_msgs.msg import Odometry
from .CoordinateConversion import *
from .CustomUI import *

from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, 
    QCheckBox, QFrame, QAction
)
from PyQt5.QtCore import pyqtSignal, QObject, QTimer

# # Signals must be defined on an object inheriting from QObject
# class RosBridgeSignals(QObject):
#     # Sends: pos_x, pos_y, pos_z, ros_yaw (radians)
#     odom_received = pyqtSignal(float, float, float, float)


class PosePane(QFrame):
    ODOM_TIMEOUT_MS = 500  # 500 ms

    def __init__(self, connection_state: QAction):
        super().__init__()
        # self.signals = RosBridgeSignals()
        # self.signals.odom_received.connect(self.update_odom_display)

        self.connection_state = connection_state

        self.init_fields()
        self.configure_fields()
        self.lay_layout()
        # self.init_ros()

        # Timer used to detect loss of /odom messages
        self.odom_timeout_timer = QTimer(self)
        self.odom_timeout_timer.setSingleShot(True)
        self.odom_timeout_timer.timeout.connect(self.odom_timeout)


    # -------------------- INIT CONFIGURATION -------------------- 
    # def init_ros(self):
    #     rospy.init_node("robot_controller_gui", anonymous=True, disable_signals=True)
    #     rospy.Subscriber("/odom", Odometry, self.odom_callback)

    def init_fields(self):
        self.check_ros = QCheckBox("ROS Coordinates")
        self.check_unity = QCheckBox("Unity Coordinates")
        self.chk_rad = QCheckBox("Rad")
        self.chk_deg = QCheckBox("Degree")
        # Labels for Position and Yaw Display
        self.label_ros_coords = QLabel("ROS (x, y, z | yaw): N/A")
        self.label_unity_coords = QLabel("Unity (x, y, z | yaw): N/A")

    def configure_fields(self):
        self.check_ros.setChecked(True)
        self.check_unity.setChecked(True)
        self.check_ros.toggled.connect(self.check_ros_state_change)
        self.check_unity.toggled.connect(self.check_unity_state_change)

        self.chk_deg.setChecked(True)

        # Exclusive check box group
        CheckBoxGroup(self.chk_deg, self.chk_rad, parent_widget=self)


    def lay_layout(self):
        # Pose system Selector Checkbox
        coor_sys_layout = initLayout("Coordinate System: ",
                                      self.check_ros,
                                      self.check_unity)

        # Unit Selector Checkbox
        unit_layout = initLayout("Angle unit: ",
                                  self.chk_deg,
                                  self.chk_rad)

        initLayout(coor_sys_layout,
                    unit_layout,
                    self.label_ros_coords,
                    self.label_unity_coords,
                    layout_class=QVBoxLayout,
                    parent_widget=self)





    # -------------------- ODOM RETRIEVER AND DISPLAY METHODS --------------------
    # def odom_callback(self, msg):
    #     pos = msg.pose.pose.position
    #     ori = msg.pose.pose.orientation

    #     ros_yaw_rad = yaw_from_quat(x=ori.x, y=ori.y, z=ori.z, w=ori.w)
    #     # Safely send parameters across threads via Qt Signal
    #     self.signals.odom_received.emit(pos.x, pos.y, pos.z, ros_yaw_rad)


    def update_odom_display(self, x=None, y=None, z=None, ros_yaw_rad=None):
        if x is None or y is None or z is None or ros_yaw_rad is None:
            self.label_ros_coords.setText("ROS (x, y, z | yaw): N/A")
            self.label_unity_coords.setText("Unity (x, y, z | yaw): N/A")
        else:
            # We received a valid /odom message, so restart the timeout countdown.
            self.odom_timeout_timer.start(self.ODOM_TIMEOUT_MS)
            if not self.connection_state.isChecked():
                self.connection_state.setChecked(True)

            if self.chk_deg.isChecked():
                ros_yaw_rad = math.degrees(ros_yaw_rad)

            self.label_ros_coords.setText(
                    f"ROS (x, y, z, yaw): ({x:.2f}, {y:.2f}, {z:.2f})\n" 
                    f"\tYaw (Z-Rot): {ros_yaw_rad:.1f})"
                )
            
            ux, uy, uz, uyaw = ros_to_unity(x, y, z, ros_yaw_rad)
            self.label_unity_coords.setText(
                    f"Unity (x, y, z): ({ux:.2f}, {uy:.2f}, {uz:.2f})\n"
                    f"\tYaw (Y-Rot): {uyaw:.1f}"
                )

    def odom_timeout(self):
        self.connection_state.setChecked(False)
        self.update_odom_display()
    


    # -------------------- CHECKBOX STATE CHANGE CONFIGURATION --------------------
    def check_ros_state_change(self):
        if self.check_ros.isChecked():
            self.label_ros_coords.show()
        else:
            self.label_ros_coords.hide()

    def check_unity_state_change(self):
        if self.check_unity.isChecked():
            self.label_unity_coords.show()
        else:
            self.label_unity_coords.hide()