import sys
from PyQt5.QtWidgets import QDialog,QApplication,QFileDialog,QAbstractItemView
from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtCore import Qt


features = {('POLYGON', 'SLPR'): [('ONE WAY', ['NO', 'YES'], 'List', 3), ('CLASS', ['INTERSTATE', 'PRIMARY', 'RESIDENTIAL', 'SECONDARY', 'SERVICE', 'STATE HWY', 'TERTIARY', 'TRACK', 'US HWY'], 'List', 11)], ('POINT', 'CALC FLD'): [('NAME', [], 'TEXT', '50'), ('SURFACE', ['BLACK TOP', 'BRICK', 'CALICHE', 'CALICHE AND GRAVEL', 'CINDER', 'CONCRETE', 'DIRT', 'GRASS', 'GRAVEL', 'LIMESTONE', 'OILED', 'PAVED ASPHALT', 'ROCK', 'SAND', 'SAND AND GRAVEL', 'SCORIA', 'SHELL', 'SHELL & OIL', 'SLAG'], 'List', 18)], ('POINT', 'RKDH'): [('TYPE', ['COUNTY', 'DO NOT USE', 'ENGINEERED', 'IMPROVED', 'PRIMITIVE', 'TEMPLATE', 'TEMPORARY ACCESS'], 'List', 16)]}



class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 300)
        self.pushButtonFile = QtWidgets.QPushButton(Dialog)
        self.pushButtonFile.setGeometry(QtCore.QRect(310, 20, 75, 23))
        self.pushButtonFile.setObjectName("pushButtonFile")
        self.lineEditFile = QtWidgets.QLineEdit(Dialog)
        self.lineEditFile.setGeometry(QtCore.QRect(70, 20, 231, 20))
        self.lineEditFile.setObjectName("lineEditFile")
        self.pushButtonLoad = QtWidgets.QPushButton(Dialog)
        self.pushButtonLoad.setGeometry(QtCore.QRect(250, 250, 75, 23))
        self.pushButtonLoad.setObjectName("pushButtonLoad")
        self.treeView = QtWidgets.QTreeView(Dialog)
        self.treeView.setGeometry(QtCore.QRect(70, 50, 256, 192))
        self.treeView.setObjectName("treeView")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButtonFile.setText(_translate("Dialog", "File"))
        self.pushButtonLoad.setText(_translate("Dialog", "Load"))

class Window(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.pushButtonFile.clicked.connect(self.dispFolder)
        self.ui.pushButtonLoad.clicked.connect(self.loadXml)
        self.show()
    def dispFolder(self):
        fname = QFileDialog.getOpenFileName(self,'Open File','/home')
        if fname[0]:
            self.ui.lineEditFile.setText(fname[0])
    def loadXml(self):
        print(features)
        model = QStandardItemModel(0,3,self.ui.treeView)
        model.setHeaderData(0,Qt.Horizontal,"CODE")
        model.setHeaderData(1,Qt.Horizontal,"DATA TYPE")
        model.setHeaderData(2,Qt.Horizontal,"LENGTH")
        self.ui.treeView.setModel(model)
        i=0
        for k,featuretype in features.items():
            parent1 = QStandardItem('{}'.format(k[1]))
            for item in featuretype:
                child = QStandardItem(item[0])
                if len(item[1])>0:
                    for listitem in item[1]:
                        gchild=QStandardItem(listitem)
                        child.appendRow(gchild)
                parent1.appendRow(child)
            model.setItem(i,0,parent1)
            self.ui.treeView.setFirstColumnSpanned(i,self.ui.treeView.rootIndex(),True)
            i+=1
from PyQt5 import QtCore, QtGui, QtWidgets

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())