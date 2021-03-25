from PyQt5 import QtCore, QtWidgets
from db_connection import *


class LinkWindow(object):
    def __init__(self, parent=None):
        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setWindowTitle("Объеденить/Разъеденить")
        self.pushButton = QtWidgets.QPushButton("Объединить", self.centralwidget,clicked=self._send_con_db_1)
        self.pushButton.setGeometry(QtCore.QRect(9, 79, 101, 23))
        self.pushButton_2 = QtWidgets.QPushButton("Разъединить", self.centralwidget,clicked=self._send_con_db_2)
        self.pushButton_2.setGeometry(QtCore.QRect(9, 109, 101, 23))
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setMaximum(99999999)
        self.spinBox.setGeometry(QtCore.QRect(10, 10, 101, 22))
        self.spinBox_2 = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_2.setMaximum(99999999)
        self.spinBox_2.setGeometry(QtCore.QRect(10, 40, 101, 22))
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("ID Родительская")
        self.label.setGeometry(QtCore.QRect(130, 10, 101, 16))
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setText("ID Дочерняя")
        self.label_2.setGeometry(QtCore.QRect(130, 40, 101, 16))
        self.con = SqlModule()
        QtCore.QMetaObject.connectSlotsByName(self.centralwidget)


    def _send_con_db_1(self,):
        self.con.send_con_db(self.spinBox.value(), self.spinBox_2.value(), 1)

    def _send_con_db_2(self):
        self.con.send_con_db(self.spinBox.value(), self.spinBox_2.value(), 2)

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = LinkWindow()
    ui.centralwidget.show()
    sys.exit(app.exec_())
