from PyQt5 import QtCore, QtWidgets
from db_connection import *


class LinkWindow(object):
    def __init__(self, parent=None):
        self.centralwidget = QtWidgets.QWidget()
        self.centralwidget.setWindowTitle("Объеденить/Разъеденить")
        self.pushButton = QtWidgets.QPushButton("Объединить", self.centralwidget, clicked=self._send_con_db_1)
        self.pushButton.setGeometry(QtCore.QRect(9, 79, 101, 23))
        self.pushButton_2 = QtWidgets.QPushButton("Разъединить", self.centralwidget, clicked=self._send_con_db_2)
        self.pushButton_2.setGeometry(QtCore.QRect(9, 109, 101, 23))
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setMaximum(99999999)
        self.spinBox.setGeometry(QtCore.QRect(10, 10, 101, 22))
        self.spinBox_2 = QtWidgets.QTextEdit(self.centralwidget)
        # self.spinBox_2.setMaximum(99999999)
        self.spinBox_2.setGeometry(QtCore.QRect(10, 40, 101, 22))
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setText("ID Родительская")
        self.label.setGeometry(QtCore.QRect(130, 10, 101, 16))
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setText("ID Дочерняя")
        self.label_2.setGeometry(QtCore.QRect(130, 40, 101, 16))
        self.con = SqlModule()
        QtCore.QMetaObject.connectSlotsByName(self.centralwidget)

    def _send_con_db_1(self, ):
        daughter_list = str(self.spinBox_2.toPlainText()).strip().split(",")
        for daughter in daughter_list:
            self.con.send_con_db(self.spinBox.value(), int(daughter.strip()), 1)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Записи были успешно объеденены")
        msg.setWindowTitle("Объединение записей")
        msg.exec_()

    def _send_con_db_2(self):
        daughter_list = str(self.spinBox_2.toPlainText()).strip().split(",")
        for daughter in daughter_list:
            self.con.send_con_db(self.spinBox.value(), int(daughter.strip()), 1)
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Записи были успешно разделены")
        msg.setWindowTitle("Разделение записей")
        msg.exec_()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    ui = LinkWindow()
    ui.centralwidget.show()
    sys.exit(app.exec_())
