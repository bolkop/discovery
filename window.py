import sys
import os
from netdisc_v02 import netdisc
# sys.path.append('C://python2.7//site-packages')

## -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'MainWindowv2.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui, Qt

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8


    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainWindow(object):
    ntd = netdisc()

    localDevicesList = []

    def browseFolder(self):
        """
        Select a file after button Browse is clicked
        and display filer path in text field
        """
        # # self.listWidget.clear()  # In case there are any existing elements in the list
        # directory = QtGui.QFileDialog.getExistingDirectory(MainWindow)
        # # execute getExistingDirectory dialog and set the directory variable to be equal
        # # to the user selected directory
        #
        # if directory:  # if user didn't pick a directory don't continue
        #     for file_name in os.listdir(directory):  # for all files, if any, in the directory
        #         print(file_name)
        #         self.configFileBrowse.setText(file_name)
        selectedFile = QtGui.QFileDialog.getOpenFileName()
        print(selectedFile)
        self.configFileBrowse.setText(selectedFile)

    def updateDiscoveredDevice(self, listView):
        """
        Add discovered devices to Discovered Devices window
        from global localDevicesList
        """
        listView.clear()
        listView.addItems(self.localDevicesList)
        self.updateComboBox()

    def updateComboBox(self):
        """
        Update the list of items in comboBox from localDevicesList
        """
        self.localDevicesComboBox.clear()
        self.localDevicesComboBox.addItems(self.localDevicesList)

    def scanLocal(self):
        """
        Search for local devices on a network and list them in "Discovered Local Devises" window.
        If there are no devices found the window i cleared.
        """
        #Clear content of "Interface Detail" window
        self.interfaceDetails.clear()

        # Search for local devices
        devices = self.ntd.do_localscan()

        #Clear list of local devices
        if devices is None:
            self.localDevicesList = []
        else:
            self.localDevicesList = devices.splitlines()
        self.updateDiscoveredDevice(self.DiscoveredLocalDev)

    def printInfo(self):
        """
        Print eth and fifo details in "Device Interface Details" window
        """

        # Text from selected line in "Discovered Local Devices"
        dev = self.DiscoveredLocalDev.currentItem().text()
        # Obtain first word from "dev"
        dev = dev.split(':', 1)

        if "DEV" in dev[0]:
            #
            results = self.ntd.do_print(unicode(dev[0]))
            print results
            self.interfaceDetails.setText(results)
        else:
            self.interfaceDetails.clear()

    def setupUi(self, MainWindow):

        # focused_widget = QtGui.QApplication.focusWidget()
        # if focused_widget:
        #     focused_widget.clearFocus()

        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(582, 585)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)

        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))

        self.tabWidget = QtGui.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 30, 591, 561))
        self.tabWidget.setStyleSheet(_fromUtf8("background-color: rgba(236, 236, 236, 255);"))
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))

        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))

        self.DiscoveredLocalDev = QtGui.QListWidget(self.tab)
        self.DiscoveredLocalDev.setGeometry(QtCore.QRect(30, 95, 410, 71))
        self.DiscoveredLocalDev.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.DiscoveredLocalDev.setObjectName(_fromUtf8("DiscoveredLocalDev"))
        self.DiscoveredLocalDev.setSpacing(2)
        self.DiscoveredLocalDev.itemSelectionChanged.connect(self.printInfo)

        # self.discoveredDevicesView.QApplication.focusWidget().clearFocus()

        # self.discoveredDevicesView.setAttribute(Qt.WA_MacShowFocusRect, 0)
        # self.discoveredDevicesView.setFocuPolicy()

        self.browseButton = QtGui.QPushButton(self.tab)
        self.browseButton.setGeometry(QtCore.QRect(354, 385, 85, 28))
        self.browseButton.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.browseButton.clicked.connect(self.browseFolder)

        self.configFileLabel = QtGui.QLabel(self.tab)
        self.configFileLabel.setGeometry(QtCore.QRect(32, 390, 77, 16))
        self.configFileLabel.setObjectName(_fromUtf8("configFileLabel"))

        self.interfaceDetailsLabel = QtGui.QLabel(self.tab)
        self.interfaceDetailsLabel.setGeometry(QtCore.QRect(32, 175, 411, 20))
        self.interfaceDetailsLabel.setStyleSheet(_fromUtf8("background-color: rgba(198, 225, 255, 0);"))
        self.interfaceDetailsLabel.setObjectName(_fromUtf8("interfaceDetailsLabel"))

        self.discoveredDevicesLable = QtGui.QLabel(self.tab)
        self.discoveredDevicesLable.setGeometry(QtCore.QRect(32, 75, 191, 20))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.discoveredDevicesLable.sizePolicy().hasHeightForWidth())

        self.discoveredDevicesLable.setSizePolicy(sizePolicy)
        self.discoveredDevicesLable.setMinimumSize(QtCore.QSize(0, 20))
        self.discoveredDevicesLable.setStyleSheet(_fromUtf8("background-color: rgba(198, 225, 255, 0);"))
        self.discoveredDevicesLable.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.discoveredDevicesLable.setIndent(0)
        self.discoveredDevicesLable.setObjectName(_fromUtf8("discoveredDevicesLable"))

        self.scanButton = QtGui.QPushButton(self.tab)
        self.scanButton.setGeometry(QtCore.QRect(330, 60, 110, 28))
        self.scanButton.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.scanButton.setCheckable(False)
        self.scanButton.setObjectName(_fromUtf8("scanButton"))
        self.scanButton.clicked.connect(self.scanLocal)

        self.configFileBrowse = QtGui.QLineEdit(self.tab)
        self.configFileBrowse.setGeometry(QtCore.QRect(115, 385, 231, 28))
        self.configFileBrowse.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.configFileBrowse.setReadOnly(True)
        self.configFileBrowse.setObjectName(_fromUtf8("configFileBrowse"))

        self.interfaceDetails = QtGui.QLabel(self.tab)
        self.interfaceDetails.setGeometry(QtCore.QRect(30, 195, 410, 170))
        self.interfaceDetails.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        #self.interfaceDetails.setReadOnly(True)
        self.interfaceDetails.setAlignment(QtCore.Qt.AlignLeft)
        self.interfaceDetails.setMargin(5)
        self.interfaceDetails.setTextInteractionFlags(QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse)
        self.interfaceDetails.setObjectName(_fromUtf8("interfaceDetails"))

        self.interfaceDetailsLabel.raise_()
        self.discoveredDevicesLable.raise_()
        self.browseButton.raise_()
        self.configFileLabel.raise_()
        self.scanButton.raise_()
        self.DiscoveredLocalDev.raise_()
        self.configFileBrowse.raise_()
        self.interfaceDetails.raise_()
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))

        self.discoveredDevicesView_2 = QtGui.QListView(self.tab_2)
        self.discoveredDevicesView_2.setGeometry(QtCore.QRect(30, 95, 410, 71))
        self.discoveredDevicesView_2.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.discoveredDevicesView_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.discoveredDevicesView_2.setObjectName(_fromUtf8("discoveredDevicesView_2"))

        self.browseButton_2 = QtGui.QPushButton(self.tab_2)
        self.browseButton_2.setGeometry(QtCore.QRect(353, 385, 85, 28))
        self.browseButton_2.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.browseButton_2.setObjectName(_fromUtf8("browseButton_2"))

        self.configFileLabel_2 = QtGui.QLabel(self.tab_2)
        self.configFileLabel_2.setGeometry(QtCore.QRect(32, 390, 77, 16))
        self.configFileLabel_2.setObjectName(_fromUtf8("configFileLabel_2"))

        self.interfaceDetailsLabel_2 = QtGui.QLabel(self.tab_2)
        self.interfaceDetailsLabel_2.setGeometry(QtCore.QRect(32, 175, 411, 20))
        self.interfaceDetailsLabel_2.setObjectName(_fromUtf8("interfaceDetailsLabel_2"))
        self.discoveredDevicesLable_2 = QtGui.QLabel(self.tab_2)
        self.discoveredDevicesLable_2.setGeometry(QtCore.QRect(32, 75, 191, 20))

        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.discoveredDevicesLable_2.sizePolicy().hasHeightForWidth())

        self.discoveredDevicesLable_2.setSizePolicy(sizePolicy)
        self.discoveredDevicesLable_2.setMinimumSize(QtCore.QSize(0, 20))
        self.discoveredDevicesLable_2.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.discoveredDevicesLable_2.setIndent(0)
        self.discoveredDevicesLable_2.setObjectName(_fromUtf8("discoveredDevicesLable_2"))

        self.scanButton_2 = QtGui.QPushButton(self.tab_2)
        self.scanButton_2.setGeometry(QtCore.QRect(330, 60, 110, 28))
        self.scanButton_2.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.scanButton_2.setObjectName(_fromUtf8("scanButton_2"))

        self.localDevicesComboBox = QtGui.QComboBox(self.tab_2)
        self.localDevicesComboBox.setGeometry(QtCore.QRect(30, 35, 169, 28))
        self.localDevicesComboBox.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.localDevicesComboBox.setStyleSheet(_fromUtf8("selection-background-color: rgb(164, 205, 255);"))
        self.localDevicesComboBox.setObjectName(_fromUtf8("localDevicesComboBox"))

        self.label = QtGui.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(32, 14, 131, 21))
        self.label.setObjectName(_fromUtf8("label"))

        self.lineEdit = QtGui.QLineEdit(self.tab_2)
        self.lineEdit.setGeometry(QtCore.QRect(114, 385, 231, 28))
        self.lineEdit.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.lineEdit.setText(_fromUtf8(""))
        self.lineEdit.setReadOnly(True)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.lineEdit_3 = QtGui.QLineEdit(self.tab_2)
        self.lineEdit_3.setGeometry(QtCore.QRect(30, 195, 410, 170))
        self.lineEdit_3.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.browseButton.setText(_translate("MainWindow", "Browse", None))
        self.configFileLabel.setText(_translate("MainWindow", "Confige File", None))
        self.interfaceDetailsLabel.setText(_translate("MainWindow", "Device Interface Details", None))
        self.discoveredDevicesLable.setText(_translate("MainWindow", "Discovered Local Devices", None))
        self.scanButton.setText(_translate("MainWindow", "Scan Network", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "   Local Devices", None))
        self.browseButton_2.setText(_translate("MainWindow", "Browse", None))
        self.configFileLabel_2.setText(_translate("MainWindow", "Confige File", None))
        self.interfaceDetailsLabel_2.setText(_translate("MainWindow", "Device Interface Details", None))
        self.discoveredDevicesLable_2.setText(_translate("MainWindow", "Discovered Remote Devices", None))
        self.scanButton_2.setText(_translate("MainWindow", "Scan Network", None))
        self.label.setText(_translate("MainWindow", "Select Local Device", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2),
                                  _translate("MainWindow", "   Remote Devices", None))


if __name__ == "__main__":
    import sys

    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.updateDiscoveredDevice(ui.DiscoveredLocalDev)
    # ui.showDiscoveredDevice("Dev 2", ui.DiscoveredLocalDev)
    MainWindow.show()

    sys.exit(app.exec_())
