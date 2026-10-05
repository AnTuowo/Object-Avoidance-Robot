import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, 
    QDialog, QFormLayout, QFrame, QMessageBox, QTabBar
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QPixmap, QColor

import time


# ----------------------------------------------------------------------
# TAB 1: Static Tab (Single Input: X and Y)
# ----------------------------------------------------------------------
class SingleTargetTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QFormLayout(self)
        
        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        
        layout.addRow("X:", self.x_input)
        layout.addRow("Y:", self.y_input)

    def get_inputs(self):
        """Returns a list with a single tuple [(x, y)] if valid, or empty list."""
        x = self.x_input.text().strip()
        y = self.y_input.text().strip()
        if x or y:
            return [(x, y)]
        return []


# ----------------------------------------------------------------------
# TAB 2 COMPONENTS: Draggable Item Widget & Add Target Dialog
# ----------------------------------------------------------------------
class DraggableItemWidget(QFrame):
    """Widget representing a single input row inside the scroll area."""
    def __init__(self, x, y, parent_container):
        super().__init__()
        self.x_val = x
        self.y_val = y
        self.parent_container = parent_container
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            DraggableItemWidget {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Drag handle / Visual indicator
        self.handle = QLabel("☰")
        self.handle.setCursor(Qt.OpenHandCursor)

        self.lbl_x = QLabel(str(self.x_val))
        self.lbl_y = QLabel(str(self.y_val))

        # Remove button
        self.btn_remove = QPushButton("☒")
        self.btn_remove.setFixedWidth(30)
        self.btn_remove.setFlat(True)
        self.btn_remove.clicked.connect(self.remove_self)

        layout.addWidget(self.handle)
        layout.addWidget(self.lbl_x, stretch=1)
        layout.addWidget(self.lbl_y, stretch=1)
        layout.addWidget(self.btn_remove)

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
        dialog = AddTargetDialog("Modify Target", self)
        if dialog.exec_() == QDialog.Accepted:
            x, y = dialog.get_values()
            self.x_val = x
            self.y_val = y
            self.lbl_x = x
            self.lbl_y = y
        event.accept()


class AddTargetDialog(QDialog):
    """Blocking modal dialog to retrieve X and Y inputs."""
    def __init__(self, title = "Add Target", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True) # Makes it blocking
        self.setFixedSize(400, 200)

        layout = QFormLayout(self)

        self.x_input = QLineEdit()
        self.y_input = QLineEdit()
        layout.addRow("X:", self.x_input)
        layout.addRow("Y:", self.y_input)

        self.btn_add = QPushButton("Add")
        self.btn_add.clicked.connect(self.accept)
        layout.addRow(self.btn_add)

    def get_values(self):
        return self.x_input.text().strip(), self.y_input_y_z.text().strip()


# ----------------------------------------------------------------------
# TAB 2: Dynamic Scroll Pane with Drag/Drop Reordering
# ----------------------------------------------------------------------
class MultipleTargetTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # 1. Header Bar (Column Headers)
        header_frame = QFrame()
        header_frame.setStyleSheet("background-color: #e0e0e0; font-weight: bold;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        lbl_drag = QLabel("")
        lbl_drag.setFixedWidth(20)
        lbl_x = QLabel("X Value")
        lbl_y = QLabel("Y Value")
        lbl_action = QLabel("Action")
        lbl_action.setFixedWidth(30)

        header_layout.addWidget(lbl_drag)
        header_layout.addWidget(lbl_x, stretch=1)
        header_layout.addWidget(lbl_y, stretch=1)
        header_layout.addWidget(lbl_action)
        main_layout.addWidget(header_frame)

        # 2. Scroll Pane (Vertical only)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) # Disable left/right scrolling
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container inside Scroll Area
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setAlignment(Qt.AlignTop)
        self.container_layout.setSpacing(5)
        
        # Enable Drag & Drop target behavior on container layout
        self.container_widget.setAcceptDrops(True)
        self.container_widget.dragEnterEvent = self.dragEnterEvent
        self.container_widget.dragMoveEvent = self.dragMoveEvent
        self.container_widget.dropEvent = self.dropEvent

        self.scroll_area.setWidget(self.container_widget)
        main_layout.addWidget(self.scroll_area)

        # 3. Add Target Button
        self.btn_add_target = QPushButton("Add Target")
        self.btn_add_target.clicked.connect(self.open_add_dialog)
        main_layout.addWidget(self.btn_add_target)

    def open_add_dialog(self):
        dialog = AddTargetDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            x, y = dialog.get_values()
            if x or y:
                self.add_item(x, y)

    def add_item(self, x, y):
        item = DraggableItemWidget(x, y, self)
        self.items.append(item)
        self.container_layout.addWidget(item)

    def remove_item(self, item_widget):
        if item_widget in self.items:
            self.items.remove(item_widget)
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
                    border: 2px solid #fbc02d;
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
        return [(item.x_val, item.y_val) for item in self.items]


# ----------------------------------------------------------------------
# MAIN APPLICATION WINDOW
# ----------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser-style Input Manager")
        self.resize(500, 500)

        # Central Setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)    #################

        # Tab Widget (Web-browser style setup)
        self.tabs = QTabWidget()
        self.tabs.setMovable(True)

        self.tab2 = SingleTargetTab()
        self.tab1 = MultipleTargetTab()

        self.tabs.addTab(self.tab1, "Static Input")
        self.tabs.addTab(self.tab2, "Target List")

        main_layout.addWidget(self.tabs)             ###############

        # Demonstration / Control Panel at bottom
        demo_panel = QHBoxLayout()
        
        self.btn_toggle_lock = QPushButton("Disable Interaction & Switch Tab")
        self.btn_toggle_lock.setCheckable(True)
        self.btn_toggle_lock.clicked.connect(self.toggle_disable_and_switch)
        
        btn_print = QPushButton("Get Inputs (Active Tab)")
        btn_print.clicked.connect(self.print_current_inputs)

        demo_panel.addWidget(self.btn_toggle_lock)
        demo_panel.addWidget(btn_print)
        main_layout.addLayout(demo_panel)             #################

    # ------------------------------------------------------------------
    # Required Methods
    # ------------------------------------------------------------------

    def set_interaction_disabled_and_switch(self, disable: bool, target_tab_index: int):
        """Method to disable/enable interaction and switch active tab."""
        # Switch tab
        if 0 <= target_tab_index < self.tabs.count():
            self.tabs.setCurrentIndex(target_tab_index)

        # Disable / Enable input interaction across tabs
        self.tabs.setEnabled(not disable)

    def print_current_inputs(self):
        """Prints input tuples from currently selected tab."""
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, "get_inputs"):
            inputs = current_widget.get_inputs()
            print(f"Inputs from Tab {self.tabs.currentIndex() + 1}: {inputs}")

    # Helper function for demo button
    def toggle_disable_and_switch(self, checked):
        if checked:
            # Switch to Tab 0 and disable all interactions
            self.set_interaction_disabled_and_switch(disable=True, target_tab_index=0)
            self.btn_toggle_lock.setText("Enable Interaction")
        else:
            self.set_interaction_disabled_and_switch(disable=False, target_tab_index=1)
            self.btn_toggle_lock.setText("Disable Interaction & Switch Tab")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # Pre-populating some items in Tab 2 for quick demonstration
    window.tab1.add_item("100", "200")
    window.tab1.add_item("300", "400")
    window.tab1.add_item("500", "600")
    window.tab1.add_item("100", "200")
    window.tab1.add_item("300", "400")
    window.tab1.add_item("500", "600")

    window.show()

    window.tab1.center_and_highlight(5)
    # window.tab1.unhighlight(2)
    
    sys.exit(app.exec_())