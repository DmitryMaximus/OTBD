import sys

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import *
from deduplication import deduplicate
from db_connection import *
from SendStatistic import send_statistic

class Delegate(QtWidgets.QStyledItemDelegate):

    def createEditor(self, parent, options, index):
        if index.column() in []:
            editor = QtWidgets.QDateEdit(parent)
            editor.setFrame(False)
            editor.setCalendarPopup(True)  # Вместо стрелок вылезает календарь
            return editor

    def setEditorData(self, editor, index):
        if index.column() in []:
            editor.setDateTime(QtCore.QDateTime.currentDateTime())

    def updateEditorGeometry(self, editor, options, index):
        editor.setGeometry(options.rect)

    def setModelData(self, editor, model, index):
        if index.column() in []:
            value = str(editor.dateTime().date().toPyDate())
            model.setData(index, value, QtCore.Qt.EditRole)


class MyDelegateInTableView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.table = QtWidgets.QTableView()  # Представление
        self.header = self.table.horizontalHeader()
        self.table.verticalHeader().setVisible(False)
        self.header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.data_model = QtGui.QStandardItemModel(parent=self.table)  # Модель
        self.table.setModel(self.data_model)

        boxMain = QtWidgets.QVBoxLayout()
        boxMain.addWidget(self.table)
        self.setLayout(boxMain)

        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.generateMenu)
        self.table.viewport().installEventFilter(self)
        self.df = pd.DataFrame([], columns=[""])

        self.changed_items = []
        self.data_model.itemChanged.connect(self.log_changed)

        self.id_col_pos = 0  # Данный параметр необходим, что корректно учитывать в какой строке изменились данные и вносить в БД присвоение происходит в методе load_table_sql

    def log_changed(self, item):
            if not [[self.data_model.item(item.row(), self.id_col_pos).text(), str(item.column()), item.text()]] in self.changed_items:
                self.changed_items += [[self.data_model.item(item.row(), self.id_col_pos).text(), str(item.column()), item.text()]]

    def load_table(self, path):
        self.data_model.removeColumns(0, self.data_model.columnCount())

        if not path:
            pass
        if ".XML" in path or ".xml" in path:
            return
        if ".xlsx" in path:
            self.df = pd.read_excel(path,dtype=str)
            self.df = self.df.fillna('')
            self.df = self.df.applymap(lambda x: str(x).strip())
            initial_len  = len(self.df)
            new_df = []
            for val in set(self.df['Код источника записи'].values.tolist()):
                if len(new_df)==0:
                    new_df = deduplicate(self.df[self.df['Код источника записи']==val])
                else:
                    new_df = pd.concat([deduplicate(self.df[self.df['Код источника записи']==val]),new_df], ignore_index=True)
            self.df=new_df
            result_len = len(self.df)
            if "Объединить" not in list(self.df):
                self.df['Объединить'] = "0"
                self.df = self.df[list(self.df)[-1:] + list(self.df)[:-1]]

        self.df = self.df.applymap(lambda x: QtGui.QStandardItem(str(x)))
        for col in list(self.df):
            self.data_model.appendColumn(self.df[col].tolist())
        self.data_model.setHorizontalHeaderLabels(list(self.df))

        delta = initial_len - result_len
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Загружено  строк изначально: " + str(initial_len) + "\nДедублицировано строк: "
                            + str(delta) + "\nКоличество строк после дедубликации: " + str(result_len))
        msg.setWindowTitle("Статистика по загрузке")
        msg.exec_()
        send_statistic(49,int(self.data_model.rowCount()))
        return self.data_model

    def load_table_sql(self, source):
        self.data_model.removeRows(0,self.data_model.rowCount())
        self.data_model.removeColumns(0, self.data_model.columnCount())

        connect = SqlModule()
        self.df = connect.create_df(source)
        if "Объединить" not in list(self.df):
            self.df['Объединить'] = "0"
            self.df = self.df[list(self.df)[-1:] + list(self.df)[:-1]]
        self.df = self.df.loc[:, ~self.df.columns.duplicated()]

        result_df = pd.DataFrame([], columns=list(confdict['COLUMNS'].values()))  # Используем вспомогательный df для замены названий колонок на человеческие и правильного порядка
        for column in list(self.df):
            if column in list(confdict['COLUMNS'].keys()):
                result_df[confdict['COLUMNS'][column]] = self.df[column]

        result_df = result_df.fillna('')
        result_df = result_df.applymap(lambda x: str(x).strip())

        self.id_col_pos = list(result_df).index("id")

        result_df = result_df.applymap(lambda x: QtGui.QStandardItem(str(x)))
        for col in list(result_df):
            self.data_model.appendColumn(result_df[col].tolist())
        self.data_model.setHorizontalHeaderLabels(list(result_df))
        return self.data_model

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress and
                event.buttons() == QtCore.Qt.RightButton and
                source is self.table.viewport()):
            self.menu = QMenu(self)
            pos = event.globalPos()
            #
            # addRow = self.menu.addAction('Добавить строку')
            # addRow.triggered.connect(
            #     lambda: self.add_row())

            # sort = self.menu.addAction('Отсортировать')
            # sort.triggered.connect(
            #     lambda: self.sort(pos))

            removeRow = self.menu.addAction('Удалить')
            removeRow.triggered.connect(
                lambda: self.remove_row_from_rigth_click(pos))

            self.menu.popup(pos)

        return super(MyDelegateInTableView, self).eventFilter(source, event)

    def generateMenu(self, pos):
        pass

    def add_row(self):
        empty_l = []
        for col in list(self.df):
            if col == "id":
                empty_l += [QStandardItem(str(self.df["id"].max()+1))]
            else:
                empty_l += [QStandardItem("")]
        self.data_model.appendRow(empty_l)

    def remove_row_from_rigth_click(self, q_point):
        buttonReply = QMessageBox.question(self, 'Подтверждение удаления', "Вы действительно хотите удалить запись?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            row = self.table.rowAt(self.table.viewport().mapFromGlobal(q_point).y())
            self.changed_items += [[self.data_model.item(row, self.id_col_pos).text(), str(0), 0]]
            self.data_model.removeRow(row)
        else:
            pass

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copy()
        else:

            super(MyDelegateInTableView, self).keyPressEvent(event)

    def copy(self):
        selection = self.table.selectionModel()
        indexes = selection.selectedIndexes()
        if len(indexes) < 1:
            return

        # Захват и перевод в dataframe
        items = pd.DataFrame()
        for idx in indexes:
            row = idx.row()
            col = idx.column()
            item = idx.data()
            if item:
                items.at[row, col] = str(str(item))

        # Перевод в csv для вывода в excel
        items = list(items.itertuples(index=False))
        s = '\n'.join(['\t'.join([str(cell) for cell in row]) for row in items])

        # Отправка в буфер
        QtWidgets.QApplication.clipboard().setText(s)

    def undo_flags(self):
        for row in range(0, self.data_model.rowCount()):
            self.data_model.item(row, 0).setText(str("0"))

    def union_rows(self):
        main_row_ind = None
        ch_row_ind = []
        for row in range(0, self.data_model.rowCount()):
            if self.data_model.item(row, 0).text().lstrip() == "2":
                main_row_ind = row
            elif self.data_model.item(row, 0).text().lstrip() == "1":
                ch_row_ind.append(row)
        if main_row_ind is not None and ch_row_ind != []:
            for col in [x for x in range(34, 55) if x not in [46, 47, 48]]:
                current_val = self.data_model.item(main_row_ind, col).text()
                for row in ch_row_ind:
                    print(str(row) + "   " + str(col))
                    ch_row_val = self.data_model.item(row, col).text() if not self.data_model.item(row, col).text() is None else ""
                    if ch_row_val != "" and ch_row_val not in current_val:
                        current_val += " | " + ch_row_val if current_val != "" else ch_row_val
                self.data_model.item(main_row_ind, col).setText(current_val)
        self.data_model.item(main_row_ind, 0).setText("0")
        for row in sorted(set(ch_row_ind), key=int, reverse=True):
            self.data_model.removeRow(row)

    def _change_row(self):
        connect=SqlModule()
        for i in self.changed_items:
            if i[1]=='0' and i[2]==0:
                connect.remove_row(i[0])
            else:
                connect.change_row(i)

    def _load_keys(self):
        connect = SqlModule()
        cursor = SqlModule().get_keys()

        values = cursor.fetchall()
        columns = [i[0] for i in cursor.description]
        self.data_model.setHorizontalHeaderLabels(columns)
        for row in values:
            self.data_model.appendRow(list(map(lambda x: QtGui.QStandardItem(str(x)),row)))

    def _update_keys(self,data):
        SqlModule().update_keys(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    windowExample = MyDelegateInTableView()
    windowExample.show()
    sys.exit(app.exec_())
