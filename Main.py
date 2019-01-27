from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QApplication, QCursor

import ModSetupWithTree as ms

class MyQtApp(ms.Ui_MainWindow, QtGui.QMainWindow):
    def __init__(self):
        super(MyQtApp, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Network Scanner -  Build 01")


def mainFunc():
    import sys

    app = QtGui.QApplication(sys.argv)
    qtApp = MyQtApp()
    qtApp.show()
    app.exec_()

if __name__ == '__main__':
    mainFunc()

