from pathlib import Path

from PyQt5.QtWidgets import (
    QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox,
    QGroupBox, QFrame
)
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QDoubleValidator

from .TargetTabs import *

from .CoordinateConversion import *
from .ProcessManager import *
from .CustomUI import *



class NavigationPane(QFrame):
    def __init__(self, control_script_path: Path):
        super().__init__()
        self.control_script_path = str(control_script_path)
        self.process_manager = ProcessManager(self.before_each_process, self.on_all_process_finish)

        self.init_fields()
        self.configure_fields()
        self.lay_layout()
        


    # -------------------- INIT CONFIGURATION -------------------- 
    def init_fields(self):
        self.chk_unity = QCheckBox("Unity")
        self.chk_ros = QCheckBox("Ros") 
        # self.input_x = QLineEdit()
        # self.input_y_z = QLineEdit()
        self.tabs = TargetTabs(
            tab_on_valid=self.on_valid_input_state, 
            tab_on_invalid=self.on_invalid_input_state
        )
        self.btn_start = QPushButton("Start")
        self.btn_cancel = QPushButton("Cancel")
        self.status_icon = StatusLabel()

        self.dist_angle_err_label = QLabel()
        self.robot_connected = False
        self.target_pose = (None, None)
        self.targets = []

    def configure_fields(self):
        self.chk_ros.setChecked(True)

        # validator = QDoubleValidator()
        # validator.setNotation(QDoubleValidator.StandardNotation)

        # self.input_x.setPlaceholderText("Enter float...")
        # self.input_x.setValidator(validator)
        # self.input_x.textChanged.connect(self.validate_inputs)

        # self.input_y_z.setPlaceholderText("Enter float...")
        # self.input_y_z.setValidator(validator)
        # self.input_y_z.textChanged.connect(self.validate_inputs)

        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_cancel.hide()
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)

        CheckBoxGroup(self.chk_ros, self.chk_unity, parent_widget=self)


    def lay_layout(self):
        # Pose system Selector Checkbox
        unit_layout = initLayout("Pos System: ", self.chk_ros, self.chk_unity)
        
        # Input Group Box
        # layout_x = initLayout("X: ", self.input_x, stretch_factor=(3, 7))
        # layout_y_z = initLayout("Y(Ros) / Z(Unity): ", self.input_y_z, stretch_factor=(3, 7))
        button_group = initLayout(self.btn_start, self.btn_cancel, self.status_icon)

        input_group = QGroupBox("Target Navigation")
        # initLayout(layout_x,
        #            layout_y_z,
        #            button_group,
        #            layout_class=QVBoxLayout,
        #            parent_widget=input_group)

        initLayout(self.tabs,
                   button_group,
                   layout_class=QVBoxLayout,
                   parent_widget=input_group)

        initLayout(unit_layout,
                   self.dist_angle_err_label,
                   input_group,
                   layout_class=QVBoxLayout,
                   stretch_factor=(0, 0, 1),
                   parent_widget=self)




    # -------------------- INTERNAL HELPER METHODS --------------------
    # def validate_inputs(self):
    #     if self.robot_connected:
    #         txt_x = self.input_x.text().strip()
    #         txt_y = self.input_y_z.text().strip()

    #         if not txt_x or not txt_y:
    #             self.btn_start.setEnabled(False)
    #             return
    #         self.btn_start.setEnabled(True)


    def on_start_clicked(self):
        if self.btn_start.text() == "Start":
            # val_x = float(self.input_x.text().strip())
            # val_y_z = float(self.input_y_z.text().strip())

            # self.targets = [(val_x, val_y_z)]
            self.targets = self.tabs.get_current_tab_input_list()

            if self.chk_unity.isChecked():
                self.targets = [
                    unity_to_ros(x, None, y, None)[:2]
                    for x, y in self.targets
                ]

            self.process_manager.execute(
                                            [
                                                build_command_dict("python3", 
                                                                    self.control_script_path, 
                                                                    str(x), str(y)
                                                                    ) for x, y in self.targets
                                            ]
                                        )

            self.on_process_start()

        elif self.btn_start.text() == "Pause":
            self.process_manager.pause_current()
            self.btn_start.setText("Resume")
        elif self.btn_start.text() == "Resume":
            self.process_manager.resume_current()
            self.btn_start.setText("Pause")


    def on_cancel_clicked(self):
        self.btn_cancel.hide()
        self.process_manager.cancel_process()
        


    def on_process_start(self):
        self.tabs.setDisabled(True)
        self.status_icon.running_state()
        self.btn_start.setText("Pause")
        self.btn_cancel.show()
        self.dist_angle_err_label.show()

    def on_all_process_finish(self):
        if self.tabs.is_multi_target_tab_active():
            self.tabs.multi_target_tab.unhighlight(self.process_manager.current_index)
        self.tabs.setDisabled(False)

        if self.robot_connected:
            self.status_icon.success_state()
        else:
            self.status_icon.fail_state()
        self.btn_start.setText("Start")
        self.btn_cancel.hide()
        self.dist_angle_err_label.hide()
        self.target_pose = (None, None)


    def before_each_process(self):
        if self.tabs.is_multi_target_tab_active():
            self.tabs.multi_target_tab.unhighlight(self.process_manager.current_index - 1)
            self.tabs.multi_target_tab.center_and_highlight(self.process_manager.current_index)
        self.target_pose = self.targets[self.process_manager.current_index]
        print(f"Executing script with target ROS parameters -> X: {self.target_pose[0]}, Y: {self.target_pose[1]}")


        
    def state_toggle(self):
        self.robot_connected = not self.robot_connected
        
        self.btn_start.setEnabled(self.robot_connected)
        if self.robot_connected == False:
            self.btn_start.setText("Start")
            self.process_manager.cancel_process()

    def update_dist_err(self, x, y, yaw):
        val_x, val_y = self.target_pose  # Ros sys
        if val_x is not None and val_y is not None:
            dist, err = get_dist_angle_err(val_x, val_y, x, y, yaw)
            self.dist_angle_err_label.setText(
                f"Dist: {dist:.2f} m  |  Angle Error: {math.degrees(err):.1f}°"
                )


    def on_valid_input_state(self):
        self.btn_start.setEnabled(True)

    def on_invalid_input_state(self):
        self.btn_start.setEnabled(False)






