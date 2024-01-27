from PySide2.QtWidgets import QApplication, QMainWindow, QTabWidget, QPushButton, QWidget, QHBoxLayout, QAction, QTabBar
from ui_takeoff_landing import GUI_DECOLAGEM
from ui_aircraft_parameters import GUI_AIRCRAFT_PARAMETERS
from ui_flight_conditions import GUI_FLIGHT_CONDITIONS
from ui_results import GUI_RESULTS
from PySide2.QtCore import QRect



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.gui_flight_conditions = None
        self.gui_results = None
        self.flight_parameters = None
        self.aircraft_parameters = None
        self.gui_aircraft_parameters = None
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
            "WINDOW_GUI_RESULTS": {"window_action": self.create_gui_results, "location": QRect(400, 4, 161, 22)},
        }

        # Dictionary to store the state of each window
        self.window_state = {
            "WINDOW_GUI_AIRCRAFT_PARAMETERS": None,
            "WINDOW_GUI_FLIGHT_CONDITIONS": None,
            "WINDOW_GUI_RESULTS": None
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

            self.gui_aircraft_parameters = GUI_AIRCRAFT_PARAMETERS()
            self.gui_aircraft_parameters.setupUi(self.gui_aircraft_parameters)

            self.create_buttons(ex=self.gui_aircraft_parameters)
            self.stacked_widget.insertTab(0, self.gui_aircraft_parameters, "")
            self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"] = self.gui_aircraft_parameters


        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"])
        self.aircraft_parameters = self.gui_aircraft_parameters.get_aircraft_parameters()

    def create_gui_flight_conditions(self):
        if self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"] is None:

            self.aircraft_parameters = self.gui_aircraft_parameters.get_aircraft_parameters()
            self.gui_flight_conditions = GUI_FLIGHT_CONDITIONS(aircraft_parameters_class=self.aircraft_parameters)
            self.gui_flight_conditions.setupUi(self.gui_flight_conditions)

            self.create_buttons(ex=self.gui_flight_conditions)
            self.stacked_widget.insertTab(1, self.gui_flight_conditions, "")
            self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"] = self.gui_flight_conditions

        else:
            self.flight_parameters = self.gui_flight_conditions.get_flight_parameters()
        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"])


    def create_gui_results(self):

        self.aircraft_parameters = self.gui_aircraft_parameters.get_aircraft_parameters()
        flight_parameters = self.gui_flight_conditions.get_flight_parameters()

        if self.window_state["WINDOW_GUI_RESULTS"] is None:

            self.gui_results = GUI_RESULTS(aircraft_parameters=self.aircraft_parameters, flight_parameters=flight_parameters)
            self.gui_results.setupUi(self.gui_results)

            self.create_buttons(ex=self.gui_results)
            self.stacked_widget.insertTab(2, self.gui_results, "")
            self.window_state["WINDOW_GUI_RESULTS"] = self.gui_results

        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_RESULTS"])


if __name__ == "__main__":

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
