from PyQt4 import QtCore, QtGui
from functools import partial

class Gui(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)

        editLayout=QtGui.QFormLayout()

        edit=QtGui.QLineEdit()
        edit.setMinimumWidth(125)
        regex=QtCore.QRegExp("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        validator=QtGui.QRegExpValidator(regex, edit)

        edit.setValidator(validator)

        editLayout.addRow("Enter Client IP:", edit)

        button=QtGui.QPushButton("Add Client")
        button.clicked.connect(partial(self.addClientButtonClicked, edit, validator))

        layout=QtGui.QVBoxLayout()
        layout.addLayout(editLayout)
        layout.addWidget(button)

        self.setLayout(layout)

    # def addClientButtonClicked(self, edit, validator):
        # print("ip=", edit.text())
        # print(validator.State==QtGui.QValidator.Intermediate)

    # def addClientButtonClicked(self, edit, validator):
        # print("ip=", edit.text())
        # print(validator.validate(edit.text(), 0))
        
    def addClientButtonClicked(self, edit, validator):
        state, pos = validator.validate(edit.text(), 0)
        print(state == QtGui.QValidator.Acceptable)

def mainFunc():

    
    import sys
    app=QtGui.QApplication(sys.argv)
    g=Gui()
    g.show()
    app.exec_()
    

if __name__ == '__main__':
    mainFunc()