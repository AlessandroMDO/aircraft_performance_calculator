from PySide2.QtWidgets import QApplication, QMainWindow, QTabWidget, QPushButton, QWidget, QHBoxLayout, QAction
from gui.gui_takeoff_landing.ui_takeoff_landing import GUI_DECOLAGEM
from gui.gui_aircraft_parameters.ui_aircraft_parameters import GUI_AIRCRAFT_PARAMETERS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aircraft Performance Parameters")
        self.resize(800, 800)
        self.setMinimumSize(800, 800)
        self.setMaximumSize(800, 800)

        # Create a stacked widget to hold different windows
        self.stacked_widget = QTabWidget()

        # Create a horizontal menu bar
        menu_widget = QWidget()
        menu_layout = QHBoxLayout(menu_widget)

        # Define actions for different windows
        self.window_actions = {
            "WINDOW_GUI_AIRCRAFT_PARAMETERS": self.create_gui_aircraft_parameters,
            "WINDOW_GUI_TAKEOFF_LANDING": self.create_gui_takeoff_landing
        }

        # Dictionary to store the state of each window
        self.window_state = {
            "WINDOW_GUI_AIRCRAFT_PARAMETERS": None,
            "WINDOW_GUI_TAKEOFF_LANDING": None
        }

        # Create menu buttons dynamically
        for window_name in self.window_actions:
            action = QAction(window_name, self)
            action.triggered.connect(self.window_actions[window_name])
            menu_button = QPushButton(window_name)
            menu_layout.addWidget(menu_button)
            menu_button.clicked.connect(action.trigger)  # Trigger the corresponding action when button clicked

        self.setMenuWidget(menu_widget)  # Set the menu widget as the central widget
        self.setCentralWidget(self.stacked_widget)

    def create_gui_aircraft_parameters(self):
        # print(self.window_state)
        if self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"] is None:
            ex = GUI_AIRCRAFT_PARAMETERS()
            ex.setupUi(ex)

            # Create a new instance of GUI_AIRCRAFT_PARAMETERS_V2
            self.stacked_widget.addTab(ex, "")
            self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"] = ex

        # Switch to the existing tab
        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"])

    def create_gui_takeoff_landing(self):

        if self.window_state["WINDOW_GUI_TAKEOFF_LANDING"] is None:
            ex = GUI_DECOLAGEM(aircraft_parameters_class=self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"])
            ex.setupUi(ex)

            # Create a new instance of GUI_DECOLAGEM_V2
            self.stacked_widget.addTab(ex, "")
            self.window_state["WINDOW_GUI_TAKEOFF_LANDING"] = ex

        # Switch to the existing tab
        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_TAKEOFF_LANDING"])


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
