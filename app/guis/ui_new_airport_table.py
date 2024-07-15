from PySide2.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QPushButton, QVBoxLayout, \
    QWidget
from PySide2.QtCore import Signal
from db.utils.db_utils import *
from PySide2.QtWidgets import *

class InputTableWindow(QMainWindow):
    closed = Signal()
    def __init__(self):
        super().__init__()

        self.setWindowTitle("New Airport Propeties")
        self.input_values = {}

        self.table_widget = QTableWidget(1, 6)

        self.headers = ["Airport Code", "Airport Name", "Runway Lenght", "Elevation", "Latitude", "Longitude"]
        self.table_widget.setHorizontalHeaderLabels(self.headers)

        for i in range(6):
            item = QTableWidgetItem()
            self.table_widget.setItem(0, i, item)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit_input)

        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        layout.addWidget(self.submit_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.set_dynamic_column_widths()

    def success_box(self, message):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(message)
        msg_box.setWindowTitle('Success')
        msg_box.exec_()

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

    def submit_input(self):

        for i, j in zip(range(6), self.headers):
            item = self.table_widget.item(0, i)
            if item is not None:
                self.input_values[j] = item.text()
            else:
                self.input_values[j] = ""

        airport_code = self.input_values['Airport Code']

        _, self.airports = execute_generic_query(db_path=r"./db/aero.db", query="select distinct iata from airports;", first_value=False)


        if airport_code in self.airports.keys():
            self.warning_box(message='Airport code already in the database. Give it another code.')

        elif any(t == '' for t in list(self.input_values.values())):
            self.warning_box(message='Please, fulfill all required values.')

        else:

            insert_query = f"""
                        INSERT INTO AIRPORTS
                        (iata, icao, aeroporto, pista, elevacao, latitude, longitude)
                        VALUES ('{self.input_values['Airport Code']}', '{self.input_values['Airport Code']}', '{self.input_values['Airport Name']}', {self.input_values['Runway Lenght']}, {self.input_values['Elevation']}, {self.input_values['Latitude']}, {self.input_values['Longitude']}) ;
                        """
            insert_data_to_db(db_path=r"./db/aero.db", query=insert_query)
            self.success_box(message='Airport successfully created!')


    def get_input_data(self):
        return self.input_values

    def closeEvent(self, event):

        self.closed.emit()
        event.accept()

    def set_dynamic_column_widths(self):
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)


if __name__ == "__main__":
    app = QApplication([])
    window = InputTableWindow()
    window.show()
    app.exec_()