import pandas as pd

def create_ssw(dataframe):
    cols = [dataframe.headerData(i,1) for i in range(0, dataframe.columnCount())]
    df = pd.DataFrame([],columns = cols)
    for row in range(0,dataframe.rowCount()):
        for col in range(0,dataframe.columnCount()):
            if dataframe.item(row,col).child() and cols[col] in ["Связь с санкционным элементом (наим)","Связь с санкционным элементом (наим лат)","INN материнской компании","ОГРН материнской компании"]:
                pass
        # df.at[row, cols[col]] = dataframe.item(row, col).text()