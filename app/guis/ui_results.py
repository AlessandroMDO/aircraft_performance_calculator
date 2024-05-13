import math
import os
import sys
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from functions.utils import get_logger
from PySide2 import QtWidgets
from functions.aero import Aero
import matplotlib.pyplot as plt
import copy
from datetime import datetime
import matplotlib as mpl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from numpy import array, hstack, vstack, zeros
from pandas import DataFrame
from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QLabel
from functions.takeoff import calc_total_takeoff_distance, calc_total_takeoff_time, calc_takeoff_distance_time_per_altitude
from functions.plot_phases import plot_phases
from functions.landing import calc_total_landing_distance, calc_total_landing_time, calc_landing_distance_time_per_altitude
from functions.manevour import calc_load_factor_turning_rate_turning_radius_graph, calc_fastest_turn, calc_tighest_turn, calc_stall_turn
from functions.gliding import gliding_range_endurance, gliding_angle_rate_of_descent
from functions.cruising_jet import (calc_cruising_jet_range, calc_cruising_jet_endurance, calc_cruise_velocity,
                                    calc_payload_x_range, calc_cruise_fuel_weight)
from functions.climb import (calc_max_climb_angle_rate_of_climb, calc_distance_time_steepest_climb,
                             calc_service_ceiling, calc_distance_time_fastest_climb)
from .ui_display_pandas_table import PandasWindow


backend = mpl.get_backend()

def show_figure(fig):

    # create a dummy figure and use its
    # manager to display "fig"
    dummy = plt.figure()
    new_manager = dummy.canvas.manager
    new_manager.canvas.figure = fig
    fig.set_canvas(new_manager.canvas)

class GUI_RESULTS(QMainWindow):

    def __init__(self, aircraft_parameters, flight_parameters, background_path="guis/RESULTS_800_800.png"):

        super(GUI_RESULTS, self).__init__()

        self.fig_phases = None
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

        self.logger = get_logger(log_name="UI_RESULTS")

        self.background_path = background_path
        self.objects_list = []

        self.statusbar = None
        self.background = None
        self.centralwidget = None

        self.layout = QVBoxLayout()


    def createToolTip(self, x, y, label_text, tooltip_text):
        # Create a label
        label = QLabel(label_text, self)
        label.setGeometry(x, y, 150, 30)

        label.enterEvent = lambda event: QToolTip.showText(self.mapToGlobal(label.pos()), tooltip_text)

    def set_label_value(self, q_label, value, threshold):
        q_label.setText(str(value))
        if float(value) > float(threshold):
            q_label.setStyleSheet("color: red;")
        else:
            q_label.setStyleSheet("")

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

        self.layout_fig_phases = QVBoxLayout(self.centralwidget)

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
            label_geometry=QRect(229, 151, 89, 22))
        self.objects_list.append(self.result_takeoff_distance)

        self.result_takeoff_time = self.create_Qlabel(
            label_name="result_takeoff_time",
            label_geometry=QRect(229, 176, 89, 22))
        self.objects_list.append(self.result_takeoff_time)

        self.display_takeoff_distance_and_time_per_altitude = QPushButton(self.centralwidget)
        self.display_takeoff_distance_and_time_per_altitude.setText("")  # Set an empty text to hide the label
        self.display_takeoff_distance_and_time_per_altitude.setGeometry(QRect(326, 151, 33, 31))
        self.display_takeoff_distance_and_time_per_altitude.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_takeoff_distance_and_time_per_altitude.clicked.connect(self.invoke_table_takeoff_distance_time)
        self.objects_list.append(self.display_takeoff_distance_and_time_per_altitude)

        self.takeoff_distance_and_time_per_altitude = PandasWindow(df=DataFrame({'A' : []}), index_column="Takeoff Altitude [m]")
        self.layout.addWidget(self.takeoff_distance_and_time_per_altitude)

        #################################################################################################################
        # -------------------------------------------------- LANDING ---------------------------------------------------#
        #################################################################################################################

        self.result_landing_distance = self.create_Qlabel(
            label_name="result_landing_distance",
            label_geometry=QRect(623, 151, 89, 22))
        self.objects_list.append(self.result_landing_distance)

        self.result_landing_time = self.create_Qlabel(
            label_name="result_landing_time",
            label_geometry=QRect(623, 176, 89, 22))
        self.objects_list.append(self.result_landing_time)

        self.display_landing_distance_and_time_per_altitude = QPushButton(self.centralwidget)
        self.display_landing_distance_and_time_per_altitude.setText("")  # Set an empty text to hide the label
        self.display_landing_distance_and_time_per_altitude.setGeometry(QRect(739, 151, 33, 31))
        self.display_landing_distance_and_time_per_altitude.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_landing_distance_and_time_per_altitude.clicked.connect(self.invoke_table_landing_distance_time)
        self.objects_list.append(self.display_landing_distance_and_time_per_altitude)

        self.landing_distance_and_time_per_altitude = PandasWindow(df=DataFrame({'A' : []}), index_column="Landing Altitude [m]")
        self.layout.addWidget(self.landing_distance_and_time_per_altitude)

        #################################################################################################################
        # ------------------------------------------------ GLIDING -----------------------------------------------------#
        #################################################################################################################

        # ------------------------------------------    CL CONSTANT    ------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        # Result Default Range
        self.result_gliding_cl_constant_default_range = self.create_Qlabel(
            label_name="result_gliding_cl_constant_default_range",
            label_geometry=QRect(530, 564, 75, 16))
        self.objects_list.append(self.result_gliding_cl_constant_default_range)

        #Result Default Endurance
        self.result_gliding_cl_constant_default_endurance = self.create_Qlabel(
            label_name="result_gliding_cl_constant_default_endurance",
            label_geometry=QRect(647, 564, 75, 16))
        self.objects_list.append(self.result_gliding_cl_constant_default_endurance)

        # Result Max Range
        # self.result_gliding_cl_constant_max_range = self.create_Qlabel(
        #     label_name="result_gliding_cl_constant_max_range",
        #     label_geometry=QRect(179, 739, 75, 16))
        # self.objects_list.append(self.result_gliding_cl_constant_max_range)

        # Result Max Endurance
        # self.result_gliding_cl_constant_max_endurance = self.create_Qlabel(
        #     label_name="result_gliding_cl_constant_max_endurance",
        #     label_geometry=QRect(179, 761, 75, 16))
        # self.objects_list.append(self.result_gliding_cl_constant_max_endurance)

        # Gráficos CL Constant
        # self.display_cl_constant_graphs = QPushButton(self.centralwidget)
        # self.display_cl_constant_graphs.setText("")  # Set an empty text to hide the label
        # self.display_cl_constant_graphs.setGeometry(QRect(62, 653, 33, 31))
        # self.display_cl_constant_graphs.setStyleSheet("border: none; background: none;")  # Hide border and background
        # self.display_cl_constant_graphs.clicked.connect(self.invoke_gliding_cl_constant_graphs)
        #self.objects_list.append(self.display_cl_constant_graphs)

        # ------------------------------------------    V CONSTANT    -------------------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        # Result Default Range
        self.result_gliding_v_constant_default_range = self.create_Qlabel(
            label_name="result_gliding_v_constant_default_range",
            label_geometry=QRect(530, 539, 75, 16))
        self.objects_list.append(self.result_gliding_v_constant_default_range)

        # Result Default Endurance
        self.result_gliding_v_constant_default_endurance = self.create_Qlabel(
            label_name="result_gliding_v_constant_default_endurance",
            label_geometry=QRect(647, 539, 75, 16))
        self.objects_list.append(self.result_gliding_v_constant_default_endurance)

        # Result Max Range
        # self.result_gliding_v_constant_max_range = self.create_Qlabel(
        #     label_name="result_gliding_v_constant_max_range",
        #     label_geometry=QRect(442, 739, 75, 16))
        # self.objects_list.append(self.result_gliding_v_constant_max_range)

        # Result Max Endurance
        # self.result_gliding_v_constant_max_endurance = self.create_Qlabel(
        #     label_name="result_gliding_v_constant_max_endurance",
        #     label_geometry=QRect(442, 761, 75, 16))
        # self.objects_list.append(self.result_gliding_v_constant_max_endurance)

        # Gráficos CL Constant
        # self.display_v_constant_graphs = QPushButton(self.centralwidget)
        # self.display_v_constant_graphs.setText("")  # Set an empty text to hide the label
        # self.display_v_constant_graphs.setGeometry(QRect(307, 653, 33, 31))
        # self.display_v_constant_graphs.setStyleSheet("border: none; background: none;")  # Hide border and background
        # self.display_v_constant_graphs.clicked.connect(self.invoke_gliding_v_constant_graphs)
        # self.objects_list.append(self.display_v_constant_graphs)


        # --------------------------------    RATE OF DESCENT AND GLIDING ANGLE    ------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#
        # self.result_rate_of_descent = self.create_Qlabel(
        #     label_name="result_rate_of_descent",
        #     label_geometry=QRect(675, 691, 75, 16))
        # self.objects_list.append(self.result_rate_of_descent)
        #
        # self.result_gliding_angle = self.create_Qlabel(
        #     label_name="result_gliding_angle",
        #     label_geometry=QRect(675, 714, 75, 16))
        # self.objects_list.append(self.result_gliding_angle)
        #
        self.display_rate_of_descent_gliding_angle_graph = self.create_QPushButton(
            handle_function=self.invoke_gliding_descending_graphs,
            label_geometry=QRect(744, 541, 33, 31))
        self.objects_list.append(self.display_rate_of_descent_gliding_angle_graph)

        #################################################################################################################
        # -------------------------------------------------- LOITER ----------------------------------------------------#
        #################################################################################################################

        self.result_loiter_time = self.create_Qlabel(
            label_name="loiter_time",
            label_geometry=QRect(554, 425, 89, 22))
        self.objects_list.append(self.result_loiter_time)

        #################################################################################################################
        # ------------------------------------------------- MANEVOUR ---------------------------------------------------#
        #################################################################################################################

        #Fastest
        self.turning_rate_fastest = self.create_Qlabel(
            label_name="turning_rate_fastest",
            label_geometry=QRect(561, 271, 61, 16))
        self.objects_list.append(self.turning_rate_fastest)

        self.load_factor_fastest = self.create_Qlabel(
            label_name="load_factor_fastest",
            label_geometry=QRect(561, 296, 61, 16))
        self.objects_list.append(self.load_factor_fastest)

        self.radius_factor_fastest = self.create_Qlabel(
            label_name="radius_factor_fastest",
            label_geometry=QRect(561, 321, 61, 16))
        self.objects_list.append(self.radius_factor_fastest)

        #Tighest
        self.turning_rate_tighest = self.create_Qlabel(
            label_name="turning_rate_tighest",
            label_geometry=QRect(630, 271, 61, 16))
        self.objects_list.append(self.turning_rate_tighest)

        self.load_factor_tighest = self.create_Qlabel(
            label_name="load_factor_tighest",
            label_geometry=QRect(630, 296, 61, 16))
        self.objects_list.append(self.load_factor_tighest)

        self.radius_factor_tighest = self.create_Qlabel(
            label_name="radius_factor_tighest",
            label_geometry=QRect(630, 321, 61, 16))
        self.objects_list.append(self.radius_factor_tighest)

        #Stall
        self.turning_rate_stall = self.create_Qlabel(
            label_name="turning_rate_stall",
            label_geometry=QRect(699, 271, 61, 16))
        self.objects_list.append(self.turning_rate_stall)

        self.load_factor_stall = self.create_Qlabel(
            label_name="load_factor_stall",
            label_geometry=QRect(699, 296, 61, 16))
        self.objects_list.append(self.load_factor_stall)

        self.radius_factor_stall = self.create_Qlabel(
            label_name="radius_factor_stall",
            label_geometry=QRect(699, 321, 61, 16))
        self.objects_list.append(self.radius_factor_stall)

        self.display_manevour_graphs = self.create_QPushButton(
            handle_function=self.invoke_manevour_graphs,
            label_geometry=QRect(685, 213, 33, 31))
        self.objects_list.append(self.display_manevour_graphs)

        #################################################################################################################
        # -------------------------------------------------- CRUISE ----------------------------------------------------#
        #################################################################################################################

        # Cruise Velocity
        self.result_cruise_velocity = self.create_Qlabel(
            label_name="result_cruise_velocity",
            label_geometry=QRect(165, 580, 57, 22))
        self.objects_list.append(self.result_cruise_velocity)

        # Minimum Drag
        self.result_cruise_minimum_drag = self.create_Qlabel(
            label_name="result_cruise_minimum_drag",
            label_geometry=QRect(269, 580, 57, 22))
        self.objects_list.append(self.result_cruise_minimum_drag)

        self.display_minimun_drag_graph = QPushButton(self.centralwidget)
        self.display_minimun_drag_graph.setText("")  # Set an empty text to hide the label
        self.display_minimun_drag_graph.setGeometry(QRect(339, 571, 33, 31))
        self.display_minimun_drag_graph.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_minimun_drag_graph.clicked.connect(self.invoke_minimum_drag_graph)
        self.objects_list.append(self.display_minimun_drag_graph)

        # Payload vs Range Drag
        self.display_payload_range_graph = QPushButton(self.centralwidget)
        self.display_payload_range_graph.setText("")  # Set an empty text to hide the label
        self.display_payload_range_graph.setGeometry(QRect(44, 571, 33, 31))
        self.display_payload_range_graph.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_payload_range_graph.clicked.connect(self.invoke_payload_range_graph)
        self.objects_list.append(self.display_payload_range_graph)

        ## Constant h-CL

        self.result_range_constant_h_cl = self.create_Qlabel(
            label_name="result_range_constant_h_cl",
            label_geometry=QRect(176, 454, 63, 22))
        self.objects_list.append(self.result_range_constant_h_cl)

        # self.result_max_range_constant_h_cl = self.create_Qlabel(
        #     label_name="result_max_range_constant_h_cl",
        #     label_geometry=QRect(455, 657, 63, 22))
        # self.objects_list.append(self.result_max_range_constant_h_cl)

        self.result_endurance_constant_h_cl = self.create_Qlabel(
            label_name="result_endurance_constant_h_cl",
            label_geometry=QRect(294, 454, 63, 22))
        self.objects_list.append(self.result_endurance_constant_h_cl)

        # self.result_max_endurance_constant_h_cl = self.create_Qlabel(
        #     label_name="result_max_endurance_constant_h_cl",
        #     label_geometry=QRect(693, 657, 63, 22))
        # self.objects_list.append(self.result_max_endurance_constant_h_cl)

        ## Constant V-CL

        self.result_range_constant_v_cl = self.create_Qlabel(
            label_name="result_range_constant_v_cl",
            label_geometry=QRect(176, 485, 63, 22))
        self.objects_list.append(self.result_range_constant_v_cl)

        # self.result_max_range_constant_v_cl = self.create_Qlabel(
        #     label_name="result_max_range_constant_v_cl",
        #     label_geometry=QRect(455, 687, 63, 22))
        # self.objects_list.append(self.result_max_range_constant_v_cl)

        self.result_endurance_constant_v_cl = self.create_Qlabel(
            label_name="result_endurance_constant_v_cl",
            label_geometry=QRect(294, 487, 63, 22))
        self.objects_list.append(self.result_endurance_constant_v_cl)

        # self.result_max_endurance_constant_v_cl = self.create_Qlabel(
        #     label_name="result_max_endurance_constant_v_cl",
        #     label_geometry=QRect(693, 687, 63, 22))
        # self.objects_list.append(self.result_max_endurance_constant_v_cl)



        ## Constant h-V

        self.result_range_constant_h_v = self.create_Qlabel(
            label_name="result_range_constant_h_v",
            label_geometry=QRect(176, 516, 63, 22))
        self.objects_list.append(self.result_range_constant_h_v)

        # self.result_max_range_constant_h_v = self.create_Qlabel(
        #     label_name="result_max_range_constant_h_v",
        #     label_geometry=QRect(455, 717, 63, 22))
        # self.objects_list.append(self.result_max_range_constant_h_v)

        self.result_endurance_constant_h_v = self.create_Qlabel(
            label_name="result_endurance_constant_h_v",
            label_geometry=QRect(294, 517, 63, 22))
        self.objects_list.append(self.result_endurance_constant_h_v)

        # self.result_max_endurance_constant_h_v = self.create_Qlabel(
        #     label_name="result_max_endurance_constant_h_v",
        #     label_geometry=QRect(693, 717, 63, 22))
        # self.objects_list.append(self.result_max_endurance_constant_h_v)


        #Gráfico Flight Path
        # self.display_flight_path_graph = QPushButton(self.centralwidget)
        # # self.display_flight_path_graph = QPushButton(self.layout_fig_phases)
        # self.display_flight_path_graph.setText("")  # Set an empty text to hide the label
        # self.display_flight_path_graph.setGeometry(QRect(9, 622, 780, 165))
        # self.display_flight_path_graph.setStyleSheet("border: none; background: none;")  # Hide border and background
        # self.display_flight_path_graph.clicked.connect(self.invoke_flight_path_graph)
        # self.objects_list.append(self.display_flight_path_graph)


        # --------------------------------------------------CLIMB -----------------------------------------------------#


        self.result_max_climb_angle = self.create_Qlabel(
            label_name="result_max_climb_angle",
            label_geometry=QRect(229, 248, 89, 22))
        self.objects_list.append(self.result_max_climb_angle)

        self.result_max_rate_of_climb = self.create_Qlabel(
            label_name="result_max_rate_of_climb",
            label_geometry=QRect(229, 273, 89, 22))
        self.objects_list.append(self.result_max_rate_of_climb)

        self.display_rate_of_climb_graph = QPushButton(self.centralwidget)
        self.display_rate_of_climb_graph.setText("")  # Set an empty text to hide the label
        self.display_rate_of_climb_graph.setGeometry(QRect(196, 213, 33, 31))
        self.display_rate_of_climb_graph.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_rate_of_climb_graph.clicked.connect(self.invoke_rate_of_climb_graph)
        self.objects_list.append(self.display_rate_of_climb_graph)

        self.climb_distance = self.create_Qlabel(
            label_name="climb_distance",
            label_geometry=QRect(229, 298, 89, 22))
        self.objects_list.append(self.climb_distance)

        self.climb_time = self.create_Qlabel(
            label_name="climb_time",
            label_geometry=QRect(229, 322, 89, 22))
        self.objects_list.append(self.climb_time)

        self.service_ceiling = self.create_Qlabel(
            label_name="service_ceiling",
            label_geometry=QRect(229, 347, 89, 22))
        self.objects_list.append(self.service_ceiling)

        # --------------------------------------------------------------------------------------------------------------#

        # Botão de Resultados
        self.download_sheets_results = QPushButton(self.centralwidget)
        self.download_sheets_results.setText("")  # Set an empty text to hide the label
        self.download_sheets_results.setGeometry(QRect(745, 48, 30, 30))
        self.download_sheets_results.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.download_sheets_results.clicked.connect(self.download_results)
        self.objects_list.append(self.download_sheets_results)

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        Results.setCentralWidget(self.centralwidget)

        self.background.raise_()

        for obj in self.objects_list:
            obj.raise_()

        self.statusbar = QStatusBar(Results)
        self.statusbar.setObjectName(u"statusbar")

        Results.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(Results)

        Results.setWindowTitle(QCoreApplication.translate("Results", u"Results", None))


    def calculate_takeoff_parameters(self):

        self.results_takeoff_distance = calc_total_takeoff_distance(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)
        self.results_takeoff_time = calc_total_takeoff_time(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)

        self.df_takeoff_per_altitude = calc_takeoff_distance_time_per_altitude(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)

        self.takeoff_distance_and_time_per_altitude.set_df(new_df=self.df_takeoff_per_altitude)

        self.result_takeoff_distance_value = self.results_takeoff_distance['TAKEOFF_DISTANCE']

        self.set_label_value(q_label=self.result_takeoff_distance,
                             value=str(round(self.result_takeoff_distance_value / 1000, 2)),
                             threshold=self.flight_parameters['takeoff_parameters']['AIRPORT_TAKEOFF_RUNWAY_DISTANCE']/1000)

        self.result_takeoff_time_value = self.results_takeoff_time['TAKEOFF_TIME']
        self.result_takeoff_time.setText(str(round(self.result_takeoff_time_value / 60, 2)))  # [min]

        self.result_takeoff_ground_distance = round(self.results_takeoff_distance['TAKEOFF_GROUND_DISTANCE'], 2)
        self.result_takeoff_rotation_distance = round(self.results_takeoff_distance['TAKEOFF_ROTATION_DISTANCE'], 2)
        self.result_takeoff_transition_distance = round(self.results_takeoff_distance['TAKEOFF_TRANSITION_DISTANCE'], 2)
        self.result_takeoff_climb_distance = round(self.results_takeoff_distance['TAKEOFF_CLIMB_DISTANCE'], 2)

        self.result_takeoff_ground_time = round(self.results_takeoff_time['TAKEOFF_GROUND_TIME'], 2)
        self.result_takeoff_rotation_time = round(self.results_takeoff_time['TAKEOFF_ROTATION_TIME'], 2)
        self.result_takeoff_transition_time = round(self.results_takeoff_time['TAKEOFF_TRANSITION_TIME'], 2)
        self.result_takeoff_climb_time = round(self.results_takeoff_time['TAKEOFF_CLIMB_TIME'], 2)

        self.createToolTip(x=10, y=153, label_text="", tooltip_text=
        f"Takeoff Distance per Phase [m]\n"
        f"Ground Distance: {self.result_takeoff_ground_distance}\n"
        f"Rotation Distance: {self.result_takeoff_rotation_distance}\n"
        f"Transition Distance: {self.result_takeoff_transition_distance}\n"
        f"Climb Distance: {self.result_takeoff_climb_distance}")

        self.createToolTip(x=10, y=178, label_text="", tooltip_text=
        f"Takeoff Time per Phase [s]\n"
        f"Ground Time: {self.result_takeoff_ground_time}\n"
        f"Rotation Time: {self.result_takeoff_rotation_time}\n"
        f"Transition Time: {self.result_takeoff_transition_time}\n"
        f"Climb Time: {self.result_takeoff_climb_time}")


    def calculate_landing_parameters(self):

        self.results_landing_distance = calc_total_landing_distance(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)
        self.results_landing_time = calc_total_landing_time(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)


        self.df_landing_per_altitude = calc_landing_distance_time_per_altitude(aircraft_parameters=self.aircraft_parameters, flight_parameters=self.flight_parameters)

        self.landing_distance_and_time_per_altitude.set_df(new_df=self.df_landing_per_altitude)


        self.result_landing_distance_value = self.results_landing_distance['LANDING_DISTANCE']

        self.result_landing_approach_distance = round(self.results_landing_distance['LANDING_APPROACH_DISTANCE'], 2)
        self.result_landing_rotation_distance = round(self.results_landing_distance['LANDING_ROTATION_DISTANCE'], 2)
        self.result_landing_roll_distance = round(self.results_landing_distance['LANDING_ROLL_DISTANCE'], 2)
        self.result_landing_flare_distance = round(self.results_landing_distance['LANDING_FLARE_DISTANCE'], 2)

        self.result_landing_approach_time = round(self.results_landing_time['LANDING_APPROACH_TIME'], 2)
        self.result_landing_rotation_time = round(self.results_landing_time['LANDING_ROTATION_TIME'], 2)
        self.result_landing_roll_time = round(self.results_landing_time['LANDING_ROLL_TIME'], 2)
        self.result_landing_flare_time = round(self.results_landing_time['LANDING_FLARE_TIME'], 2)


        self.result_landing_time_value = self.results_landing_time['LANDING_TIME']
        self.result_landing_time.setText(str(round(self.result_landing_time_value / 60, 2)))  # [min]

        self.set_label_value(q_label=self.result_landing_distance,
                             value=str(round(self.result_landing_distance_value / 1000, 2)),
                             threshold=self.flight_parameters['landing_parameters']['AIRPORT_LANDING_RUNWAY_DISTANCE'] / 1000)


        self.createToolTip(x=411, y=153, label_text="", tooltip_text=
        f"Landing Distance per Phase [m]\n"
        f"Approach Distance: {self.result_landing_approach_distance}\n"
        f"Rotation Distance: {self.result_landing_rotation_distance}\n"
        f"Roll Distance: {self.result_landing_roll_distance}\n"
        f"Flare Distance: {self.result_landing_flare_distance}")

        self.createToolTip(x=411, y=177, label_text="", tooltip_text=
        f"Landing Time  per Phase [s]\n"
        f"Approach Time: {self.result_landing_approach_time}\n"
        f"Rotation Time: {self.result_landing_rotation_time}\n"
        f"Roll Time: {self.result_landing_roll_time}\n"
        f"Flare Time: {self.result_landing_flare_time}")




    def update_parameters(self, new_aircraft_parameters, new_flight_parameters):

        self.aircraft_parameters = new_aircraft_parameters
        self.flight_parameters = new_flight_parameters

    def calculate_manevour_parameters(self):

        self.graph_load_factor_turning_rate_turning_radius_graph = calc_load_factor_turning_rate_turning_radius_graph(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)

        self.results_fastest_turn = calc_fastest_turn(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)
        self.results_tighest_turn = calc_tighest_turn(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)
        self.results_stall = calc_stall_turn(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)

        velocity_fastest_turn = self.results_fastest_turn['VELOCITY_FASTEST_TURN']
        load_factor_fastest_turn = round(self.results_fastest_turn['LOAD_FACTOR_FASTEST_TURN'], 2)
        eficiency_fastest_turn = self.results_fastest_turn['EFICIENCY_FASTEST_TURN']
        radius_fastest_turn = round(self.results_fastest_turn['RADIUS_FASTEST_TURN']/1000, 2)
        turning_rate_fastest_turn = round(self.results_fastest_turn['TURNING_RATE_FASTEST_TURN'], 2)

        velocity_tighest_turn = self.results_tighest_turn['VELOCITY_TIGHEST_TURN']
        load_factor_tighest_turn = round(self.results_tighest_turn['LOAD_FACTOR_TIGHEST_TURN'], 2)
        eficiency_tighest_turn = self.results_tighest_turn['EFICIENCY_TIGHEST_TURN']
        radius_tighest_turn = round(self.results_tighest_turn['RADIUS_TIGHEST_TURN']/1000, 2)
        turning_rate_tighest_turn = round(self.results_tighest_turn['TURNING_RATE_TIGHEST_TURN'], 2)

        velocity_stall = self.results_stall['VELOCITY_STALL']
        load_factor_stall = round(self.results_stall['LOAD_FACTOR_STALL'], 2)
        eficiency_stall = self.results_stall['EFICIENCY_STALL']
        radius_stall = round(self.results_stall['RADIUS_STALL']/1000, 2)
        turning_rate_stall = round(self.results_stall['TURNING_RATE_STALL'], 2)

        self.turning_rate_fastest.setText(str(turning_rate_fastest_turn))
        self.load_factor_fastest.setText(str(load_factor_fastest_turn))
        self.radius_factor_fastest.setText(str(radius_fastest_turn))

        self.turning_rate_tighest.setText(str(turning_rate_tighest_turn))
        self.load_factor_tighest.setText(str(load_factor_tighest_turn))
        self.radius_factor_tighest.setText(str(radius_tighest_turn))

        self.turning_rate_stall.setText(str(turning_rate_stall))
        self.load_factor_stall.setText(str(load_factor_stall))
        self.radius_factor_stall.setText(str(radius_stall))


    def calculate_cruising_parameters(self):


        self.results_cruise_velocity = calc_cruise_velocity(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters, plot=True)

        self.cruise_velocity_value = round(self.results_cruise_velocity['CRUISE_VELOCITY'], 2)
        self.result_cruise_velocity.setText(str(self.cruise_velocity_value))

        self.minimum_cruise_drag_value = self.results_cruise_velocity['MINIMUM_DRAG']
        self.result_cruise_minimum_drag.setText(str(round(self.minimum_cruise_drag_value / 1000, 2)))
        self.result_cruise_minimum_drag_graph = self.results_cruise_velocity['CRUISE_DRAG_GRAPH']

        self.cruise_velocities = self.results_cruise_velocity['CRUISE_VELOCITIES']

        self.result_graph_payload_range_graph = calc_payload_x_range(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)
        self.results_calc_cruise_fuel_weight = calc_cruise_fuel_weight(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)


        # Range
        self.results_cruising_range = calc_cruising_jet_range(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)

        # Loiter time

        self.result_loiter_time_value = self.results_cruising_range['LOITER_TIME']
        self.result_loiter_time.setText(str(round(self.result_loiter_time_value / 3600, 2)))

        ## h_CL
        self.result_range_constant_h_cl_value = self.results_cruising_range['RANGE_CONSTANT_HEIGHT_CL']
        self.result_max_range_constant_h_cl_value = self.results_cruising_range['MAX_RANGE_CONSTANT_HEIGHT_CL']

        self.result_range_constant_h_cl.setText(str(round(self.result_range_constant_h_cl_value / 1000, 2)))
        # self.result_max_range_constant_h_cl.setText(str(round(self.result_max_range_constant_h_cl_value / 1000, 2)))

        ## v_CL
        self.result_range_constant_v_cl_value = self.results_cruising_range['RANGE_CONSTANT_VELOCITY_CL']
        self.result_max_range_constant_v_cl_value = self.results_cruising_range['MAX_RANGE_CONSTANT_VELOCITY_CL']

        self.result_range_constant_v_cl.setText(str(round(self.result_range_constant_v_cl_value / 1000, 2)))
        # self.result_max_range_constant_v_cl.setText(str(round(self.result_max_range_constant_v_cl_value / 1000, 2)))

        ## h_V
        self.result_range_constant_h_v_value = self.results_cruising_range['RANGE_CONSTANT_HEIGHT_VELOCITY']
        self.result_max_range_constant_h_v_value = self.results_cruising_range['MAX_RANGE_CONSTANT_HEIGHT_VELOCITY']

        self.result_range_constant_h_v.setText(str(round(self.result_range_constant_h_v_value / 1000, 2)))
        # self.result_max_range_constant_h_v.setText(str(round(self.result_max_range_constant_h_v_value / 1000, 2)))

        ################ Endurance
        self.results_cruising_endurance = calc_cruising_jet_endurance(flight_parameters=self.flight_parameters, aircraft_parameters=self.aircraft_parameters)

        self.result_endurance_constant_h_cl_value = self.results_cruising_endurance['ENDURANCE_CONSTANT_HEIGHT_CL']
        self.result_max_endurance_constant_h_cl_value = self.results_cruising_endurance['MAX_ENDURANCE_CONSTANT_HEIGHT_CL']

        self.result_endurance_constant_h_cl.setText(str(round(self.result_endurance_constant_h_cl_value / 3600, 2)))
        # self.result_max_endurance_constant_h_cl.setText(str(round(self.result_max_endurance_constant_h_cl_value / 3600, 2)))

        self.result_endurance_constant_v_cl_value = self.results_cruising_endurance['ENDURANCE_CONSTANT_VELOCITY_CL']
        self.result_max_endurance_constant_v_cl_value = self.results_cruising_endurance['MAX_ENDURANCE_CONSTANT_VELOCITY_CL']

        self.result_endurance_constant_v_cl.setText(str(round(self.result_endurance_constant_v_cl_value / 3600, 2)))
        # self.result_max_endurance_constant_v_cl.setText(str(round(self.result_max_endurance_constant_v_cl_value / 3600, 2)))

        self.result_endurance_constant_h_v_value = self.results_cruising_endurance['ENDURANCE_CONSTANT_HEIGHT_VELOCITY']
        self.result_max_endurance_constant_h_v_value = self.results_cruising_endurance['MAX_ENDURANCE_CONSTANT_HEIGHT_VELOCITY']

        self.result_endurance_constant_h_v.setText(str(round(self.result_endurance_constant_h_v_value / 3600, 2)))
        # self.result_max_endurance_constant_h_v.setText(str(round(self.result_max_endurance_constant_h_v_value / 3600, 2)))

        self.createToolTip(x=10, y=456, label_text="", tooltip_text=
        f"Max Range & Endurance H-CL\n"
        f"Max Range [km]: {str(round(self.result_max_range_constant_h_cl_value / 1000, 2))}\n"
        f"Max Endurance: {str(round(self.result_max_endurance_constant_h_cl_value / 3600, 2))}")

        self.createToolTip(x=10, y=487, label_text="", tooltip_text=
        f"Max Range & Endurance V-CL\n"
        f"Max Range [km]: {str(round(self.result_max_range_constant_v_cl_value / 1000, 2))}\n"
        f"Max Endurance: {str(round(self.result_max_endurance_constant_v_cl_value / 3600, 2))}")

        self.createToolTip(x=10, y=518, label_text="", tooltip_text=
        f"Max Range & Endurance H-V\n"
        f"Max Range [km]: {str(round(self.result_max_range_constant_h_v_value / 1000, 2))}\n"
        f"Max Endurance: {str(round(self.result_max_endurance_constant_h_v_value / 3600, 2))}")


    def calculate_climb_parameters(self):
        self.result_max_climb_angle_rate_of_climb = calc_max_climb_angle_rate_of_climb(flight_parameters=self.flight_parameters,
                                                                                       aircraft_parameters=self.aircraft_parameters,
                                                                                       plot=True)

        self.result_service_ceiling_graph = calc_service_ceiling(flight_parameters=self.flight_parameters,
                                                                                       aircraft_parameters=self.aircraft_parameters)

        self.result_max_climb_angle_value = self.result_max_climb_angle_rate_of_climb['MAX_GAMMA_CLIMB']
        self.result_max_climb_angle.setText(str(round(math.degrees(self.result_max_climb_angle_value), 2)))

        self.result_rate_of_climb_value = self.result_max_climb_angle_rate_of_climb['MAX_RATE_OF_CLIMB']
        self.result_max_rate_of_climb.setText(str(round(self.result_rate_of_climb_value, 2)))

        self.result_graph_rate_of_climb = self.result_max_climb_angle_rate_of_climb['GRAPH_RATE_OF_CLIMB_PER_VELOCITY']

        self.result_cimb_time_distance_steepest = calc_distance_time_steepest_climb(flight_parameters=self.flight_parameters,
                                                                           aircraft_parameters=self.aircraft_parameters)

        self.result_distance_time_fastest_climb = calc_distance_time_fastest_climb(flight_parameters=self.flight_parameters,
                                                                                   aircraft_parameters=self.aircraft_parameters)

        self.climb_distance.setText(str(round(self.result_distance_time_fastest_climb['FASTEST_CLIMB_DISTANCE'] / 1000, 2)))
        self.createToolTip(x=10, y=302, label_text="", tooltip_text=
        f"Climb Distances [km]\n"
        f"Steepest Climb Distance: {round(self.result_cimb_time_distance_steepest['STEEPEST_CLIMB_DISTANCE'] / 1000, 2)}\n"
        f"Fastest Climb Distance: {round(self.result_distance_time_fastest_climb['FASTEST_CLIMB_DISTANCE'] / 1000, 2)}")


        self.climb_time.setText(str(round(self.result_distance_time_fastest_climb['FASTEST_CLIMB_TIME'] / 60, 2)))
        self.createToolTip(x=10, y=327, label_text="", tooltip_text=
        f"Climb Time [min]\n"
        f"Steepest Climb Time: {round(self.result_cimb_time_distance_steepest['STEEPEST_CLIMB_TIME'] / 60, 2)}\n"
        f"Fastest Climb Time: {round(self.result_distance_time_fastest_climb['FASTEST_CLIMB_TIME'] / 60, 2)}")


        self.service_ceiling.setText(str(round(self.result_service_ceiling_graph['SERVICE_CEILING'] / 1000, 2)))
        self.createToolTip(x=10, y=349, label_text="", tooltip_text=
        f"Ceiling Altitudes [km]\n"
        f"Service Ceiling: {round(self.result_service_ceiling_graph['SERVICE_CEILING'] / 1000, 2)}\n"
        f"Performance Ceiling: {round(self.result_service_ceiling_graph['PERFORMANCE_CEILING'] / 1000, 2)}\n"
        f"Operational Ceiling: {round(self.result_service_ceiling_graph['OPERATIONAL_CEILING'] / 1000, 2)}")

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

        # self.result_gliding_cl_constant_max_endurance.setText(str(self.result_gliding_cl_constant_max_endurance_value))
        # self.result_gliding_cl_constant_max_range.setText(str(self.result_gliding_cl_constant_max_range_value))

        # V Constant
        self.gliding_v_constant_graphs = self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_RANGE_ENDURANCE_CONSTANT_AIRSPEED_GRAPH']

        self.result_gliding_v_constant_default_range_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_RANGE_CONSTANT_AIRSPEED_STANDARD'] / 1000, 2)
        self.result_gliding_v_constant_default_endurance_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_ENDURANCE_CONSTANT_AIRSPEED_STANDARD'] / 3600, 2)

        # self.result_gliding_v_constant_max_endurance_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_MAX_ENDURANCE_CONSTANT_AIRSPEED'] / 3600, 2)
        # self.result_gliding_v_constant_max_range_value = round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_MAX_RANGE_CONSTANT_AIRSPEED'] / 1000, 2)

        self.result_gliding_v_constant_default_range.setText(str(self.result_gliding_v_constant_default_range_value))
        self.result_gliding_v_constant_default_endurance.setText(str(self.result_gliding_v_constant_default_endurance_value))

        # self.result_gliding_v_constant_max_endurance.setText(str(self.result_gliding_v_constant_max_endurance_value))
        # self.result_gliding_v_constant_max_range.setText(str(self.result_gliding_v_constant_max_range_value))


        # Rate of descent and gliding angle
        self.result_rate_of_descent_gliding_angle = gliding_angle_rate_of_descent(aircraft_parameters=self.aircraft_parameters,
                                                                                  flight_parameters=self.flight_parameters,
                                                                                  plot=True)
        self.result_rate_of_descent_value = self.result_rate_of_descent_gliding_angle['GLIDING_RATE_OF_DESCENT']
        self.result_gliding_angle_value = self.result_rate_of_descent_gliding_angle['GLIDING_ANGLE']

        self.gliding_rate_of_descent_graph = self.result_rate_of_descent_gliding_angle['RATE_OF_DESCENT_GRAPH']
        self.gliding_descending_angle_graph = self.result_rate_of_descent_gliding_angle['GLIDING_ANGLE_GRAPH']

        # self.result_gliding_angle.setText(str(self.result_gliding_angle_value))
        # self.result_rate_of_descent.setText(str(self.result_rate_of_descent_value))


    def download_results(self):

        self.results_data = {
            "CURRENT_DATE": str(datetime.now()),
            "AIRCRAFT_NAME": self.aircraft_parameters['AIRCRAFT_NAME'],
            "NUMBER_OF_PASSENGERS": self.flight_parameters['NUMBER_OF_PASSENGERS'],
            "FUEL_WEIGHT__KILOS": self.flight_parameters['FUEL_WEIGHT'] /(self.aero.g),
            "DISPATCHED_CARGO__WEIGHT_KILOS": self.flight_parameters['DISPATCHED_CARGO_WEIGHT'] /(self.aero.g),
            "CRUISE_ALTITUDE__METERS": self.flight_parameters['CRUISE_ALTITUDE'],
            "CRUISE_VELOCITY__METERS_PER_SECOND": self.flight_parameters['CRUISE_VELOCITY'],
            "GLIDING_VELOCITY__METERS_PER_SECOND": self.flight_parameters['GLIDING_VELOCITY'],
            "DEPARTURE_LOCATIOM": self.flight_parameters['takeoff_parameters']['AIRPORT_TAKEOFF_NAME'],
            "ARRIVAL_LOCATION": self.flight_parameters['landing_parameters']['AIRPORT_LANDING_NAME'],
            "TAKEOFF_DISTANCE__METERS": round(self.results_takeoff_distance['TAKEOFF_DISTANCE'],2),
            "TAKEOFF_TIME__SECONDS": round(self.results_takeoff_time['TAKEOFF_TIME'], 2),
            "LANDING_DISTANCE__METERS": round(self.results_landing_distance['LANDING_DISTANCE'], 2),
            "LANDING_TIME__SECONDS": round(self.results_landing_time['LANDING_TIME'], 2),
            "MAX_LOITER_TIME__SECONDS": round(self.results_cruising_range['LOITER_TIME'], 2),
            "MAX_CLIMB_ANGLE__DEGREE": round(self.result_max_climb_angle_rate_of_climb['MAX_GAMMA_CLIMB'], 2),
            "MAX_RATE_OF_CLIMB__METERS_PER_SECOND": round(self.result_max_climb_angle_rate_of_climb['MAX_RATE_OF_CLIMB'], 2),
            "CLIMB_DISTANCE_FASTEST_METERS": round(self.result_distance_time_fastest_climb['FASTEST_CLIMB_DISTANCE'], 2),
            "CLIMB_DISTANCE_STEEPEST_METERS": round(self.result_cimb_time_distance_steepest['STEEPEST_CLIMB_DISTANCE'], 2),
            "CLIMB_TIME_FASTEST_SECONDS": round(self.result_distance_time_fastest_climb['FASTEST_CLIMB_TIME'], 2),
            "CLIMB_TIME_STEEPEST_SECONDS": round(self.result_cimb_time_distance_steepest['STEEPEST_CLIMB_TIME'], 2),
            "SERVICE_CEILING__METERS": round(self.result_service_ceiling_graph['SERVICE_CEILING'], 2),
            "PERFORMANCE_CEILING__METERS": round(self.result_service_ceiling_graph['PERFORMANCE_CEILING'], 2),
            "OPERATIONAL_CEILING__METERS": round(self.result_service_ceiling_graph['OPERATIONAL_CEILING'], 2),
            "CRUISE_RANGE_HEIGHT_CL__METERS": round(self.results_cruising_range['RANGE_CONSTANT_HEIGHT_CL'], 2),
            "CRUISE_RANGE_VELOCITY_CL__METERS": round(self.results_cruising_range['RANGE_CONSTANT_VELOCITY_CL'], 2),
            "CRUISE_RANGE_HEIGHT_VELOCITY__METERS": round(self.results_cruising_range['RANGE_CONSTANT_HEIGHT_VELOCITY'], 2),
            "ENDURANCE_RANGE_HEIGHT_CL__SECONDS": round(self.results_cruising_endurance['ENDURANCE_CONSTANT_HEIGHT_CL'], 2),
            "ENDURANCE_RANGE_VELOCITY_CL__SECONDS": round(self.results_cruising_endurance['ENDURANCE_CONSTANT_VELOCITY_CL'], 2),
            "ENDURANCE_RANGE_HEIGHT_VELOCITY__SECONDS": round(self.results_cruising_endurance['ENDURANCE_CONSTANT_HEIGHT_VELOCITY'], 2),
            "MINIMUM_DRAG__NEWTON": round(self.results_cruise_velocity['MINIMUM_DRAG'], 2),
            "FASTEST_TURNING_RATE__RAD_PER_SECOND": round(self.results_fastest_turn['TURNING_RATE_FASTEST_TURN'], 2),
            "TIGHTEST_TURNING_RATE__RAD_PER_SECOND": round(self.results_tighest_turn['TURNING_RATE_TIGHEST_TURN'], 2),
            "FASTEST_LOAD_FACTOR": round(self.results_fastest_turn['LOAD_FACTOR_FASTEST_TURN'], 2),
            "TIGHTEST_LOAD_FACTOR": round(self.results_tighest_turn['LOAD_FACTOR_TIGHEST_TURN'], 2),
            "FASTEST_TURNING_RADIUS__METERS": round(self.results_fastest_turn['RADIUS_FASTEST_TURN'], 2),
            "TIGHTEST_TURNING_RADIUS__METERS": round(self.results_stall['RADIUS_STALL'], 2),
            "GLIDING_DISTANCE_V__METERS": round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_RANGE_CONSTANT_LIFT_STANDARD'], 2),
            "GLIDING_TIME_V__SECONDS": round(self.result_gliding_range_endurance['GLIDING_CONSTANT_LIFT']['GLIDING_ENDURANCE_CONSTANT_LIFT_STANDARD'], 2),
            "GLIDING_DISTANCE_CL__METERS": round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_RANGE_CONSTANT_AIRSPEED_STANDARD'], 2),
            "GLIDING_TIME_CL__SECONDS": round(self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_ENDURANCE_CONSTANT_AIRSPEED_STANDARD']),
            "CRUISE_DISTANCE_METERS": round(self.phase_parameters['CRUISE_DISTANCE_METERS'], 2),
            "NECESSARY_FUEL_KILOS": round(self.phase_parameters['NECESSARY_FUEL_KILOS'], 2),
            "ESTIMATED_TOTAL_FLIGHT_TIME_SECONDS": round(self.phase_parameters['ESTIMATED_TOTAL_FLIGHT_TIME_SECONDS'], 2)
        }

        self.df_results = DataFrame([self.results_data])
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV file", "", "CSV Files (*.csv)")
        self.df_results.to_csv(file_path, sep=";", mode="a", index=False)

    def calculate_flight_phases(self):

        results_takeoff_time = {
            "TAKEOFF_GROUND_TIME": self.result_takeoff_ground_time,
            "TAKEOFF_ROTATION_TIME": self.result_takeoff_rotation_time,
            "TAKEOFF_TRANSITION_TIME": self.result_takeoff_transition_time,
            "TAKEOFF_CLIMB_TIME": self.result_takeoff_climb_time
        }

        results_climb_time = {
            "FASTEST_CLIMB_TIME": self.result_distance_time_fastest_climb['FASTEST_CLIMB_TIME']
        }

        results_cruise_time = {
            "RESULT_CRUISE_VELOCITY": self.results_cruise_velocity,
            "RESULT_ENDURANCE_CONSTANT_H_V_VALUE": self.result_endurance_constant_h_v_value,
            "DELTA_FUEL": (self.results_calc_cruise_fuel_weight['DELTA_FUEL']/9.81)/1000,
            "VALID_FUEL": self.results_calc_cruise_fuel_weight['VALID_FUEL']
        }

        results_descending_time = {
            "RESULT_DESCENDING_TIME": self.result_gliding_range_endurance['GLIDING_CONSTANT_AIRSPEED']['GLIDING_ENDURANCE_CONSTANT_AIRSPEED_STANDARD']
        }

        results_landing_time = {
            "LANDING_APPROACH_TIME": self.result_landing_approach_time,
            "LANDING_ROTATION_TIME": self.result_landing_rotation_time,
            "LANDING_ROLL_TIME": self.result_landing_roll_time,
            "LANDING_FLARE_TIME": self.result_landing_flare_time
        }

        self.fig_phases, self.phase_parameters = plot_phases(
            flight_parameters=self.flight_parameters,
            results_takeoff_time=results_takeoff_time,
            results_climb_time=results_climb_time,
            results_cruise_time=results_cruise_time,
            results_descending_time=results_descending_time,
            results_landing_time=results_landing_time)

        self.copy_fig_phases, self.phase_parameters = plot_phases(
            flight_parameters=self.flight_parameters,
            results_takeoff_time=results_takeoff_time,
            results_climb_time=results_climb_time,
            results_cruise_time=results_cruise_time,
            results_descending_time=results_descending_time,
            results_landing_time=results_landing_time)

        # self.copy_fig_phases = copy.copy(self.fig_phases)

        self.canvas = FigureCanvas(self.fig_phases)
        self.canvas.setMinimumSize(7.5, 1.8)  # Convert inches to pixels
        for i in range(self.layout_fig_phases.count()): self.layout_fig_phases.itemAt(i).widget().close()
        self.layout_fig_phases.addWidget(self.canvas, alignment=Qt.AlignBottom)

        self.display_flight_path_graph = QPushButton(self.centralwidget)
        self.display_flight_path_graph.setText("")  # Set an empty text to hide the label
        self.display_flight_path_graph.setGeometry(QRect(9, 622, 780, 165))
        self.display_flight_path_graph.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.display_flight_path_graph.clicked.connect(self.invoke_flight_path_graph)







    def invoke_rate_of_climb_graph(self):

        c1 = self.result_graph_rate_of_climb.canvas
        c2 = self.result_service_ceiling_graph['RATE_OF_CLIMB_PER_ALTITUDE'].canvas

        c1.draw()
        c2.draw()

        a1 = array(c1.buffer_rgba())
        a2 = array(c2.buffer_rgba())
        a = hstack((a1, a2))

        mpl.use(backend)

        fig, ax = plt.subplots(figsize=(10,5))
        fig.subplots_adjust(0, 0, 1, 1)
        ax.set_axis_off()
        ax.matshow(a)
        fig.show()

    def invoke_flight_path_graph(self):

        show_figure(self.copy_fig_phases)
        self.copy_fig_phases.show()

    def invoke_manevour_graphs(self):

        self.graph_load_factor_turning_rate_turning_radius_graph.show()

    def invoke_minimum_drag_graph(self):
        self.result_cruise_minimum_drag_graph.show()

    def invoke_table_takeoff_distance_time(self):
        self.takeoff_distance_and_time_per_altitude.show()

    def invoke_table_landing_distance_time(self):
        self.landing_distance_and_time_per_altitude.show()

    def invoke_payload_range_graph(self):
        self.result_graph_payload_range_graph.show()


    def invoke_gliding_descending_graphs(self):

        # self.gliding_rate_of_descent_graph.show()
        # self.gliding_descending_angle_graph.show()
        # self.gliding_v_constant_graphs.show()
        # self.gliding_cl_constant_graphs.show()

        fig1 = self.gliding_rate_of_descent_graph.canvas
        fig2 = self.gliding_descending_angle_graph.canvas
        fig3 = self.gliding_v_constant_graphs.canvas
        fig4 = self.gliding_cl_constant_graphs.canvas


        fig1.draw()
        fig2.draw()
        fig3.draw()
        fig4.draw()

        # Convert canvas to numpy arrays
        a1 = array(fig1.buffer_rgba())
        a2 = array(fig2.buffer_rgba())
        a3 = array(fig3.buffer_rgba())
        a4 = array(fig4.buffer_rgba())

        # Combine arrays into a single array
        top_row = hstack((a1, a2))
        bottom_row = hstack((a3, a4))
        a_combined = vstack((top_row, bottom_row))

        mpl.use(backend)

        dpi = 400  # Adjust DPI as needed

        fig, ax = plt.subplots(figsize=(10, 7), dpi=dpi)
        ax.matshow(a_combined)
        ax.set_axis_off()
        plt.tight_layout()
        fig.show()





    def invoke_gliding_v_constant_graphs(self):

        self.gliding_v_constant_graphs.show()

    def invoke_gliding_cl_constant_graphs(self):

        self.gliding_cl_constant_graphs.show()

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

        #Manevour
        self.calculate_manevour_parameters()

        #Phases
        self.calculate_flight_phases()


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
