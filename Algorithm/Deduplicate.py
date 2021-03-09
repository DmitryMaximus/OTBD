import pandas as pd
dlm = ' || '
func = lambda x: [dlm+str(i)+dlm for i in x.values]
examp = {   'Комментарии пользователя': func,
            'Активная запись':'first',
            'Идентификатор Записи':'first',
            'Дата генерации записи':'first',
            'Дата обновления записи':'first',
            'Вид изменения записи':'first',
            'Код источника записи': lambda x: [dlm+str(i)+dlm for i in x.values],
            'Идентификатор записи согласно источнику': func,
            'Прямопоименованное/подконтрольное': func,
            'Списки SSW': func,
            'Тип записи':'first',
            'Фамилия':func,
            'Имя':func,
            'Отчество':func,
            'др.':func,
            'ФИО':func,
            'Наименование(главное рус)':func,
            'Наименование(полное)':func,
            'Наименование(транслит)':func,
            'Наименование(главное лат)':func,
            'Дата рождения':func,
            'Орг форма':func,
            'Наименование(главное рус) без орг. Формы':func,
            'Наименование(полное) без орг. Формы':func,
            'Наименование(транслит) без орг. Формы':func,
            'Наименование(главное лат) без орг. Формы':func,
            'Наименование(главное рус) с орг. Формой':func,
            'Наименование(полное) с орг. Формой':func,
            'Наименование(транслит) с орг. Формой':func,
            'Наименование(главное лат) с орг. Формой':func,
            'ИНН':func,
            'ОГРН':func,
            'Иное':func,
            'Альтернативные наименования':func,
            'Альтернативные наименования для загрузки 1':func,
            'Альтернативные наименования для загрузки 2':func,
            'Альтернативные наименования для загрузки 3':func,
            'Альтернативные наименования для загрузки 4':func,
            'Альтернативные наименования для загрузки 5':func,
            'ПИН клиента':func,
            'Коды санкционных ограничений':func,
            'Комментарий санкции':func,
            'Страна ограничений':func,
            'Программа ограничений':func,
            'Тип ограничений':func,
            'Адрес1':func,
            'Резиденство':func,
            'Статус наименования':func,
            'Связь с санкционным элементом (наим)':func,
            'Связь с санкционным элементом (наим лат)':func,
            'INN материнской компании':func,
            'Другое':func,
            'Спарк Данные компании':func}
check_subset = ['Активная запись','Прямопоименованное/подконтрольное','Списки SSW','Тип записи','Фамилия', 'Имя', 'Отчество', 'др.', 'ФИО',
            'Наименование(главное рус)', 'Наименование(полное)', 'Наименование(транслит)', 'Наименование(главное лат)', 'Дата рождения','ИНН',
         'ОГРН', 'Иное', 'Альтернативные наименования', 'Альтернативные наименования для загрузки 1', 'Альтернативные наименования для загрузки 2',
         'Альтернативные наименования для загрузки 3', 'Альтернативные наименования для загрузки 4', 'Альтернативные наименования для загрузки 5', 'ПИН клиента',
         'Коды санкционных ограничений', 'Комментарий санкции', 'Страна ограничений', 'Программа ограничений', 'Тип ограничений','Статус наименования',
         'Связь с санкционным элементом (наим)', 'Связь с санкционным элементом (наим лат)', 'INN материнской компании']

def get_data_sql(path):
    #Временно забирает данные из Excel
    try:
        return read_ex(path)['Result']
    except:
        return None
def read_ex(path) -> dict:
    print("Импорт данных Excel")
    sheet_to_df_map = pd.read_excel(path, sheet_name=None)
    return sheet_to_df_map


def check_format(l_check: list) -> bool:
    print("Проверка форматов")

    example = set(list(examp.keys()))

    if set(l_check) == set(example):
        return True
    else:
        return False


def deduplicate_list(input: dict):
    print("Начало обработки Excel")
    empty_df = pd.DataFrame([],columns=list(examp.keys()))
    check = [check_format(input[sheets]) for sheets in list(input.keys())]
    for iter in range(len(check)):
        if check[iter] == True:
            input[list(input.keys())[iter]] = input[list(input.keys())[iter]][input[list(input.keys())[iter]]['Активная запись']==True]
            input[list(input.keys())[iter]].drop_duplicates(inplace=True, keep='first', subset=check_subset)
            empty_df = pd.concat([empty_df,input[list(input.keys())[iter]]])
    empty_df = empty_df.drop_duplicates(keep='first')
    df = empty_df
    return df

def dedup_ul(dataframe:pd.DataFrame())->pd.DataFrame():
    df_ul_inn = dataframe[(dataframe['Тип записи']=="ЮЛ") & (dataframe['ИНН'].apply(lambda x:~pd.isna(x))) & (dataframe['ОГРН'].apply(lambda x:~pd.isna(x)))]
    df_ul_no_inn = dataframe[(dataframe['Тип записи'] == "ЮЛ") & (dataframe['ИНН'].apply(lambda x: pd.isna(x))) & (dataframe['ОГРН'].apply(lambda x:pd.isna(x)))]
    df_fl = dataframe[dataframe['Тип записи'] == "ФЛ"]
    agg_cols = ['ИНН','ОГРН']
    for i in agg_cols:
        del examp[i]
    df_ul_inn = df_ul_inn.groupby(agg_cols, as_index=False).agg(examp)
    return df_ul_inn


def save_excel(path):
    return


if __name__ == '__main__':
    from tkinter.filedialog import askopenfilename, askdirectory
    file_path = askopenfilename(title="Выберите файл для импорта")
    save_path = askdirectory(title="Выберите папку для сохранения")
    input = read_ex(file_path)
    l_input = deduplicate_list(input)
    l_input = dedup_ul(l_input)
