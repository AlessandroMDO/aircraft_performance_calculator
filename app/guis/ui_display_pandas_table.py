import sys
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt
import pandas as pd

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data, index_column):
        super(TableModel, self).__init__()
        self._data = data
        self.index_column_name = index_column

    def data(self, index, role):
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return str(self._data.index[index.row()])
            else:
                return str(self._data.iloc[index.row(), index.column() - 1])

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return self._data.shape[1] + 1

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                # For the index column
                if section == 0:
                    return self.index_column_name
                else:
                    return str(self._data.columns[section - 1])
            elif orientation == Qt.Vertical:
                return str(section + 1)


class PandasWindow(QtWidgets.QMainWindow):

    def __init__(self, df, index_column):
        super().__init__()

        self.table = QtWidgets.QTableView()
        self.data = df
        self.index_column = index_column

        self.model = TableModel(self.data, index_column=self.index_column)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)

        self.adjust_window_size()


    def set_df(self, new_df):
        self.data = new_df
        self.model = TableModel(self.data, index_column=self.index_column)
        self.table.setModel(self.model)
        self.setCentralWidget(self.table)

        self.adjust_window_size()

    def adjust_window_size(self):
        header_widths = [self.table.horizontalHeader().sectionSize(i) for i in range(self.table.model().columnCount(None))]
        total_width = sum(header_widths) + self.table.verticalHeader().width() + 4
        self.resize(total_width, self.height())

if __name__ == "__main__":

    data = {
        'A': [1, 2, 3, 4],
        'B': [5, 6, 7, 8],
        'C': [9, 10, 11, 12]
    }
    index = ['X', 'Y', 'Z', 'W']
    df = pd.DataFrame(data, index=index)

    app = QtWidgets.QApplication(sys.argv)
    window = PandasWindow(df)
    window.show()
    app.exec_()
