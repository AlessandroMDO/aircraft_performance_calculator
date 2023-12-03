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

class GUI_AIRCRAFT_PARAMETERS(QMainWindow):

    def __init__(self, background_path="AIRCRAFT_PARAMETERS_800_600.png"):

        super(GUI_AIRCRAFT_PARAMETERS, self).__init__()

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

        # self.aircrafts = execute_generic_query(db_path=r"../../db/utils/aero.db", query="select nome_aeronave, id from Airplanes;", first_value=False)
        _, self.aircrafts_parameters = execute_generic_query(db_path=r"../../db/utils/aero.db", query="select * from Airplanes;", first_value=False)

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

    def setupUi(self, Aircraft_Parameters):
        if not Aircraft_Parameters.objectName():
            Aircraft_Parameters.setObjectName(u"Aircraft_Parameters")
        Aircraft_Parameters.resize(800, 600)
        Aircraft_Parameters.setMinimumSize(QSize(800, 600))
        Aircraft_Parameters.setMaximumSize(QSize(800, 600))
        self.centralwidget = QWidget(Aircraft_Parameters)
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

        # self.run_load_button = QPushButton(self.centralwidget)
        # self.run_load_button.setText("")  # Set an empty text to hide the label
        # self.run_load_button.setGeometry(QRect(508, 547, 168, 33))
        # self.run_load_button.setStyleSheet("border: none; background: none;")  # Hide border and background
        # self.run_analysis_button.clicked.connect(self.invoke_load_aircraft_from_db)

        # --------------------------------------------------------------------------------------------------------------#
        # -------------------------------------------- LIST AIRCRAFTS IN DB --------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#
        self.aircraft_list_db = QComboBox(self.centralwidget)
        self.aircraft_list_db.setObjectName(u"aircraft_list_db")
        self.aircraft_list_db.setGeometry(QRect(543, 129, 231, 20))
        self.aircraft_list_db.setFont(font)
        self.aircraft_list_db.setLayoutDirection(Qt.LeftToRight)
        self.aircraft_list_db.setEditable(False)
        self.aircraft_list_db.setPalette(palette)

        count_aircrafts = 0
        for aircraft in self.aircrafts_parameters.keys():
            self.aircraft_list_db.addItem("")
            self.aircraft_list_db.setItemText(count_aircrafts,
                                              QCoreApplication.translate("Aircraft_Parameters", f"{aircraft}", None))
            count_aircrafts += 1

        self.aircraft_list_db.currentIndexChanged.connect(self.handle_aircraft_db_change)

        self.aircraft_list_db.setToolTip(
            QCoreApplication.translate("Aircraft_Parameters", u"Select aircraft already created.", None))
        # self.aircraft_list_db.raise_()

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- AIRCRAFT NAME TEXT BOX -------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.new_aircraft_name = QTextEdit(self.centralwidget)
        self.new_aircraft_name.setObjectName(u"new_aircraft_name")
        self.new_aircraft_name.setGeometry(QRect(132, 129, 231, 20))
        self.new_aircraft_name.setFont(font)
        self.new_aircraft_name.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.new_aircraft_name.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.new_aircraft_name.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.new_aircraft_name.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.new_aircraft_name.setLineWrapColumnOrWidth(500000)
        self.new_aircraft_name.setTabStopWidth(80)
        self.new_aircraft_name.setAcceptRichText(True)
        self.new_aircraft_name.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Type the aircraft name.", None))
        self.new_aircraft_name.textChanged.connect(self.handle_aircraft_name_value)

        # --------------------------------------------------------------------------------------------------------------#
        # ----------------------------------------------- CL_MAX TEXT BOX ----------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.cl_max = QTextEdit(self.centralwidget)
        self.cl_max.setObjectName(u"cl_max")
        self.cl_max.setGeometry(QRect(79, 161, 112, 20))
        self.cl_max.setFont(font)
        self.cl_max.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.cl_max.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cl_max.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cl_max.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.cl_max.setLineWrapColumnOrWidth(500000)
        self.cl_max.setTabStopWidth(80)
        self.cl_max.setAcceptRichText(True)
        self.cl_max.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Type the maxium lift coefficient.", None))
        self.cl_max.textChanged.connect(self.handle_cl_max_value)
        self.cl_max.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['cl_max']))

        # --------------------------------------------------------------------------------------------------------------#
        # ----------------------------------------------- CD0 TEXT BOX ----------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.cd0 = QTextEdit(self.centralwidget)
        self.cd0.setObjectName(u"cd0")
        self.cd0.setGeometry(QRect(62, 193, 112, 20))
        self.cd0.setFont(font)
        self.cd0.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.cd0.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cd0.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.cd0.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.cd0.setLineWrapColumnOrWidth(500000)
        self.cd0.setTabStopWidth(80)
        self.cd0.setAcceptRichText(True)
        self.cd0.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Type the drag coefficient at zero lift.", None))
        self.cd0.textChanged.connect(self.handle_cd0_value)
        self.cd0.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['cd0']))

        # --------------------------------------------------------------------------------------------------------------#
        # ----------------------------------------------- K TEXT BOX ----------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.k = QTextEdit(self.centralwidget)
        self.k.setObjectName(u"k")
        self.k.setGeometry(QRect(251, 225, 112, 20))
        self.k.setFont(font)
        self.k.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.k.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.k.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.k.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.k.setLineWrapColumnOrWidth(500000)
        self.k.setTabStopWidth(80)
        self.k.setAcceptRichText(True)
        self.k.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"K = 1/(pi * aspect_ratio * Oswald efficiency)", None))
        self.k.textChanged.connect(self.handle_k_value)
        self.k.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['k']))

        # --------------------------------------------------------------------------------------------------------------#
        # ---------------------------------------------- WING AREA TEXT BOX --------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.wing_area = QTextEdit(self.centralwidget)
        self.wing_area.setObjectName(u"wing_area")
        self.wing_area.setGeometry(QRect(143, 466, 112, 20))
        self.wing_area.setFont(font)
        self.wing_area.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.wing_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wing_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.wing_area.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.wing_area.setLineWrapColumnOrWidth(500000)
        self.wing_area.setTabStopWidth(80)
        self.wing_area.setAcceptRichText(True)
        self.wing_area.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"The relevant surface area", None))
        self.wing_area.textChanged.connect(self.handle_wing_area_value)
        self.wing_area.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['area']))


        # --------------------------------------------------------------------------------------------------------------#
        Aircraft_Parameters.setCentralWidget(self.centralwidget)

        self.background.raise_()
        self.new_aircraft_name.raise_()
        self.cl_max.raise_()
        self.cd0.raise_()
        self.k.raise_()
        self.wing_area.raise_()
        self.aircraft_list_db.raise_()

        self.statusbar = QStatusBar(Aircraft_Parameters)
        self.statusbar.setObjectName(u"statusbar")
        Aircraft_Parameters.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(Aircraft_Parameters)

        Aircraft_Parameters.setWindowTitle(QCoreApplication.translate("Aircraft_Parameters", u"Aircraft_Parameters", None))

        # # --------------------------------------------------------------------------------------------------------------#
        # # -------------------------------------------- LIST AIRCRAFTS IN DB --------------------------------------------#
        # # --------------------------------------------------------------------------------------------------------------#
        # self.aircraft_list_db = QComboBox(self.centralwidget)
        # self.aircraft_list_db.setObjectName(u"aircraft_list_db")
        # self.aircraft_list_db.setGeometry(QRect(543, 129, 231, 20))
        # self.aircraft_list_db.setFont(font)
        # self.aircraft_list_db.setLayoutDirection(Qt.LeftToRight)
        # self.aircraft_list_db.setEditable(False)
        # self.aircraft_list_db.setPalette(palette)
        #
        # count_aircrafts = 0
        # for aircraft in self.aircrafts_parameters.keys():
        #     self.aircraft_list_db.addItem("")
        #     self.aircraft_list_db.setItemText(count_aircrafts, QCoreApplication.translate("Aircraft_Parameters", f"{aircraft}", None))
        #     count_aircrafts += 1
        #
        # self.aircraft_list_db.currentIndexChanged.connect(self.handle_aircraft_db_change)
        #
        # self.aircraft_list_db.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Select aircraft already created.", None))
        # self.aircraft_list_db.raise_()

    def handle_aircraft_name_value(self):
        self.text_aircraft_name = self.new_aircraft_name.toPlainText()

        if not self.text_aircraft_name:
            self.new_aircraft_name.setPlainText(" ")

        self.logger.debug(f"Aircraft name: {self.text_aircraft_name}")

    def handle_cl_max_value(self):
        text_cl_max = self.cl_max.toPlainText()

        if not text_cl_max:
            self.cl_max.setPlainText("0")
        else:
            try:
                cl_max = float(text_cl_max)
                if 0 <= cl_max < 100:
                    self.cl_max_value = cl_max
                else:
                    self.cl_max.clear()
            except ValueError:
                self.cl_max.clear()

        self.logger.debug(f"CL max: {self.cl_max_value}")

    def handle_cd0_value(self):
        text_cd0 = self.cd0.toPlainText()

        if not text_cd0:
            self.cd0.setPlainText("0")
        else:
            try:
                cd0 = float(text_cd0)
                if 0 <= cd0 < 100:
                    self.cd0_value = cd0
                else:
                    self.cd0.clear()
            except ValueError:
                self.cd0.clear()

        self.logger.debug(f"CD0: {self.cd0_value}")

    def handle_k_value(self):

        text_k = self.k.toPlainText()

        if not text_k:
            self.k.setPlainText("0")
        else:
            try:
                k = float(text_k)
                if 0 <= k < 100:
                    self.k_value = k
                else:
                    self.k.clear()
            except ValueError:
                self.k.clear()

        self.logger.debug(f"K value: {self.k_value}")

    def handle_wing_area_value(self):
        text_wing_area = self.wing_area.toPlainText()

        if not text_wing_area:
            self.wing_area.setPlainText("0")
        else:
            try:
                wing_area = float(text_wing_area)
                if 0 <= wing_area < 50000:
                    self.wing_area_value = wing_area
                else:
                    self.wing_area.clear()
            except ValueError:
                self.wing_area.clear()

        self.logger.debug(f"Wing area: {self.wing_area_value}")

    def handle_aircraft_db_change(self):

        self.current_aircraft_db = self.aircraft_list_db.currentText()

        self.new_aircraft_name.setPlainText(self.current_aircraft_db)
        self.wing_area.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['area']))
        self.cd0.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['cd0']))
        self.cl_max.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['cl_max']))
        self.k.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['k']))

        self.logger.debug(f"Current Aircraft DB: {self.current_aircraft_db}")

    # Essa função deve ser invocada por outras classes que necessitam de parâmetros da aeronave
    def get_aircraft_parameters(self):

        result = {
            'OEW': 1,
            'WINGSPAN': 1,
            'TSFC': 1,
            'MTOW': 5000,
            'CL_MAX': self.cl_max_value,
            'SURFACE_AREA': self.wing_area_value,
            'K': self.k_value,
            'CD0': self.cd0_value
        }

        self.logger.debug(f"Current aircraft parameters: {result}")

        return result



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = GUI_AIRCRAFT_PARAMETERS()
    w = QtWidgets.QMainWindow()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())
