from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os, configparser
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
from Algorithm.model import *
from Algorithm.tree_model import *


class UI_OTBD(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.x, self.y, self.w, self.h = 0, 0, 1200, 651
        self.setGeometry(self.x, self.y, self.w, self.h)

        self.window = MainWindow(self)
        self.setCentralWidget(self.window)
        self.setWindowTitle("Работа с ОТБД")
        self.show()


class GeneralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GeneralWidget, self).__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)

        self.tableView = MyDelegateInTableView()
        self.tableView.setLayout(lay)
        self.pushButton = QtWidgets.QPushButton("Отобразить список", clicked=self.__load_sql)
        self.pushButton_1 = QtWidgets.QPushButton("Внести изменения в БД")

        self.comb_list = QtWidgets.QComboBox(self)
        self.comb_list.addItem("X-com")
        self.comb_list.addItem("AB")
        self.comb_list.addItem("User")

        lay.addWidget(self.tableView)
        lay.addWidget(self.comb_list)
        lay.addWidget(self.pushButton)
        lay.addWidget(self.pushButton_1)

    @QtCore.pyqtSlot()
    def __load_sql(self):
        self.tableView.load_table_sql(self.comb_list.currentText())


class OptionsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OptionsWidget, self).__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)
        hlay = QtWidgets.QHBoxLayout()
        lay.addLayout(hlay)
        self.treeView = MyTree()

        self.pushButton_2 = QtWidgets.QPushButton("Задать приоритет")
        self.pushButton_3 = QtWidgets.QPushButton("Выгрузить в формате SSW")
        self.pushButton_4 = QtWidgets.QPushButton("Выгрузить в формате Excel")

        self.priority = QtWidgets.QComboBox(self)
        self.priority.addItem("X-com")
        self.priority.addItem("AB")
        self.priority.addItem("User")

        lay.addWidget(self.treeView)
        lay.addWidget(self.priority)
        lay.addWidget(self.pushButton_2)
        lay.addWidget(self.pushButton_3)


class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MainWindow, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        tab_holder = QtWidgets.QTabWidget()
        tab_1 = GeneralWidget()
        tab_2 = OptionsWidget()
        # Add tabs
        tab_holder.addTab(tab_1, "Работа со списками")
        tab_holder.addTab(tab_2, "Общий список")

        layout.addWidget(tab_holder)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = UI_OTBD()
    sys.exit(app.exec_())
