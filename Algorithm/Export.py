import pandas as pd
from delta import aggregation
def export_excel(model,path):
    cols = [model.headerData(i, 1) for i in range(0, model.columnCount())]
    df = pd.DataFrame([], columns=cols)
    for column in range(0,model.columnCount()):
        for row in range(0,  model.rowCount()):
            df.at[row,cols[column]] = model.item(row,column).text()

    df.to_excel(path+"/Export.xlsx",index=False)


def export_excel_tree(model,path):
    cols = [model.headerData(i, 1) for i in range(0, model.columnCount())]
    df = aggregation(model)
    df = pd.DataFrame([], columns=cols)
