from PyQt5.QtWidgets import QDialog, QApplication,QAbstractItemView
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import QMessageBox, QMenu
from link_window import *
from Progress import ProgressBar
from PyQt5.QtWidgets import (QWidget, QProgressBar,
    QPushButton, QApplication)
class MyTree(QDialog):
    def __init__(self):
        super().__init__()
        self.treeView = QtWidgets.QTreeView()
        self.treeView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.treeView.setGeometry(QtCore.QRect(70, 50, 256, 192))
        self.treeView.setObjectName("treeView")
        boxMain = QtWidgets.QVBoxLayout()
        boxMain.addWidget(self.treeView)
        self.setLayout(boxMain)
        self.source = []
        self.connect = SqlModule()

        self.treeView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView.customContextMenuRequested.connect(self.generateMenu)
        self.treeView.viewport().installEventFilter(self)
        self.link_wind = LinkWindow()
        self.model=None

    def load_table_sql(self, source):

        df = self.connect.create_df(source)
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.drop(df[df.is_active != 1].index)

        result_df = pd.DataFrame([],
                                 columns=list(confdict['COLUMNS'].values())[1:])  # Используем вспомогательный df для замены названий колонок на человеческие и правильного порядка
        for column in list(df):
            if column in list(confdict['COLUMNS'].keys())[1:]:
                result_df[confdict['COLUMNS'][column]] = df[column]

        result_df = result_df.fillna('')
        result_df = result_df.applymap(lambda x: str(x).strip())

        return result_df

    def create_link(self, df_p: pd.DataFrame, df_ch: pd.DataFrame) -> dict:
        """
        :param df_p: родительский дф
        :param df_ch: дочерний дф
        :return: возвращает словарь связей для загрузки в таблицу Connections {id_p:id_ch}
        """
        result_dict = {}
        self.Progress = ProgressBar(len(df_p))
        for i, row in df_p.iterrows():
            # Совпадение ИНН + ОГРН непуст
            result_list = []
            mask = (df_ch['ИНН'] != "") & (df_ch['ИНН'] == row['ИНН'])  & (df_ch['Тип записи'] == "0")
            result_list = list(df_ch.loc[df_ch[mask].index]['id'].values)

            if len(result_list) == 0:
                mask = (df_ch['ФИО'] != "") & (df_ch['Дата рождения'] != "") & (df_ch['Тип записи'] == "1") & (df_ch['Дата рождения'] != row['Дата рождения']) \
                       & (df_ch['ФИО'] != row['ФИО'])
                result_list = list(df_ch.loc[df_ch[mask].index]['id'].values)

            result_dict[row['id']] = result_list
            self.Progress.SendStep()
        return result_dict


    def populate_list(self, prior_df="AB",mode=0):

        remember_con = self.connect.get_connections(1)
        ignore_con = self.connect.get_connections(2)
        if mode == 0:
            if prior_df == "AB":
                parent_df = self.load_table_sql("AB")
                ch_1 = self.load_table_sql("X-com")
                ch_2 = self.load_table_sql("User")
                ch_3 = self.load_table_sql("TR санкции")

            elif prior_df == "X-com":
                parent_df = self.load_table_sql("X-com")
                ch_1 = self.load_table_sql("AB")
                ch_2 = self.load_table_sql("User")
                ch_3 = self.load_table_sql("TR санкции")
            else:
                parent_df = self.load_table_sql("User")
                ch_1 = self.load_table_sql("AB")
                ch_2 = self.load_table_sql("X-com")
                ch_3 = self.load_table_sql("TR санкции")

            d_ch1 = self.create_link(parent_df, ch_1)
            d_ch2 = self.create_link(parent_df, ch_2)
            d_ch3 = self.create_link(parent_df, ch_3)
            for element in remember_con:
                if str(element[0]) in d_ch1.keys():
                    if str(element[1]) not in d_ch1[str(element[0])]:
                        temp = d_ch1[str(element[0])]
                        temp += [str(element[1])]
                        d_ch1[str(element[0])] = temp
                elif str(element[0]) in d_ch2.keys():
                    if str(element[1]) not in d_ch2[str(element[0])]:
                        temp = d_ch2[str(element[0])]
                        temp += [str(element[1])]
                        d_ch2[str(element[0])] = temp
                elif str(element[0]) in d_ch3.keys():
                    if str(element[1]) not in d_ch3[str(element[0])]:
                        temp = d_ch3[str(element[0])]
                        temp += [str(element[1])]
                        d_ch3[str(element[0])] = temp


            for element in ignore_con:
                if str(element[0]) in d_ch1.keys():
                    if str(element[1]) in d_ch1[str(element[0])]:
                        QApplication.processEvents()
                        temp = d_ch1[str(element[0])]
                        temp.remove(str(element[1]))
                        d_ch1[str(element[0])] = temp
                elif str(element[0]) in d_ch2.keys():
                    if str(element[1]) in d_ch2[str(element[0])]:
                        QApplication.processEvents()
                        temp = d_ch2[str(element[0])]
                        temp.remove(str(element[1]))
                        d_ch2[str(element[0])] = temp
                elif str(element[0]) in d_ch3.keys():
                    if str(element[1]) not in d_ch3[str(element[0])]:
                        QApplication.processEvents()
                        temp = d_ch3[str(element[0])]
                        temp += [str(element[1])]
                        d_ch3[str(element[0])] = temp

            model = QStandardItemModel(0, len(list(parent_df)), self.treeView)
            for i in range(0, len(list(parent_df))):
                model.setHeaderData(i, Qt.Horizontal, list(parent_df)[i])
            self.Progress = ProgressBar(len(parent_df))
            for i, row in parent_df.iterrows():

                p_row = row.apply(lambda x: QtGui.QStandardItem(str(x))).values
                if row['id'] in d_ch1.keys():
                    for i in d_ch1[row['id']]:
                        p_row[0].appendRow(ch_1[ch_1['id'] == i].apply(lambda x: QtGui.QStandardItem(str(*x.values))).values)

                if row['id'] in d_ch2.keys():
                    for i in d_ch2[row['id']]:
                        p_row[0].appendRow(ch_1[ch_1['id'] == i].apply(lambda x: QtGui.QStandardItem(str(*x.values))).values)

                if row['id'] in d_ch3.keys():
                    for i in d_ch3[row['id']]:
                        p_row[0].appendRow(ch_1[ch_1['id'] == i].apply(lambda x: QtGui.QStandardItem(str(*x.values))).values)
                model.appendRow(p_row)
                self.Progress.SendStep()
            comp_id_list = []
            for i in list(d_ch1.values()):
                for j in i:
                    if j not in comp_id_list:
                        comp_id_list.append(j)

            for i in list(d_ch2.values()):
                for j in i:
                    if j not in comp_id_list:
                        comp_id_list.append(j)

            for i in list(d_ch3.values()):
                for j in i:
                    if j not in comp_id_list:
                        comp_id_list.append(j)

            for i, row in ch_1.iterrows():
                if row['id'] not in comp_id_list:
                    QApplication.processEvents()
                    model.appendRow(row.apply(lambda x: QtGui.QStandardItem(x)).values)

            for i, row in ch_2.iterrows():
                if row['id'] not in comp_id_list:
                    QApplication.processEvents()
                    model.appendRow(row.apply(lambda x: QtGui.QStandardItem(x)).values)

            for i, row in ch_3.iterrows():
                if row['id'] not in comp_id_list:
                    QApplication.processEvents()
                    model.appendRow(row.apply(lambda x: QtGui.QStandardItem(x)).values)
        else:
            if prior_df == "AB":
                QApplication.processEvents()
                parent_df = self.load_table_sql("AB")
                ch_1 = self.load_table_sql("X-com")
                ch_2 = self.load_table_sql("User")

            elif prior_df == "X-com":
                QApplication.processEvents()
                parent_df = self.load_table_sql("X-com")
                ch_1 = self.load_table_sql("AB")
                ch_2 = self.load_table_sql("User")
            else:
                QApplication.processEvents()
                parent_df = self.load_table_sql("User")
                ch_1 = self.load_table_sql("AB")
                ch_2 = self.load_table_sql("X-com")

            d_ch1 = self.create_link(parent_df, ch_1)
            d_ch2 = self.create_link(parent_df, ch_2)
            for element in remember_con:
                QApplication.processEvents()
                if str(element[0]) in d_ch1.keys():
                    if str(element[1]) not in d_ch1[str(element[0])]:
                        temp = d_ch1[str(element[0])]
                        temp += [str(element[1])]
                        d_ch1[str(element[0])] = temp
                elif str(element[0]) in d_ch2.keys():
                    if str(element[1]) not in d_ch2[str(element[0])]:
                        temp = d_ch2[str(element[0])]
                        temp += [str(element[1])]
                        d_ch2[str(element[0])] = temp


            for element in ignore_con:
                QApplication.processEvents()
                if str(element[0]) in d_ch1.keys():
                    if str(element[1]) in d_ch1[str(element[0])]:
                        temp = d_ch1[str(element[0])]
                        temp.remove(str(element[1]))
                        d_ch1[str(element[0])] = temp
                elif str(element[0]) in d_ch2.keys():
                    if str(element[1]) in d_ch2[str(element[0])]:
                        temp = d_ch2[str(element[0])]
                        temp.remove(str(element[1]))
                        d_ch2[str(element[0])] = temp


            model = QStandardItemModel(0, len(list(parent_df)), self.treeView)
            for i in range(0, len(list(parent_df))):
                model.setHeaderData(i, Qt.Horizontal, list(parent_df)[i])

            for i, row in parent_df.iterrows():

                p_row = row.apply(lambda x: QtGui.QStandardItem(str(x))).values
                if row['id'] in d_ch1.keys():
                    for i in d_ch1[row['id']]:
                        p_row[0].appendRow(ch_1[ch_1['id'] == i].apply(lambda x: QtGui.QStandardItem(str(*x.values))).values)

                if row['id'] in d_ch2.keys():
                    for i in d_ch2[row['id']]:
                        p_row[0].appendRow(ch_1[ch_1['id'] == i].apply(lambda x: QtGui.QStandardItem(str(*x.values))).values)

                model.appendRow(p_row)

            comp_id_list = []
            for i in list(d_ch1.values()):
                QApplication.processEvents()
                for j in i:
                    if j not in comp_id_list:
                        comp_id_list.append(j)

            for i in list(d_ch2.values()):
                QApplication.processEvents()
                for j in i:
                    if j not in comp_id_list:
                        comp_id_list.append(j)

            for i, row in ch_1.iterrows():
                QApplication.processEvents()
                if row['id'] not in comp_id_list:
                    model.appendRow(row.apply(lambda x: QtGui.QStandardItem(x)).values)

            for i, row in ch_2.iterrows():
                QApplication.processEvents()
                if row['id'] not in comp_id_list:
                    model.appendRow(row.apply(lambda x: QtGui.QStandardItem(x)).values)

        self.model = model
        self.treeView.setModel(model)
        return model

    def remove_row(self, q_point):
        buttonReply = QMessageBox.question(self, 'Подтверждение удаления', "Вы действительно хотите удалить запись?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            pass# self.treeView.rowsRemoved(self.treeView.selectedIndexes()
        else:
            pass
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress and
                event.buttons() == QtCore.Qt.RightButton and
                source is self.treeView.viewport()):
            self.menu = QMenu(self)
            pos = event.globalPos()

            removeRow = self.menu.addAction('Объединить\\Разъединить')
            removeRow.triggered.connect(self.create_con)

            collapse = self.menu.addAction('Скрыть все строки')
            collapse.triggered.connect(self.collapse)

            un_collapse = self.menu.addAction('Раскрыть все строки')
            un_collapse.triggered.connect(self.un_collapse)

            self.menu.popup(pos)
        return super(MyTree, self).eventFilter(source, event)

    def generateMenu(self, pos):
        pass

    def create_con(self):
        self.link_wind.centralwidget.show()

    def collapse(self):
        self.treeView.collapseAll()

    def un_collapse(self):
        self.treeView.expandAll()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyTree()
    w.show()
    sys.exit(app.exec_())
