try:
    from PyQt5 import QtCore, QtWidgets
    from ui_OTBD import UI_OTBD
    from ui_SOZ import MainWindow as UI_SOZ
    import sys
    print("ok")
    input()
except Exception as e:
    print(str(e))
    print("В системе возникла ошибка, нажмите Enter для завершения")
    input()
