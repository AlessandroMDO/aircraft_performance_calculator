from PySide2.QtWidgets import QApplication, QMainWindow, QTabWidget, QPushButton, QWidget, QHBoxLayout, QAction, QTabBar
from ui_takeoff_landing import GUI_DECOLAGEM
from ui_aircraft_parameters import GUI_AIRCRAFT_PARAMETERS
from ui_flight_conditions import GUI_FLIGHT_CONDITIONS
from PySide2.QtCore import QRect



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aircraft Performance Parameters")
        self.resize(800, 800)
        self.setMinimumSize(800, 800)
        self.setMaximumSize(800, 800)

        self.stacked_widget = QTabWidget()
        self.bar = QTabBar()

        self.stacked_widget.setTabBar(self.bar)
        self.bar.hide()

        self.window_actions = {
            "WINDOW_GUI_AIRCRAFT_PARAMETERS": {"window_action": self.create_gui_aircraft_parameters, "location": QRect(46, 4, 161, 22)},
            "WINDOW_GUI_FLIGHT_CONDITIONS": {"window_action": self.create_gui_flight_conditions, "location": QRect(229, 4, 161, 22)},
            "WINDOW_GUI_TAKEOFF_LANDING": {"window_action": self.create_gui_takeoff_landing, "location": QRect(400, 4, 161, 22)},
        }

        # Dictionary to store the state of each window
        self.window_state = {
            "WINDOW_GUI_AIRCRAFT_PARAMETERS": None,
            "WINDOW_GUI_FLIGHT_CONDITIONS": None,
            "WINDOW_GUI_TAKEOFF_LANDING": None
        }


        self.setCentralWidget(self.stacked_widget)

        first_window_name = next(iter(self.window_actions.keys()))
        self.window_actions[first_window_name]['window_action']()

    def create_buttons(self, ex):

        for window_name in self.window_actions:

            button_loc = self.window_actions[window_name]['location']

            menu_button = QPushButton(ex)
            menu_button.setText("")  # Set an empty text to hide the label
            menu_button.setGeometry(button_loc)
            menu_button.setStyleSheet("border: none; background: none;")
            menu_button.clicked.connect(self.window_actions[window_name]['window_action'])
            menu_button.raise_()

    def create_gui_aircraft_parameters(self):
        if self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"] is None:

            ex = GUI_AIRCRAFT_PARAMETERS()
            ex.setupUi(ex)

            self.create_buttons(ex=ex)
            self.stacked_widget.insertTab(0, ex, "")
            self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"] = ex


        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"])

    def create_gui_flight_conditions(self):
        if self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"] is None:
            ex = GUI_FLIGHT_CONDITIONS()
            ex.setupUi(ex)

            self.create_buttons(ex=ex)
            self.stacked_widget.insertTab(1, ex, "")
            self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"] = ex


        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"])

    def create_gui_takeoff_landing(self):

        if self.window_state["WINDOW_GUI_TAKEOFF_LANDING"] is None:
            ex = GUI_DECOLAGEM(aircraft_parameters_class=self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"])
            ex.setupUi(ex)

            self.create_buttons(ex=ex)
            self.stacked_widget.insertTab(2, ex, "")
            self.window_state["WINDOW_GUI_TAKEOFF_LANDING"] = ex



        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_TAKEOFF_LANDING"])


if __name__ == "__main__":

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
