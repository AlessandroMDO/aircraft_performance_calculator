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

        self.oew_value = None
        self.ne_value = None
        self.e_value = None
        self.aero = Aero()

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
        self.np.setAcceptRichText(True)
        self.np.setToolTip(QCoreApplication.translate("Flight_Conditions", u"Number of passengers", None))
        self.np.textChanged.connect(self.handle_np_value)
        # self.np.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['np']))

        # --------------------------------------------------------------------------------------------------------------#
        Flight_Conditions.setCentralWidget(self.centralwidget)

        self.background.raise_()
        self.np.raise_()

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
