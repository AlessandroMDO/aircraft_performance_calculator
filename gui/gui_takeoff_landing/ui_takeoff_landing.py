import os
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import QtWidgets
from functions.utils import get_logger
from db.utils.db_utils import *
from functions.aero import Aero
from functions.landing import total_landing_distance, total_landing_time
from functions.takeoff import total_takeoff_distance, total_takeoff_time
from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QStackedWidget, QHBoxLayout, QPushButton, QWidget, QLabel, QCheckBox, QTextEdit


class GUI_DECOLAGEM(QMainWindow):
    def __init__(self, aircraft_parameters_class, background_path="TAKEOFF_LANDING_800_600.png"):

        self.aero = Aero()

        super(GUI_DECOLAGEM, self).__init__()

        self.logger = get_logger()

        self.aircraft_parameters_class = aircraft_parameters_class

        self.runway_condition_options = execute_generic_query(db_path=r"../../db/utils/aero.db", query="select superficie from GroundType;")
        self.airports = execute_generic_query(db_path=r"../../db/utils/aero.db", query="select iata, icao from Airports;", first_value=False)

        self.background_path = background_path
        self.run_analysis_button = None
        self.takeoff_parameters = None
        self.landing_parameters = None
        self.airport_landing_parameters = None
        self.current_landing_airport_iata = None
        self.airport_list_landing = None
        self.airport_takeoff_parameters = {}
        self.current_takeoff_airport_iata = None
        self.airport_takeoff_id = None
        self.wind_velocity_landing = None
        self.wind_velocity_landing_value = 0

        self.vento_contra_landing = None
        self.vento_contra_landing_flag = 1

        self.runway_slope_landing = None
        self.runway_slope_landing_value = 0

        self.runway_temperature_landing_value = None
        self.runway_temperature_landing = 0

        self.runway_condition_landing = None
        self.runway_condition_landing_mu = None
        self.runway_condition_landing_text = None



        # self.current_takeoff_airport = self.airports[0][0]
        # self.current_landing_airport = self.airports[0][0]



        self.runway_temperature_takeoff_value = 0
        self.runway_temperature_takeoff = None

        self.runway_slope_takeoff_value = 0
        self.runway_slope_takeoff = None

        self.vento_contra_takeoff_flag = 1
        self.vento_contra_takeoff = None

        self.wind_velocity_takeoff_value = 0
        self.wind_velocity_takeoff = None

        self.runway_condition_takeoff = None
        self.runway_condition_takeoff_text = None
        self.runway_condition_takeoff_mu = 0

        self.statusbar = None

        self.background = None
        self.airport_list_takeoff = None
        self.centralwidget = None

    def setupUi(self, Takeoff_Landing):
        if not Takeoff_Landing.objectName():
            Takeoff_Landing.setObjectName(u"Takeoff_Landing")
        Takeoff_Landing.resize(800, 600)
        Takeoff_Landing.setMinimumSize(QSize(800, 600))
        Takeoff_Landing.setMaximumSize(QSize(800, 600))
        self.centralwidget = QWidget(Takeoff_Landing)
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
        self.background.setGeometry(QRect(0, 0, 800, 600))
        self.background.setMinimumSize(QSize(800, 600))
        self.background.setMaximumSize(QSize(800, 600))
        self.background.setLayoutDirection(Qt.LeftToRight)
        self.background.setAutoFillBackground(False)
        self.background.setPixmap(QPixmap(self.background_path))
        self.background.update()
        self.background.setScaledContents(True)
        self.background.setAlignment(Qt.AlignCenter)
        self.background.setIndent(0)
        self.background.setText("")

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.run_analysis_button = QPushButton(self.centralwidget)
        self.run_analysis_button.setText("")  # Set an empty text to hide the label
        self.run_analysis_button.setGeometry(QRect(315, 541, 168, 33))
        self.run_analysis_button.setStyleSheet("border: none; background: none;")  # Hide border and background
        self.run_analysis_button.clicked.connect(self.invoke_run_analysis)

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#
        # ----------------------------------------------- TAKEOFF ------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- WIND VELOCITY TAKEOFF TEXT BOX ---------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.wind_velocity_takeoff = QTextEdit(self.centralwidget)
        self.wind_velocity_takeoff.setObjectName(u"wind_velocity_takeoff")
        self.wind_velocity_takeoff.setGeometry(QRect(215, 192, 79, 21))
        self.wind_velocity_takeoff.setFont(font)
        self.wind_velocity_takeoff.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.wind_velocity_takeoff.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wind_velocity_takeoff.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wind_velocity_takeoff.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.wind_velocity_takeoff.setLineWrapColumnOrWidth(500000)
        self.wind_velocity_takeoff.setTabStopWidth(80)
        self.wind_velocity_takeoff.setAcceptRichText(True)
        self.wind_velocity_takeoff.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the wind velocity.", None))
        self.wind_velocity_takeoff.textChanged.connect(self.handle_wind_velocity_takeoff_value)

        # -------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- RUNWAY SLOPE TAKEOFF TEXT BOX ---------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        self.runway_slope_takeoff = QTextEdit(self.centralwidget)
        self.runway_slope_takeoff.setObjectName(u"runway_slope_takeoff")
        self.runway_slope_takeoff.setGeometry(QRect(215, 250, 157, 21))
        self.runway_slope_takeoff.setFont(font)
        self.runway_slope_takeoff.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.runway_slope_takeoff.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_slope_takeoff.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_slope_takeoff.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.runway_slope_takeoff.setLineWrapColumnOrWidth(500000)
        self.runway_slope_takeoff.setTabStopWidth(80)
        self.runway_slope_takeoff.setAcceptRichText(True)
        self.runway_slope_takeoff.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the runway slope.", None))
        self.runway_slope_takeoff.textChanged.connect(self.handle_slope_takeoff_value)

        # -------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- TEMPERATURE TAKEOFF TEXT BOX ----------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        self.runway_temperature_takeoff = QTextEdit(self.centralwidget)
        self.runway_temperature_takeoff.setObjectName(u"runway_temperature_takeoff")
        self.runway_temperature_takeoff.setGeometry(QRect(215, 279, 157, 21))
        self.runway_temperature_takeoff.setFont(font)
        self.runway_temperature_takeoff.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.runway_temperature_takeoff.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_temperature_takeoff.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_temperature_takeoff.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.runway_temperature_takeoff.setLineWrapColumnOrWidth(500000)
        self.runway_temperature_takeoff.setTabStopWidth(80)
        self.runway_temperature_takeoff.setAcceptRichText(True)
        self.runway_temperature_takeoff.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the runway temperature.", None))
        self.runway_temperature_takeoff.textChanged.connect(self.handle_runway_temperature_takeoff_value)

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- WIND VELOCITY TAKEOFF CHECKBOX ---------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.vento_contra_takeoff = QCheckBox(self.centralwidget)
        self.vento_contra_takeoff.setObjectName(u"vento_contra_takeoff")
        self.vento_contra_takeoff.setGeometry(QRect(304, 192, 67, 16))
        self.vento_contra_takeoff.setText(QCoreApplication.translate("Takeoff_Landing", u"Against", None))
        self.vento_contra_takeoff.setChecked(False)
        self.vento_contra_takeoff.stateChanged.connect(self.handle_wind_takeoff_against_checkbox)

        # --------------------------------------------------------------------------------------------------------------#
        Takeoff_Landing.setCentralWidget(self.centralwidget)
        self.background.raise_()

        self.wind_velocity_takeoff.raise_()
        self.vento_contra_takeoff.raise_()
        self.runway_slope_takeoff.raise_()
        self.runway_temperature_takeoff.raise_()
        self.run_analysis_button.raise_()
        self.statusbar = QStatusBar(Takeoff_Landing)
        self.statusbar.setObjectName(u"statusbar")
        Takeoff_Landing.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(Takeoff_Landing)

        Takeoff_Landing.setWindowTitle(QCoreApplication.translate("Takeoff_Landing", u"Takeoff_Landing", None))

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- AIRPORTS LIST TAKEOFF --------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#
        self.airport_list_takeoff = QComboBox(self.centralwidget)
        self.airport_list_takeoff.setObjectName(u"airport_list_takeoff")
        self.airport_list_takeoff.setGeometry(QRect(215, 163, 157, 21))
        self.airport_list_takeoff.setFont(font)
        self.airport_list_takeoff.setLayoutDirection(Qt.LeftToRight)
        self.airport_list_takeoff.setEditable(False)
        self.airport_list_takeoff.setPalette(palette)

        count_airports_takeoff = 0
        for airport_code in self.airports:
            self.airport_list_takeoff.addItem("")
            airport_code_content = f"IATA: {airport_code[0]} / ICAO: {airport_code[1]}"
            self.airport_list_takeoff.setItemText(count_airports_takeoff, QCoreApplication.translate("Takeoff_Landing", f"{airport_code_content}", None))
            count_airports_takeoff += 1

        self.airport_list_takeoff.currentIndexChanged.connect(self.handle_airport_list_takeoff_change)

        self.airport_list_takeoff.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Select the departure airport", None))
        self.airport_list_takeoff.raise_()

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------ RUNWAY CONDITION TAKEOFF ------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.runway_condition_takeoff = QComboBox(self.centralwidget)
        self.runway_condition_takeoff.setObjectName(u"runway_condition_takeoff")
        self.runway_condition_takeoff.setGeometry(QRect(215, 221, 157, 21))

        self.runway_condition_takeoff.setPalette(palette1)
        self.runway_condition_takeoff.setFont(font)
        self.runway_condition_takeoff.setLayoutDirection(Qt.LeftToRight)
        self.runway_condition_takeoff.setEditable(False)

        self.runway_condition_takeoff.raise_()
        self.runway_condition_takeoff.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Select the runway condition", None))

        count_runway_condition_takeoff = 0
        runway_condition_options = self.runway_condition_options
        for airport_runway_condition in runway_condition_options:
            self.runway_condition_takeoff.addItem("")
            self.runway_condition_takeoff.setItemText(count_runway_condition_takeoff, QCoreApplication.translate("Takeoff_Landing", f"{airport_runway_condition}", None))
            count_runway_condition_takeoff += 1

        self.runway_condition_takeoff.currentIndexChanged.connect(self.handle_runway_takeoff_condition_change)

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#
        # ----------------------------------------------- LANDING ------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- WIND VELOCITY LANDING TEXT BOX ---------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.wind_velocity_landing = QTextEdit(self.centralwidget)
        self.wind_velocity_landing.setObjectName(u"wind_velocity_landing")
        self.wind_velocity_landing.setGeometry(QRect(614, 192, 79, 21))
        self.wind_velocity_landing.setFont(font)
        self.wind_velocity_landing.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.wind_velocity_landing.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wind_velocity_landing.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wind_velocity_landing.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.wind_velocity_landing.setLineWrapColumnOrWidth(500000)
        self.wind_velocity_landing.setTabStopWidth(80)
        self.wind_velocity_landing.setAcceptRichText(True)
        self.wind_velocity_landing.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the wind velocity.", None))
        self.wind_velocity_landing.textChanged.connect(self.handle_wind_velocity_landing_value)

        self.wind_velocity_landing.raise_()
        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- WIND VELOCITY CHECKBOX LANDING ---------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.vento_contra_landing = QCheckBox(self.centralwidget)
        self.vento_contra_landing.setObjectName(u"vento_contra_landing")
        self.vento_contra_landing.setGeometry(QRect(703, 192, 67, 16))
        self.vento_contra_landing.setText(QCoreApplication.translate("Takeoff_Landing", u"Against", None))
        self.vento_contra_landing.setChecked(False)
        self.vento_contra_landing.stateChanged.connect(self.handle_wind_landing_against_checkbox)

        # -------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- RUNWAY SLOPE LANDING TEXT BOX ---------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        self.runway_slope_landing = QTextEdit(self.centralwidget)
        self.runway_slope_landing.setObjectName(u"runway_slope_landing")
        self.runway_slope_landing.setGeometry(QRect(614, 250, 157, 21))
        self.runway_slope_landing.setFont(font)
        self.runway_slope_landing.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.runway_slope_landing.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_slope_landing.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_slope_landing.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.runway_slope_landing.setLineWrapColumnOrWidth(500000)
        self.runway_slope_landing.setTabStopWidth(80)
        self.runway_slope_landing.setAcceptRichText(True)
        self.runway_slope_landing.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the runway slope.", None))
        self.runway_slope_landing.textChanged.connect(self.handle_slope_landing_value)

        self.runway_slope_landing.raise_()
        # --------------------------------------------------------------------------------------------------------------#
        # ----------------------------------------- RUNWAY TEMPERATURE LANDING -----------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.runway_temperature_landing = QTextEdit(self.centralwidget)
        self.runway_temperature_landing.setObjectName(u"runway_temperature_landing")
        self.runway_temperature_landing.setGeometry(QRect(614, 279, 157, 21))
        self.runway_temperature_landing.setFont(font)
        self.runway_temperature_landing.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.runway_temperature_landing.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_temperature_landing.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_temperature_landing.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.runway_temperature_landing.setLineWrapColumnOrWidth(500000)
        self.runway_temperature_landing.setTabStopWidth(80)
        self.runway_temperature_landing.setAcceptRichText(True)
        self.runway_temperature_landing.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the runway temperature.", None))
        self.runway_temperature_landing.textChanged.connect(self.handle_runway_temperature_landing_value)

        self.runway_temperature_landing.raise_()

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- AIRPORTS LIST LANDING --------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#
        self.airport_list_landing = QComboBox(self.centralwidget)
        self.airport_list_landing.setObjectName(u"airport_list_landing")
        self.airport_list_landing.setGeometry(QRect(614, 163, 157, 21))
        self.airport_list_landing.setFont(font)
        self.airport_list_landing.setLayoutDirection(Qt.LeftToRight)
        self.airport_list_landing.setEditable(False)
        self.airport_list_landing.setPalette(palette)

        count_airports_landing = 0
        for airport_code in self.airports:
            self.airport_list_landing.addItem("")
            airport_code_content = f"IATA: {airport_code[0]} / ICAO: {airport_code[1]}"
            self.airport_list_landing.setItemText(count_airports_landing, QCoreApplication.translate("Takeoff_Landing", f"{airport_code_content}", None))
            count_airports_landing += 1

        self.airport_list_landing.currentIndexChanged.connect(self.handle_airport_list_landing_change)

        self.airport_list_landing.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Select the arrival airport", None))
        self.airport_list_landing.raise_()

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------ RUNWAY CONDITION LANDING ------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.runway_condition_landing = QComboBox(self.centralwidget)
        self.runway_condition_landing.setObjectName(u"runway_condition_landing")
        self.runway_condition_landing.setGeometry(QRect(614, 221, 157, 21))

        self.runway_condition_landing.setPalette(palette1)
        self.runway_condition_landing.setFont(font)
        self.runway_condition_landing.setLayoutDirection(Qt.LeftToRight)
        self.runway_condition_landing.setEditable(False)

        self.runway_condition_landing.raise_()
        self.runway_condition_landing.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Select the runway condition", None))

        count_runway_condition_landing = 0
        runway_condition_options = self.runway_condition_options
        for airport in runway_condition_options:
            self.runway_condition_landing.addItem("")
            self.runway_condition_landing.setItemText(count_runway_condition_landing, QCoreApplication.translate("Takeoff_Landing", f"{airport}", None))
            count_runway_condition_landing += 1

        self.runway_condition_landing.currentIndexChanged.connect(self.handle_runway_landing_condition_change)

    # -----------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------- HANDLE TAKEOFF FUNCTIONS --------------------------------------------#
    # -----------------------------------------------------------------------------------------------------------------#

    def handle_runway_takeoff_condition_change(self):

        self.runway_condition_takeoff_text = self.runway_condition_takeoff.currentText()

    def calculate_runway_takeoff_condition_parameter(self):
        self.runway_condition_takeoff_mu = execute_generic_query(
            db_path=r"../../db/utils/aero.db",
            query=f"select (min_mu_decolagem + max_mu_decolagem)/2 from GroundType where superficie='{self.runway_condition_takeoff_text}';")

    def handle_wind_velocity_takeoff_value(self):

        text_value_wind_velocity = self.wind_velocity_takeoff.toPlainText()

        if not text_value_wind_velocity:
            self.wind_velocity_takeoff.setPlainText("0")
        else:
            try:
                wind_velocity = float(text_value_wind_velocity)
                if 0 <= wind_velocity < 10000:
                    self.wind_velocity_takeoff_value = int(self.vento_contra_takeoff_flag) * wind_velocity
                else:
                    self.wind_velocity_takeoff.clear()
            except ValueError:
                self.wind_velocity_takeoff.clear()

        self.logger.debug(f"Wind Velocity Takeoff: {self.wind_velocity_takeoff_value}")


    def handle_runway_temperature_takeoff_value(self):

        text_runway_temperature_takeoff = self.runway_temperature_takeoff.toPlainText()

        # Checamos se a caixa de texto está vazia
        if not text_runway_temperature_takeoff:
            self.wind_velocity_takeoff.setPlainText("0")
        else:
            try:
                temperature_takeoff = float(text_runway_temperature_takeoff)
                if 0 <= temperature_takeoff < 1000:
                    self.runway_temperature_takeoff_value = temperature_takeoff
                else:
                    self.runway_temperature_takeoff.clear()
            except ValueError:
                self.runway_temperature_takeoff.clear()

        self.logger.debug(f"Runway Temperature Takeoff: {self.runway_temperature_takeoff_value}")


    def handle_slope_takeoff_value(self):

        text_runway_slope_takeoff = self.runway_slope_takeoff.toPlainText()

        # Checamos se a caixa de texto está vazia
        if not text_runway_slope_takeoff:
            self.runway_slope_takeoff.setPlainText("0")
        else:
            try:
                runway_slope_value = float(text_runway_slope_takeoff)
                self.runway_slope_takeoff_value = runway_slope_value
            except ValueError:
                self.runway_slope_takeoff.clear()

        self.logger.debug(f"Runway Slope Takeoff: {self.runway_slope_takeoff_value}")


    def handle_wind_takeoff_against_checkbox(self):

        self.vento_contra_takeoff_flag = -1 if self.vento_contra_takeoff.isChecked() else 1
        self.handle_wind_velocity_takeoff_value()

    def handle_airport_list_takeoff_change(self):

        current_takeoff_airport = self.airport_list_takeoff.currentText()

        self.current_takeoff_airport_iata = current_takeoff_airport[6:9]
        self.airport_takeoff_parameters = {}

    def calculate_takeoff_airport_parameters(self):
        print(self.airport_list_takeoff.currentText())
        print(self.current_takeoff_airport_iata)
        print(self.current_takeoff_airport_iata is None)
        airport_takeoff_results = execute_generic_query(
            db_path=r"../../db/utils/aero.db",
            query=f"select elevacao, pista, latitude, longitude, '{self.current_takeoff_airport_iata}' as airport_code from airports where iata='{self.current_takeoff_airport_iata}';",
            first_value=False)

        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_ELEVATION'] = airport_takeoff_results[0][0]
        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_RUNWAY_DISTANCE'] = airport_takeoff_results[0][1]
        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_LATITUDE'] = airport_takeoff_results[0][2]
        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_LONGITUDE'] = airport_takeoff_results[0][3]
        self.airport_takeoff_parameters['AIRPORT_IATA_CODE'] = airport_takeoff_results[0][4]

        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_DENSITY'] = self.aero.get_density(self.airport_takeoff_parameters['AIRPORT_TAKEOFF_ELEVATION'])

    # -----------------------------------------------------------------------------------------------------------------#
    # ------------------------------------------- HANDLE LANDING FUNCTIONS --------------------------------------------#
    # -----------------------------------------------------------------------------------------------------------------#

    def handle_runway_landing_condition_change(self):

        self.runway_condition_landing_text = self.runway_condition_landing.currentText()

    def calculate_runway_landing_condition_parameter(self):
        self.runway_condition_landing_mu = execute_generic_query(
            db_path=r"../../db/utils/aero.db",
            query=f"select (min_mu_decolagem + max_mu_decolagem)/2 from GroundType where superficie='{self.runway_condition_landing_text}';")

    def handle_runway_temperature_landing_value(self):

        text_runway_temperature_landing = self.runway_temperature_landing.toPlainText()

        # Checamos se a caixa de texto está vazia
        if not text_runway_temperature_landing:
            self.wind_velocity_takeoff.setPlainText("0")
        else:
            try:
                temperature_landing = float(text_runway_temperature_landing)
                if 0 <= temperature_landing < 1000:
                    self.runway_temperature_landing_value = temperature_landing
                else:
                    self.runway_temperature_landing.clear()
            except ValueError:
                self.runway_temperature_landing.clear()

        self.logger.debug(f"Runway Temperature Landing: {self.runway_temperature_landing_value}")


    def handle_slope_landing_value(self):

        text_runway_slope_landing = self.runway_slope_landing.toPlainText()
        self.logger.debug(f"Runway Slope Landing: {text_runway_slope_landing}")

        # Checamos se a caixa de texto está vazia
        if not text_runway_slope_landing:
            self.runway_slope_landing.setPlainText("0")
        else:
            try:
                runway_slope_value = float(text_runway_slope_landing)

                if abs(runway_slope_value) <= 45:
                    self.runway_slope_landing_value = runway_slope_value
                else:
                    self.runway_slope_landing.clear()
            except ValueError:
                self.runway_slope_landing.clear()

        self.logger.debug(f"Runway Slope Landing: {self.runway_slope_landing_value}")

    def handle_wind_landing_against_checkbox(self):
        self.vento_contra_landing_flag = -1 if self.vento_contra_landing.isChecked() else 1
        self.handle_wind_velocity_landing_value()

    def handle_wind_velocity_landing_value(self):

        text_value_wind_velocity = self.wind_velocity_landing.toPlainText()

        if not text_value_wind_velocity:
            self.wind_velocity_landing.setPlainText("0")
        else:
            try:
                wind_velocity = float(text_value_wind_velocity)
                if 0 <= wind_velocity < 10000:
                    self.wind_velocity_landing_value = int(self.vento_contra_landing_flag) * wind_velocity
                else:
                    self.wind_velocity_landing.clear()
            except ValueError:
                self.wind_velocity_landing.clear()

        self.logger.debug(f"Wind Velocity Landing: {self.wind_velocity_landing_value}")

    def handle_airport_list_landing_change(self):

        current_landing_airport = self.airport_list_landing.currentText()
        self.current_landing_airport_iata = current_landing_airport[6:9]
        self.airport_landing_parameters = {}

    def calculate_landing_airport_parameters(self):
        airport_landing_results = execute_generic_query(
            db_path=r"../../db/utils/aero.db",
            query=f"select elevacao, pista, latitude, longitude, '{self.current_landing_airport_iata}' as airport_code from airports where iata='{self.current_landing_airport_iata}';",
            first_value=False)

        self.airport_landing_parameters['AIRPORT_LANDING_ELEVATION']        = airport_landing_results[0][0]
        self.airport_landing_parameters['AIRPORT_LANDING_RUNWAY_DISTANCE']  = airport_landing_results[0][1]
        self.airport_landing_parameters['AIRPORT_LANDING_LATITUDE']         = airport_landing_results[0][2]
        self.airport_landing_parameters['AIRPORT_LANDING_LONGITUDE']        = airport_landing_results[0][3]
        self.airport_landing_parameters['AIRPORT_IATA_CODE']                = airport_landing_results[0][4]

    # -----------------------------------------------------------------------------------------------------------------#
    # -----------------------------------------------------------------------------------------------------------------#
    # -----------------------------------------------------------------------------------------------------------------#

    def invoke_run_analysis(self):

        # Guardando os parametros do aeroporto takeoff na variavel self.airport_takeoff_parameters
        self.calculate_takeoff_airport_parameters()
        self.logger.debug(f"Airport Takeoff Parameters: {self.airport_takeoff_parameters}")

        # Guardando os parametros do aeroporto landing na variavel self.airport_landing_parameters
        self.calculate_landing_airport_parameters()
        self.logger.debug(f"Airport Landing Parameters: {self.airport_landing_parameters}")

        # Guardando o atrito da pista decolagem self.runway_condition_takeoff_mu
        self.calculate_runway_takeoff_condition_parameter()
        self.logger.debug(f"Runway Condition Takeoff Mu: {self.runway_condition_takeoff_mu}")

        # Guardando o atrito da pista pouso self.runway_condition_landing_mu
        self.calculate_runway_landing_condition_parameter()
        self.logger.debug(f"Runway Condition Landing Mu: {self.runway_condition_landing_mu}")


        # self.landing_parameters = {
        #     "altitude_landing": self.airport_landing_parameters['airport_landing_elevation'],
        #     "mu_landing": self.runway_condition_landing_mu,
        #     "runway_slope_landing": self.runway_slope_landing_value,
        #     "runway_temperature_landing": self.runway_temperature_landing_value,
        #     "wind_velocity_landing": self.wind_velocity_landing_value
        # }
        #
        # self.takeoff_parameters = {
        #     "altitude_takeoff": self.airport_takeoff_parameters['airport_takeoff_elevation'],
        #     "mu_takeoff": self.runway_condition_takeoff_mu,
        #     "runway_slope_takeoff": self.runway_slope_takeoff_value,
        #     "runway_temperature_takeoff": self.runway_temperature_takeoff_value,
        #     "wind_velocity_takeoff": self.wind_velocity_takeoff_value
        # }

        # print(self.takeoff_parameters)
        # print(self.landing_parameters)

        # aircraft_parameters = {
        #     'stall_velocity': 25,
        #     'mtow': 5000,
        #     'surface_area': 500,
        #     'K': 0.4,
        #     'CD0': 0.04,
        #     'T': 200,
        #     'D': 100
        # }

        self.aircraft_parameters = self.aircraft_parameters_class.get_aircraft_parameters()

        self.takeoff_parameters = {
            "STALL_VELOCITY": self.aero.calculate_stall_velocity(
                W=self.aircraft_parameters['MTOW'],
                S=self.aircraft_parameters['SURFACE_AREA'],
                CL_max=self.aircraft_parameters['CL_MAX'],
                rho=self.airport_takeoff_parameters['AIRPORT_TAKEOFF_DENSITY'],
                logger=self.logger),
            "ALTITUDE_TAKEOFF": self.airport_takeoff_parameters['AIRPORT_TAKEOFF_ELEVATION'],
            "MU_TAKEOFF": self.runway_condition_takeoff_mu,
            "RUNWAY_SLOPE_TAKEOFF": self.runway_slope_takeoff_value,
            "RUNWAY_TEMPERATURE_TAKEOFF": self.runway_temperature_takeoff_value,
            "WIND_VELOCITY_TAKEOFF": self.wind_velocity_takeoff_value,
            "T": 200,
            "D": 100
        }

        self.logger.debug(f"Takeoff Parameters: {self.takeoff_parameters}")

        self.takeoff_distance = total_takeoff_distance(takeoff_parameters=self.takeoff_parameters, aircraft_parameters=self.aircraft_parameters, show=True)
        self.takeoff_time = total_takeoff_time(takeoff_parameters=self.takeoff_parameters, aircraft_parameters=self.aircraft_parameters, show=True)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = GUI_DECOLAGEM()
    w = QtWidgets.QMainWindow()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())
