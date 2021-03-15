# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from Algorithm.ui_OTBD import UI_OTBD
from Algorithm.ui_SOZ import MainWindow as UI_SOZ
import sys
# import Algorithm.sql_connect

class Ui_MainWindow(object):
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(237, 195)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.clicked.connect(self.show_ui_SOZ)
        self.pushButton.setGeometry(QtCore.QRect(10, 20, 211, 31))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.clicked.connect(self.show_ui_OTBD)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 60, 211, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(10, 100, 211, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(10, 140, 211, 31))
        self.pushButton_4.setObjectName("pushButton_4")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def show_ui_SOZ(self):
        self.UI_SOZ = UI_SOZ()
        self.UI_SOZ.show()

    def show_ui_OTBD(self):
        self.ui_OTBD = UI_OTBD()
        self.ui_OTBD.show()


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Меню"))
        self.pushButton.setText(_translate("MainWindow", "Система обработки записей"))
        self.pushButton_2.setText(_translate("MainWindow", "Модуль работы в ЭТБД"))
        self.pushButton_3.setText(_translate("MainWindow", "Модуль выгрузки данных"))
        self.pushButton_4.setText(_translate("MainWindow", "Модуль работы с БСЛ"))

    def exit(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    ui = Ui_MainWindow()
    ui.MainWindow.show()
    ui.exit()
