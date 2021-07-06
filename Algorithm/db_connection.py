import jaydebeapi
import os
import datetime
import pandas as pd
from Config_read import confdict


class SqlModule(object):
    def __init__(self, parent=None):
        self.database = confdict['SERVER_DATA']['database']
        self.user = confdict['SERVER_DATA']['user']
        self.password = confdict['SERVER_DATA']['password']
        self.server = confdict['SERVER_DATA']['server']
        self.sql_conn = jaydebeapi.connect("com.microsoft.sqlserver.jdbc.SQLServerDriver",
                                           f"""jdbc:sqlserver://{self.server}; databaseName={self.database}""",
                                           [self.user, self.password], confdict['SERVER_DATA']['path_to_manager'])
        self.curs = self.sql_conn.cursor()
        self.sources = {"X-com": "1", 'AB': "2", "User": "3", "TR общий": "4", "TR санкции": "5"}
        self.company_types = {"ЮЛ": 0, "ФЛ": 1,"Иное":2}

    def get_source(self, mode=1):
        if not isinstance(mode, int):
            return self.sources[mode]
        else:
            return mode

    def ask_type(self, table_name: str, col_name: str) -> str:
        sql = "SELECT DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '%s' AND COLUMN_NAME = '%s'" % (table_name, col_name)
        self.curs.execute(sql)
        try:
            result = self.curs.fetchone()[0]
            return result
        except:
            return None

    def clear_list(self, source_code):

        sql = "DELETE Records " \
              "FROM Records " \
              "WHERE Records.source = " + self.sources[source_code] + ";"

        self.curs.execute(sql)
        self.sql_conn.commit()

    def convert_date(self, date):
        try:
            if date != '' and date != None:
                date = "'" + datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S').strftime('%Y-%d-%m %H:%M:%S') + "'"
            else:
                date = 'NULL'
        except:
            if date != '' and date != None:
                date = "'" + datetime.datetime.strptime(date, '%Y/%m/%d').strftime('%Y-%d-%m %H:%M:%S') + "'"
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
        data = (curr_record_id, self.company_types[new_row[11]], org_type, new_row[12], new_row[13], new_row[14], new_row[15], new_row[16], new_row[17], new_row[18],
                new_row[19], new_row[20], self.convert_date(new_row[21]), new_row[22], new_row[31], new_row[32], new_row[33], new_row[40], new_row[46], new_row[47])
        sql = "INSERT INTO Companies VALUES (%s,%s,%s,'%s','%s','%s','%s','%s','%s','%s','%s','%s',%s,'%s','%s','%s','%s','%s','%s','%s');" % data
        self.curs.execute(sql)
        self.sql_conn.commit()
        self.curs.execute("SELECT MAX(id) from Companies;")
        curr_company_id = self.curs.fetchone()[0]

        # Заполняем Alternative_names
        for name in [new_row[35], new_row[36], new_row[37], new_row[38], new_row[39]]:
            if name.strip() != '':
                name_stat = 1 if new_row[48].strip() == "Действующий" else 0
                data = (name, curr_company_id, name_stat)
                sql = "INSERT INTO alternative_names VALUES ('%s',%s,%s);" % data
                self.curs.execute(sql)
                self.sql_conn.commit()

        # Заполняем unstructured_names
        if new_row[34].strip() != '':
            data = (new_row[34], curr_company_id)
            sql = "INSERT INTO unstructured_names VALUES ('%s',%s);" % data
            self.curs.execute(sql)
            self.sql_conn.commit()

        # Заполняем Sanctions
        type = new_row[45]
        data = (new_row[41], new_row[43], new_row[44], type, new_row[49], new_row[50], new_row[51], new_row[52], new_row[53], new_row[54], curr_company_id)
        sql = "INSERT INTO Sanctions VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',%s);" % data
        self.curs.execute(sql)
        self.sql_conn.commit()

    def create_df(self, source: str):
        self.sql_conn.close()
        self.sql_conn = jaydebeapi.connect("com.microsoft.sqlserver.jdbc.SQLServerDriver",
                                           f"""jdbc:sqlserver://{self.server}; databaseName={self.database}""",
                                           [self.user, self.password], confdict['SERVER_DATA']['path_to_manager'])
        self.curs = self.sql_conn.cursor()

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
              "WHERE Records.source = " + self.sources[source] + ";"
        return pd.read_sql(sql, self.sql_conn)

    def update_dedup(self,values,company_id,key,mode=1):
        def get_current_value(key, company_id):
            table_name = confdict['COLS_TO_TABLE'][str(key)]
            col_name = confdict['COLS_TO_NAMES'][str(key)]

            if int(key) in [i for i in range(2, 18)] + [25] + [i for i in range(35, 38)]:  # Обновление таблицы Companies
                sql = "SELECT %s FROM %s WHERE id = %s" % (col_name, table_name, company_id)

            elif int(key) in [i for i in range(26, 35)]:  # Обновление таблицы Sanctions
                sql = "SELECT %s FROM %s INNER JOIN Companies ON  companies.id = Sanctions.company_id WHERE companies.id = %s" % (col_name, table_name, company_id)

            else:
                sql = ''
            if sql != '':
                self.curs.execute(sql)
                try:
                    current_value = self.curs.fetchone()[0]
                except:
                    current_value = 'no_value'
                return current_value

        def dedup_update_row(key, value, row_id):
            table_name = confdict['COLS_TO_TABLE'][str(key)]
            col_name = confdict['COLS_TO_NAMES'][str(key)]

            if int(key) in [i for i in range(2, 18)] + [25] + [i for i in range(35, 38)]:  # Обновление таблицы Companies
                sql = "UPDATE %s SET %s = %s WHERE id = %s" % (table_name, col_name, value, row_id)

            elif int(key) in [i for i in range(26, 35)]:  # Обновление таблицы Sanctions
                sql = "UPDATE %s SET %s = %s FROM %s INNER JOIN Companies ON  companies.id = Sanctions.company_id WHERE companies.record = %s" % (
                    table_name, col_name, value, table_name, row_id)
            else:
                sql = ''
            if sql != '':
                self.curs.execute(sql)
                self.sql_conn.commit()


        if int(key) == 17 and values not in get_current_value(8,company_id): #доп проверка текущие главное наименование != добавляемому альтернативному
            data = (values, company_id)
            sql = "INSERT INTO [Sanctions].[dbo].[alternative_names] VALUES ('%s',%s,1);" % data
            self.curs.execute(sql)
            self.sql_conn.commit()
        elif int(key) == 16 and values not in get_current_value(16,company_id):
            data = (values, company_id)
            sql = "INSERT INTO [Sanctions].[dbo].[alternative_names] VALUES ('%s',%s,1);" % data
            self.curs.execute(sql)
            self.sql_conn.commit()
        elif int(key) != 17 and int(key) != 16:
            cur_value  = get_current_value(key,company_id)
            if cur_value != 'no_value' and values not in cur_value:
                values = cur_value + " | " + values
                dedup_update_row(key,values,company_id)

    def change_row(self, coord: list):
        """

        :param coord: [id_компании, Номер колонки с изменениями,value]
        :return:
        """
        row_id = coord[0]
        table_name = confdict['COLS_TO_TABLE'][str(coord[1])]
        col_name = confdict['COLS_TO_NAMES'][str(coord[1])]
        data_type = self.ask_type(confdict['COLS_TO_TABLE'][str(coord[1])], confdict['COLS_TO_NAMES'][str(coord[1])])

        if data_type == 'int':
            data = coord[2]
        elif data_type in ['str', 'nvarchar']:
            data = "'" + coord[2] + "'"
        elif data_type == 'datetime':
            data = 'GetDate()'
        else:
            data = coord[2]

        if int(coord[1]) in [i for i in range(0, 3)] + [i for i in range(38, 43)]:  # Обновление таблицы Records
            sql = "UPDATE %s SET %s = %s WHERE id = %s" % (table_name, col_name, data, row_id)

        elif int(coord[1]) in [i for i in range(3, 18)] + [25] + [i for i in range(35, 38)]:  # Обновление таблицы Companies
            sql = "UPDATE %s SET %s = %s WHERE record = %s" % (table_name, col_name, data, row_id)

        elif int(coord[1]) in [i for i in range(26, 35)]:  # Обновление таблицы Sanctions
            sql = "UPDATE %s SET %s = %s FROM %s INNER JOIN Companies ON  companies.id = Sanctions.company_id WHERE companies.record = %s" % (
                table_name, col_name, data, table_name, row_id)

        elif int(coord[1]) in [i for i in range(20, 25)]:
            sql = "SELECT distinct  id from Companies where record =  %s" % row_id
            self.curs.execute(sql)
            company_id  = self.curs.fetchone()[0]
            data = (data, company_id, '1')
            sql = "INSERT INTO alternative_names VALUES ('%s',%s,%s);" % data
            self.curs.execute(sql)
            self.sql_conn.commit()

        else:
            sql = ''
        if sql != '':
            self.curs.execute(sql)
            self.sql_conn.commit()

    def send_con_db(self, id_p, id_ch, mode=1):
        try:
            m = 1 if mode == 2 else 2
            data = (id_p, id_ch, m)
            sql = "DELETE from Connections WHERE [main_company] = %s and [child_company] = %s and mode = %s" % data
            self.curs.execute(sql)
            self.sql_conn.commit()
        except:
            pass
        if mode == 1:
            data = (id_p, id_ch, mode)
            sql = "INSERT INTO Connections VALUES (%s,%s,%s);" % data
            self.curs.execute(sql)
            self.sql_conn.commit()
        elif mode == 2:
            data = (id_p, id_ch, mode)
            sql = "INSERT INTO Connections VALUES (%s,%s,%s);" % data
            self.curs.execute(sql)
            self.sql_conn.commit()

    def get_connections(self, mode=1):
        data = (mode)
        sql = "SELECT DISTINCT main_company,child_company from Connections where mode = %s" % data
        self.curs.execute(sql)
        self.sql_conn.commit()
        return self.curs.fetchall()

    def remove_row(self, row):
        data = (row)
        sql = "DELETE Records FROM Records WHERE Records.id =  %s" % data
        self.curs.execute(sql)
        self.sql_conn.commit()

    def complex_row_remove(self, vals):
        source = self.sources[vals[7]]
        if vals[3] != '':
            data = (vals[3],source)
            sql = "DELETE Records FROM Records LEFT JOIN Companies ON Records.id = Companies.record WHERE Companies.id = %s and Records.source = %s" % data
        elif vals[31] != '':
            data = (vals[31],source)
            sql = "DELETE Records FROM Records LEFT JOIN Companies ON Records.id = Companies.record WHERE Companies.inn = '%s' and Records.source = %s" % data
        elif vals[16] != '':
            data = (vals[16],source)
            sql = "DELETE Records FROM Records LEFT JOIN Companies ON Records.id = Companies.record WHERE Companies.FIO = '%s' and Records.source = %s" % data
        elif vals[16] != '':
            data = (vals[16],source)
            sql = "DELETE Records FROM Records LEFT JOIN Companies ON Records.id = Companies.record WHERE Companies.FIO = '%s' and Records.source = %s" % data
        elif vals[17] != '':
            data = (vals[17],source)
            sql = "DELETE Records FROM Records LEFT JOIN Companies ON Records.id = Companies.record WHERE Companies.name_main_rus = '%s' and Records.source = %s" % data
        self.curs.execute(sql)
        self.sql_conn.commit()

    def get_keys(self):
        sql = "SELECT  * FROM key_ref"
        self.curs.execute(sql)
        self.sql_conn.commit()
        result = self.curs
        return result

    def update_keys(self,data):
        id_list = [i[0] for i in data]
        for id in id_list:
            sql = "DELETE key_ref FROM key_ref  WHERE key_ref.id = %s" % id
            self.curs.execute(sql)
            self.sql_conn.commit()

        for item in data:
            if len(item)>1:
                sql ="INSERT INTO key_ref VALUES ({},'{}','{}','{}','{}','{}');".format(*item)
                self.curs.execute(sql)
                self.sql_conn.commit()