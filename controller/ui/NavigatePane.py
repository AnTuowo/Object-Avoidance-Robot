from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

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
    def running_state(self):
        self.show()
        self.setEnabled(False)
        self.setText("Running")
        self.setStyleSheet(self.style_format_str % ("LemonChiffon", "Gold", "Gold"))
    def success_state(self):
        self.show()
        self.setEnabled(True)
        self.setText("Done  [x]")
        self.setStyleSheet(self.style_format_str % ("HoneyDew", "SpringGreen", "SpringGreen"))
    def fail_state(self):
        self.show()
        self.setEnabled(True)
        self.setText("Failed  [x]")
        self.setStyleSheet(self.style_format_str % ("LightPink", "Red", "Red"))