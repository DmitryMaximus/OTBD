import pandas as pd

dlm = ' | '
func = lambda x: [dlm + str(i) + dlm for i in x.values]
examp = ['Комментарии пользователя', 'Активная запись', 'Идентификатор Записи', 'Дата генерации записи', 'Дата обновления записи', 'Вид изменения записи',
         'Код источника записи', 'Идентификатор записи согласно источнику', 'Прямопоименованное/подконтрольное', 'Списки SSW', 'Тип записи', 'Фамилия',
         'Имя', 'Отчество', 'др.', 'ФИО', 'Наименование(главное рус)', 'Наименование(полное)', 'Наименование(транслит)', 'Наименование(главное лат)',
         'Дата рождения', 'Орг форма', 'Наименование(главное рус) без орг. Формы', 'Наименование(полное) без орг. Формы', 'Наименование(транслит) без орг. Формы',
         'Наименование(главное лат) без орг. Формы', 'Наименование(главное рус) с орг. Формой', 'Наименование(полное) с орг. Формой', 'Наименование(транслит) с орг. Формой',
         'Наименование(главное лат) с орг. Формой', 'ИНН', 'ОГРН', 'Иное', 'Альтернативные наименования', 'Альтернативные наименования для загрузки 1',
         'Альтернативные наименования для загрузки 2', 'Альтернативные наименования для загрузки 3', 'Альтернативные наименования для загрузки 4',
         'Альтернативные наименования для загрузки 5', 'ПИН клиента', 'Коды санкционных ограничений', 'Комментарий санкции', 'Страна ограничений', 'Программа ограничений',
         'Тип ограничений', 'Адрес1', 'Резиденство', 'Статус наименования', 'Связь с санкционным элементом (наим)', 'Связь с санкционным элементом (наим лат)',
         'INN материнской компании', 'ОГРН материнской компании', 'Другое', 'Спарк Данные компании']

check_subset = ['Активная запись', 'Прямопоименованное/подконтрольное', 'Списки SSW', 'Тип записи', 'Фамилия', 'Имя', 'Отчество', 'др.', 'ФИО',
                'Наименование(главное рус)', 'Наименование(полное)', 'Наименование(транслит)', 'Наименование(главное лат)', 'Дата рождения', 'ИНН',
                'ОГРН', 'Иное', 'Альтернативные наименования', 'Альтернативные наименования для загрузки 1', 'Альтернативные наименования для загрузки 2',
                'Альтернативные наименования для загрузки 3', 'Альтернативные наименования для загрузки 4', 'Альтернативные наименования для загрузки 5', 'ПИН клиента',
                'Коды санкционных ограничений', 'Комментарий санкции', 'Страна ограничений', 'Программа ограничений', 'Тип ограничений', 'Статус наименования',
                'Связь с санкционным элементом (наим)', 'Связь с санкционным элементом (наим лат)', 'INN материнской компании']
agg_list = ['Альтернативные наименования для загрузки 1', 'Альтернативные наименования для загрузки 2',
            'Альтернативные наименования для загрузки 3', 'Альтернативные наименования для загрузки 4', 'Альтернативные наименования для загрузки 5', 'ПИН клиента',
            'Коды санкционных ограничений', 'Комментарий санкции', 'Страна ограничений', 'Программа ограничений', 'Тип ограничений', 'Статус наименования',
            'Связь с санкционным элементом (наим)', 'Связь с санкционным элементом (наим лат)', 'INN материнской компании', 'ОГРН материнской компании']

def check_format(l_check: list) -> bool:
    print("Проверка форматов")

    example = examp

    if set(l_check) == set(example):
        return True
    else:
        return False


def deduplicate_list(input):
    print("Начало обработки Excel")
    empty_df = pd.DataFrame([], columns=list(examp))
    check = check_format(list(input))
    if check == True:
        input = input[input['Активная запись'] == "Действующий"]
        input.drop_duplicates(inplace=True, keep='first', subset=check_subset)
    return input


def combine_row(df, idx):
    try:
        main_row = df.iloc[idx[0]]
    except:
        return None
    else:
        for item in idx[1:]:
            for column in agg_list:
                if column == 'Коды санкционных ограничений':
                    curr_val = main_row[column].split(',')
                    new_val = df.loc[item][column] if main_row[column] != "" else df.loc[item][column]
                    new_val = new_val.split(',')
                    for val in new_val:
                        if str(val).lstrip() not in curr_val:
                            curr_val += [str(val).lstrip()]
                    curr_val = ', '.join(set(curr_val))
                    main_row[column] = curr_val

                elif df.loc[item][column] not in main_row[column]:
                    main_row[column] += " | " + df.loc[item][column] if main_row[column] != "" else df.loc[item][column]

        return main_row


def deduplicate(input):
    dataframe = deduplicate_list(input)
    dataframe = dataframe.fillna("")
    dataframe = dataframe.applymap(str)
    resulting_df = pd.DataFrame([], columns=list(examp))
    counter = 0

    for i, row in dataframe.iterrows():
        idx = []
        if i in dataframe.index:
            if len(dataframe[(dataframe['ИНН'] == row['ИНН']) & (row['Тип записи'] == 'ЮЛ')& (row['ИНН'] != "")& (row['ОГРН'] != "")
                             & (dataframe['ОГРН'] == row['ОГРН'])].index) > 1:
                idx = list(dataframe[(dataframe['ИНН'] == row['ИНН'])
                                     & (dataframe['ОГРН'] == row['ОГРН'])].index.values)

            elif len(dataframe[(dataframe['ИНН'] == row['ИНН'])
                               & (row['ИНН'] != "")
                               & (row['ОГРН'] == "")
                               & (row['Тип записи'] == 'ЮЛ')
                               & (dataframe['Наименование(главное рус)'] == row['Наименование(главное рус)'])
                               & (dataframe['ОГРН'] == row['ОГРН'])].index) > 1:
                idx = list(dataframe[(dataframe['ИНН'] == row['ИНН'])
                                     & (dataframe['Наименование(главное рус)'] == row['Наименование(главное рус)'])
                                     & (row['ОГРН'] == "")].index.values)

            elif len(dataframe[(row['ИНН'] == "") & (row['ОГРН'] == "") & (row['Тип записи'] == 'ЮЛ')
                               & (dataframe['Наименование(главное рус)'] == row['Наименование(главное рус)']) ].index) > 1:
                idx = list(dataframe[(dataframe['ИНН'] == "") & (row['Тип записи'] == 'ЮЛ')
                                     & (dataframe['Наименование(главное рус)'] == row['Наименование(главное рус)'])
                                     & (row['ОГРН'] == "")].index.values)

            elif len(dataframe[(row['ИНН'] == "") & (row['Тип записи'] == 'ФЛ')& (row['Дата рождения'] != "")
                               & (dataframe['Дата рождения'] == row['Дата рождения']) & (dataframe['ФИО'] == row['ФИО'])].index) > 1:
                idx = list(dataframe[(dataframe['ИНН'] == "") & (row['Тип записи'] == 'ФЛ')
                                     & (dataframe['Дата рождения'] == row['Дата рождения']) & (dataframe['ФИО'] == row['ФИО'])].index.values)

            if idx != []:
                row_c = combine_row(dataframe, idx)
                if row_c is not None:
                    resulting_df.loc[counter] = row_c
                    counter += 1
                    for ind in idx:
                        dataframe.drop(ind, inplace=True)
            else:
                resulting_df.loc[counter] = row
                counter += 1
    resulting_df["Коды санкционных ограничений"] = resulting_df["Коды санкционных ограничений"].apply(lambda x: ','.join(set([i.lstrip() for i in x.split(',')])))

    return resulting_df


if __name__ == '__main__':
    from tkinter.filedialog import askopenfilename, askdirectory

    file_path = askopenfilename(title="Выберите файл для импорта")
    input = pd.read_excel(file_path)
    df = deduplicate(input)
