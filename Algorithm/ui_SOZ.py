#!/usr/bin/env python
# -*- coding:utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import time
import pandas as pd
import Algorithm.sql_connect


class CustomProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._filters = dict()

    @property
    def filters(self):
        return self._filters

    def setFilter(self, expresion, column):
        if expresion:
            self.filters[column] = expresion
        elif column in self.filters:
            del self.filters[column]
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        for column, expresion in self.filters.items():
            text = self.sourceModel().index(source_row, column, source_parent).data()
            regex = QtCore.QRegExp(
                expresion, QtCore.Qt.CaseInsensitive, QtCore.QRegExp.RegExp
            )
            if regex.indexIn(text) == -1:
                return False
        return True


class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, df=pd.DataFrame(), parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent=parent)
        self._df = df.copy()
        self.bolds = dict()

    def toDataFrame(self):
        return self._df.copy()

    def headerData(self, section, orientation, role=QtCore.Qt.DisplayRole):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                try:
                    return self._df.columns.tolist()[section]
                except (IndexError,):
                    return QtCore.QVariant()
            elif role == QtCore.Qt.FontRole:
                return self.bolds.get(section, QtCore.QVariant())
        elif orientation == QtCore.Qt.Vertical:
            if role == QtCore.Qt.DisplayRole:
                try:
                    # return self.df.index.tolist()
                    return self._df.index.tolist()[section]
                except (IndexError,):
                    return QtCore.QVariant()
        return QtCore.QVariant()

    def setFont(self, section, font):
        self.bolds[section] = font
        self.headerDataChanged.emit(QtCore.Qt.Horizontal, 0, self.columnCount())

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()

        if not index.isValid():
            return QtCore.QVariant()

        return QtCore.QVariant(str(self._df.iloc[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):

            value = value.toPyObject()
        else:

            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.centralwidget = QtWidgets.QWidget(self)
        self.setWindowTitle("Система обработки записей")
        self.view = QtWidgets.QTableView(self.centralwidget)
        self.view.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.view.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.resize(800, 600)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.addWidget(self.view, 1, 0, 1, 3)

        self.radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.radioButton.setText("Перезаписать список")
        self.comboBox_1 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_1.addItems(["Добавить новый список", "Test_1", "Test_2"])
        self.pushButton_3 = QtWidgets.QPushButton("Объединить", self.centralwidget, clicked=self.union)
        self.pushButton_4 = QtWidgets.QPushButton("Импорт данных в БД", self.centralwidget)
        self.pushButton_5 = QtWidgets.QPushButton("Проверка форматов", self.centralwidget)
        self.pushButton_7 = QtWidgets.QPushButton("Снять флаги", self.centralwidget, clicked =self.flags_off)

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

        self.pushButton = QtWidgets.QPushButton("Загрузить", self.centralwidget,clicked=self.load_sites)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        # self.lineEdit_2.setMaximumSize(QtCore.QSize(930, 16777215))
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.label = QtWidgets.QLabel(self.centralwidget)

        self.gridLayout_6 = QtWidgets.QGridLayout()
        self.gridLayout.addLayout(self.gridLayout_6, 0, 0, 1, 1)

        self.gridLayout_6.addWidget(self.toolButton, 1, 2, 1, 1)
        self.gridLayout_6.addWidget(self.pushButton, 1, 1, 1, 1)
        self.gridLayout_6.addWidget(self.lineEdit_2, 1, 0, 1, 1)
        self.gridLayout_6.addWidget(self.lineEdit, 2, 0, 1, 1)
        self.gridLayout_6.addWidget(self.comboBox, 2, 1, 1, 10)
        # self.gridLayout_6.addWidget(self.label, 2, 5, 1, 1)

        self.setCentralWidget(self.centralwidget)
        # self.label.setText("Текстовый фильтр")
        # self.comboBox.setMinimumSize(QtCore.QSize(100, 10))
        self.df = self.load_sites()
        self.comboBox.addItems(["{0}".format(col) for col in self.model._df.columns])

        self.lineEdit.textChanged.connect(self.on_lineEdit_textChanged)
        self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)

        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)

    @QtCore.pyqtSlot()
    def load_sites(self):

        path = self.lineEdit_2.text()
        if not path:
            df = pd.DataFrame([], columns=[""])
        if ".XML" in path or ".xml" in path:
            return
        if ".xlsx" in path:
            df = pd.read_excel(path)
            df = df.fillna('')
            df = df.applymap(str)
            if "Объединить" not in list(df):
                df['Объединить'] = "0"
                df = df[list(df)[-1:]+list(df)[:-1]]

        self.model = PandasModel(df)
        self.proxy = CustomProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)
        self.view.resizeColumnsToContents()
        self.view.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.view.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.comboBox.clear()
        self.comboBox.addItems(["{0}".format(col) for col in self.model._df.columns])
        return df

    @QtCore.pyqtSlot(int)
    def on_view_horizontalHeader_sectionClicked(self, logicalIndex):

        self.logicalIndex = logicalIndex
        self.menuValues = QtWidgets.QMenu(self)
        self.signalMapper = QtCore.QSignalMapper(self)
        self.comboBox.blockSignals(True)
        self.comboBox.setCurrentIndex(self.logicalIndex)
        self.comboBox.blockSignals(True)

        valuesUnique = self.model._df.iloc[:, self.logicalIndex].unique()

        actionAll = QtWidgets.QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()
        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):
            action = QtWidgets.QAction(actionName, self)
            self.signalMapper.setMapping(action, actionNumber)
            action.triggered.connect(self.signalMapper.map)
            self.menuValues.addAction(action)
        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)
        headerPos = self.view.mapToGlobal(self.horizontalHeader.pos())
        posY = headerPos.y() + self.horizontalHeader.height()
        posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)

        self.menuValues.exec_(QtCore.QPoint(posX, posY))

    @QtCore.pyqtSlot()
    def flags_off(self):
        path = self.lineEdit_2.text()

        df = pd.read_excel(path)
        df = df.fillna('')
        df = df.applymap(str)
        df = df.drop(columns=["Объединить"])
        if "Объединить" not in list(df):
            df['Объединить'] = "0"
            df = df[list(df)[-1:]+list(df)[:-1]]

        self.model = PandasModel(df)
        self.proxy = CustomProxyModel(self)
        self.proxy.setSourceModel(self.model)
        self.view.setModel(self.proxy)
        self.view.resizeColumnsToContents()
        self.view.setEditTriggers(QtWidgets.QAbstractItemView.AllEditTriggers)
        self.view.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.comboBox.clear()
        self.comboBox.addItems(["{0}".format(col) for col in self.model._df.columns])

    @QtCore.pyqtSlot()
    def union(self):
        time.sleep(5)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setWindowTitle("Информационное окно")
        msg.setText("Объединение строк прошло успешно")
        msg.exec_()

    @QtCore.pyqtSlot()
    def on_actionAll_triggered(self):
        filterColumn = self.logicalIndex
        self.proxy.setFilter("", filterColumn)

    @QtCore.pyqtSlot(int)
    def on_signalMapper_mapped(self, i):
        stringAction = self.signalMapper.mapping(i).text()
        filterColumn = self.logicalIndex
        self.proxy.setFilter(stringAction, filterColumn)

    @QtCore.pyqtSlot(str)
    def on_lineEdit_textChanged(self, text):
        self.proxy.setFilter(text, self.proxy.filterKeyColumn())

    @QtCore.pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)

    @QtCore.pyqtSlot()
    def get_file_path_click(self):
        fname = QFileDialog.getOpenFileName(self.centralwidget, 'Open file',
                                            'c:\\', "Image files (*.XML *.xlsx)")[0]
        if not fname:
            return
        self.lineEdit_2.setText(fname)


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    main.resize(800, 600)
    sys.exit(app.exec_())
