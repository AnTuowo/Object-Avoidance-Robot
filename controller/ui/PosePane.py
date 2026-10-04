import math
from .CoordinateConversion import *
from .CustomUI import *

from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, 
    QCheckBox, QFrame
)


class PosePane(QFrame):

    def __init__(self):
        super().__init__()

        self.init_fields()
        self.configure_fields()
        self.lay_layout()


    # -------------------- INIT CONFIGURATION -------------------- 
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

        


    # -------------------- ODOM DISPLAY METHODS --------------------
    def update_odom_display(self, x=None, y=None, z=None, ros_yaw_rad=None):
        if x is None or y is None or z is None or ros_yaw_rad is None:
            self.label_ros_coords.setText("ROS (x, y, z | yaw): N/A")
            self.label_unity_coords.setText("Unity (x, y, z | yaw): N/A")
        else:
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