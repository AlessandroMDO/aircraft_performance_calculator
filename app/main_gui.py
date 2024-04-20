from PySide2.QtWidgets import QApplication, QMainWindow, QTabWidget, QPushButton, QTabBar
from guis.ui_aircraft_parameters import GUI_AIRCRAFT_PARAMETERS
from guis.ui_flight_conditions import GUI_FLIGHT_CONDITIONS
from guis.ui_results import GUI_RESULTS
from PySide2.QtCore import QRect
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from functions.aero import Aero


aero = Aero()


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

        my_pixmap = QPixmap("gui_icon.png")
        my_icon = QIcon(my_pixmap)

        self.setWindowIcon(my_icon)

        self.stacked_widget = QTabWidget()
        self.bar = QTabBar()

        self.stacked_widget.setTabBar(self.bar)
        self.bar.hide()

        self.window_actions = {
            "WINDOW_GUI_AIRCRAFT_PARAMETERS": {"window_action": self.create_gui_aircraft_parameters, "location": QRect(50, 5, 161, 22)},
            "WINDOW_GUI_FLIGHT_CONDITIONS": {"window_action": self.create_gui_flight_conditions, "location": QRect(316, 5, 161, 22)},
            "WINDOW_GUI_RESULTS": {"window_action": self.create_gui_results, "location": QRect(578, 5, 161, 22)}}

        # Dictionary to store the state of each window
        self.window_state = {
            "WINDOW_GUI_AIRCRAFT_PARAMETERS": None,
            "WINDOW_GUI_FLIGHT_CONDITIONS": None,
            "WINDOW_GUI_RESULTS": None}


        self.setCentralWidget(self.stacked_widget)

        first_window_name = next(iter(self.window_actions.keys()))
        self.window_actions[first_window_name]['window_action']()

    def warning_box(self, message, ok_and_decline=False):

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle('Warning')

        if ok_and_decline is False:
            msg_box.exec_()
        else:
            ok_button = QPushButton('Yes')
            msg_box.addButton(ok_button, QMessageBox.AcceptRole)

            decline_button = QPushButton('No')
            msg_box.addButton(decline_button, QMessageBox.RejectRole)
            result = msg_box.exec_()

            return result

    def check_payload(self, flight_parameters, aircraft_parameters):

        NP = flight_parameters['NUMBER_OF_PASSENGERS']  # number of passengers
        FW = flight_parameters['FUEL_WEIGHT']  # fuel weight
        CW = flight_parameters['DISPATCHED_CARGO_WEIGHT']
        OEW = aircraft_parameters['OEW']
        MTOW = aircraft_parameters['MTOW']

        TOW = float(NP * aero.person_weight + OEW + FW + CW)

        if TOW > MTOW:
            perc = round(TOW/MTOW, 2)
            self.warning_box(f"The current weight conguration exceeds MTOW by {perc}%.\nThe results may be incorrent. Please fix it.")

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

        else:
            self.aircraft_parameters = self.gui_aircraft_parameters.get_aircraft_parameters(convert_units=True)
        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_AIRCRAFT_PARAMETERS"])


    def create_gui_flight_conditions(self):
        if self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"] is None:

            self.aircraft_parameters = self.gui_aircraft_parameters.get_aircraft_parameters(convert_units=True)
            self.gui_flight_conditions = GUI_FLIGHT_CONDITIONS(aircraft_parameters_class=self.aircraft_parameters)
            self.gui_flight_conditions.setupUi(self.gui_flight_conditions)

            self.create_buttons(ex=self.gui_flight_conditions)
            self.stacked_widget.insertTab(1, self.gui_flight_conditions, "")
            self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"] = self.gui_flight_conditions

        else:
            self.aircraft_parameters = self.gui_aircraft_parameters.get_aircraft_parameters(convert_units=True)
            self.gui_flight_conditions.update_parameters(new_aircraft_parameters=self.aircraft_parameters)
        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_FLIGHT_CONDITIONS"])


    def create_gui_results(self):

        self.aircraft_parameters = self.gui_aircraft_parameters.get_aircraft_parameters(convert_units=True)
        flight_parameters = self.gui_flight_conditions.get_flight_parameters()

        if self.window_state["WINDOW_GUI_RESULTS"] is None:

            self.check_payload(aircraft_parameters=self.aircraft_parameters, flight_parameters=flight_parameters)
            self.gui_results = GUI_RESULTS(aircraft_parameters=self.aircraft_parameters, flight_parameters=flight_parameters)
            self.gui_results.setupUi(self.gui_results)
            self.gui_results.calculate_all_results()

            self.create_buttons(ex=self.gui_results)
            self.stacked_widget.insertTab(2, self.gui_results, "")
            self.window_state["WINDOW_GUI_RESULTS"] = self.gui_results

        else:
            self.flight_parameters = self.gui_flight_conditions.get_flight_parameters()
            self.aircraft_parameters = self.gui_aircraft_parameters.get_aircraft_parameters(convert_units=True)

            self.check_payload(aircraft_parameters=self.aircraft_parameters, flight_parameters=flight_parameters)

            self.gui_results.update_parameters(new_flight_parameters=self.flight_parameters, new_aircraft_parameters=self.aircraft_parameters)
            self.gui_results.calculate_all_results()

        self.stacked_widget.setCurrentWidget(self.window_state["WINDOW_GUI_RESULTS"])


if __name__ == "__main__":

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()


#https://tree.nathanfriend.io/?s=(%27op2!(%27fancy3~fullPath!false~trailingSlash3~rootDot3)~7(%277%27app-db*utilsA.db-func2A0climb0gli4Cplot_geo085-guis*6results068_C6flight_condi206aircraft_parameters5-main_gui5-tests**B%27)~version!%271%27)*-9-B905*2tions3!true4ding05.py6ui_7source!8takeoff9%20%20A*aeroB%5CnClan4%01CBA987654320-*