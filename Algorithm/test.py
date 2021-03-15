import sys
from PyQt5.Qt import *
from PyQt5 import QtWidgets, QtGui, QtCore


class Delegate(QtWidgets.QStyledItemDelegate):                                # +++ Delegate

    def createEditor(self, parent, options, index):
        if index.column() == 5:
            editor = QtWidgets.QDateEdit(parent)
            editor.setFrame(False)
            editor.setCalendarPopup(True) # Вместо стрелок вылезает календарь
            return editor
        elif index.column() == 4:
            editor = QtWidgets.QSpinBox(parent)
            return editor

    def setEditorData(self, editor, index):
        if index.column() == 5:
            editor.setDateTime(QtCore.QDateTime.currentDateTime())
        elif index.column() == 4:
            value = index.model().data(index, QtCore.Qt.EditRole)
            try: value = int(value)
            except: value = 0
            editor.setValue(value)

    def updateEditorGeometry(self, editor, options, index):
        editor.setGeometry(options.rect)

    def setModelData(self, editor, model, index):
        if index.column() == 5:
            value = str(editor.dateTime().date().toPyDate())
            model.setData(index, value, QtCore.Qt.EditRole)
        elif index.column() == 4:
            value = str(editor.value())
            model.setData(index, value, QtCore.Qt.EditRole)


class MyDelegateInTableView(QtWidgets.QWidget):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.table = QtWidgets.QTableView()                     # Представление
        self.data_model = QtGui.QStandardItemModel(parent=self.table)  # Модель
        today = str(QtCore.QDateTime.currentDateTime().date().toPyDate())

        myPCIntel = ['Intel® NUC NUC8i3BEK', 'Intel Core i3 8-го поколения (i3-8109U)',
                     'RAM - 8 GB (DDR4, частота 2400MHz)', 'M.2 NVMe SSD 512Гб', '3', today]
        myPCAMD = ['AMD Sempron', 'Процессор AMD Sempron 140', 'DDR3 2048MB 1333MHz Kingston',
                   '1Tb Seagate Barracuda 7200.12', '5', today]
        for i in range(len(myPCIntel)):
            item1 = QtGui.QStandardItem(myPCIntel[i])
            item2 = QtGui.QStandardItem(myPCAMD[i])
            self.data_model.appendColumn([item1, item2])
        self.data_model.setHorizontalHeaderLabels(
            ['Название', 'Процессор', 'Оперативная память', 'Постоянная память', 'Количество компьютеров', 'Дата поступления'])
        self.table.setModel(self.data_model)

        # LAYOUT
        boxMain = QtWidgets.QVBoxLayout()
        boxMain.addWidget(self.table)
        self.setLayout(boxMain)

        # DELEGATE # Назначение делегатов столбцам таблицы
#        self.table.setItemDelegateForColumn(4, SpinBoxDelegate())
#        self.table.setItemDelegateForColumn(5, MyDateEditDelegate())
        delegate = Delegate(self)                                              # +++
        self.table.setItemDelegateForColumn(4, delegate)                       # +++
        self.table.setItemDelegateForColumn(5, delegate)                       # +++



if __name__ == '__main__':
    app = QApplication(sys.argv)
    windowExample = MyDelegateInTableView()
    windowExample.show()
    sys.exit(app.exec_())