from tree_model import *
from proxy import *
from db_connection import *
from Config_read import confdict
from SendStatistic import send_statistic
from Progress import ProgressBar

class ExportModule(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.x, self.y, self.w, self.h = 0, 0, 1200, 651
        self.setGeometry(self.x, self.y, self.w, self.h)

        self.window = MainWindow(self)
        self.setCentralWidget(self.window)
        self.setWindowTitle("Выгрузка данных")
        self.show()

class GeneralWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(GeneralWidget, self).__init__(parent)
        lay = QtWidgets.QVBoxLayout(self)
        self.lay_h = QtWidgets.QHBoxLayout(self)
        self.lay_h.setAlignment(Qt.AlignRight)
        self.tableView = DataFrameWidget()
        self.pushButton = QtWidgets.QPushButton("Отобразить список", clicked=self.__load_df)
        self.pushButton_1 = QtWidgets.QPushButton("Выгрузить информацию в формате SSW", clicked=self.__export_ssw)
        self.sanction_text = QtWidgets.QLineEdit()
        self.sanction_text.setMaximumHeight(25)
        self.affilation_text = QtWidgets.QLineEdit()
        self.affilation_text.setMaximumHeight(25)
        self.rewrite_radio = QtWidgets.QRadioButton()
        self.radio_label = QtWidgets.QLabel("Перезаписать поля комментариев?")
        self.comb_list = QtWidgets.QComboBox(self)
        self.comb_list.addItem("X-com")
        self.comb_list.addItem("AB")
        self.comb_list.addItem("User")
        self.comb_list.addItem("TR общий")
        self.comb_list.addItem("TR санкции")
        self.comb_list.addItem("TR без обработки")
        self.comb_list.addItem("Объединенный список")
        self.col_dict = confdict['COLUMNS']


        lay.addWidget(self.comb_list)
        lay.addWidget(self.pushButton)
        lay.addWidget(self.tableView)
        lay.addLayout(self.lay_h)
        self.lay_h.addWidget(self.radio_label)
        self.lay_h.addWidget(self.rewrite_radio)
        lay.addWidget(self.sanction_text)
        lay.addWidget(self.affilation_text)
        lay.addWidget(self.pushButton_1)

    @QtCore.pyqtSlot()
    def __load_df(self):
        self.connect = SqlModule()
        if not self.comb_list.currentText() == "Объединенный список":
            df = self.connect.create_df(self.comb_list.currentText())
            df = df.loc[:, ~df.columns.duplicated()]
            df = df.rename(columns = confdict['COLUMNS'])
            df['SSW_flag'] = 0
            self.tableView.setDataFrame(df)
        else:
            try:
                df = pd.read_excel(os.path.dirname(os.path.realpath(__file__)) + "\data_temp.xlsx")
                if not 'Активная запись' in list(df):
                    df['Активная запись'] = '1'
                df['SSW_flag'] = 0
                df.fillna('',inplace=True)
                self.tableView.setDataFrame(df)
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Объединенный список")
                msg.setWindowTitle("Объединенный список")
                msg.setDetailedText("Нет версии объединенного списка, пожалуйста создайте объединенный список")
                msg.exec_()

    @QtCore.pyqtSlot()
    def __export_ssw(self):
        def join(iterator, separator):
            it = map(str, iterator)
            separator = str(separator)
            string = next(it, '')
            for s in it:
                string += separator + s
            return string

        def transliterate(name_to_convert):
            name_to_convert = name_to_convert if name_to_convert is not None else ''
            alphabet_rus = ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М",
                            "Н", "О", "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ",
                            "Ы", "Ь", "Э", "Ю", "Я", "а", "б", "в", "г", "д", "е", "ё", "ж", "з",
                            "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х",
                            "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]
            repl_2 = ["A", "B", "V", "G", "D", "E", "", "J", "Z", "I", "I", "K", "L", "M",
                      "N", "O", "P", "R", "S", "T", "U", "F", "H", "C", "C", "H", "H", "",
                      "Y", "", "E", "U", "A", "a", "b", "v", "g", "d", "e", "", "j", "z", "i",
                      "i", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "c", "c",
                      "h", "h", "", "y", "", "e", "u", "a"]
            repl_3 = ["A", "B", "V", "G", "D", "E", "", "J", "Z", "I", "I", "K", "L", "M",
                      "N", "O", "P", "R", "S", "T", "U", "F", "H", "C", "C", "Q", "Q", "X",
                      "Y", "X", "E", "U", "A", "a", "b", "v", "g", "d", "e", "", "j", "z",
                      "i", "i", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h",
                      "c", "c", "q", "q", "x", "y", "x", "e", "u", "a"]
            repl_4 = ["A", "B", "W", "G", "D", "E", "E", "V", "Z", "I", "J", "K", "L", "M",
                      "N", "O", "P", "R", "S", "T", "U", "F", "H", "C", "4", "H", "H", "X",
                      "Y", "X", "E", "U", "Q", "A", "B", "W", "G", "D", "E", "E", "V", "Z",
                      "I", "J", "K", "L", "M", "N", "O", "P", "R", "S", "T", "U", "F", "H",
                      "C", "4", "H", "H", "X", "Y", "X", "E", "U", "Q"]
            repl_5 = ["A", "B", "V", "G", "D", "E", "YO", "ZH", "Z", "I", "J", "K", "L", "M",
                      "N", "O", "P", "R", "S", "T", "U", "F", "X", "CZ", "C", "SH", "SHH", "",
                      "Y", "", "E", "YU", "YA", "a", "b", "v", "g", "d", "e", "yo", "zh", "z",
                      "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "x", "cz",
                      "c", "sh", "shh", "", "y", "", "e", "yu", "ya"]
            repl_6 = ["A", "B", "V", "G", "D", "E", "YO", "ZH", "Z", "I", "J", "K", "L", "M",
                      "N", "O", "P", "R", "S", "T", "U", "F", "X", "C4", "C", "SH", "SHH", "",
                      "Y", "", "E", "YU", "YA", "a", "b", "v", "g", "d", "e", "yo", "zh", "z",
                      "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "x", "c4",
                      "c", "sh", "shh", "", "y", "", "e", "yu", "ya", ]
            repl_7 = ["A", "B", "V", "G", "D", "E", "JO", "ZH", "Z", "I", "JJ", "K", "L", "M",
                      "N", "O", "P", "R", "S", "T", "U", "F", "KH", "C", "CH", "SH", "SHH", "",
                      "Y", "", "EH", "JU", "JA", "a", "b", "v", "g", "d", "e", "jo", "zh", "z",
                      "i", "jj", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh",
                      "c", "ch", "sh", "shh", "", "y", "", "eh", "ju", "ja"]
            repl_8 = ["A", "B", "V", "G", "D", "E", "E", "ZH", "Z", "I", "I", "K", "L", "M",
                      "N", "O", "P", "R", "S", "T", "U", "F", "KH", "TC", "CH", "SH", "SHCH",
                      "", "Y", "", "E", "IU", "IA", "a", "b", "v", "g", "d", "e", "j", "zh", "z",
                      "i", "i", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh", "tc",
                      "ch", "sh", "shch", "", "y", "", "e", "iu", "ia"]
            repl_9 = ["A", "B", "V", "G", "D", "E", "E", "ZH", "Z", "I", "Y", "K", "L", "M",
                      "N", "O", "P", "R", "S", "T", "U", "F", "KH", "TS", "CH", "SH", "SHCH",
                      "", "Y", "", "E", "YU", "YA", "a", "b", "v", "g", "d", "e", "j", "zh",
                      "z", "i", "y", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f",
                      "kh", "ts", "ch", "sh", "shch", "", "y", "", "e", "yu", "ya"]
            repl_10 = ["A", "B", "V", "G", "D", "E", "E", "J", "Z", "I", "I", "K", "L", "M",
                       "N", "O", "P", "R", "S", "T", "U", "F", "H", "C", "CH", "SH", "SC", "",
                       "Y", "", "E", "IU", "IA", "a", "b", "v", "g", "d", "e", "j", "j", "z", "i",
                       "i", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "h", "c", "ch",
                       "sh", "sc", "", "y", "", "e", "iu", "ia", ]
            repl_11 = ["A", "B", "V", "G", "D", "E", "E", "ZH", "Z", "I", "I", "K", "L", "M",
                       "N", "O", "P", "R", "S", "T", "U", "F", "KH", "TS", "CH", "SH", "SHCH",
                       "", "Y", "IE", "E", "IU", "IA", "a", "b", "v", "g", "d", "e", "j", "zh",
                       "z", "i", "i", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u", "f", "kh",
                       "ts", "ch", "sh", "shch", "", "y", "ie", "e", "iu", "ia"]

            array_translit = []
            for repl in [repl_2, repl_3, repl_4, repl_5, repl_6, repl_7, repl_8, repl_9, repl_10, repl_11]:
                alphabet_dict = dict(zip(alphabet_rus, repl))
                text = name_to_convert
                for key in alphabet_dict:
                    text = text.replace(key, alphabet_dict[key])
                array_translit.append(text)
            return array_translit

        def write_txt(dataframe, path_to_folder):
            counter = 0
            path_to_folder = path_to_folder + '\\Sanctions_converted.txt'
            file = open(path_to_folder, 'w', encoding="utf-8")
            file.write('EXTERNAL_ID CATEGORY NAME_TYPE NAME INN MAIN_ENTRY')
            dataframe["Main"] = "Main"
            # dataframe['id'] += 1
            dataframe = dataframe.fillna('')
            Progress = ProgressBar(len(dataframe))
            for i, row in dataframe.iterrows():
                counter += 1
                if row['Type'] == 'Individual':
                    line = join(row[['id', 'Type', 'Main', 'Name_lat', 'Name_tran', *list(dataframe)[5:-1]]], "|")
                    file.write('\n' + line)
                elif row['Type'] == 'Group':
                    cols = ['id', 'Type', 'Main', 'Name_lat', 'INN', 'Name_tran', *list(dataframe)[5:-1]]
                    cols.remove('Name_additional_149')
                    line = join(row[cols], "|")
                    file.write('\n' + line)
                else:
                    print("Тип лица в строке " + str(i + 1) + " задан некорректно")
                Progress.SendStep()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText('Было выгружено ' + str(counter) + ' строк(и)')
            msg.setWindowTitle("Статистика по выгрузке SSW")
            msg.exec_()
            file.close()

        dir = QFileDialog.getExistingDirectory(self, "Select Directory")
        ssw_df =  self.tableView.df[self.tableView.df['SSW_flag']==1]

        col_array = ['id', 'Type', 'Name_lat', 'INN', 'Name_tran']
        for iterator in range(1, 150):
            col_array.append(str('Name_additional_' + str(iterator)))

        arr_empty = [None, '', 'None', 'nan']
        col_array.append('SDGT')
        col_array.append('Affiliated')
        exampl_df = pd.DataFrame(columns=col_array)
        ssw_df.fillna('',inplace=True)
        Progress = ProgressBar(len(ssw_df))
        for i, row in ssw_df.iterrows():
            if row['Дата обновления записи']  not in arr_empty:
                row['Дата обновления записи'] = pd.to_datetime(row['Дата обновления записи'])
            if row['Дата генерации записи']  not in arr_empty:
                row['Дата генерации записи'] = pd.to_datetime(row['Дата генерации записи'])
            if row['Дата рождения']  not in arr_empty:
                row['Дата рождения'] = pd.to_datetime(row['Дата рождения'])
            if (row['Тип записи'] == 0 and row['ИНН'] not in exampl_df['INN'].values and row['ОГРН'] not in arr_empty) \
                    or (row['Тип записи'] == 0 and row['ОГРН'] in arr_empty and row['Наименование(главное лат)'] not in exampl_df['Name_lat'].values) \
                    or (row['Тип записи'] == 1 and row['Наименование(главное лат)'] not in exampl_df['Name_lat'].values) \
                    or (row['Тип записи'] == 0 and row['ИНН']  in arr_empty and row['ОГРН'] in arr_empty and row['Наименование(главное лат)'] not in exampl_df['Name_lat'].values):
                exampl_df.at[i, 'id'] = row['id_company']
                exampl_df.at[i, 'INN'] = row['ИНН']
                exampl_df.at[i, 'Type'] = 'Group' if row['Тип записи'] == 0 else 'Individual'
                exampl_df.at[i, 'Name_lat'] = row['Наименование(главное лат)']
                exampl_df.at[i, 'Name_tran'] = row['Наименование(транслит)']

                name_vspom = list(set([row['Альтернативные наименования для загрузки '+str(i)] for i in range(1,6)]))
                name_tran = list(set(transliterate(row['Наименование(главное рус)'])))
                name_tran_ext = list(set(transliterate(row['Наименование(полное)'])))
                name_tran += name_tran_ext
                name_tran = list(set(name_tran))
                temp_list = []
                temp_list.append(row['Наименование(главное лат)'])
                temp_list.append(row['Наименование(транслит)'])
                temp_list.extend(name_tran)
                temp_list.extend(name_vspom)
                temp_list = list(set(temp_list))

                if row['Наименование(главное лат)'] in temp_list:
                    temp_list.remove(row['Наименование(главное лат)'])
                if row['Наименование(транслит)'] in temp_list:
                    temp_list.remove(row['Наименование(транслит)'])

                    if len(temp_list) > 0:
                        for iterator in range(5, 5 + len(temp_list)):
                            exampl_df.at[i, list(exampl_df)[iterator]] = temp_list[iterator - 5]

                    if self.rewrite_radio.isChecked():
                        exampl_df.at[i, 'SDGT'] = self.sanction_text.text()
                    else:
                        sanctions_str = ''
                        for item in row['Коды санкционных ограничений'].split(','):
                            if item.strip() in confdict['MAPPING_SANCTIONS'].keys():
                                sanctions_str += confdict['MAPPING_SANCTIONS'][item.strip()] + ', '

                        sanctions_str = sanctions_str[:-2] if sanctions_str[-2:] == ', ' else sanctions_str
                        if sanctions_str != '':
                            exampl_df.at[i, 'SDGT'] = 'Sanctions ' + ' (' + sanctions_str+')'
                        else:
                            exampl_df.at[i, 'SDGT'] = self.sanction_text.text()

                    if self.rewrite_radio.isChecked():
                        exampl_df.at[i, 'Affiliated'] = self.affilation_text.text()
                    elif row['Тип записи'] == 1:
                        exampl_df.at[i, 'Affiliated'] = 'Note dd ' + str(row['Дата генерации записи'].strftime('%d.%m.%Y')
                                                                         if row['Дата обновления записи'] in arr_empty else row['Дата обновления записи'].strftime('%d.%m.%Y')) \
                                                        + ((' Date of birth ' + row['Дата рождения'].strftime('%d.%m.%Y')) if not (
                                    pd.isna(row['Дата рождения']) or row['Дата рождения'] in arr_empty) else '')
                    else:
                        if row['Связь с санкционным элементом (наим лат)'] not in arr_empty:
                            exampl_df.at[i, 'Affiliated'] = 'Note dd ' + str(row['Дата генерации записи'].strftime('%d.%m.%Y')
                                                                             if row['Дата обновления записи'] in arr_empty else row['Дата обновления записи'].strftime('%d.%m.%Y')) \
                                                            + ' Affiliated to: ' + row['Связь с санкционным элементом (наим лат)']
                        elif row['Связь с санкционным элементом (наим лат)'] in arr_empty:
                            exampl_df.at[i, 'Affiliated'] = 'Note dd ' + str(row['Дата генерации записи'].strftime('%d.%m.%Y')
                                                                             if row['Дата обновления записи'] in arr_empty else row['Дата обновления записи'].strftime('%d.%m.%Y'))
                elif row['Тип записи'] == 0 and row['ИНН'] in exampl_df['INN'].values and row['ОГРН'] not in arr_empty:
                    affiliated = exampl_df.loc[exampl_df[exampl_df['INN'] == row['ИНН']].index.values, 'Affiliated']
                    if row['Связь с санкционным элементом (наим лат)'] not in str(affiliated.values):
                        if 'Affiliated to: ' not in str(affiliated):
                            affiliated += "Affiliated to: " + row['Связь с санкционным элементом (наим лат)']
                        else:
                            affiliated += ", " + row['Связь с санкционным элементом (наим лат)']
                        exampl_df.at[exampl_df[exampl_df['INN'] == row['ИНН']].index.values, 'Affiliated'] = affiliated
                elif row['Тип записи'] == 0 and row['ИНН'] in exampl_df['INN'].values and row['ОГРН'] in arr_empty and row['Наименование(главное лат)'] in exampl_df['Name_lat'].values:
                    affiliated = exampl_df.loc[exampl_df[(exampl_df['INN'] == row['ИНН']) & (exampl_df['Name_lat'] == row['Наименование(главное лат)'])].index.values, 'Affiliated']
                    if not self.rewrite_radio.isChecked():
                        if row['Связь с санкционным элементом (наим лат)'] not in str(affiliated.values):
                            if 'Affiliated to: ' not in str(affiliated):
                                affiliated += "Affiliated to: " + row['Связь с санкционным элементом (наим лат)']
                            else:
                                affiliated += ", " + row['Связь с санкционным элементом (наим лат)']
                            exampl_df.at[
                                exampl_df[(exampl_df['INN'] == row['ИНН']) & (exampl_df['Name_lat'] == row['Наименование(главное лат)'])].index.values, 'Affiliated'] = affiliated
                    else:
                        exampl_df[exampl_df[(exampl_df['INN'] == row['ИНН']) & (exampl_df['Name_lat'] == row['Наименование(главное лат)'])].index.values, 'Affiliated'] = self.affilation_text.text()
            Progress.SendStep()
        exampl_df['INN'] = exampl_df['INN'].apply(lambda x: 'INN' + str(x) if not x in arr_empty else x)
        exampl_df = exampl_df.sort_values('id', ascending=True)
        write_txt(exampl_df, dir)
        send_statistic(49,len(exampl_df))

class MainWindow(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MainWindow, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(GeneralWidget())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = ExportModule()
    sys.exit(app.exec_())
