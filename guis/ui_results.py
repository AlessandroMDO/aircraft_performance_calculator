import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from functions.utils import get_logger
from PySide2 import QtWidgets
from db.utils.db_utils import *
from functions.aero import Aero
from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QStackedWidget, QHBoxLayout, QPushButton, QWidget, QLabel, QCheckBox, QTextEdit
from functions.takeoff import total_takeoff_distance, total_takeoff_time

class GUI_RESULTS(QMainWindow):

    def __init__(self, aircraft_parameters, flight_parameters, background_path="guis/RESULTS_800_800.png"):

        super(GUI_RESULTS, self).__init__()

        self.aero = Aero()

        self.aircrafts_parameters = aircraft_parameters
        self.flight_parameters = flight_parameters

        self.logger = get_logger()

        self.background_path = background_path

        _, self.aircrafts_parameters = execute_generic_query(db_path=r"./db/utils/aero.db", query="select * from Airplanes;", first_value=False)
        self.airports, _ = execute_generic_query(db_path=r"./db/utils/aero.db", query="select iata, icao from Airports;", first_value=False)
        self.runway_condition_options, _ = execute_generic_query(db_path=r"./db/utils/aero.db", query="select superficie from GroundType;")

        self.statusbar = None
        self.background = None
        self.centralwidget = None

    def setupUi(self, Results):
        if not Results.objectName():
            Results.setObjectName(u"Results")
        Results.resize(800, 800)
        Results.setMinimumSize(QSize(800, 830))
        Results.setMaximumSize(QSize(800, 830))
        self.centralwidget = QWidget(Results)
        self.centralwidget.setObjectName(u"centralwidget")

        palette = QPalette()
        brush = QBrush(QColor(255, 255, 255, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        brush1 = QBrush(QColor(188, 188, 188, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush1)

        font = QFont()
        font.setPointSize(10)


        palette1 = QPalette()
        palette1.setBrush(QPalette.Active, QPalette.Base, brush)
        palette1.setBrush(QPalette.Active, QPalette.Window, brush1)
        palette1.setBrush(QPalette.Inactive, QPalette.Base, brush)
        palette1.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        palette1.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        palette1.setBrush(QPalette.Disabled, QPalette.Window, brush1)

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------- BACKGROUND IMAGE -----------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.background = QLabel(self.centralwidget)
        self.background.setObjectName(u"background")
        self.background.setGeometry(QRect(0, 0, 800, 800))
        self.background.setMinimumSize(QSize(800, 800))
        self.background.setMaximumSize(QSize(800, 800))
        self.background.setLayoutDirection(Qt.LeftToRight)
        self.background.setAutoFillBackground(False)
        self.background.setPixmap(QPixmap(self.background_path))
        self.background.update()
        self.background.setScaledContents(True)
        self.background.setAlignment(Qt.AlignCenter)
        self.background.setIndent(0)
        self.background.setText("")

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- TAKEOFF DISTANCE VALUE -----------------------------------------------#


        self.result_takeoff_distance = QLabel(self.centralwidget)
        self.result_takeoff_distance.setObjectName(u"result_takeoff_distance")
        self.result_takeoff_distance.setGeometry(QRect(258, 194, 132, 21))
        self.result_takeoff_distance.setAlignment(Qt.AlignCenter)
        self.result_takeoff_distance.setFont(font)
        self.result_takeoff_distance.setText("valorrr")





        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#




        Results.setCentralWidget(self.centralwidget)

        self.background.raise_()
        self.result_takeoff_distance.raise_()




        self.statusbar = QStatusBar(Results)
        self.statusbar.setObjectName(u"statusbar")

        Results.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(Results)

        Results.setWindowTitle(QCoreApplication.translate("Results", u"Results", None))


    def calculate_takeoff_distance(self):

        takeoff_parameters = self.flight_parameters['takeoff_parameters']
        result_takeoff_distance = total_takeoff_distance(takeoff_parameters=takeoff_parameters, aircraft_parameters=self.aircrafts_parameters)
        return result_takeoff_distance








    def warning_box(self, message):

        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(message)
        msg_box.setWindowTitle('Warning')
        msg_box.exec_()

    def success_box(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle('Success')
        msg_box.exec_()


    def save_current_aicraft_to_db(self):

        result = self.get_aircraft_parameters()

        if result['AIRCRAFT_NAME'] in self.aircrafts_parameters.keys():
            self.warning_box(message='Aircraft already in the database. Give it another name.')

        elif result['AIRCRAFT_NAME'] is None:
            self.warning_box(message='The aircraft name must not be empty. Give it a name.')

        else:

            insert_query = f""" 
            INSERT INTO airplanes 
            (nome_aeronave, cd0, area, cl_max, oew, tsfc, b, e, t0, ne) 
            VALUES (
                '{result['AIRCRAFT_NAME']}', {result['CD0']}, {result['S']}, {result['CL_MAX']}, {result['OEW'] / 1000}, {result['TSFC']}, {result['b']}, {result['e']}, {result['T0'] / 1000}, {result['NE']}) ;
            """

            insert_data_to_db(db_path=r"./db/utils/aero.db", query=insert_query)
            _, self.aircrafts_parameters = execute_generic_query(db_path=r"./db/utils/aero.db", query="select * from Airplanes;", first_value=False)

            self.aircraft_list_db.clear()

            count_aircrafts = 0
            for aircraft in self.aircrafts_parameters.keys():
                self.aircraft_list_db.addItem("")
                self.aircraft_list_db.setItemText(count_aircrafts, QCoreApplication.translate("Results", f"{aircraft}", None))
                count_aircrafts += 1

            self.success_box(message='Aircraft successfully created!')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = GUI_RESULTS()
    w = QtWidgets.QMainWindow()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())
