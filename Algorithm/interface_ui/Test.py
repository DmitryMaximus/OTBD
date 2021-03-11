from PyQt5 import QtCore, QtGui, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.m_tablewidget = QtWidgets.QTableWidget(0, 3)
        self.m_tablewidget.setHorizontalHeaderLabels(
            ["Col 1", "Col 2", "Col 3"]
        )
        self.m_button = QtWidgets.QPushButton("Add Row", clicked=self.onClicked)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QVBoxLayout(central_widget)
        lay.addWidget(self.m_tablewidget)
        lay.addWidget(self.m_button, alignment=QtCore.Qt.AlignLeft)

    @QtCore.pyqtSlot()
    def addRow(self):
        button = self.sender()
        if not isinstance(button, QtWidgets.QPushButton):
            return
        p = button.mapTo(self.m_tablewidget.viewport(), QtCore.QPoint())
        ix = self.m_tablewidget.indexAt(p)
        if not ix.isValid() or ix.column() != 0:
            return
        r = ix.row()
        ix_combobox = 0
        text = ""
        combo = self.m_tablewidget.cellWidget(r, 1)
        if isinstance(combo, QtWidgets.QComboBox):
            ix_combobox = combo.currentIndex()
        item = self.m_tablewidget.item(r, 2)
        if item is not None:
            text = item.text()
        self.insert_row(row=r + 1, ix_combobox=ix_combobox, text=text)

    @QtCore.pyqtSlot()
    def onClicked(self):
        self.insert_row()

    def insert_row(self, d=None, ix_combobox=0, text="", row=-1):
        if d is None:
            d = {
                "a": ["x", "y", "z"],
                "b": ["4", "5", "6"],
                "c": ["21", "22", "23"],
            }
        combobox = QtWidgets.QComboBox()
        for k, v in d.items():
            combobox.addItem(k, v)
        combobox.setCurrentIndex(ix_combobox)
        item = QtWidgets.QTableWidgetItem()
        copyROw_button = QtWidgets.QPushButton("ADD ROW", clicked=self.addRow)
        if row == -1:
            row = self.m_tablewidget.rowCount()
        self.m_tablewidget.insertRow(row)
        for i, combo in enumerate((copyROw_button, combobox)):
            self.m_tablewidget.setCellWidget(row, i, combo)
        if text:
            self.m_tablewidget.setItem(row, 2, QtWidgets.QTableWidgetItem(text))


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)

    w = MainWindow()
    w.resize(640, 480)
    w.show()

    sys.exit(app.exec_())