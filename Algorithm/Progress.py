#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import (QWidget, QProgressBar,
    QPushButton, QApplication)
from PyQt5.QtCore import QBasicTimer

class ProgressBar(QWidget):

    def __init__(self,arr_len):
        super().__init__()

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)

        self.step = 0
        self.setGeometry(150, 150, 280, 170)
        self.setWindowTitle('Прогресс выполнения')
        self.show()


        self.step_count = arr_len/100 if not arr_len == 0 else 1
        self.add_steps = 1 if not (1/self.step_count) > 1 else (1/self.step_count)
        self.current_val = 0
        self.check_len(arr_len)

    def check_len(self,arr_len):
        if  arr_len == 0:
            self.close()


    def UpdateProgress(self):
        QApplication.processEvents()

        self.step += self.add_steps
        if self.step < 100:
            self.pbar.setValue(int(self.step))

        else:
            self.pbar.setValue(100)
            self.close()

    def SendStep(self):
        self.current_val += 1
        if self.step_count > 1:
            if self.current_val%int(self.step_count) == 0:
                self.UpdateProgress()
        else:
                self.UpdateProgress()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ProgressBar()
    sys.exit(app.exec_())