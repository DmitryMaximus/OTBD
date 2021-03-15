import sys
import pyodbc
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.Qt import *
from Algorithm.deduplication import deduplicate

class Delegate(QtWidgets.QStyledItemDelegate):

    def createEditor(self, parent, options, index):
        if index.column() in [4, 5, 21]:
            editor = QtWidgets.QDateEdit(parent)
            editor.setFrame(False)
            editor.setCalendarPopup(True)  # Вместо стрелок вылезает календарь
            return editor

    def setEditorData(self, editor, index):
        if index.column() in [4, 5, 21]:
            editor.setDateTime(QtCore.QDateTime.currentDateTime())

    def updateEditorGeometry(self, editor, options, index):
        editor.setGeometry(options.rect)

    def setModelData(self, editor, model, index):
        if index.column() in [4, 5, 21]:
            value = str(editor.dateTime().date().toPyDate())
            model.setData(index, value, QtCore.Qt.EditRole)


class MyDelegateInTableView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.table = QtWidgets.QTableView()  # Представление
        self.data_model = QtGui.QStandardItemModel(parent=self.table)  # Модель
        self.table.setModel(self.data_model)

        boxMain = QtWidgets.QVBoxLayout()
        boxMain.addWidget(self.table)
        self.setLayout(boxMain)

        delegate = Delegate()
        self.table.setItemDelegateForColumn(4, delegate)
        self.table.setItemDelegateForColumn(5, delegate)
        self.table.setItemDelegateForColumn(21, delegate)

        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.generateMenu)
        self.table.viewport().installEventFilter(self)
        self.df = pd.DataFrame([], columns=[""])

    def load_table(self, path):
        self.data_model.removeColumns(0, self.data_model.columnCount())

        if not path:
            pass
        if ".XML" in path or ".xml" in path:
            return
        if ".xlsx" in path:
            self.df = pd.read_excel(path)
            self.df = self.df.fillna('')
            self.df = self.df.applymap(lambda x: str(x).strip())
            self.df = deduplicate(self.df)
            if "Объединить" not in list(self.df):
                self.df['Объединить'] = "0"
                self.df = self.df[list(self.df)[-1:] + list(self.df)[:-1]]


        self.df = self.df.applymap(lambda x: QtGui.QStandardItem(str(x)))
        for col in list(self.df):
            self.data_model.appendColumn(self.df[col].tolist())
        self.data_model.setHorizontalHeaderLabels(list(self.df))
        return self.data_model

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseButtonPress and
                event.buttons() == QtCore.Qt.RightButton and
                source is self.table.viewport()):
            self.menu = QMenu(self)
            pos = event.globalPos()

            addRow = self.menu.addAction('Добавить строку')
            addRow.triggered.connect(
                lambda: self.add_row())

            sort = self.menu.addAction('Отсортировать')
            sort.triggered.connect(
                lambda: self.sort(pos))

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
            empty_l += ""
        self.data_model.appendRow(empty_l)

    def remove_row_from_rigth_click(self, q_point):
        buttonReply = QMessageBox.question(self, 'Подтверждение удаления', "Вы действительно хотите удалить запись?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if buttonReply == QMessageBox.Yes:
            row = self.table.rowAt(self.table.viewport().mapFromGlobal(q_point).y())
            self.data_model.removeRow(row)
        else:
            pass

    def keyPressEvent(self, event):
        if event.matches(QtGui.QKeySequence.Copy):
            self.copy()
        else:
            # Pass up
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

        # Перевод в csv
        items = list(items.itertuples(index=False))
        s = '\n'.join(['\t'.join([str(cell) for cell in row]) for row in items])

        # Отправка в буфер
        QtWidgets.QApplication.clipboard().setText(s)

    def sort(self, q_point):
        pass
        # TODO
        # """Sort table by given column number."""
        # Ncol = self.table.rowAt(self.table.viewport().mapFromGlobal(q_point).x())
        # self.data_model = self.data_model.sort_values(self.headers[Ncol],
        #                                          ascending=Qt.AscendingOrder)

    def undo_flags(self):
        for row in range(0,self.data_model.rowCount()):
            self.data_model.item(row,0).setText(str("0"))

    def union_rows(self):
        main_row_ind=None
        ch_row_ind=[]
        for row in range(0,self.data_model.rowCount()):
            if self.data_model.item(row,0).text().lstrip()=="2":
                main_row_ind = row
            elif self.data_model.item(row,0).text().lstrip()=="1":
                ch_row_ind.append(row)
        if main_row_ind is not None and ch_row_ind!=[]:
            for col in [x for x in range(34, 55) if x not in [46, 47, 48]]:
                current_val = self.data_model.item(main_row_ind,col).text()
                for row in ch_row_ind:
                    print(str(row)+"   "+str(col))
                    ch_row_val = self.data_model.item(row,col).text() if not self.data_model.item(row,col).text() is None else ""
                    if ch_row_val != "" and ch_row_val not in current_val:
                        current_val +=  " | " + ch_row_val if current_val!= "" else ch_row_val
                self.data_model.item(main_row_ind, col).setText(current_val)
        self.data_model.item(main_row_ind, 0).setText("0")
        for row in sorted(set(ch_row_ind), key=int, reverse=True):
            self.data_model.removeRow(row)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    windowExample = MyDelegateInTableView()
    windowExample.show()
    sys.exit(app.exec_())
