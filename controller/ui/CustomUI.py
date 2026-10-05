from PyQt5.QtWidgets import (
    QLayout, QWidget, QHBoxLayout, 
    QLabel, QPushButton, QCheckBox,
    QButtonGroup, QMessageBox
)
from typing import Type, Union
import subprocess





def initLayout( *args: any,
                layout_class: Type[QLayout] = QHBoxLayout, 
                parent_widget = None,
                stretch_factor: tuple = None
                ):
    container_layout = layout_class(parent_widget)
    for ele in args:
        if isinstance(ele, QLayout):
            container_layout.addLayout(ele)
        elif isinstance(ele, QWidget):
            container_layout.addWidget(ele)
        else:
            container_layout.addWidget(QLabel(str(ele)))
    if stretch_factor is not None and len(stretch_factor) == len(args):
        for i in range(0, len(stretch_factor), 1):
            container_layout.setStretch(i, stretch_factor[i])
    return container_layout
                

class CheckBoxGroup(QButtonGroup):
    def __init__(self, 
                 *args: Union[QCheckBox, str],
                 exclusive: bool = True,
                 parent_widget = None
                 ):
        super().__init__(parent_widget)
        self.setExclusive(exclusive)
        for ele in args:
            if isinstance(ele, str): 
                ele = QCheckBox(ele)
            self.addButton(ele)



class StatusLabel(QPushButton):
    def __init__(self):
        super().__init__()
        self.hide()
        self.clicked.connect(self.hide)
        self.style_format_str = """
            QPushButton {
                background-color: %s;
                color: %s;
                border: 2px solid %s;
                border-radius: 50px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: gainsboro;
            }
        """
    def set_state(self, 
                  text: str = "", 
                  bg_color: str = "white",
                  txt_border_cl: str = "black",
                  enable: bool = True):
        self.show()
        self.setEnabled(enable)
        self.setText(text)
        self.setStyleSheet(self.style_format_str % (bg_color, txt_border_cl, txt_border_cl))
    def running_state(self):
        self.set_state("Running", "LemonChiffon", "Gold", False)
    def success_state(self):
        self.set_state("Done  [x]", "HoneyDew", "SpringGreen")
    def fail_state(self):
        self.set_state("Failed  [x]", "LightPink", "Red")






def ros_launch_msg_box(program_name: str,
                       ros_setup_path: str,
                       argument: str) -> subprocess.Popen:
    reply = QMessageBox.question(
        None,
        f"Start {program_name}",
        f"Do you want to start the {program_name}?",
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes
    )

    if reply == QMessageBox.Yes:
        command = f"""
                source {str(ros_setup_path)}
                {argument}
            """

        return subprocess.Popen([
            "gnome-terminal",
            "--disable-factory",  # Keeps process attached to Python
            "--",
            "bash",
            "-c",
            command
        ])