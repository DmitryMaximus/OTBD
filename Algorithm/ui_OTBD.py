from model import *
from tree_model import *
from delta import *
from Export import *
from proxy import *

class UI_OTBD(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.x, self.y, self.w, self.h = 0, 0, 1200, 651
        self.setGeometry(self.x, self.y, self.w, self.h)

        self.window = MainWindow(self)
        self.setCentralWidget(self.window)
        self.setWindowTitle("Работа с ЭТБД")
        self.show()


class GeneralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GeneralWidget, self).__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)

        self.tableView = MyDelegateInTableView()
        self.tableView.setLayout(lay)
        self.pushButton = QtWidgets.QPushButton("Отобразить список", clicked=self.__load_sql)
        self.pushButton_1 = QtWidgets.QPushButton("Внести изменения в БД", clicked=self.__change_row)
        self.pushButton_2 = QtWidgets.QPushButton("Выгрузить в Excel", clicked=self.__export_excel)
        self.comb_list = QtWidgets.QComboBox(self)
        self.comb_list.addItem("X-com")
        self.comb_list.addItem("AB")
        self.comb_list.addItem("User")
        self.comb_list.addItem("TR санкции")

        self.treemodel = None

        lay.addWidget(self.tableView)
        lay.addWidget(self.comb_list)
        lay.addWidget(self.pushButton)
        lay.addWidget(self.pushButton_1)
        lay.addWidget(self.pushButton_2)
    @QtCore.pyqtSlot()
    def __load_sql(self):
        self.tableView.load_table_sql(self.comb_list.currentText())
    @QtCore.pyqtSlot()
    def __change_row(self):
        self.tableView._change_row()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Данные успешно изменены в БД")
        msg.setWindowTitle("Изменение данных в БД")
        msg.exec_()


    def __export_excel(self):

        path_to_save = QFileDialog.getExistingDirectory()
        export_excel(self.tableView.data_model, path_to_save)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Данные успешно выгружены в Excel")
        msg.setWindowTitle("Выгрузка")
        msg.exec_()

class OptionsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OptionsWidget, self).__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)
        hlay = QtWidgets.QHBoxLayout()
        lay.addLayout(hlay)
        self.lay_h = QtWidgets.QHBoxLayout(self)
        self.lay_h.setAlignment(Qt.AlignRight)

        self.treeView = MyTree()
        self.rewrite_radio = QtWidgets.QRadioButton()
        self.radio_label = QtWidgets.QLabel("Использовать рефенитив для формирования представления?")

        self.pushButton_2 = QtWidgets.QPushButton("Отобразить дерево", clicked = self.__populate_list)
        self.pushButton_4 = QtWidgets.QPushButton("Выгрузка дельты",clicked = self.__create_delta)
        self.pushButton_5 = QtWidgets.QPushButton("Выгрузка Excel",clicked = self.__export_excel_tree)

        self.priority = QtWidgets.QComboBox(self)
        self.priority.addItem("X-com")
        self.priority.addItem("AB")
        self.priority.addItem("User")

        lay.addWidget(self.treeView)
        lay.addLayout(self.lay_h)
        self.lay_h.addWidget(self.radio_label)
        self.lay_h.addWidget(self.rewrite_radio)
        lay.addWidget(self.priority)
        lay.addWidget(self.pushButton_2)
        # lay.addWidget(self.pushButton_3)
        lay.addWidget(self.pushButton_4)
        lay.addWidget(self.pushButton_5)

    def __populate_list(self):
        if self.rewrite_radio.isChecked():
            self.treemodel = self.treeView.populate_list(self.priority.currentText())
        else:
            self.treemodel = self.treeView.populate_list(self.priority.currentText(),mode=0)
        df = aggregation(self.treemodel).fillna("")
        df = df.applymap(str)
        df = df.fillna("")
        df.to_excel(os.path.dirname(os.path.abspath(__file__)) + "\data_temp.xlsx",index=False)

    def __create_delta(self):

        path_to_save = QFileDialog.getExistingDirectory()
        create_delta(self.treemodel,path_to_save)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Дельта успешно выгружена")
        msg.setWindowTitle("Выгрузка дельты")
        msg.exec_()

    def __export_excel_tree(self):
        path_to_save = QFileDialog.getExistingDirectory()
        export_excel_tree(self.treemodel, path_to_save)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Данные успешно выгружены в Excel")
        msg.setWindowTitle("Выгрузка")
        msg.exec_()

class UnionWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UnionWidget, self).__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)
        hlay = QtWidgets.QHBoxLayout()
        lay.addLayout(hlay)
        self.show_df = QtWidgets.QPushButton("Отобразить данные", clicked=self.shot_union)
        self.tableView = DataFrameWidget()
        lay.addWidget(self.tableView)
        lay.addWidget(self.show_df)
    def shot_union(self):
        try:
            QApplication.processEvents()
            df = pd.read_excel(os.path.dirname(os.path.realpath(__file__)) + "\data_temp.xlsx")
            self.tableView.setDataFrame(df)
        except:
            pass

class SettingWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SettingWidget, self).__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)

        self.pushButton_2 = QtWidgets.QPushButton("Обновить данные", clicked=self.__update_data)
        self.tableView = MyDelegateInTableView()
        self.tableView.setLayout(lay)
        self.__load_keys()

        lay.addWidget(self.tableView)
        lay.addWidget(self.pushButton_2)

    def __load_keys(self):
        self.tableView._load_keys()

    @QtCore.pyqtSlot()
    def __update_data(self):
        data = []
        self.Progress = ProgressBar(self.tableView.data_model.rowCount())

        for row in range(0, self.tableView.data_model.rowCount()):
            row_val_list = []
            for col in range(0, self.tableView.data_model.columnCount()):
                row_val_list += [self.tableView.data_model.item(row, col).text()]
            if row_val_list[0] in set([i[0] for i in self.tableView.changed_items]):
                data += [row_val_list]
            self.Progress.SendStep()
        for elem in self.tableView.changed_items:
            if elem[1] == '0' and elem[2]==0:
                data+=[[elem[0]]]
        self.tableView._update_keys(data)

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MainWindow, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        tab_holder = QtWidgets.QTabWidget()
        tab_holder.addTab(GeneralWidget(), "Работа со списками")
        tab_holder.addTab(OptionsWidget(), "Общий список")
        tab_holder.addTab(UnionWidget(), "Объединенное представление")
        tab_holder.addTab(SettingWidget(), "Ключевые слова рефенитив")

        layout.addWidget(tab_holder)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = UI_OTBD()
    sys.exit(app.exec_())
