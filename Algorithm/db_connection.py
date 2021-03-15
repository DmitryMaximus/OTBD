import pyodbc
import jaydebeapi
import os
import time

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

    def clear_list(self, source_code):

        sql = "DELETE Records " \
              "FROM Records " \
              "WHERE Records.source = " + self.sources[source_code] + ";"

        self.curs.execute(sql)
        self.sql_conn.commit()

    def add_record(self, new_row: list):
        """
        Принимает на вход список ["Активная запись","Дата генерации записи","Дата обновления записи",
                                    "Код источника записи","Идентификатор записи согласно источнику","Списки SSW"]
        """
        if new_row[0] == "Действующий":
            new_row[0] = "1"
        else:
            new_row[0] = "0"

        # sql = "INSERT INTO Records VALUES (" + new_row[0] + ",'" + new_row[1] + "','" + new_row[2] + "'," + self.sources[new_row[3]] + ",'" + new_row[4] + "','" + new_row[5] \
        #       + "'," + str(1) + ");"
        sql = "INSERT INTO Records VALUES (" + new_row[0] + "," + "GetDate()" + "," + "GetDate()" + "," + self.sources[new_row[3]] + ",'" + new_row[4] + "','" + new_row[5] \
              + "'," + str(1) + ");"

        self.curs.execute(sql)
        self.sql_conn.commit()
