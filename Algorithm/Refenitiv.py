import requests
from requests.auth import HTTPBasicAuth
from db_connection import *
import pandas as  pd
from deduplication import examp


class ParseRef(object):
    def __init__(self,path=None):
        self.conn = SqlModule()
        self.curs = SqlModule().curs
        self.key_list = self.get_key_list()
        self.path_to_csv = input("Вставьте путь до файла csv") if path is None else path
        self.drop_current_ref()

    def get_data(self):
        response = requests.get("https://www.world-check.com/datafile/premium/premium-world-check.csv",
                                auth=HTTPBasicAuth('rufbnd0002', 'Ktn02020'), allow_redirects=True, stream=True)

        text_file = open(r"C:\Users\Root\Desktop\Refenitiv.csv", "wb")
        for chunk in response.iter_content(chunk_size=1024):
            text_file.write(chunk)

    def read_csv_gen(self):
        for chunk in pd.read_csv(self.path_to_csv, chunksize=1000,delimiter="\t",encoding='ANSI'):
            yield chunk

    def drop_current_ref(self):
        self.conn.clear_list('TR общий')
        print("Список TR общий очищен")
        self.conn.clear_list('TR санкции')
        print("Список TR санкции очищен")

    def get_key_list(self):
        conn = SqlModule().sql_conn
        keys = pd.read_sql("SELECT abbr,code FROM [Sanctions].[dbo].[key_ref];", conn)
        keys['abbr'] = keys['abbr'].apply(lambda x:  x.strip())
        return keys

    def add_code(self,row:pd.Series, key_list)->str:
        code_zip = dict(zip(key_list.abbr, key_list.code))
        keywords_l = row['KEYWORDS'].split('~')
        codes_arr = []
        for i in keywords_l:
            if i in list(code_zip.keys()):
                codes_arr += [code_zip[i]]
            else:
                codes_arr += ''

        codes_str = ', '.join(codes_arr)
        codes_unq_str = ', '.join(list(set(codes_str.split(', '))))
        return codes_unq_str

    def parse_data(self):
        rf_generator = self.read_csv_gen()
        iter = 0
        try:
            while True:
                df = next(rf_generator)
                df = self.change_df(df)
                df = df[df['Тип записи']!='']
                if len(df)>0:
                    for i, row in df.iterrows():
                        SqlModule.add_record(SqlModule(), row.to_list())
                        iter+=1
                        if iter == 1000:
                            iter=0
                            print("Вставлено 1000 строк")
        except StopIteration:
            print("Загрузка рефенитива завершена")

    def change_df(self,df):
            df = df.fillna('')
            df_rf = pd.DataFrame([], columns=["Объединение"] + examp)
            comp_type = {'F': 'ФЛ', 'M': 'ФЛ', 'U': 'ФЛ', 'E': 'ЮЛ'}
            iter = 0
            for i, row in df.iterrows():
                if any([i in self.key_list['abbr'] for i in row['KEYWORDS'].split('~')]) and not pd.isna(row['KEYWORDS']):
                    df_rf.at[iter, 'Коды санкционных ограничений'] = self.add_code(row, self.key_list)
                    print(self.add_code(row, self.key_list))
                    df_rf.at[iter, 'Код источника записи'] = 'TR санкции'
                else:
                    df_rf.at[iter, 'Код источника записи'] = 'TR общий'

                if comp_type[row['E/I']] == 'ЮЛ' and '{RU-INN}' in row['IDENTIFICATION NUMBERS']:
                    df_rf.at[iter, 'Активная запись'] = '1'
                    df_rf.at[iter, 'Тип записи'] = comp_type[row['E/I']]
                    df_rf.at[iter, 'ИНН'] = row['IDENTIFICATION NUMBERS'].split('{RU-INN}')[1].split('{')[0].replace(";", '')
                    df_rf.at[iter, 'ОГРН'] = row['IDENTIFICATION NUMBERS'].split('{RU-OGRN}')[1].split('{')[0].replace(";", '') if '{RU-OGRN}' in row['IDENTIFICATION NUMBERS'] else ''
                    df_rf.at[iter, 'Иное'] = row['IDENTIFICATION NUMBERS'].replace(
                        row['IDENTIFICATION NUMBERS'].split('{RU-OGRN}')[1].split('{')[0] if '{RU-OGRN}' in row['IDENTIFICATION NUMBERS'] else '', '') \
                        .replace(row['IDENTIFICATION NUMBERS'].split('{RU-INN}')[1].split('{')[0], '').replace('{RU-INN}', '').replace('{RU-OGRN}', '')
                    df_rf.at[iter, 'Наименование(главное лат)'] = row['LAST NAME'].replace("'", "")
                    df_rf.at[iter, 'Альтернативные наименования'] = row['ALIASES'].replace("'", "") + '; ' + row['ALTERNATIVE SPELLING'].replace("'", "")
                    df_rf.at[iter, 'Резиденство'] = row['CITIZENSHIP'].replace("'", "")
                    df_rf.at[iter, 'Дата генерации записи'] = row['ENTERED'] if not '/00' else row['DOB'].replace('/00', '/01')
                    df_rf.at[iter, 'Дата обновления записи'] = row['UPDATED'] if not '/00' else row['DOB'].replace('/00', '/01')
                    df_rf.at[iter, 'Комментарии пользователя'] = row['FURTHER INFORMATION'].split('[BIOGRAPHY]')[1].split('[')[0].replace("'",'') if '[BIOGRAPHY]' in row['FURTHER INFORMATION'] else ''
                    df_rf.at[iter, 'Идентификатор записи согласно источнику'] = str(row['UID'])
                    df_rf.at[iter, 'Активная запись'] = 'Действующий'
                elif comp_type[row['E/I']] == 'ФЛ':
                    df_rf.at[iter, 'Активная запись'] = '1'
                    df_rf.at[iter, 'Тип записи'] = comp_type[row['E/I']]
                    df_rf.at[iter, 'Наименование(главное лат)'] = row['LAST NAME'].replace("'", "") + " " + row['FIRST NAME'].replace("'", "")
                    df_rf.at[iter, 'Дата рождения'] = row['DOB'] if not '/00' else row['DOB'].replace('/00', '/01')
                    df_rf.at[iter, 'Фамилия'] = row['LAST NAME'].replace("'", "")
                    df_rf.at[iter, 'Имя'] = row['FIRST NAME'].replace("'", "")
                    df_rf.at[iter, 'Альтернативные наименования'] = row['ALIASES'].replace("'", "") + '; ' + row['ALTERNATIVE SPELLING'].replace("'", "")
                    df_rf.at[iter, 'Резиденство'] = row['CITIZENSHIP'].replace("'", "")
                    df_rf.at[iter, 'Дата генерации записи'] = row['ENTERED']
                    df_rf.at[iter, 'Дата обновления записи'] = row['UPDATED']
                    df_rf.at[iter, 'Комментарии пользователя'] = row['FURTHER INFORMATION'].split('[BIOGRAPHY]')[1].split('[')[0].replace("'",'') if '[BIOGRAPHY]' in row['FURTHER INFORMATION'] else ''
                    df_rf.at[iter, 'Идентификатор записи согласно источнику'] = str(row['UID'])
                    df_rf.at[iter, 'Активная запись'] = 'Действующий'
                else:
                    df_rf.at[iter, 'Активная запись'] = '1'
                    df_rf.at[iter, 'Тип записи'] = 'Иное'
                    df_rf.at[iter, 'ИНН'] = row['IDENTIFICATION NUMBERS'].split('{RU-INN}')[1].split('{')[0].replace(";", '') if '{RU-INN}' in row['IDENTIFICATION NUMBERS'] else ''
                    df_rf.at[iter, 'ОГРН'] = row['IDENTIFICATION NUMBERS'].split('{RU-OGRN}')[1].split('{')[0].replace(";", '') if '{RU-OGRN}' in row['IDENTIFICATION NUMBERS'] else ''
                    df_rf.at[iter, 'Иное'] = row['IDENTIFICATION NUMBERS'].replace(
                        row['IDENTIFICATION NUMBERS'].split('{RU-OGRN}')[1].split('{')[0] if '{RU-OGRN}' in row['IDENTIFICATION NUMBERS'] else '', '') \
                        .replace(row['IDENTIFICATION NUMBERS'].split('{RU-INN}')[1].split('{')[0], '').replace('{RU-INN}', '').replace('{RU-OGRN}', '') if '{RU-INN}' in row['IDENTIFICATION NUMBERS']  and '{RU-OGRN}' in row['IDENTIFICATION NUMBERS'] else row['IDENTIFICATION NUMBERS']
                    df_rf.at[iter, 'Дата рождения'] = row['DOB'] if not '/00' else row['DOB'].replace('/00', '/01')
                    df_rf.at[iter, 'Фамилия'] = row['LAST NAME'].replace("'", "")
                    df_rf.at[iter, 'Имя'] = row['FIRST NAME'].replace("'", "")
                    df_rf.at[iter, 'Наименование(главное лат)'] = row['LAST NAME'].replace("'", "")
                    df_rf.at[iter, 'Альтернативные наименования'] = row['ALIASES'].replace("'", "") + '; ' + row['ALTERNATIVE SPELLING'].replace("'", "")
                    df_rf.at[iter, 'Резиденство'] = row['CITIZENSHIP'].replace("'", "")
                    df_rf.at[iter, 'Дата генерации записи'] = row['ENTERED'] if not '/00' else row['DOB'].replace('/00', '/01')
                    df_rf.at[iter, 'Дата обновления записи'] = row['UPDATED'] if not '/00' else row['DOB'].replace('/00', '/01')
                    df_rf.at[iter, 'Комментарии пользователя'] = row['FURTHER INFORMATION'].split('[BIOGRAPHY]')[1].split('[')[0].replace("'",'') if '[BIOGRAPHY]' in row['FURTHER INFORMATION'] else ''
                    df_rf.at[iter, 'Идентификатор записи согласно источнику'] = str(row['UID'])
                    df_rf.at[iter, 'Активная запись'] = 'Действующий'
                    iter += 1
            df_rf = df_rf.fillna('')
            return df_rf


if __name__ == '__main__':
    parser = ParseRef()
    parser.parse_data()
