import requests
from enum import Enum
from tkinter.filedialog import askopenfilename
import pandas as pd
import os
from getpass import getpass
import time
import sys
import datetime

class DocumentType(Enum):
    # Паспорт гражданина СССР
    passport_ussr = "01"
    # Свидетельство о рождении
    birth_certificate = "03"
    # Паспорт иностранного гражданина
    passport_foreign = "10"
    # Вид на жительство в России
    residence_permit = "12"
    # Разрешение на временное проживание в России
    residence_permit_temp = "15"
    # Свидетельство о предоставлении временного убежища на территории России
    asylum_certificate_temp = "19"
    # Паспорт гражданина России
    passport_russia = "21"
    # Свидетельство о рождении, выданное уполномоченным органом иностранного государства
    birth_certificate_foreign = "23"
    # Вид на жительство иностранного гражданина
    residence_permit_foreign = "62"

def auth():
    user = os.environ.get("USERNAME")
    password = getpass("Введите пароль и нажмите Enter").replace("@", "%40")
    return user,password

def suggest_inn(surname, name, patronymic, birthdate, doctype, docnumber, docdate,crd):
    url = "https://service.nalog.ru/inn-proc.do"
    data = {
        "fam": surname,
        "nam": name,
        "otch": patronymic,
        "bdate": birthdate,
        "bplace": "",
        "doctype": doctype,
        "docno": docnumber,
        "docdt": docdate,
        "c": "innMy",
        "captcha": "",
        "captchaToken": "",
    }
    user, password = crd

    # proxies = {'http': 'https://' + str(user) + ':' + str(password) + '@localhost:8081', 'https': 'http://' + str(user) + ':' + str(password) + '@localhost:8081'}
    resp = requests.post(url=url, data=data, timeout=100)
    resp.raise_for_status()
    return resp.json()


def suggest_inn_excel():
    type_pass_eq = {"01":"21", "05":"10", "012":"03", "018":"19"}
    root = askopenfilename()
    clients = pd.read_excel(root, dtype=str)
    clients.fillna("", inplace=True)
    clients['Тип документа'] = clients['Тип документа'].apply(lambda x: x.replace("00", "0"))
    cred = auth()
    clients['ИНН_ФНС'] = ''
    coldown=0
    for i, row in clients.iterrows():
        if row["Тип документа"] in type_pass_eq.keys() and row['ИНН_ФНС'] in ['',None]:
            # coldown+=1
            # if coldown == 5:
            response = None
            count = 0
            while response == None:
                try:
                    if count != 25:
                        time.sleep(5)
                        response = suggest_inn(
                            surname=row["Фамилия"].strip(),
                            name=row["Имя"].strip(),
                            patronymic=row["Отчество"].strip() if not row["Отчество"].strip()=="" else "нет",
                            birthdate=row["Дата рождения"],
                            doctype=type_pass_eq[row["Тип документа"]],
                            docnumber=row["№Документа"].strip(),
                            docdate=datetime.datetime.strftime(pd.to_datetime(row['Дата документа'],format="%Y-%m-%d",errors='coerce'),'%d.%m.%Y') if row['Дата документа'] != '' else '',
                            crd=cred
                        )
                    else:
                        break
                except:
                    print(i)
                    print(sys.exc_info()[0])
                    print(sys.exc_info()[1])
                    time.sleep(7)
                    if '400 Client Error:' in str(sys.exc_info()[1]):
                        response = {'inn':'Ошибка'}
                count += 1
            clients.at[i,'ИНН_ФНС'] = "0" if 'inn' not in response else response['inn']
            clients.to_excel(root,index=False)
            print(response)


if __name__ == "__main__":
    response = suggest_inn(
        surname="Сидоров",
        name="Виктор",
        patronymic="Васильевич",
        birthdate="01.01.1992",
        doctype=DocumentType.passport_russia.value,
        docnumber="12 34 567890",
        docdate="01.01.2020", crd = auth()
    )
    suggest_inn_excel()

