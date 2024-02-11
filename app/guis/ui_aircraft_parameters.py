import sys

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from functions.utils import get_logger
from PySide2 import QtWidgets
from functions.aero import Aero
from PySide2.QtWidgets import QMainWindow, QPushButton, QWidget, QLabel, QTextEdit
from db.utils.db_utils import *

class GUI_AIRCRAFT_PARAMETERS(QMainWindow):

    def __init__(self, background_path="guis/AIRCRAFT_PARAMETERS_800_800.png"):

        super(GUI_AIRCRAFT_PARAMETERS, self).__init__()

        self.tsfc_value = 1
        self.oew_value = 300
        self.ne_value = 2
        self.e_value = 0.8
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

        _, self.aircrafts_parameters = execute_generic_query(db_path=r"db/aero.db", query="select * from Airplanes;", first_value=False)

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

        Aircraft_Parameters.resize(800, 800)
        Aircraft_Parameters.setMinimumSize(QSize(800, 830))
        Aircraft_Parameters.setMaximumSize(QSize(800, 830))

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


        # palette1 = QPalette()
        # palette1.setBrush(QPalette.Active, QPalette.Base, brush)
        # palette1.setBrush(QPalette.Active, QPalette.Window, brush1)
        # palette1.setBrush(QPalette.Inactive, QPalette.Base, brush)
        # palette1.setBrush(QPalette.Inactive, QPalette.Window, brush1)
        # palette1.setBrush(QPalette.Disabled, QPalette.Base, brush1)
        # palette1.setBrush(QPalette.Disabled, QPalette.Window, brush1)

        # --------------------------------------------------------------------------------------------------------------#
        # --------------------------------------------- BACKGROUND IMAGE -----------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.background = QLabel(self.centralwidget)
        self.background.setObjectName(u"background")
        self.background.setGeometry(QRect(0, 0, 800, 800))
        # self.background.setMinimumSize(QSize(800, 800))
        # self.background.setMaximumSize(QSize(800, 800))
        # self.background.setLayoutDirection(Qt.LeftToRight)
        # self.background.setAutoFillBackground(False)
        self.background.setPixmap(QPixmap(self.background_path))
        self.background.update()
        # self.background.setScaledContents(True)
        # self.background.setAlignment(Qt.AlignCenter)
        # self.background.setIndent(0)
        # self.background.setText("")

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
        self.aircraft_list_db.setGeometry(QRect(543, 194.7, 231, 25.7))
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

        self.aircraft_list_db.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Select aircraft already created.", None))

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- AIRCRAFT NAME TEXT BOX -------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.new_aircraft_name = QTextEdit(self.centralwidget)
        self.new_aircraft_name.setObjectName(u"new_aircraft_name")
        self.new_aircraft_name.setGeometry(QRect(132, 194.7, 231, 25.7))
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
        self.cl_max.setGeometry(QRect(251, 237.11, 112, 25.06))
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
        self.cd0.setGeometry(QRect(251, 278.55, 112, 25.06))
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
        # ------------------------------------------- OSWALD NUMBER BOX ------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.e = QTextEdit(self.centralwidget)
        self.e.setObjectName(u"e")
        self.e.setGeometry(QRect(251, 319.04, 112, 25.06))
        self.e.setFont(font)
        self.e.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.e.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.e.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.e.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.e.setLineWrapColumnOrWidth(500000)
        self.e.setTabStopWidth(80)
        self.e.setAcceptRichText(True)
        self.e.setText(str(self.e_value))
        self.e.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Oswald efficiency)", None))
        self.e.textChanged.connect(self.handle_e_value)
        self.e.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['e']))

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- OEW NUMBER BOX ------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.oew = QTextEdit(self.centralwidget)
        self.oew.setObjectName(u"oew")
        self.oew.setGeometry(QRect(251, 361.45, 112, 25.06))
        self.oew.setFont(font)
        self.oew.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.oew.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.oew.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.oew.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.oew.setLineWrapColumnOrWidth(500000)
        self.oew.setTabStopWidth(80)
        self.oew.setAcceptRichText(True)
        self.oew.setText(str(self.oew_value))
        self.oew.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Operational Empty Weight)", None))
        self.oew.textChanged.connect(self.handle_oew_value)
        self.oew.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['oew']))

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- WINGSPAN NUMBER BOX ------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.b = QTextEdit(self.centralwidget)
        self.b.setObjectName(u"b")
        self.b.setGeometry(QRect(251, 402.89, 112, 25.06))
        self.b.setFont(font)
        self.b.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.b.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.b.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.b.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.b.setLineWrapColumnOrWidth(500000)
        self.b.setTabStopWidth(80)
        self.b.setAcceptRichText(True)
        self.b.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Wingspan)", None))
        self.b.textChanged.connect(self.handle_b_value)
        self.b.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['b']))

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- TSFC NUMBER BOX ------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.tsfc = QTextEdit(self.centralwidget)
        self.tsfc.setObjectName(u"tsfc")
        self.tsfc.setGeometry(QRect(251, 485.78, 112, 25.06))
        self.tsfc.setFont(font)
        self.tsfc.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.tsfc.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tsfc.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tsfc.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.tsfc.setLineWrapColumnOrWidth(500000)
        self.tsfc.setTabStopWidth(80)
        self.tsfc.setAcceptRichText(True)
        self.tsfc.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"TSFC)", None))
        self.tsfc.textChanged.connect(self.handle_tsfc_value)
        self.tsfc.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['tsfc']))

        # --------------------------------------------------------------------------------------------------------------#
        # ------------------------------------------- T0 NUMBER BOX ------------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.t0 = QTextEdit(self.centralwidget)
        self.t0.setObjectName(u"t0")
        self.t0.setGeometry(QRect(251, 527, 112, 25.06))
        self.t0.setFont(font)
        self.t0.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.t0.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.t0.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.t0.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.t0.setLineWrapColumnOrWidth(500000)
        self.t0.setTabStopWidth(80)
        self.t0.setAcceptRichText(True)
        self.t0.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Thrust per engine)", None))
        self.t0.textChanged.connect(self.handle_t0_value)
        self.t0.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['t0']))

        # --------------------------------------------------------------------------------------------------------------#
        # -------------------------------------- NUMBER OF ENGINES NUMBER BOX ------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.ne = QTextEdit(self.centralwidget)
        self.ne.setObjectName(u"ne")
        self.ne.setGeometry(QRect(251, 567, 112, 25.06))
        self.ne.setFont(font)
        self.ne.setInputMethodHints(Qt.ImhFormattedNumbersOnly)
        self.ne.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ne.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ne.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.ne.setLineWrapColumnOrWidth(500000)
        self.ne.setTabStopWidth(80)
        self.ne.setAcceptRichText(True)
        self.ne.setToolTip(QCoreApplication.translate("Aircraft_Parameters", u"Number of engines)", None))
        self.ne.textChanged.connect(self.handle_ne_value)
        self.ne.setText(str(self.aircrafts_parameters[self.aircraft_list_db.currentText()]['ne']))

        # --------------------------------------------------------------------------------------------------------------#
        # ---------------------------------------------- WING AREA TEXT BOX --------------------------------------------#
        # --------------------------------------------------------------------------------------------------------------#

        self.wing_area = QTextEdit(self.centralwidget)
        self.wing_area.setObjectName(u"wing_area")
        self.wing_area.setGeometry(QRect(251, 444.34, 112, 25.06))
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
        # --------------------------------------------------------------------------------------------------------------#

        self.create_db_button = QPushButton(self.centralwidget)
        self.create_db_button.setText("")  # Set an empty text to hide the label
        self.create_db_button.setGeometry(QRect(107, 738, 169, 39))
        self.create_db_button.setStyleSheet("border: none; background: none;")
        self.create_db_button.clicked.connect(self.save_current_aicraft_to_db)

        self.delete_aircraft_db_button = QPushButton(self.centralwidget)
        self.delete_aircraft_db_button.setText("")  # Set an empty text to hide the label
        self.delete_aircraft_db_button.setGeometry(QRect(518, 738, 169, 39))
        self.delete_aircraft_db_button.setStyleSheet("border: none; background: none;")
        self.delete_aircraft_db_button.clicked.connect(self.delete_current_aicraft_from_db)

        # --------------------------------------------------------------------------------------------------------------#
        Aircraft_Parameters.setCentralWidget(self.centralwidget)

        self.background.raise_()
        self.new_aircraft_name.raise_()
        self.cl_max.raise_()
        self.cd0.raise_()
        self.e.raise_()
        self.oew.raise_()
        self.b.raise_()
        self.tsfc.raise_()
        self.t0.raise_()
        self.ne.raise_()
        self.wing_area.raise_()
        self.aircraft_list_db.raise_()
        self.create_db_button.raise_()
        self.delete_aircraft_db_button.raise_()

        self.statusbar = QStatusBar(Aircraft_Parameters)
        self.statusbar.setObjectName(u"statusbar")

        Aircraft_Parameters.setStatusBar(self.statusbar)

        QMetaObject.connectSlotsByName(Aircraft_Parameters)

        Aircraft_Parameters.setWindowTitle(QCoreApplication.translate("Aircraft_Parameters", u"Aircraft_Parameters", None))

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

    def handle_e_value(self):

        text_e = self.e.toPlainText()

        if not text_e:
            self.e.setPlainText("0")
        else:
            try:
                e = float(text_e)
                if 0 <= e < 100:
                    self.e_value = e
                else:
                    self.e.clear()
            except ValueError:
                self.e.clear()

        self.logger.debug(f"e value: {self.e_value}")

    def handle_oew_value(self):

        text_oew = self.oew.toPlainText()

        if not text_oew:
            self.oew.setPlainText("0")
        else:
            try:
                oew = float(text_oew)
                if 0 <= oew < 1000000:
                    self.oew_value = oew
                else:
                    self.oew.clear()
            except ValueError:
                self.oew.clear()

        self.logger.debug(f"oew value: {self.oew_value}")

    def handle_b_value(self):

        text_b = self.b.toPlainText()

        if not text_b:
            self.b.setPlainText("0")
        else:
            try:
                b = float(text_b)
                if 0 <= b < 1000000:
                    self.b_value = b
                else:
                    self.b.clear()
            except ValueError:
                self.b.clear()

        self.logger.debug(f"b value: {self.b_value}")

    def handle_tsfc_value(self):

        text_tsfc = self.tsfc.toPlainText()

        if not text_tsfc:
            self.tsfc.setPlainText("0")
        else:
            try:
                tsfc = float(text_tsfc)
                if 0 <= tsfc < 10:
                    self.tsfc_value = tsfc
                else:
                    self.tsfc.clear()
            except ValueError:
                self.tsfc.clear()

        self.logger.debug(f"tsfc value: {self.tsfc_value}")

    def handle_t0_value(self):

        text_t0 = self.t0.toPlainText()

        if not text_t0:
            self.t0.setPlainText("0")
        else:
            try:
                t0 = float(text_t0)
                if 0 <= t0 < 10000000:
                    self.t0_value = t0
                else:
                    self.t0.clear()
            except ValueError:
                self.t0.clear()

        self.logger.debug(f"T0 value: {self.t0_value}")

    def handle_ne_value(self):

        text_ne = self.ne.toPlainText()

        if not text_ne:
            self.ne.setPlainText("0")
        else:
            try:
                ne = float(text_ne)
                if 0 <= ne < 10:
                    self.ne_value = ne
                else:
                    self.ne.clear()
            except ValueError:
                self.ne.clear()

        self.logger.debug(f"Number of engines value: {self.ne_value}")

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
        self.cd0.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['cd0']))
        self.wing_area.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['area']))
        self.cl_max.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['cl_max']))
        self.e.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['e']))
        self.oew.setPlainText(str(round(self.aircrafts_parameters[self.current_aircraft_db]['oew'] / 1000, 3)))
        self.b.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['b']))
        self.tsfc.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['tsfc']))
        self.t0.setPlainText(str(round(self.aircrafts_parameters[self.current_aircraft_db]['t0'] /1000, 3)))
        self.ne.setPlainText(str(self.aircrafts_parameters[self.current_aircraft_db]['ne']))

        self.logger.debug(f"Current Aircraft DB: {self.current_aircraft_db}")

    # Essa função deve ser invocada por outras classes que necessitam de parâmetros da aeronave
    def get_aircraft_parameters(self, convert_units=False):

        result = {
            'AIRCRAFT_NAME': self.text_aircraft_name,
            'OEW': self.oew_value * 1000 if convert_units is False else self.oew_value * 1000 * self.aero.g,
            'b': self.b_value,
            'e': self.e_value,
            'AR': (self.b_value ** 2) / self.wing_area_value,
            'TSFC': self.tsfc_value,
            'T0': self.t0_value * 1000,
            'NE': self.ne_value,
            'CL_MAX': self.cl_max_value,
            'S': self.wing_area_value,
            'K': 1 / (3.14 * self.e_value * ((self.b_value ** 2) / self.wing_area_value)),
            'CD0': self.cd0_value
        }

        self.logger.debug(f"Current aircraft parameters: {result}")

        return result

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



    def success_box(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle('Success')
        msg_box.exec_()

    def delete_current_aicraft_from_db(self):

        result = self.get_aircraft_parameters()
        aircraft_name = result['AIRCRAFT_NAME']

        if aircraft_name is not None:
            result = self.warning_box(message=f"Are you sure you want to delete '{aircraft_name}' from the database ?\nThis action can't be undone.", ok_and_decline=True)
            if result == 0:
                delete_query = f"delete from airplanes where nome_aeronave = '{aircraft_name}'"
                delete_db_query(db_path=r"./db/aero.db", query=delete_query)

                _, self.aircrafts_parameters = execute_generic_query(db_path=r"./db/aero.db", query="select * from Airplanes;", first_value=False)

                self.aircraft_list_db.clear()

                count_aircrafts = 0
                for aircraft in self.aircrafts_parameters.keys():
                    self.aircraft_list_db.addItem("")
                    self.aircraft_list_db.setItemText(count_aircrafts, QCoreApplication.translate("Aircraft_Parameters", f"{aircraft}", None))
                    count_aircrafts += 1




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
                '{result['AIRCRAFT_NAME']}', {result['CD0']}, {result['S']}, {result['CL_MAX']}, {result['OEW']}, {result['TSFC']}, {result['b']}, {result['e']}, {result['T0']}, {result['NE']}) ;
            """

            insert_data_to_db(db_path=r"./db/aero.db", query=insert_query)
            _, self.aircrafts_parameters = execute_generic_query(db_path=r"./db/aero.db", query="select * from Airplanes;", first_value=False)

            self.aircraft_list_db.clear()

            count_aircrafts = 0
            for aircraft in self.aircrafts_parameters.keys():
                self.aircraft_list_db.addItem("")
                self.aircraft_list_db.setItemText(count_aircrafts, QCoreApplication.translate("Aircraft_Parameters", f"{aircraft}", None))
                count_aircrafts += 1

            self.success_box(message='Aircraft successfully created!')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    ex = GUI_AIRCRAFT_PARAMETERS()
    w = QtWidgets.QMainWindow()
    ex.setupUi(w)
    w.show()
    sys.exit(app.exec_())
