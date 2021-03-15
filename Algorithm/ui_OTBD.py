# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
import pandas as pd
from Algorithm.proxy import DataFrameApp, WidgetedCell,ExampleWidgetForWidgetedCell,DataFrameWidget
# import Algorithm.sql_connect

class UI_OTBD(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(UI_OTBD, self).__init__(parent)
        self.resize(1436, 1010)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.Result = QtWidgets.QWidget()
        self.Result.setObjectName("Result")
        self.treeView = QtWidgets.QTreeView(self.Result)
        self.treeView.setGeometry(QtCore.QRect(0, 0, 1411, 911))
        self.treeView.setObjectName("treeView")
        self.treeView.header().setSortIndicatorShown(True)
        self.comboBox_3 = QtWidgets.QComboBox(self.Result)
        self.comboBox_3.setGeometry(QtCore.QRect(1228, 919, 171, 22))
        self.comboBox_3.setObjectName("comboBox_3")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.comboBox_3.addItem("")
        self.label_2 = QtWidgets.QLabel(self.Result)
        self.label_2.setGeometry(QtCore.QRect(1100, 920, 121, 20))
        self.label_2.setObjectName("label_2")
        self.tabWidget.addTab(self.Result, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tableView = DataFrameWidget()#QtWidgets.QTableView(self.tab_2)
        # self.load_sites()
        # self.tableView.setGeometry(QtCore.QRect(0, 0, 1411, 871))
        # self.tableView.setSortingEnabled(True)
        # self.tableView.setObjectName("tableView")
        # self.tableView.verticalHeader().setSortIndicatorShown(True)
        self.pushButton = QtWidgets.QPushButton(self.tab_2)
        self.pushButton.setGeometry(QtCore.QRect(0, 880, 111, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_2.setGeometry(QtCore.QRect(0, 910, 111, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.comboBox = QtWidgets.QComboBox(self.tab_2)
        self.comboBox.setGeometry(QtCore.QRect(1196, 880, 211, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.pushButton_3 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_3.setGeometry(QtCore.QRect(1070, 880, 111, 23))
        self.pushButton_3.setObjectName("pushButton_3")
        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(140, 880, 101, 21))
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.tab_2)
        self.lineEdit.setGeometry(QtCore.QRect(250, 880, 391, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.comboBox_2 = QtWidgets.QComboBox(self.tab_2)
        self.comboBox_2.setGeometry(QtCore.QRect(650, 880, 151, 22))
        self.comboBox_2.setObjectName("comboBox_2")
        self.pushButton_4 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_4.setGeometry(QtCore.QRect(140, 910, 111, 23))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_5.setGeometry(QtCore.QRect(270, 910, 111, 23))
        self.pushButton_5.setObjectName("pushButton_5")
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 1, 1, 1)
        self.setCentralWidget(self.centralwidget)

        self.retranslateUi(UI_OTBD)
        self.tabWidget.setCurrentIndex(1)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.comboBox_3.setItemText(0, _translate("MainWindow", "Test_1"))
        self.comboBox_3.setItemText(1, _translate("MainWindow", "Test_2"))
        self.comboBox_3.setItemText(2, _translate("MainWindow", "Xcomp"))
        self.label_2.setText(_translate("MainWindow", "Приоритетный список"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.Result), _translate("MainWindow", "Результирующая таблица"))
        self.pushButton.setText(_translate("MainWindow", "Добавить строку"))
        self.pushButton_2.setText(_translate("MainWindow", "Удалить строку"))
        self.comboBox.setItemText(0, _translate("MainWindow", "Test_1"))
        self.comboBox.setItemText(1, _translate("MainWindow", "Test_2"))
        self.comboBox.setItemText(2, _translate("MainWindow", "Xcomp"))
        self.pushButton_3.setText(_translate("MainWindow", "Отобразить список"))
        self.label.setText(_translate("MainWindow", "Текстовый фильтр"))
        self.pushButton_4.setText(_translate("MainWindow", "Объединить строки"))
        self.pushButton_5.setText(_translate("MainWindow", "Снять флаги"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Пользовательские списки"))

    @QtCore.pyqtSlot()
    def load_sites(self):
        df=pd.read_excel(r"C:\Users\Root\Desktop\Projects\OTBD\Test_data\Шаблон.xlsx")
        df = df.applymap(str)
        df = df.fillna("")
        for i, row in df.iterrows():
            df.at[i, "Объединить"] = WidgetedCell(ExampleWidgetForWidgetedCell)

        self.df = df
        self.tableView._data_model.setDataFrame(df)


    def form_tree(self,dataframe):
            tree_level_inn = dataframe[(dataframe['Тип записи'] == "ЮЛ") & (dataframe['ИНН'].apply(lambda x: ~pd.isna(x))) & (dataframe['ОГРН'].apply(lambda x: ~pd.isna(x)))]
            tree_level_no_inn = dataframe[(dataframe['Тип записи'] == "ЮЛ") & (dataframe['ИНН'].apply(lambda x: pd.isna(x))) & (dataframe['ОГРН'].apply(lambda x: pd.isna(x)))]
            tree_level_inn_fl = dataframe[dataframe['Тип записи'] == "ФЛ"]
            agg_cols = ['ИНН', 'ОГРН']
            for i in agg_cols:
                del dataframe[i]
            tree_level_inn = tree_level_inn.groupby(agg_cols, as_index=False).agg(dataframe)

    # @QtCore.pyqtSlot()
    # def update_data(self):
    #     df = pd.read_excel(r"C:\Users\Root\Desktop\Projects\OTBD\Test_data\Шаблон.xlsx")
    #     df = df.applymap(str)
    #     df = df.fillna("")
    #
    #     if self.comboBox.Currenttext() == "Xcomp":
    #         for i, row in df.iterrows():
    #             df.at[i, "Объединить"] = WidgetedCell(ExampleWidgetForWidgetedCell)
    #         self.df = df
    #         self.tableView._data_model.setDataFrame(self.df)
    #     if self.comboBox.Currenttext() == "Test_1":
    #         df_t = pd.DataFrame([],columns=list(df))
    #         self.tableView._data_model.setDataFrame(df_t)

class DataModel(QtCore.QAbstractTableModel):
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

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main = UI_OTBD()
    main.show()

    sys.exit(app.exec_())