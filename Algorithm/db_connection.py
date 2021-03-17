import pyodbc
import jaydebeapi
import os
import time
import datetime
import pandas as pd


class SqlModule(object):
    def __init__(self, parent=None):
        self.database = 'Sanctions'
        self.user = 'HUE_login'
        self.password = 'Switchback123_1'
        self.sql_conn = jaydebeapi.connect("com.microsoft.sqlserver.jdbc.SQLServerDriver",
                                           f"""jdbc:sqlserver://DESKTOP-9PBT7C3;
                                            databaseName={self.database}""",
                                           [self.user, self.password], os.getcwd() + "\sqljdbc42.jar")
        self.curs = self.sql_conn.cursor()
        self.sources = {"X-com": "1", 'AB': "2", "User": "3"}
        self.company_types = {"ЮЛ": 0, "ФЛ": 1}

    def clear_list(self, source_code):

        sql = "DELETE Records " \
              "FROM Records " \
              "WHERE Records.source = " + self.sources[source_code] + ";"

        self.curs.execute(sql)
        self.sql_conn.commit()

    def convert_date(self,date):
        if date != '' and date != None:
            date = datetime.datetime.strptime(date, '%Y-%m-%d')

        else:
            date = 'NULL'
        return date

    def add_record(self, new_row: list):

        if new_row[2] == "Действующий":
            new_row[2] = "1"
        else:
            new_row[2] = "0"

        # Заполняем Records
        sql = "INSERT INTO Records VALUES (" + new_row[2] + "," + "GetDate()" + "," + "GetDate()" + "," + self.sources[new_row[7]] + ",'" + new_row[8] + "','" + new_row[10] \
              + "','" + new_row[1] + "'," + str(1) + ");"

        self.curs.execute(sql)
        self.sql_conn.commit()
        self.curs.execute("SELECT MAX(id) from Records;")
        curr_record_id = self.curs.fetchone()[0]

        # Заполняем Companies
        org_type = 0 if new_row[9] == "0" else 1
        data = (curr_record_id,self.company_types[new_row[11]], org_type,new_row[12],new_row[13],new_row[14],new_row[15],new_row[16],new_row[17],new_row[18],
                new_row[19],new_row[20],self.convert_date(new_row[21]),new_row[22],new_row[31],new_row[32],new_row[33],new_row[40],new_row[46],new_row[47])
        sql = "INSERT INTO Companies VALUES (%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,'%s','%s','%s','%s','%s','%s','%s');" % data
        self.curs.execute(sql)
        self.sql_conn.commit()
        self.curs.execute("SELECT MAX(id) from Companies;")
        curr_company_id = self.curs.fetchone()[0]

        # Заполняем Alternative_names
        for name in [new_row[35],new_row[36],new_row[37],new_row[38],new_row[39]]:
            if name.strip() != '' :
                name_stat = 1 if new_row[48].strip() =="Действующий" else 0
                data = (name,curr_company_id,name_stat)
                sql = "INSERT INTO alternative_names VALUES ('%s',%s,%s);" % data
                self.curs.execute(sql)
                self.sql_conn.commit()

        # Заполняем unstructured_names
        if new_row[34].strip() != '':
            data = (new_row[34],curr_company_id)
            sql = "INSERT INTO unstructured_names VALUES ('%s',%s);" % data
            self.curs.execute(sql)
            self.sql_conn.commit()

        # Заполняем Sanctions
            type = 'NULL' if new_row[45] =='' else new_row[45]
            data = (new_row[41],new_row[43],new_row[44],type,new_row[49],new_row[50],new_row[51],new_row[52],new_row[53],new_row[54],curr_company_id)
            sql = "INSERT INTO Sanctions VALUES ('%s','%s','%s',%s,'%s','%s','%s','%s','%s','%s',%s);" % data
            self.curs.execute(sql)
            self.sql_conn.commit()

    def create_df(self,source:str):
        sql = "SELECT DISTINCT * FROM " \
              "Records " \
                "INNER JOIN Companies " \
                "ON Records.id = Companies.record " \
                "LEFT JOIN unstructured_names " \
                "ON Companies.id=unstructured_names.company " \
                "LEFT JOIN Sanctions " \
                "ON Sanctions.[company_id] = Companies.id " \
                "LEFT JOIN " \
                    "(SELECT distinct alternative_names.company, tab_1.name as 'alt_name_1', tab_2.name as " \
                    "'alt_name_2', tab_3.name as 'alt_name_3', tab_4.name as 'alt_name_4', " \
                    "tab_5.name as 'alt_name_5' " \
                    "FROM  alternative_names " \
                    "LEFT JOIN (SELECT alternative_names.*, g_index= ROW_NUMBER() OVER(PARTITION BY [company] ORDER BY [company]) FROM alternative_names) tab_1 " \
                    "ON alternative_names.company = tab_1.company and tab_1.g_index=1 " \
                    "LEFT JOIN (SELECT alternative_names.*, g_index= ROW_NUMBER() OVER(PARTITION BY [company] ORDER BY [company]) FROM alternative_names) tab_2 " \
                    "ON alternative_names.company = tab_2.company and tab_2.g_index=2 " \
                    "LEFT JOIN (SELECT alternative_names.*, g_index= ROW_NUMBER() OVER(PARTITION BY [company] ORDER BY [company]) FROM alternative_names) tab_3 " \
                    "ON alternative_names.company = tab_3.company and tab_3.g_index=3 " \
                    "LEFT JOIN (SELECT alternative_names.*, g_index= ROW_NUMBER() OVER(PARTITION BY [company] ORDER BY [company]) FROM alternative_names) tab_4 " \
                    "ON alternative_names.company = tab_4.company and tab_4.g_index=4 " \
                    "LEFT JOIN (SELECT alternative_names.*, g_index= ROW_NUMBER() OVER(PARTITION BY [company] ORDER BY [company]) FROM alternative_names) tab_5 " \
                    "ON alternative_names.company = tab_5.company and tab_5.g_index=5) alt_names " \
                    "ON alt_names.company = Companies.id " \
                    "WHERE Records.source = "+ self.sources[source]+";"
        return pd.read_sql(sql,self.sql_conn)