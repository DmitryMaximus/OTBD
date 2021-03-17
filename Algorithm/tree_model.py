import sys
from PyQt5.QtWidgets import QDialog,QApplication,QFileDialog,QAbstractItemView
from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from Algorithm.db_connection import *

features = {('POLYGON', 'SLPR'): [('ONE WAY', ['NO', 'YES'], 'List', 3), ('CLASS', ['INTERSTATE', 'PRIMARY', 'RESIDENTIAL', 'SECONDARY', 'SERVICE', 'STATE HWY', 'TERTIARY', 'TRACK', 'US HWY'], 'List', 11)], ('POINT', 'CALC FLD'): [('NAME', [], 'TEXT', '50'), ('SURFACE', ['BLACK TOP', 'BRICK', 'CALICHE', 'CALICHE AND GRAVEL', 'CINDER', 'CONCRETE', 'DIRT', 'GRASS', 'GRAVEL', 'LIMESTONE', 'OILED', 'PAVED ASPHALT', 'ROCK', 'SAND', 'SAND AND GRAVEL', 'SCORIA', 'SHELL', 'SHELL & OIL', 'SLAG'], 'List', 18)], ('POINT', 'RKDH'): [('TYPE', ['COUNTY', 'DO NOT USE', 'ENGINEERED', 'IMPROVED', 'PRIMITIVE', 'TEMPLATE', 'TEMPORARY ACCESS'], 'List', 16)]}


features = {('POLYGON', 'SLPR'): [('ONE WAY', ['NO', 'YES'], 'List', 3), ('CLASS', ['INTERSTATE', 'PRIMARY', 'RESIDENTIAL', 'SECONDARY', 'SERVICE', 'STATE HWY', 'TERTIARY', 'TRACK', 'US HWY'], 'List', 11)], ('POINT', 'CALC FLD'): [('NAME', [], 'TEXT', '50'), ('SURFACE', ['BLACK TOP', 'BRICK', 'CALICHE', 'CALICHE AND GRAVEL', 'CINDER', 'CONCRETE', 'DIRT', 'GRASS', 'GRAVEL', 'LIMESTONE', 'OILED', 'PAVED ASPHALT', 'ROCK', 'SAND', 'SAND AND GRAVEL', 'SCORIA', 'SHELL', 'SHELL & OIL', 'SLAG'], 'List', 18)], ('POINT', 'RKDH'): [('TYPE', ['COUNTY', 'DO NOT USE', 'ENGINEERED', 'IMPROVED', 'PRIMITIVE', 'TEMPLATE', 'TEMPORARY ACCESS'], 'List', 16)]}
class MyTree(QDialog):
    def __init__(self):
        super().__init__()
        self.treeView = QtWidgets.QTreeView()
        self.treeView.setGeometry(QtCore.QRect(70, 50, 256, 192))
        self.treeView.setObjectName("treeView")
        boxMain = QtWidgets.QVBoxLayout()
        boxMain.addWidget(self.treeView)
        self.setLayout(boxMain)
        self.source = []
        self.loadXml()
        # self.create_header()


    def load_table_sql(self,source):

        connect = SqlModule()
        df = connect.create_df(source)
        df = df.fillna('')
        df = df.applymap(lambda x: str(x).strip())
        df = df.loc[:, ~df.columns.duplicated()]

        df = df.applymap(lambda x: QtGui.QStandardItem(str(x)))

        return df

    def create_header(self):
        df_xc = self.load_table_sql("X-com")
        df_ab = self.load_table_sql("AB")
        model = QStandardItemModel(0,len(list(df_xc)),self.treeView)
        for i in range(0,len(list(df_xc))):
            model.setHeaderData(i, Qt.Horizontal, list(df_xc)[i])

        for i, row in df_xc.iterrows():
            model.appendRow(row.values)


        self.treeView.setModel(model)

    def loadXml(self):
        print(features)
        model = QStandardItemModel(0,3,self.treeView)
        model.setHeaderData(0,Qt.Horizontal,"CODE")
        model.setHeaderData(1,Qt.Horizontal,"DATA TYPE")
        model.setHeaderData(2,Qt.Horizontal,"LENGTH")
        self.treeView.setModel(model)
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
            self.treeView.setFirstColumnSpanned(i,self.treeView.rootIndex(),True)
            i+=1



if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyTree()
    w.show()
    sys.exit(app.exec_())