from pathlib import Path

from PyQt5.QtWidgets import (
    QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QGroupBox, QButtonGroup, QFrame
)
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QDoubleValidator

from .CoordinateConversion import *
from .ProcessManager import *
from .CustomUI import *



class NavigationPane(QFrame):
    def __init__(self, control_script_path: Path):
        super().__init__()
        self.control_script_path = str(control_script_path)

        self.init_fields()
        self.configure_fields()
        self.lay_layout()
        


    # -------------------- INIT CONFIGURATION -------------------- 
    def init_fields(self):
        self.process = QProcess()
        self.chk_unity = QCheckBox("Unity")
        self.chk_ros = QCheckBox("Ros") 
        self.input_x = QLineEdit()
        self.input_y_z = QLineEdit()
        self.btn_start = QPushButton("Start")
        self.btn_cancel = QPushButton("Cancel")
        self.status_icon = StatusLabel()

    def configure_fields(self):
        self.process.finished.connect(self.on_process_finish)

        self.chk_ros.setChecked(True)

        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)

        self.input_x.setPlaceholderText("Enter float...")
        self.input_x.setValidator(validator)
        self.input_x.textChanged.connect(self.validate_inputs)

        self.input_y_z.setPlaceholderText("Enter float...")
        self.input_y_z.setValidator(validator)
        self.input_y_z.textChanged.connect(self.validate_inputs)

        self.btn_start.setEnabled(False)
        self.btn_start.clicked.connect(self.on_start_clicked)
        self.btn_cancel.hide()
        self.btn_cancel.clicked.connect(self.on_cancel_clicked)

        CheckBoxGroup(self.chk_ros, self.chk_unity, parent_widget=self)


    def lay_layout(self):
        # Pose system Selector Checkbox
        unit_layout = initLayout("Pos System: ", self.chk_ros, self.chk_unity)
        
        # Input Group Box
        layout_x = initLayout("X: ", self.input_x)
        layout_y_z = initLayout("Y(Ros) / Z(Unity): ", self.input_y_z)
        button_group = initLayout(self.btn_start, self.btn_cancel, self.status_icon)

        input_group = QGroupBox("Target Navigation")
        initLayout(layout_x,
                   layout_y_z,
                   button_group,
                   layout_class=QVBoxLayout,
                   parent_widget=input_group)
        
        initLayout(unit_layout,
                   input_group,
                   layout_class=QVBoxLayout,
                   parent_widget=self)




    # -------------------- INTERNAL HELPER METHODS --------------------
    def validate_inputs(self):
        txt_x = self.input_x.text().strip()
        txt_y = self.input_y_z.text().strip()

        if not txt_x or not txt_y:
            self.btn_start.setEnabled(False)
            return
        self.btn_start.setEnabled(True)


    def on_start_clicked(self):
        if self.btn_start.text() == "Start":
            val_x = float(self.input_x.text().strip())
            val_y_z = float(self.input_y_z.text().strip())

            if self.chk_unity.isChecked():
                val_x, val_y_z, _, _ = unity_to_ros(val_x, None, val_y_z, None)

            self.on_process_start()
            print(f"Executing script with target ROS parameters -> X: {val_x}, Y: {val_y_z}")
            self.process.start("python3", [self.control_script_path, str(val_x), str(val_y_z)])

            self.btn_cancel.show()

        elif self.btn_start.text() == "Pause":
            pause_process(self.process)
            self.btn_start.setText("Resume")
        elif self.btn_start.text() == "Resume":
            resume_process(self.process)
            self.btn_start.setText("Pause")


    def on_cancel_clicked(self):
        self.btn_cancel.hide()
        cancel_process(self.process)
        


    def on_process_start(self):
        self.status_icon.running_state()
        self.btn_start.setText("Pause")

    def on_process_finish(self):
        self.status_icon.success_state()
        self.btn_start.setText("Start")
        self.btn_cancel.hide()
        







