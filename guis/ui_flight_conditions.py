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

class GUI_FLIGHT_CONDITIONS(QMainWindow):

    def __init__(self, background_path="guis/FLIGHT_CONDITIONS_800_800.png"):

        super(GUI_FLIGHT_CONDITIONS, self).__init__()

        self.fw_value = None
        self.oew_value = None
        self.ne_value = None
        self.e_value = None
        self.aero = Aero()
        self.display_altitude_landing_value = None

        self.k = None
        self.cd0 = None
        self.cl_max = None
        self.wing_area = None
        self.logger = get_logger()

        self.aircraft_list_db = None
        self.current_aircraft_db = None
        self.wing_area_value = None
        self.k_value = None
        self.cd0_value = None
        self.cl_max_value = None
        self.text_aircraft_name = None
        self.new_aircraft_name = None
        self.background_path = background_path

        _, self.aircrafts_parameters = execute_generic_query(db_path=r"./db/utils/aero.db", query="select * from Airplanes;", first_value=False)
        self.airports, _ = execute_generic_query(db_path=r"./db/utils/aero.db", query="select iata, icao from Airports;", first_value=False)
        self.runway_condition_options, _ = execute_generic_query(db_path=r"./db/utils/aero.db", query="select superficie from GroundType;")

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

    def setupUi(self, Flight_Conditions):
        if not Flight_Conditions.objectName():
            Flight_Conditions.setObjectName(u"Flight_Conditions")
        Flight_Conditions.resize(800, 800)
        Flight_Conditions.setMinimumSize(QSize(800, 830))
        Flight_Conditions.setMaximumSize(QSize(800, 830))
        self.centralwidget = QWidget(Flight_Conditions)
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
        # ----------------------------------- NUMBER OF PASSANGERS NUMBER BOX ------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.np = QTextEdit(self.centralwidget)
        self.np.setObjectName(u"np")
        self.np.setGeometry(QRect(298, 117, 95, 22))
        self.np.setFont(font)
        self.np.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.np.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.np.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.np.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.np.setLineWrapColumnOrWidth(500000)
        self.np.setTabStopWidth(80)
        self.np.setText("10")
        self.np.setAcceptRichText(True)
        self.np.setToolTip(QCoreApplication.translate("Flight_Conditions", u"Number of passengers", None))
        self.np.textChanged.connect(self.handle_np_value)

        # --------------------------------------------------------------------------------------------------------------#
        # ----------------------------------- FUEL WEIGHT NUMBER BOX ------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.fw = QTextEdit(self.centralwidget)
        self.fw.setObjectName(u"fw")
        self.fw.setGeometry(QRect(298, 147, 95, 22))
        self.fw.setFont(font)
        self.fw.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.fw.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.fw.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.fw.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.fw.setLineWrapColumnOrWidth(500000)
        self.fw.setTabStopWidth(80)
        self.fw.setAcceptRichText(True)
        self.fw.setToolTip(QCoreApplication.translate("Flight_Conditions", u"Fuel Weight", None))
        self.fw.textChanged.connect(self.handle_fw_value)

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------- DISPATCHED CARGO NUMBER BOX --------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.pw = QTextEdit(self.centralwidget)
        self.pw.setObjectName(u"pw")
        self.pw.setGeometry(QRect(298, 177, 95, 22))
        self.pw.setFont(font)
        self.pw.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.pw.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pw.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pw.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.pw.setLineWrapColumnOrWidth(500000)
        self.pw.setTabStopWidth(80)
        self.pw.setAcceptRichText(True)
        self.pw.setToolTip(QCoreApplication.translate("Flight_Conditions", u"Dispatched Cargo Weight", None))
        self.pw.textChanged.connect(self.handle_pw_value)


        # ------------------------------------------------------------------------------------------------------------ #
        # -------------------------------------------- TAKEOFF---------------------------------------------------------#
        # ------------------------------------------------------------------------------------------------------------ #

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- WIND VELOCITY TAKEOFF TEXT BOX ---------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.wind_velocity_takeoff = QTextEdit(self.centralwidget)
        self.wind_velocity_takeoff.setObjectName(u"wind_velocity_takeoff")
        self.wind_velocity_takeoff.setGeometry(QRect(214, 314, 79, 28))
        self.wind_velocity_takeoff.setFont(font)
        self.wind_velocity_takeoff.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.wind_velocity_takeoff.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wind_velocity_takeoff.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wind_velocity_takeoff.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.wind_velocity_takeoff.setLineWrapColumnOrWidth(500000)
        self.wind_velocity_takeoff.setTabStopWidth(80)
        self.wind_velocity_takeoff.setAcceptRichText(True)
        self.wind_velocity_takeoff.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the wind velocity.", None))
        self.wind_velocity_takeoff.setText("0")
        self.wind_velocity_takeoff.textChanged.connect(self.handle_wind_velocity_takeoff_value)

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- WIND VELOCITY TAKEOFF CHECKBOX ---------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.vento_contra_takeoff = QCheckBox(self.centralwidget)
        self.vento_contra_takeoff.setObjectName(u"vento_contra_takeoff")
        self.vento_contra_takeoff.setGeometry(QRect(303, 314, 67, 16))
        self.vento_contra_takeoff.setText(QCoreApplication.translate("Takeoff_Landing", u"Against", None))
        self.vento_contra_takeoff.setChecked(False)
        self.vento_contra_takeoff.stateChanged.connect(self.handle_wind_takeoff_against_checkbox)

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- AIRPORTS LIST TAKEOFF --------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#
        self.airport_list_takeoff = QComboBox(self.centralwidget)
        self.airport_list_takeoff.setObjectName(u"airport_list_takeoff")
        self.airport_list_takeoff.setGeometry(QRect(215, 275.33, 157, 28))
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
        self.airport_list_takeoff.setCurrentIndex(0)
        self.logger.debug(self.airport_list_takeoff.currentIndex())

        current_takeoff_airport = self.airport_list_takeoff.currentText()
        self.logger.debug(f"current_takeoff_airport: {current_takeoff_airport}")

        self.current_takeoff_airport_iata = current_takeoff_airport[6:9]
        self.logger.debug(f"current_takeoff_airport_iata: {self.current_takeoff_airport_iata}")

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------ RUNWAY CONDITION TAKEOFF ------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.runway_condition_takeoff = QComboBox(self.centralwidget)
        self.runway_condition_takeoff.setObjectName(u"runway_condition_takeoff")
        self.runway_condition_takeoff.setGeometry(QRect(215, 352.67, 157, 28))

        self.runway_condition_takeoff.setPalette(palette1)
        self.runway_condition_takeoff.setFont(font)
        self.runway_condition_takeoff.setLayoutDirection(Qt.LeftToRight)
        self.runway_condition_takeoff.setEditable(False)

        self.runway_condition_takeoff.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Select the runway condition", None))

        count_runway_condition_takeoff = 0
        runway_condition_options = self.runway_condition_options
        for airport_runway_condition in runway_condition_options:
            self.runway_condition_takeoff.addItem("")
            self.runway_condition_takeoff.setItemText(count_runway_condition_takeoff, QCoreApplication.translate("Takeoff_Landing", f"{airport_runway_condition}", None))
            count_runway_condition_takeoff += 1

        self.runway_condition_takeoff.currentIndexChanged.connect(self.handle_runway_takeoff_condition_change)
        self.runway_condition_takeoff.setCurrentIndex(0)
        self.runway_condition_takeoff_text = self.runway_condition_takeoff.currentText()

        # -------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- RUNWAY SLOPE TAKEOFF TEXT BOX ---------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        self.runway_slope_takeoff = QTextEdit(self.centralwidget)
        self.runway_slope_takeoff.setObjectName(u"runway_slope_takeoff")
        self.runway_slope_takeoff.setGeometry(QRect(215, 391.33, 157, 28))
        self.runway_slope_takeoff.setFont(font)
        self.runway_slope_takeoff.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.runway_slope_takeoff.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_slope_takeoff.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_slope_takeoff.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.runway_slope_takeoff.setLineWrapColumnOrWidth(500000)
        self.runway_slope_takeoff.setTabStopWidth(80)
        self.runway_slope_takeoff.setAcceptRichText(True)
        self.runway_slope_takeoff.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the runway slope.", None))
        self.runway_slope_takeoff.setText("0")
        self.runway_slope_takeoff.textChanged.connect(self.handle_slope_takeoff_value)

        self.display_altitude_takeoff = QLabel(self.centralwidget)
        self.display_altitude_takeoff.setObjectName(u"altitude_takeoff")
        self.display_altitude_takeoff.setGeometry(QRect(215, 435, 157, 12))
        self.display_altitude_takeoff.setFont(font)

        self.display_runway_lenght_takeoff = QLabel(self.centralwidget)
        self.display_runway_lenght_takeoff.setObjectName(u"runway_takeoff")
        self.display_runway_lenght_takeoff.setGeometry(QRect(215, 455, 157, 12))
        self.display_runway_lenght_takeoff.setFont(font)

        self.display_airport_name_takeoff = QLabel(self.centralwidget)
        self.display_airport_name_takeoff.setObjectName(u"airport_name_takeoff")
        self.display_airport_name_takeoff.setGeometry(QRect(33, 488, 299, 15))
        self.display_airport_name_takeoff.setAlignment(Qt.AlignCenter)
        self.display_airport_name_takeoff.setFont(font)































        # ------------------------------------------------------------------------------------------------------------ #
        # -------------------------------------------- LANDING ------------------------------------------------------- #
        # ------------------------------------------------------------------------------------------------------------ #

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- AIRPORTS LIST LANDING --------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.airport_list_landing = QComboBox(self.centralwidget)
        self.airport_list_landing.setObjectName(u"airport_list_landing")
        self.airport_list_landing.setGeometry(QRect(614, 275.33, 157, 28))
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
        self.airport_list_landing.setCurrentIndex(3)

        current_landing_airport = self.airport_list_landing.currentText()
        self.logger.debug(f"current_landing_airport: {current_landing_airport}")

        self.current_landing_airport_iata = current_landing_airport[6:9]
        self.logger.debug(f"current_landing_airport_iata: {self.current_landing_airport_iata}")

















        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- WIND VELOCITY LANDING TEXT BOX ---------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.wind_velocity_landing = QTextEdit(self.centralwidget)
        self.wind_velocity_landing.setObjectName(u"wind_velocity_landing")
        self.wind_velocity_landing.setGeometry(QRect(614, 314, 79, 28))
        self.wind_velocity_landing.setFont(font)
        self.wind_velocity_landing.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.wind_velocity_landing.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wind_velocity_landing.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wind_velocity_landing.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.wind_velocity_landing.setLineWrapColumnOrWidth(500000)
        self.wind_velocity_landing.setTabStopWidth(80)
        self.wind_velocity_landing.setAcceptRichText(True)
        self.wind_velocity_landing.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the wind velocity.", None))
        self.wind_velocity_landing.setText("0")
        self.wind_velocity_landing.textChanged.connect(self.handle_wind_velocity_landing_value)


        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- WIND VELOCITY CHECKBOX LANDING ---------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.vento_contra_landing = QCheckBox(self.centralwidget)
        self.vento_contra_landing.setObjectName(u"vento_contra_landing")
        self.vento_contra_landing.setGeometry(QRect(703, 318, 67, 16))
        self.vento_contra_landing.setText(QCoreApplication.translate("Takeoff_Landing", u"Against", None))
        self.vento_contra_landing.setChecked(False)
        self.vento_contra_landing.stateChanged.connect(self.handle_wind_landing_against_checkbox)

        # -------------------------------------------------------------------------------------------------------------#
        # --------------------------------------- RUNWAY SLOPE LANDING TEXT BOX ---------------------------------------#
        # -------------------------------------------------------------------------------------------------------------#

        self.runway_slope_landing = QTextEdit(self.centralwidget)
        self.runway_slope_landing.setObjectName(u"runway_slope_landing")
        self.runway_slope_landing.setGeometry(QRect(614, 391.33, 157, 28))
        self.runway_slope_landing.setFont(font)
        self.runway_slope_landing.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.runway_slope_landing.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_slope_landing.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.runway_slope_landing.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.runway_slope_landing.setLineWrapColumnOrWidth(500000)
        self.runway_slope_landing.setTabStopWidth(80)
        self.runway_slope_landing.setAcceptRichText(True)
        self.runway_slope_landing.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Type the runway slope.", None))
        self.runway_slope_landing.setText("0")
        self.runway_slope_landing.textChanged.connect(self.handle_slope_landing_value)

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------ RUNWAY CONDITION LANDING ------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.runway_condition_landing = QComboBox(self.centralwidget)
        self.runway_condition_landing.setObjectName(u"runway_condition_landing")
        self.runway_condition_landing.setGeometry(QRect(614, 352.67, 157, 28))

        self.runway_condition_landing.setPalette(palette1)
        self.runway_condition_landing.setFont(font)
        self.runway_condition_landing.setLayoutDirection(Qt.LeftToRight)
        self.runway_condition_landing.setEditable(False)

        self.runway_condition_landing.setToolTip(QCoreApplication.translate("Takeoff_Landing", u"Select the runway condition", None))

        count_runway_condition_landing = 0
        runway_condition_options = self.runway_condition_options
        for airport in runway_condition_options:
            self.runway_condition_landing.addItem("")
            self.runway_condition_landing.setItemText(count_runway_condition_landing, QCoreApplication.translate("Takeoff_Landing", f"{airport}", None))
            count_runway_condition_landing += 1

        self.runway_condition_landing.currentIndexChanged.connect(self.handle_runway_landing_condition_change)
        self.runway_condition_landing.setCurrentIndex(1)
        self.runway_condition_landing_text = self.runway_condition_landing.currentText()


        self.display_altitude_landing = QLabel(self.centralwidget)
        self.display_altitude_landing.setObjectName(u"altitude_landig")
        self.display_altitude_landing.setGeometry(QRect(614, 435, 157, 12))
        self.display_altitude_landing.setFont(font)

        self.display_runway_lenght_landing = QLabel(self.centralwidget)
        self.display_runway_lenght_landing.setObjectName(u"runway_landig")
        self.display_runway_lenght_landing.setGeometry(QRect(614, 455, 157, 12))
        self.display_runway_lenght_landing.setFont(font)

        self.display_airport_name_landing = QLabel(self.centralwidget)
        self.display_airport_name_landing.setObjectName(u"airport_name_landig")
        self.display_airport_name_landing.setGeometry(QRect(464, 488, 299, 15))
        self.display_airport_name_landing.setAlignment(Qt.AlignCenter)
        self.display_airport_name_landing.setFont(font)





































































        Flight_Conditions.setCentralWidget(self.centralwidget)

        self.background.raise_()
        self.np.raise_()
        self.fw.raise_()
        self.pw.raise_()

        self.display_altitude_landing.raise_()
        self.display_runway_lenght_landing.raise_()
        self.display_airport_name_landing.raise_()

        self.display_altitude_takeoff.raise_()
        self.display_runway_lenght_takeoff.raise_()
        self.display_airport_name_takeoff.raise_()

        self.wind_velocity_takeoff.raise_()
        self.vento_contra_takeoff.raise_()
        self.airport_list_takeoff.raise_()
        self.airport_list_landing.raise_()
        self.runway_condition_takeoff.raise_()
        self.runway_slope_takeoff.raise_()
        self.wind_velocity_landing.raise_()
        self.vento_contra_landing.raise_()
        self.runway_slope_landing.raise_()
        self.runway_condition_landing.raise_()




        self.statusbar = QStatusBar(Flight_Conditions)
        self.statusbar.setObjectName(u"statusbar")

        Flight_Conditions.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(Flight_Conditions)

        Flight_Conditions.setWindowTitle(QCoreApplication.translate("Flight_Conditions", u"Flight_Conditions", None))



    def handle_np_value(self):

        text_np = self.np.toPlainText()

        if not text_np:
            self.np.setPlainText("0")
        else:
            try:
                np = int(text_np)
                if 0 <= np < 10000:
                    self.np_value = np
                else:
                    self.np.clear()
            except ValueError:
                self.np.clear()

        self.logger.debug(f"Number of passengers: {self.np_value}")

    def handle_fw_value(self):

        text_fw = self.fw.toPlainText()

        if not text_fw:
            self.fw.setPlainText("0")
        else:
            try:
                fw = int(text_fw)
                if 0 <= fw < 10000:
                    self.fw_value = fw
                else:
                    self.fw.clear()
            except ValueError:
                self.fw.clear()

        self.logger.debug(f"Fuel weight (ton): {self.fw_value}")

    def handle_pw_value(self):

        text_pw = self.pw.toPlainText()

        if not text_pw:
            self.pw.setPlainText("0")
        else:
            try:
                pw = float(text_pw)
                if 0 <= pw < 10000:
                    self.pw_value = pw
                else:
                    self.pw.clear()
            except ValueError:
                self.pw.clear()

        self.logger.debug(f"Dispatched Cargo Weight (ton): {self.pw_value}")

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

    def handle_wind_takeoff_against_checkbox(self):

        self.vento_contra_takeoff_flag = -1 if self.vento_contra_takeoff.isChecked() else 1
        self.handle_wind_velocity_takeoff_value()

    def handle_airport_list_takeoff_change(self):

        current_takeoff_airport = self.airport_list_takeoff.currentText()
        self.logger.debug(f"current_takeoff_airport: {current_takeoff_airport}")

        self.current_takeoff_airport_iata = current_takeoff_airport[6:9]
        self.logger.debug(f"current_takeoff_airport_iata: {self.current_takeoff_airport_iata}")
        self.airport_takeoff_parameters = {}

        self.calculate_takeoff_airport_parameters()

        self.display_altitude_takeoff_value = f"{self.airport_takeoff_parameters['AIRPORT_TAKEOFF_ELEVATION']}"
        self.display_runway_lenght_takeoff_value = f"{self.airport_takeoff_parameters['AIRPORT_TAKEOFF_RUNWAY_DISTANCE']}"
        self.display_airport_name_takeoff_value = f"{self.airport_takeoff_parameters['AIRPORT_NAME']}"


        self.display_altitude_takeoff.setText(self.display_altitude_takeoff_value)
        self.display_runway_lenght_takeoff.setText(self.display_runway_lenght_takeoff_value)
        self.display_airport_name_takeoff.setText(self.display_airport_name_takeoff_value)

    def handle_airport_list_landing_change(self):

        current_landing_airport = self.airport_list_landing.currentText()
        self.current_landing_airport_iata = current_landing_airport[6:9]
        self.airport_landing_parameters = {}

        self.calculate_landing_airport_parameters()

        self.display_altitude_landing_value = f"{self.airport_landing_parameters['AIRPORT_LANDING_ELEVATION']}"
        self.display_runway_lenght_landing_value = f"{self.airport_landing_parameters['AIRPORT_LANDING_RUNWAY_DISTANCE']}"
        self.display_airport_name_landing_value = f"{self.airport_landing_parameters['AIRPORT_NAME']}"


        self.display_altitude_landing.setText(self.display_altitude_landing_value)
        self.display_runway_lenght_landing.setText(self.display_runway_lenght_landing_value)
        self.display_airport_name_landing.setText(self.display_airport_name_landing_value)



    def handle_runway_takeoff_condition_change(self):

        self.runway_condition_takeoff_text = self.runway_condition_takeoff.currentText()

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

    def handle_slope_landing_value(self):

        text_runway_slope_landing = self.runway_slope_landing.toPlainText()
        self.logger.debug(f"Runway Slope Landing: {text_runway_slope_landing}")

    def handle_runway_landing_condition_change(self):

        self.runway_condition_landing_text = self.runway_condition_landing.currentText()

    def calculate_takeoff_airport_parameters(self):
        self.logger.debug('----------------')
        self.logger.debug(self.airport_list_takeoff.currentText())
        self.logger.debug(self.current_takeoff_airport_iata)
        self.logger.debug(self.current_takeoff_airport_iata is None)
        airport_takeoff_results, _ = execute_generic_query(
            db_path=r"./db/utils/aero.db",
            query=f"select elevacao, pista, latitude, longitude, '{self.current_takeoff_airport_iata}' as airport_code, aeroporto from airports where iata='{self.current_takeoff_airport_iata}';",
            first_value=False)

        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_ELEVATION'] = airport_takeoff_results[0][0]
        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_RUNWAY_DISTANCE'] = airport_takeoff_results[0][1]
        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_LATITUDE'] = airport_takeoff_results[0][2]
        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_LONGITUDE'] = airport_takeoff_results[0][3]
        self.airport_takeoff_parameters['AIRPORT_IATA_CODE'] = airport_takeoff_results[0][4]
        self.airport_takeoff_parameters['AIRPORT_NAME'] = airport_takeoff_results[0][5]

        self.airport_takeoff_parameters['AIRPORT_TAKEOFF_DENSITY'] = self.aero.get_density(self.airport_takeoff_parameters['AIRPORT_TAKEOFF_ELEVATION'])

    def calculate_landing_airport_parameters(self):
        airport_landing_results, _ = execute_generic_query(
            db_path=r"./db/utils/aero.db",
            query=f"select elevacao, pista, latitude, longitude, '{self.current_landing_airport_iata}' as airport_code, aeroporto from airports where iata='{self.current_landing_airport_iata}';",
            first_value=False)

        self.airport_landing_parameters['AIRPORT_LANDING_ELEVATION']        = airport_landing_results[0][0]
        self.airport_landing_parameters['AIRPORT_LANDING_RUNWAY_DISTANCE']  = airport_landing_results[0][1]
        self.airport_landing_parameters['AIRPORT_LANDING_LATITUDE']         = airport_landing_results[0][2]
        self.airport_landing_parameters['AIRPORT_LANDING_LONGITUDE']        = airport_landing_results[0][3]
        self.airport_landing_parameters['AIRPORT_IATA_CODE']                = airport_landing_results[0][4]
        self.airport_landing_parameters['AIRPORT_NAME']                     = airport_landing_results[0][5]
















    # Essa função deve ser invocada por outras classes que necessitam de parâmetros da aeronave
    def get_flight_parameters(self):
        pass

        # result = {
        #     'AIRCRAFT_NAME': self.text_aircraft_name,
        #     'OEW': self.oew_value * 1000,
        #     'b': self.b_value,
        #     'e': self.e_value,
        #     'AR': (self.b_value ** 2) / self.wing_area_value,
        #     'TSFC': self.tsfc_value,
        #     'T0': self.t0_value * 1000,
        #     'NE': self.ne_value,
        #     'CL_MAX': self.cl_max_value,
        #     'S': self.wing_area_value,
        #     'K': 1 / (3.14 * self.e_value * ((self.b_value ** 2) / self.wing_area_value)),
        #     'CD0': self.cd0_value
        # }
        #
        # self.logger.debug(f"Current aircraft parameters: {result}")

        # return result

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
                self.aircraft_list_db.setItemText(count_aircrafts, QCoreApplication.translate("Flight_Conditions", f"{aircraft}", None))
                count_aircrafts += 1

            self.success_box(message='Aircraft successfully created!')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = GUI_FLIGHT_CONDITIONS()
    w = QtWidgets.QMainWindow()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())