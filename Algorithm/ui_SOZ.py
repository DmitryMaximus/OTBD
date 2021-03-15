#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import pandas as pd
from Algorithm.model import *
from Algorithm.db_connection import *


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setWindowTitle("Система обработки записей")
        self.view = MyDelegateInTableView()
        self.resize(800, 600)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.addWidget(self.view, 1, 0, 1, 3)

        self.radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton.setText("Перезаписать список")
        self.comboBox_1 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_1.addItems(["X-com", "AB", "User"])
        self.pushButton_3 = QtWidgets.QPushButton("Объединить", self.centralwidget,clicked=self.__union_rows)  # , clicked=self.union
        self.pushButton_4 = QtWidgets.QPushButton("Импорт данных в БД", self.centralwidget, clicked=self.insert_db)
        self.pushButton_5 = QtWidgets.QPushButton("Проверка форматов", self.centralwidget)
        self.pushButton_7 = QtWidgets.QPushButton("Снять флаги", self.centralwidget, clicked=self.__undo_flags)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 7)

        self.horizontalLayout.addWidget(self.pushButton_3)
        self.horizontalLayout.addWidget(self.pushButton_7)
        self.horizontalLayout.addWidget(self.pushButton_5)
        self.horizontalLayout.addWidget(self.pushButton_4)
        self.horizontalLayout.addWidget(self.comboBox_1)
        self.horizontalLayout.addWidget(self.radioButton)

        self.toolButton = QtWidgets.QToolButton(self.centralwidget)
        self.toolButton.setText("...")
        self.toolButton.clicked.connect(self.get_file_path_click)

        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.pushButton = QtWidgets.QPushButton("Загрузить", self.centralwidget,
                                                clicked=self.__load_data)
        self.label = QtWidgets.QLabel(self.centralwidget)

        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout.addLayout(self.gridLayout_6, 0, 0, 1, 1)

        self.gridLayout_6.addWidget(self.toolButton, 1, 2, 1, 1)
        self.gridLayout_6.addWidget(self.pushButton, 1, 1, 1, 1)
        self.gridLayout_6.addWidget(self.lineEdit_2, 1, 0, 1, 1)

        self.setCentralWidget(self.centralwidget)

        self.connect_sql = SqlModule()

    @QtCore.pyqtSlot()
    def __load_data(self):
        self.view.load_table(self.lineEdit_2.text())

    @QtCore.pyqtSlot()
    def __undo_flags(self):
        self.view.undo_flags()

    @QtCore.pyqtSlot()
    def __union_rows(self):
        self.view.union_rows()

    @QtCore.pyqtSlot()
    def get_file_path_click(self):
        fname = QFileDialog.getOpenFileName(self.centralwidget, 'Open file',
                                            'c:\\', "Image files (*.XML *.xlsx)")[0]
        if not fname:
            return
        self.lineEdit_2.setText(fname)

    @QtCore.pyqtSlot()
    def insert_db(self):
        if self.radioButton.isChecked():
            self.connect_sql.clear_list(self.comboBox_1.currentText())

        for row in range(0, self.view.data_model.rowCount()):
            val_list = []
            for col in range(0, self.view.data_model.columnCount()):
                if col in [2,4,5,7,8,10]:
                    val_list += [self.view.data_model.item(row,col).text()]
            self.connect_sql.add_record(val_list)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    main.resize(800, 600)
    sys.exit(app.exec_())
