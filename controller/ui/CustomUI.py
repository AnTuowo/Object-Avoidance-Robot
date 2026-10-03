from PyQt5.QtWidgets import (
    QLayout, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QPushButton, QCheckBox,
    QGroupBox, QButtonGroup, QFrame
)
from PyQt5.QtCore import QProcess
from PyQt5.QtGui import QDoubleValidator
from typing import Type, Union





def initLayout( *args: any,
                layout_class: Type[QLayout] = QHBoxLayout, 
                parent_widget = None
                ):
    container_layout = layout_class(parent_widget)
    for ele in args:
        if isinstance(ele, QLayout):
            container_layout.addLayout(ele)
        elif isinstance(ele, QWidget):
            container_layout.addWidget(ele)
        else:
            container_layout.addWidget(QLabel(str(ele)))
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