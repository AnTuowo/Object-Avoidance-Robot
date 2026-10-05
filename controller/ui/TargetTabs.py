from __future__ import annotations
import sys
from PyQt5.QtWidgets import (
    QApplication, QTabWidget, QWidget, QVBoxLayout, 
    QLabel, QLineEdit, QPushButton, QScrollArea, 
    QDialog, QFrame
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag

from .CustomUI import *


ITEM_STRETCH_FACTOR = (1, 1, 0, 0)

class SingleTargetTab(QWidget):
    def __init__(self, 
                 on_valid_input: function = None, 
                 on_invalid_input: function = None,
                 parent=None):
        super().__init__(parent)
        self.on_valid = on_valid_input
        self.on_invalid = on_invalid_input
        
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)

        self.input_x = QLineEdit()
        self.input_x.setPlaceholderText("Enter float...")
        self.input_x.setValidator(validator)
        self.input_x.textChanged.connect(self.validate_inputs)

        self.input_y_z = QLineEdit()
        self.input_y_z.setPlaceholderText("Enter float...")
        self.input_y_z.setValidator(validator)
        self.input_y_z.textChanged.connect(self.validate_inputs)

        layout_x = initLayout("X: ", self.input_x, stretch_factor=(3, 7))
        layout_y_z = initLayout("Y(Ros) / Z(Unity): ", self.input_y_z, stretch_factor=(3, 7))
        initLayout(layout_x, layout_y_z, layout_class=QVBoxLayout, parent_widget=self)



    def get_inputs(self):
        """Returns a list with a single tuple [(x, y)] if valid, or empty list."""
        x = float(self.input_x.text().strip())
        y = float(self.input_y_z.text().strip())
        return [(x, y)]

    def update_on_input_valid_state(self):
        """Call on switch tab"""
        self.validate_inputs()

    def validate_inputs(self):
        txt_x = self.input_x.text().strip()
        txt_y = self.input_y_z.text().strip()

        if not txt_x or not txt_y:
            if self.on_invalid: 
                self.on_invalid()
            return
        if self.on_valid:
            self.on_valid()


class DraggableItemWidget(QFrame):
    """Widget representing a single input row inside the scroll area."""
    def __init__(self, x, y, parent_container):
        super().__init__(parent_container)
        self.x_val = x
        self.y_val = y
        self.parent_container = parent_container

        self.lbl_x = QLabel(str(x))
        self.lbl_y = QLabel(str(y))

        # Drag handle / Visual indicator
        self.handle = QLabel("☰")
        self.handle.setCursor(Qt.OpenHandCursor)
        # Remove button
        self.btn_remove = QPushButton("☒")
        self.btn_remove.setFixedWidth(30)
        self.btn_remove.setFlat(True)
        self.btn_remove.clicked.connect(self.remove_self)

        layout = initLayout(self.lbl_x, self.lbl_y, self.btn_remove, self.handle,  
                            stretch_factor=ITEM_STRETCH_FACTOR, parent_widget=self)
        layout.setContentsMargins(10, 5, 10, 5)
        self.setStyleSheet("background-color: #ffffff;")


    def remove_self(self):
        self.parent_container.remove_item(self)

    # --- Drag and Drop Implementation ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        drag = QDrag(self)
        mime_data = QMimeData()
        drag.setMimeData(mime_data)

        # Create a semi-transparent pixmap preview of the widget while dragging
        pixmap = self.grab()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        self.hide() # Hide during drag
        result = drag.exec_(Qt.MoveAction)
        self.show()

    def mouseDoubleClickEvent(self, event):
        dialog = AddTargetDialog(self, "Modify Target", "Modify")
        if dialog.exec_() == QDialog.Accepted:
            x, y = dialog.get_values()
            self.x_val = x
            self.y_val = y
            self.lbl_x.setText(str(x))
            self.lbl_y.setText(str(y))
        event.accept()


class AddTargetDialog(QDialog):
    """Blocking modal dialog to retrieve X and Y inputs."""
    def __init__(self, parent=None, title: str = "Add target", btn_text: str = "Add"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True) # Makes it blocking
        self.setFixedSize(400, 200)

        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)

        self.input_x = QLineEdit()
        self.input_x.setPlaceholderText("Enter float...")
        self.input_x.setValidator(validator)
        self.input_x.textChanged.connect(self.validate_inputs)

        self.input_y_z = QLineEdit()
        self.input_y_z.setPlaceholderText("Enter float...")
        self.input_y_z.setValidator(validator)
        self.input_y_z.textChanged.connect(self.validate_inputs)

        layout_x = initLayout("X: ", self.input_x, stretch_factor=(3, 7))
        layout_y_z = initLayout("Y(Ros) / Z(Unity): ", self.input_y_z, stretch_factor=(3, 7))

        self.btn_add = QPushButton(btn_text)
        self.btn_add.clicked.connect(self.accept)
        self.btn_add.setEnabled(False)

        initLayout(layout_x,
                   layout_y_z,
                   self.btn_add,
                   layout_class=QVBoxLayout,
                   parent_widget=self)

    def get_values(self):
        return self.input_x.text().strip(), self.input_y_z.text().strip()

    def validate_inputs(self):
        txt_x = self.input_x.text().strip()
        txt_y = self.input_y_z.text().strip()

        if not txt_x or not txt_y:
            self.btn_add.setEnabled(False)
            return
        self.btn_add.setEnabled(True)


class MultipleTargetTab(QWidget):
    def __init__(self, 
                 on_valid_input: function = None, 
                 on_invalid_input: function = None,
                 parent=None):
        super().__init__(parent)
        self.on_valid = on_valid_input
        self.on_invalid = on_invalid_input
        self.items = []

        self.setStyleSheet("""
            MultipleTargetTab {
                background-color: snow;
                border: 5px solid slategrey;
                border-radius: 10px;
            }
        """)

        # 1. Header Bar (Column Headers)
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #e0e0e0; font-weight: bold;")
        header_layout = initLayout("X Value", "Y Value", "  ", "\t", 
                                   parent_widget=header_frame, stretch_factor=(1,1,0,0))


        # 2. Scroll Pane (Vertical only)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Disable left/right scrolling
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container inside Scroll Area
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setAlignment(Qt.AlignTop)  # <--- Keeps items pushed to the top
        
        # Enable Drag & Drop target behavior on container layout
        self.container_widget.setAcceptDrops(True)
        self.container_widget.dragEnterEvent = self.dragEnterEvent
        self.container_widget.dragMoveEvent = self.dragMoveEvent
        self.container_widget.dropEvent = self.dropEvent

        self.scroll_area.setWidget(self.container_widget)
        

        # 3. Add Target Button
        self.btn_add_target = QPushButton("Add Target")
        self.btn_add_target.clicked.connect(self.open_add_dialog)

        main_layout = initLayout(header_frame, self.scroll_area, self.btn_add_target, 
                                 layout_class=QVBoxLayout, parent_widget=self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        

    def open_add_dialog(self):
        dialog = AddTargetDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            x, y = dialog.get_values()
            self.add_item(x, y)

    def add_item(self, x, y):
        item = DraggableItemWidget(x, y, self)
        self.items.append(item)
        self.update_on_input_valid_state()
        self.container_layout.addWidget(item)

    def remove_item(self, item_widget):
        if item_widget in self.items:
            self.items.remove(item_widget)
            self.update_on_input_valid_state()
            self.container_layout.removeWidget(item_widget)
            item_widget.deleteLater()

    # --- Reordering via Drag and Drop ---
    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        source = event.source() # The DraggableItemWidget being dragged
        if isinstance(source, DraggableItemWidget):
            # Calculate target insert index based on vertical mouse position
            drop_pos = event.pos()
            new_index = 0
            for i in range(self.container_layout.count()):
                widget = self.container_layout.itemAt(i).widget()
                if widget:
                    # Use geometry() to safely calculate vertical mid-point
                    widget_rect = widget.geometry()
                    widget_mid_y = widget_rect.y() + (widget_rect.height() // 2)
                    
                    if drop_pos.y() > widget_mid_y:
                        new_index = i + 1

            # Reorder in list and layout
            self.container_layout.removeWidget(source)
            if source in self.items:
                self.items.remove(source)

            new_index = min(new_index, len(self.items))
            self.items.insert(new_index, source)
            self.container_layout.insertWidget(new_index, source)

            event.acceptProposedAction()

    def center_and_highlight(self, index):
        """Scrolls to the target input object by index and highlights it."""
        if 0 <= index < len(self.items):
            item = self.items[index]
            
            # Ensure scrolling completes to center the item
            total_height = self.scroll_area.height()
            item_height = total_height / len(self.items)
            target_position = (
                round(total_height - item_height * (index + 0.5))
            )
            self.scroll_area.ensureWidgetVisible(item, 0, target_position)

            # Highlight effect (Flash yellow)
            item.setStyleSheet("""
                DraggableItemWidget {
                    background-color: #fff9c4;
                    border: 8px solid #fbc02d;
                    border-radius: 4px;
                }
            """)

    def unhighlight(self, index):
        """Un-highlight an input object by index."""
        if 0 <= index < len(self.items):
            item = self.items[index]
            item.setStyleSheet("background-color: #ffffff;")

    def get_inputs(self):
        """Returns list of tuples [(x1, y1), (x2, y2), ...] matching active order."""
        return [(float(item.x_val), float(item.y_val)) for item in self.items]

    def update_on_input_valid_state(self):
        if len(self.items) == 0:
            if self.on_invalid: self.on_invalid()
        else:
            if self.on_valid: self.on_valid()


class TargetTabs(QTabWidget):
    def __init__(self, 
                 tab_on_valid: function = None, 
                 tab_on_invalid: function = None):
        super().__init__()

        self.setMovable(True)

        self.single_target_tab = SingleTargetTab(tab_on_valid, tab_on_invalid)
        self.multi_target_tab = MultipleTargetTab(tab_on_valid, tab_on_invalid)

        self.addTab(self.single_target_tab, "Single Target")
        self.addTab(self.multi_target_tab, "Multiple Target")

        # Connect tab switching signal
        self.currentChanged.connect(self.on_tab_changed)

    def print_current_inputs(self):
        """Prints input tuples from currently selected tab."""
        current_widget = self.currentWidget()
        if hasattr(current_widget, "get_inputs"):
            inputs = current_widget.get_inputs()
            print(f"Inputs from Tab {self.currentIndex() + 1}: {inputs}")

    def get_current_tab_input_list(self):
        """Returns input tuples from currently selected tab."""
        current_widget = self.currentWidget()
        if hasattr(current_widget, "get_inputs"):
            return current_widget.get_inputs()

    def on_tab_changed(self):
        """Change state base on input validity every time switching tab."""
        current_widget = self.currentWidget()
        if hasattr(current_widget, "update_on_input_valid_state"):
            current_widget.update_on_input_valid_state()

    def is_multi_target_tab_active(self):
        return self.currentWidget() == self.multi_target_tab  # The "Multiple Target" tab




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = QWidget()

    tabs = TargetTabs()
    
    btn_print = QPushButton("Get Inputs (Active Tab)")
    btn_print.clicked.connect(tabs.print_current_inputs)

    initLayout(tabs,
               btn_print,
               layout_class=QVBoxLayout,
               parent_widget=main_window)



    
    # Pre-populating some items in Tab 2 for quick demonstration
    tabs.multi_target_tab.add_item("100", "200")
    tabs.multi_target_tab.add_item("300", "400")
    tabs.multi_target_tab.add_item("500", "600")

    main_window.show()
    sys.exit(app.exec_())



