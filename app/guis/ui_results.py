import math
import os
import sys

# current_dir = os.path.dirname(os.path.realpath(__file__))
# parent_dir = os.path.dirname(current_dir)
# sys.path.append(parent_dir)

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from functions.utils import get_logger
from PySide2 import QtWidgets
from functions.aero import Aero
from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QLabel
from functions.takeoff import total_takeoff_distance, total_takeoff_time
from functions.landing import total_landing_distance, total_landing_time
from functions.gliding import gliding_range_endurance, gliding_angle_rate_of_descent
from functions.cruising_jet import calc_cruising_jet_range, calc_cruising_jet_endurance, calc_cruise_velocity
from functions.climb import calc_max_climb_angle_rate_of_climb

class GUI_RESULTS(QMainWindow):

    def __init__(self, aircraft_parameters, flight_parameters, background_path="guis/RESULTS_800_800.png"):

        super(GUI_RESULTS, self).__init__()

        self.font = QFont()
        self.font.setPointSize(10)

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
        self.objects_list = []

        self.statusbar = None
        self.background = None
        self.centralwidget = None

    def create_Qlabel(self, label_name, label_geometry, label_aligment=Qt.AlignCenter, label_default_text="0"):

        q_label = QLabel(self.centralwidget)
        q_label.setObjectName(u"{}".format(label_name))
        q_label.setGeometry(label_geometry)
        q_label.setAlignment(label_aligment)
        q_label.setFont(self.font)
        q_label.setText(label_default_text)

        return q_label
        
    def create_QPushButton(self, label_geometry, handle_function):
        qbutton = QPushButton(self.centralwidget)
        qbutton.setText("")  # Set an empty text to hide the label
        qbutton.setGeometry(label_geometry)
        qbutton.setStyleSheet("border: none; background: none;")  # Hide border and background
        qbutton.clicked.connect(handle_function)

        return qbutton

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

        # font = QFont()
        # font.setPointSize(10)

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

        #################################################################################################################
        # -------------------------------------------------- TAKEOFF ---------------------------------------------------#
        #################################################################################################################

        self.result_takeoff_distance = self.create_Qlabel(
            label_name="result_takeoff_distance",
            label_geometry=QRect(231, 149, 89, 22))
        self.objects_list.append(self.result_takeoff_distance)

        self.result_takeoff_time = self.create_Qlabel(
            label_name="result_takeoff_time",
            label_geometry=QRect(231, 174, 89, 22))
        self.objects_list.append(self.result_takeoff_time)

        #################################################################################################################
        # -------------------------------------------------- LANDING ---------------------------------------------------#
        #################################################################################################################

        self.result_landing_distance = self.create_Qlabel(
            label_name="result_landing_distance",
            label_geometry=QRect(232, 248, 89, 22))
        self.objects_list.append(self.result_landing_distance)

        self.result_landing_time = self.create_Qlabel(
            label_name="result_landing_time",
            label_geometry=QRect(232, 273, 89, 22))
        self.objects_list.append(self.result_landing_time)

        #################################################################################################################
        # ------------------------------------------------ GLIDING -----------------------------------------------------#
        #################################################################################################################

        # ------------------------------------------    CL CONSTANT    ------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        # Result Default Range
        self.result_gliding_cl_constant_default_range = self.create_Qlabel(
            label_name="result_gliding_cl_constant_default_range",
            label_geometry=QRect(179, 622, 75, 16))
        self.objects_list.append(self.result_gliding_cl_constant_default_range)

        # Result Default Endurance
        self.result_gliding_cl_constant_default_endurance = self.create_Qlabel(
            label_name="result_gliding_cl_constant_default_endurance",
            label_geometry=QRect(179, 645, 75, 16))
        self.objects_list.append(self.result_gliding_cl_constant_default_endurance)

        # Result Max Range
        self.result_gliding_cl_constant_max_range = self.create_Qlabel(
            label_name="result_gliding_cl_constant_max_range",
            label_geometry=QRect(179, 670, 75, 16))
        self.objects_list.append(self.result_gliding_cl_constant_max_range)

        # Result Max Endurance
        self.result_gliding_cl_constant_max_endurance = self.create_Qlabel(
            label_name="result_gliding_cl_constant_max_endurance",
            label_geometry=QRect(179, 692, 75, 16))
        self.objects_list.append(self.result_gliding_cl_constant_max_endurance)

        # Gráficos CL Constant
        self.display_cl_constant_graphs = QPushButton(self.centralwidget)
        self.display_cl_constant_graphs.setText("")  # Set an empty text to hide the label
        self.display_cl_constant_graphs.setGeometry(QRect(62, 584, 33, 31))
        self.display_cl_constant_graphs.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_cl_constant_graphs.clicked.connect(self.invoke_gliding_cl_constant_graphs)

        # ------------------------------------------    V CONSTANT    -------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        # Result Default Range
        self.result_gliding_v_constant_default_range = self.create_Qlabel(
            label_name="result_gliding_v_constant_default_range",
            label_geometry=QRect(442, 622, 75, 16))
        self.objects_list.append(self.result_gliding_v_constant_default_range)

        # Result Default Endurance
        self.result_gliding_v_constant_default_endurance = self.create_Qlabel(
            label_name="result_gliding_v_constant_default_endurance",
            label_geometry=QRect(442, 645, 75, 16))
        self.objects_list.append(self.result_gliding_v_constant_default_endurance)

        # Result Max Range
        self.result_gliding_v_constant_max_range = self.create_Qlabel(
            label_name="result_gliding_v_constant_max_range",
            label_geometry=QRect(442, 670, 75, 16))
        self.objects_list.append(self.result_gliding_v_constant_max_range)

        # Result Max Endurance
        self.result_gliding_v_constant_max_endurance = self.create_Qlabel(
            label_name="result_gliding_v_constant_max_endurance",
            label_geometry=QRect(442, 692, 75, 16))
        self.objects_list.append(self.result_gliding_v_constant_max_endurance)

        # Gráicos CL Constant
        self.display_v_constant_graphs = QPushButton(self.centralwidget)
        self.display_v_constant_graphs.setText("")  # Set an empty text to hide the label
        self.display_v_constant_graphs.setGeometry(QRect(307, 584, 33, 31))
        self.display_v_constant_graphs.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_v_constant_graphs.clicked.connect(self.invoke_gliding_v_constant_graphs)
        self.objects_list.append(self.display_v_constant_graphs)


        # --------------------------------    RATE OF DESCENT AND GLIDING ANGLE    ------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#
        self.result_rate_of_descent = self.create_Qlabel(
            label_name="result_rate_of_descent",
            label_geometry=QRect(675, 622, 75, 16))
        self.objects_list.append(self.result_rate_of_descent)

        self.result_gliding_angle = self.create_Qlabel(
            label_name="result_gliding_angle",
            label_geometry=QRect(675, 645, 75, 16))
        self.objects_list.append(self.result_gliding_angle)

        self.display_rate_of_descent_gliding_angle_graph = self.create_QPushButton(
            handle_function=self.invoke_rate_of_descent_gliding_angle_graph,
            label_geometry=QRect(642, 584, 33, 31))
        self.objects_list.append(self.display_rate_of_descent_gliding_angle_graph)

        #################################################################################################################
        # -------------------------------------------------- CRUISE ----------------------------------------------------#
        #################################################################################################################

        # Cruise Velocity
        self.result_cruise_velocity = self.create_Qlabel(
            label_name="result_cruise_velocity",
            label_geometry=QRect(127, 405, 57, 22))
        self.objects_list.append(self.result_cruise_velocity)

        # Minimum Drag
        self.result_cruise_minimum_drag = self.create_Qlabel(
            label_name="result_cruise_minimum_drag",
            label_geometry=QRect(25, 405, 57, 22))
        self.objects_list.append(self.result_cruise_minimum_drag)

        self.display_minimun_drag_graph = QPushButton(self.centralwidget)
        self.display_minimun_drag_graph.setText("")  # Set an empty text to hide the label
        self.display_minimun_drag_graph.setGeometry(QRect(35, 434, 33, 31))
        self.display_minimun_drag_graph.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_minimun_drag_graph.clicked.connect(self.invoke_minimum_drag_graph)
        self.objects_list.append(self.display_minimun_drag_graph)

        ## Constant h-CL

        self.result_range_constant_h_cl = self.create_Qlabel(
            label_name="result_range_constant_h_cl",
            label_geometry=QRect(354, 384, 63, 22))
        self.objects_list.append(self.result_range_constant_h_cl)

        self.result_max_range_constant_h_cl = self.create_Qlabel(
            label_name="result_max_range_constant_h_cl",
            label_geometry=QRect(459, 384, 63, 22))
        self.objects_list.append(self.result_max_range_constant_h_cl)

        self.result_endurance_constant_h_cl = self.create_Qlabel(
            label_name="result_endurance_constant_h_cl",
            label_geometry=QRect(576, 384, 63, 22))
        self.objects_list.append(self.result_endurance_constant_h_cl)

        self.result_max_endurance_constant_h_cl = self.create_Qlabel(
            label_name="result_max_endurance_constant_h_cl",
            label_geometry=QRect(697, 384, 63, 22))
        self.objects_list.append(self.result_max_endurance_constant_h_cl)

        ## Constant V-CL

        self.result_range_constant_v_cl = self.create_Qlabel(
            label_name="result_range_constant_v_cl",
            label_geometry=QRect(354, 414, 63, 22))
        self.objects_list.append(self.result_range_constant_v_cl)

        self.result_max_range_constant_v_cl = self.create_Qlabel(
            label_name="result_max_range_constant_v_cl",
            label_geometry=QRect(459, 414, 63, 22))
        self.objects_list.append(self.result_max_range_constant_v_cl)

        self.result_endurance_constant_v_cl = self.create_Qlabel(
            label_name="result_endurance_constant_v_cl",
            label_geometry=QRect(576, 414, 63, 22))
        self.objects_list.append(self.result_endurance_constant_v_cl)

        self.result_max_endurance_constant_v_cl = self.create_Qlabel(
            label_name="result_max_endurance_constant_v_cl",
            label_geometry=QRect(697, 414, 63, 22))
        self.objects_list.append(self.result_max_endurance_constant_v_cl)



        ## Constant h-V

        self.result_range_constant_h_v = self.create_Qlabel(
            label_name="result_range_constant_h_v",
            label_geometry=QRect(354, 444, 63, 22))
        self.objects_list.append(self.result_range_constant_h_v)

        self.result_max_range_constant_h_v = self.create_Qlabel(
            label_name="result_max_range_constant_h_v",
            label_geometry=QRect(459, 444, 63, 22))
        self.objects_list.append(self.result_max_range_constant_h_v)


        self.result_endurance_constant_h_v = self.create_Qlabel(
            label_name="result_endurance_constant_h_v",
            label_geometry=QRect(576, 444, 63, 22))
        self.objects_list.append(self.result_endurance_constant_h_v)

        self.result_max_endurance_constant_h_v = self.create_Qlabel(
            label_name="result_max_endurance_constant_h_v",
            label_geometry=QRect(697, 444, 63, 22))
        self.objects_list.append(self.result_max_endurance_constant_h_v)

        # --------------------------------------------------CLIMB -----------------------------------------------------#


        self.result_max_climb_angle = self.create_Qlabel(
            label_name="result_max_climb_angle",
            label_geometry=QRect(641, 149, 89, 22))
        self.objects_list.append(self.result_max_climb_angle)

        self.result_max_rate_of_climb = self.create_Qlabel(
            label_name="result_max_rate_of_climb",
            label_geometry=QRect(641, 174, 89, 22))
        self.objects_list.append(self.result_max_rate_of_climb)

        self.display_rate_of_climb_graph = QPushButton(self.centralwidget)
        self.display_rate_of_climb_graph.setText("")  # Set an empty text to hide the label
        self.display_rate_of_climb_graph.setGeometry(QRect(750, 158, 33, 31))
        self.display_rate_of_climb_graph.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_rate_of_climb_graph.clicked.connect(self.invoke_rate_of_climb_graph)
        self.objects_list.append(self.display_rate_of_climb_graph)





        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        Results.setCentralWidget(self.centralwidget)

        self.background.raise_()
        self.result_gliding_cl_constant_default_range.raise_()
        self.display_cl_constant_graphs.raise_()
        self.result_gliding_cl_constant_default_endurance.raise_()
        self.result_gliding_cl_constant_max_endurance.raise_()
        self.result_gliding_cl_constant_max_range.raise_()

        for obj in self.objects_list:
            obj.raise_()




        self.statusbar = QStatusBar(Results)
        self.statusbar.setObjectName(u"statusbar")

        Results.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(Results)

        Results.setWindowTitle(QCoreApplication.translate("Results", u"Results", None))


    def calculate_takeoff_parameters(self):

        self.results_takeoff_distance = total_takeoff_distance(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)
        self.results_takeoff_time = total_takeoff_time(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)

        self.result_takeoff_distance_value = self.results_takeoff_distance['TAKEOFF_DISTANCE']
        self.result_takeoff_distance.setText(str(round(self.result_takeoff_distance_value / 1000, 2)))  # [km]

        self.result_takeoff_time_value = self.results_takeoff_time['TAKEOFF_TIME']
        self.result_takeoff_time.setText(str(round(self.result_takeoff_time_value / 60, 2)))  # [min]

    def calculate_landing_parameters(self):
        self.results_landing_distance = total_landing_distance(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)
        self.results_landing_time = total_landing_time(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)

        self.result_landing_distance_value = self.results_landing_distance['LANDING_DISTANCE']
        self.result_landing_distance.setText(str(round(self.result_landing_distance_value / 1000, 2)))  # [km]

        self.result_landing_time_value = self.results_landing_time['LANDING_TIME']
        self.result_landing_time.setText(str(round(self.result_landing_time_value / 60, 2)))  # [min]




    def update_parameters(self, new_aircraft_parameters, new_flight_parameters):

        self.aircraft_parameters = new_aircraft_parameters
        self.flight_parameters = new_flight_parameters

    def calculate_cruising_parameters(self):

        self.results_cruise_velocity = calc_cruise_velocity(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters, plot=True)

        self.cruise_velocity_value = round(self.results_cruise_velocity['CRUISE_VELOCITY'], 2)
        self.result_cruise_velocity.setText(str(self.cruise_velocity_value))

        self.minimum_cruise_drag_value = self.results_cruise_velocity['MINIMUM_DRAG']
        self.result_cruise_minimum_drag.setText(str(round(self.minimum_cruise_drag_value / 1000, 2)))
        self.result_cruise_minimum_drag_graph = self.results_cruise_velocity['CRUISE_DRAG_GRAPH']

        self.cruise_velocities = self.results_cruise_velocity['CRUISE_VELOCITIES']

        # Range
        self.results_cruising_range = calc_cruising_jet_range(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)

        ## h_CL
        self.result_range_constant_h_cl_value = self.results_cruising_range['RANGE_CONSTANT_HEIGHT_CL']
        self.result_max_range_constant_h_cl_value = self.results_cruising_range['MAX_RANGE_CONSTANT_HEIGHT_CL']

        self.result_range_constant_h_cl.setText(str(round(self.result_range_constant_h_cl_value / 1000, 2)))
        self.result_max_range_constant_h_cl.setText(str(round(self.result_max_range_constant_h_cl_value / 1000, 2)))

        ## v_CL
        self.result_range_constant_v_cl_value = self.results_cruising_range['RANGE_CONSTANT_VELOCITY_CL']
        self.result_max_range_constant_v_cl_value = self.results_cruising_range['MAX_RANGE_CONSTANT_VELOCITY_CL']

        self.result_range_constant_v_cl.setText(str(round(self.result_range_constant_v_cl_value / 1000, 2)))
        self.result_max_range_constant_v_cl.setText(str(round(self.result_max_range_constant_v_cl_value / 1000, 2)))

        ## h_V
        self.result_range_constant_h_v_value = self.results_cruising_range['RANGE_CONSTANT_HEIGHT_VELOCITY']
        self.result_max_range_constant_h_v_value = self.results_cruising_range['MAX_RANGE_CONSTANT_HEIGHT_VELOCITY']

        self.result_range_constant_h_v.setText(str(round(self.result_range_constant_h_v_value / 1000, 2)))
        self.result_max_range_constant_h_v.setText(str(round(self.result_max_range_constant_h_v_value / 1000, 2)))


        # Endurance
        self.results_cruising_endurance = calc_cruising_jet_endurance(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)

        self.result_endurance_constant_h_cl_value = self.results_cruising_endurance['ENDURANCE_CONSTANT_HEIGHT_CL']
        self.result_max_endurance_constant_h_cl_value = self.results_cruising_endurance['MAX_ENDURANCE_CONSTANT_HEIGHT_CL']

        self.result_endurance_constant_h_cl.setText(str(round(self.result_endurance_constant_h_cl_value / 3600, 2)))
        self.result_max_endurance_constant_h_cl.setText(str(round(self.result_max_endurance_constant_h_cl_value / 3600, 2)))


        self.result_endurance_constant_v_cl_value = self.results_cruising_endurance['ENDURANCE_CONSTANT_VELOCITY_CL']
        self.result_max_endurance_constant_v_cl_value = self.results_cruising_endurance['MAX_ENDURANCE_CONSTANT_VELOCITY_CL']

        self.result_endurance_constant_v_cl.setText(str(round(self.result_endurance_constant_v_cl_value / 3600, 2)))
        self.result_max_endurance_constant_v_cl.setText(str(round(self.result_max_endurance_constant_v_cl_value / 3600, 2)))

        self.result_endurance_constant_h_v_value = self.results_cruising_endurance['ENDURANCE_CONSTANT_HEIGHT_VELOCITY']
        self.result_max_endurance_constant_h_v_value = self.results_cruising_endurance['MAX_ENDURANCE_CONSTANT_HEIGHT_VELOCITY']

        self.result_endurance_constant_h_v.setText(str(round(self.result_endurance_constant_h_v_value / 3600, 2)))
        self.result_max_endurance_constant_h_v.setText(str(round(self.result_max_endurance_constant_h_v_value / 3600, 2)))


    def calculate_climb_parameters(self):
        self.result_max_climb_angle_rate_of_climb = calc_max_climb_angle_rate_of_climb(flight_parameters=self.flight_parameters,
                                                                                       aircraft_parameters=self.aircraft_parameters,
                                                                                       plot=True)

        self.result_max_climb_angle_value = self.result_max_climb_angle_rate_of_climb['MAX_GAMMA_CLIMB']
        self.result_max_climb_angle.setText(str(round(math.degrees(self.result_max_climb_angle_value), 2)))

        self.result_rate_of_climb_value = self.result_max_climb_angle_rate_of_climb['MAX_RATE_OF_CLIMB']
        self.result_max_rate_of_climb.setText(str(round(self.result_rate_of_climb_value, 2)))

        self.result_graph_rate_of_climb = self.result_max_climb_angle_rate_of_climb['GRAPH_RATE_OF_CLIMB_PER_VELOCITY']


    def calculate_gliding_parameters(self):

        self.result_gliding_range_endurance = gliding_range_endurance(flight_parameters=self.flight_parameters,
                                                                      aircraft_parameters=self.aircraft_parameters,
                                                                      graph_CL=True, graph_V=True)

        # CL Constant
        self.gliding_cl_constant_graphs = self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_ENDURANCE_CONSTANT_LIFT_GRAPH']

        self.result_gliding_cl_constant_default_range_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_CONSTANT_LIFT_STANDARD'] / 1000, 2)
        self.result_gliding_cl_constant_default_endurance_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_ENDURANCE_CONSTANT_LIFT_STANDARD'] / 3600, 2)
        self.result_gliding_cl_constant_max_endurance_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_MAX_ENDURANCE_CONSTANT_LIFT'] / 3600, 2)
        self.result_gliding_cl_constant_max_range_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_MAX_RANGE_CONSTANT_LIFT'] / 1000, 2)

        self.result_gliding_cl_constant_default_range.setText(str(self.result_gliding_cl_constant_default_range_value))
        self.result_gliding_cl_constant_default_endurance.setText(str(self.result_gliding_cl_constant_default_endurance_value))
        self.result_gliding_cl_constant_max_endurance.setText(str(self.result_gliding_cl_constant_max_endurance_value))
        self.result_gliding_cl_constant_max_range.setText(str(self.result_gliding_cl_constant_max_range_value))

        # V Constant
        self.gliding_v_constant_graphs = self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_RANGE_ENDURANCE_CONSTANT_AIRSPEED_GRAPH']

        self.result_gliding_v_constant_default_range_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_RANGE_CONSTANT_AIRSPEED_STANDARD'] / 1000, 2)
        self.result_gliding_v_constant_default_endurance_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_ENDURANCE_CONSTANT_AIRSPEED_STANDARD'] / 3600, 2)
        self.result_gliding_v_constant_max_endurance_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_MAX_ENDURANCE_CONSTANT_AIRSPEED'] / 3600, 2)
        self.result_gliding_v_constant_max_range_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_MAX_RANGE_CONSTANT_AIRSPEED'] / 1000, 2)

        self.result_gliding_v_constant_default_range.setText(str(self.result_gliding_v_constant_default_range_value))
        self.result_gliding_v_constant_default_endurance.setText(str(self.result_gliding_v_constant_default_endurance_value))
        self.result_gliding_v_constant_max_endurance.setText(str(self.result_gliding_v_constant_max_endurance_value))
        self.result_gliding_v_constant_max_range.setText(str(self.result_gliding_v_constant_max_range_value))


        # Rate of descent and gliding angle
        self.result_rate_of_descent_gliding_angle = gliding_angle_rate_of_descent(aircraft_parameters=self.aircraft_parameters,
                                                                                  flight_parameters=self.flight_parameters,
                                                                                  plot=True)

        self.result_rate_of_descent_value = self.result_rate_of_descent_gliding_angle['GLIDING_RATE_OF_DESCENT']
        self.result_gliding_angle_value = self.result_rate_of_descent_gliding_angle['GLIDING_ANGLE']
        self.gliding_rate_of_descent_gliding_angle_graph = self.result_rate_of_descent_gliding_angle['GLIDING_ANGLE_RATE_OF_DESCENT_GRAPH']

        self.result_gliding_angle.setText(str(self.result_gliding_angle_value))
        self.result_rate_of_descent.setText(str(self.result_rate_of_descent_value))








    def invoke_gliding_cl_constant_graphs(self):

        self.gliding_cl_constant_graphs.show()
    def invoke_rate_of_climb_graph(self):

        self.result_graph_rate_of_climb.show()

    def invoke_minimum_drag_graph(self):
        self.result_cruise_minimum_drag_graph.show()



    def invoke_gliding_v_constant_graphs(self):

        self.gliding_v_constant_graphs.show()

    def invoke_rate_of_descent_gliding_angle_graph(self):

        self.gliding_rate_of_descent_gliding_angle_graph.show()

    def calculate_all_results(self):

        # Takeoff
        self.calculate_takeoff_parameters()

        #Climb

        self.calculate_climb_parameters()

        # Landing
        self.calculate_landing_parameters()


        # Cruise
        self.calculate_cruising_parameters()


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
