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
from functions.gliding import gliding_range_endurance

class GUI_RESULTS(QMainWindow):

    def __init__(self, aircraft_parameters, flight_parameters, background_path="guis/RESULTS_800_800.png"):

        super(GUI_RESULTS, self).__init__()

        self.display_cl_constant_graphs = None
        self.result_gliding_cl_constant_max_endurance = None
        self.result_gliding_cl_constant_default_endurance = None
        self.result_gliding_cl_constant_max_range = None
        self.result_gliding_cl_constant_default_range = None
        self.result_gliding_cl_constant_max_range_value = 0
        self.result_gliding_cl_constant_default_range_value = 0
        self.result_takeoff_distance = 0
        self.result_gliding_range_endurance = {}
        self.aero = Aero()

        self.aircraft_parameters = aircraft_parameters
        self.flight_parameters = flight_parameters

        self.logger = get_logger()

        self.background_path = background_path

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
        # --------------------------------------------------------------------------------------------------------------#


        self.result_takeoff_distance = QLabel(self.centralwidget)
        self.result_takeoff_distance.setObjectName(u"result_takeoff_distance")
        self.result_takeoff_distance.setGeometry(QRect(258, 194, 132, 21))
        self.result_takeoff_distance.setAlignment(Qt.AlignCenter)
        self.result_takeoff_distance.setFont(font)
        self.result_takeoff_distance.setText("valorrr")





        # ---------------------------------------------- GLIDING ------------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        # ------------------------------------------    CL CONSTANT    ------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        # Result Default Range
        self.result_gliding_cl_constant_default_range = QLabel(self.centralwidget)
        self.result_gliding_cl_constant_default_range.setObjectName(u"result_gliding_cl_constant_default_range")
        self.result_gliding_cl_constant_default_range.setGeometry(QRect(179, 622, 75, 16))
        self.result_gliding_cl_constant_default_range.setAlignment(Qt.AlignCenter)
        self.result_gliding_cl_constant_default_range.setFont(font)
        self.result_gliding_cl_constant_default_range.setText("0")

        # Result Default Endurance
        self.result_gliding_cl_constant_default_endurance = QLabel(self.centralwidget)
        self.result_gliding_cl_constant_default_endurance.setObjectName(u"result_gliding_cl_constant_default_endurance")
        self.result_gliding_cl_constant_default_endurance.setGeometry(QRect(179, 645, 75, 16))
        self.result_gliding_cl_constant_default_endurance.setAlignment(Qt.AlignCenter)
        self.result_gliding_cl_constant_default_endurance.setFont(font)
        self.result_gliding_cl_constant_default_endurance.setText("0")

        # Result Max Range
        self.result_gliding_cl_constant_max_range = QLabel(self.centralwidget)
        self.result_gliding_cl_constant_max_range.setObjectName(u"result_gliding_cl_constant_max_range")
        self.result_gliding_cl_constant_max_range.setGeometry(QRect(179, 670, 75, 16))
        self.result_gliding_cl_constant_max_range.setAlignment(Qt.AlignCenter)
        self.result_gliding_cl_constant_max_range.setFont(font)
        self.result_gliding_cl_constant_max_range.setText("0")

        # Result Max Endurance
        self.result_gliding_cl_constant_max_endurance = QLabel(self.centralwidget)
        self.result_gliding_cl_constant_max_endurance.setObjectName(u"result_gliding_cl_constant_max_endurance")
        self.result_gliding_cl_constant_max_endurance.setGeometry(QRect(179, 692, 75, 16))
        self.result_gliding_cl_constant_max_endurance.setAlignment(Qt.AlignCenter)
        self.result_gliding_cl_constant_max_endurance.setFont(font)
        self.result_gliding_cl_constant_max_endurance.setText("0")


        # -------------------------------------------------------------------------------------------------------------#
        self.display_cl_constant_graphs = QPushButton(self.centralwidget)
        self.display_cl_constant_graphs.setText("")  # Set an empty text to hide the label
        self.display_cl_constant_graphs.setGeometry(QRect(62, 584, 33, 31))
        self.display_cl_constant_graphs.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_cl_constant_graphs.clicked.connect(self.invoke_gliding_cl_constant_graphs)


        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#




        Results.setCentralWidget(self.centralwidget)

        self.background.raise_()
        self.result_takeoff_distance.raise_()
        self.result_gliding_cl_constant_default_range.raise_()
        self.display_cl_constant_graphs.raise_()
        self.result_gliding_cl_constant_default_endurance.raise_()
        self.result_gliding_cl_constant_max_endurance.raise_()
        self.result_gliding_cl_constant_max_range.raise_()




        self.statusbar = QStatusBar(Results)
        self.statusbar.setObjectName(u"statusbar")

        Results.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(Results)

        Results.setWindowTitle(QCoreApplication.translate("Results", u"Results", None))


    def calculate_takeoff_distance(self):

        takeoff_parameters = self.flight_parameters['takeoff_parameters']
        self.result_takeoff_distance = total_takeoff_distance(takeoff_parameters=takeoff_parameters, aircraft_parameters=self.aircrafts_parameters)


    def update_parameters(self, new_aircraft_parameters, new_flight_parameters):

        self.aircraft_parameters = new_aircraft_parameters
        self.flight_parameters = new_flight_parameters

    def calculate_gliding_parameters(self):

        self.result_gliding_range_endurance = gliding_range_endurance(flight_parameters=self.flight_parameters,
                                                                      aircraft_parameters=self.aircraft_parameters,
                                                                      graph_CL=True, graph_V=True)

        self.gliding_cl_constant_graphs = self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_ENDURANCE_CONSTANT_LIFT_GRAPH']

        self.result_gliding_cl_constant_default_range_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_CONSTANT_LIFT_STANDARD'] / 1000, 2)
        self.result_gliding_cl_constant_default_endurance_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_ENDURANCE_CONSTANT_LIFT_STANDARD'] / 3600, 2)
        self.result_gliding_cl_constant_max_endurance_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_MAX_ENDURANCE_CONSTANT_LIFT'] / 3600, 2)
        self.result_gliding_cl_constant_max_range_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_MAX_RANGE_CONSTANT_LIFT'] / 1000, 2)

        self.result_gliding_cl_constant_default_range.setText(str(self.result_gliding_cl_constant_default_range_value))
        self.result_gliding_cl_constant_default_endurance.setText(str(self.result_gliding_cl_constant_default_endurance_value))
        self.result_gliding_cl_constant_max_endurance.setText(str(self.result_gliding_cl_constant_max_endurance_value))
        self.result_gliding_cl_constant_max_range.setText(str(self.result_gliding_cl_constant_max_range_value))

    def invoke_gliding_cl_constant_graphs(self):

        self.gliding_cl_constant_graphs.show()

    def calculate_all_results(self):

        # Takeoff
        # self.calculate_takeoff_distance()

        # Landing


        # Cruise


        # Gliding
        self.calculate_gliding_parameters()



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




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = GUI_RESULTS()
    w = QtWidgets.QMainWindow()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())
