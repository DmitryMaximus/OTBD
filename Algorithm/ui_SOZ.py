#!/usr/bin/env python
# -*- coding:utf-8 -*-

from model import *
from db_connection import *


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
        self.pushButton_3 = QtWidgets.QPushButton("Объединить", self.centralwidget, clicked=self.__union_rows)  # , clicked=self.union
        self.pushButton_4 = QtWidgets.QPushButton("Импорт данных в БД", self.centralwidget, clicked=self.insert_data)
        self.pushButton_5 = QtWidgets.QPushButton("Проверка форматов", self.centralwidget)
        self.pushButton_7 = QtWidgets.QPushButton("Снять флаги", self.centralwidget, clicked=self.__undo_flags)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 7)

        self.horizontalLayout.addWidget(self.pushButton_3)
        self.horizontalLayout.addWidget(self.pushButton_7)
        self.horizontalLayout.addWidget(self.pushButton_5)
        self.horizontalLayout.addWidget(self.pushButton_4)
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

        self.rows_deduplicated = 0

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
                                            'c:\\', "Excel files (*.XML *.xlsx)")[0]
        if not fname:
            return
        self.lineEdit_2.setText(fname)

    def parse_data(self):
        data = {"X-com": [], 'AB': [], "User": []}
        col_num = 7
        for row in range(0, self.view.data_model.rowCount()):
            row_val_list = []
            for col in range(0, self.view.data_model.columnCount()):
                row_val_list += [self.view.data_model.item(row, col).text()]
            data[self.view.data_model.item(row, col_num).text()] += [row_val_list]

        return data

    def show_info(self, rows_insert: int, rows_dedup):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Добавлено/удалено  строк: " + str(rows_insert) + "\nДедублицировано строк: "
                    + str(rows_dedup))
        msg.setWindowTitle("Статистика по загрузке")
        msg.exec_()

    def insert_db_dedup(self, data):
        rows_insert = 0
        rows_dedup = 0

        data_db = self.connect_sql.create_df(data[0][7])
        for row in data:
            if str(row[2]).strip().lower() == "удаление":
                self.connect_sql.complex_row_remove(row)
            else:
                if row[11] == 'ЮЛ':
                    values_d = {}
                    if len(data_db[data_db['inn'] == row[31]]) > 0:
                        company_id = data_db[data_db['inn'] == row[31]]['id'].values[0][1]
                        convert_d = {40:36,41:27,43:28,44:29,45:30,49:31,50:32,51:33,52:34,53:35,17:17}
                        for i in [41, 43, 44, 45, 49, 50, 51, 52, 53, 40]:
                            if not pd.isna(row[i]) or row[i] != '':
                                values_d[i] = row[i]
                        for iter in range(1, 6):
                            if data_db['alt_name_' + str(iter)].values[0] == None:
                                values_d[17] = row[17]  # Делаем из Наименование(главное рус) альтернативное наименование

                        for key in values_d.keys():
                            self.connect_sql.update_dedup(values_d[key],company_id,convert_d[key],mode=1)
                            rows_dedup +=1
                    else:
                        self.connect_sql.add_record(row)
                        rows_insert+=1

                elif row[11] == 'ФЛ':
                    values_d = {}
                    if len(data_db[(data_db['name_main_rus'] == row[31]) & (data_db['birth_date'] == row[21])]) > 0:
                        company_id = data_db[data_db['inn'] == row[31]]['id'].values[0][1]
                        convert_d = {40: 36, 41: 27, 43: 28, 44: 29, 45: 30, 49: 31, 50: 32, 51: 33, 52: 34, 53: 35, 17: 17, 16:16}
                        for i in [41, 43, 44, 45, 49, 50, 51, 52, 53, 40]:
                            if not pd.isna(row[i]) or row[i] != '':
                                values_d[i] = row[i]
                        for iter in range(1, 6):
                            if data_db['alt_name_' + str(iter)].values[0] == None:
                                values_d[16] = row[16]  # Делаем из Наименование(главное рус) альтернативное наименование

                        for key in values_d.keys():
                            self.connect_sql.update_dedup(values_d[key], company_id, convert_d[key], mode=1)
                            rows_dedup += 1
                    else:
                        self.connect_sql.add_record(row)
                        rows_insert += 1
        self.show_info(rows_insert,rows_dedup)

    def insert_db_rewrite(self, data):
        self.connect_sql.clear_list(data[0][7])

        for row in data:
            if str(row[2]).strip().lower() != "удаление":
                self.connect_sql.add_record(row)
            else:
                self.connect_sql.complex_row_remove(row)

    @QtCore.pyqtSlot()
    def insert_data(self):
        try:
            data_dict = self.parse_data()
            if self.radioButton.isChecked():
                ret = QMessageBox().question(self, '', "Вы действительно хотите перезаписать список?", QMessageBox().Yes | QMessageBox().No)
                if ret == QMessageBox().Yes:
                    counter = 0
                    for i in data_dict.keys():  # проверка что спискb не пустые, чтобы очистить список в базе
                        if len(data_dict[i]) > 0:
                            self.insert_db_rewrite(data_dict[i])
                            counter += len(data_dict[i])
                    QMessageBox(QMessageBox.Information, "Импорт данных в БД", "В базу данных было успешно импортировано " + str(counter) + " строк").exec_()
            else:
                ret = QMessageBox().question(self, '', "Вы действительно хотите добавить/удалить записи?", QMessageBox().Yes | QMessageBox().No)
                if ret == QMessageBox().Yes:
                    for i in data_dict.keys():  # проверка что спискb не пустые, чтобы очистить список в базе
                        if len(data_dict[i]) > 1:
                            self.insert_db_dedup(data_dict[i])

        except:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Проверьте корректность вводимых данных в поле 'Код источника записи'")
            msg.setWindowTitle("Ошибка при загрузке данных")
            msg.exec_()




if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    main.resize(800, 600)
    sys.exit(app.exec_())
