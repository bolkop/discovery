import sys
import os
from netdisc_v02 import netdisc
import time

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QApplication, QCursor

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

    ntd = netdisc() # object class netdisc
    localDevicesList = []   # Global list to hold all discovered local devices
    remoteDevicesList = []   # Global list to hold all discovered remote devices
    selectedLocalDevice = None  # Global variable for selected local device 
    selectedRemoteDevice = None  # Global variable for selected global device 
    localConfigFile = None   # Configuration File for local device
    remoteConfigFile = None   # Configuration File for remote device
    
    def waiting_effects(function):
        def new_function(self):
            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            try:
                function(self)
            except Exception as e:
                raise e
                print("Error {}".format(e.args[0]))
            finally:
                QApplication.restoreOverrideCursor()
        return new_function
    
    def browseLocalFolder(self):
        """
        Select a config file for local device after button Browse is clicked
        and display filer path in text field
        """
        # Set file filter
        filter = "xml(*.xml)"
        self.localConfigFile = QtGui.QFileDialog.getOpenFileName(None, "", "", filter)
        # print(selectedFile)
        self.configFileBrowse.setText(self.localConfigFile)

        #Enable or disable "Update Local Device" button
        if self.configFileBrowse.text() != "":
            self.updateLocalButton.setEnabled(True)
        else:
            self.updateLocalButton.setEnabled(False)
            
    def browseRemoteFolder(self):
        """
        Select a config file for remote device after button Browse is clicked
        and display filer path in text field
        """
        # Set file filter
        filter = "xml(*.xml)"
        self.remoteConfigFile = QtGui.QFileDialog.getOpenFileName(None, "", "", filter)
        # print(selectedFile)
        self.configRemoteFileBrowse.setText(self.remoteConfigFile)

        #Enable or disable "Update Local Device" button
        if self.configRemoteFileBrowse.text() != "":
            self.updateRemoteButton.setEnabled(True)
        else:
            self.updateRemoteButton.setEnabled(False)

    def updateDiscoveredDeviceList(self, listView):
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
        
        for dev in self.localDevicesList:
        
            # Remove MAC address and other info. Show only name DEV-? and IP address
            devSplited = dev.split()
            tmpList = " ".join([devSplited[index] for index in [0,2,3,4]])
            self.localDevicesComboBox.addItem(tmpList)
        
    @waiting_effects
    def scanLocal(self):
        """
        Search for local devices on a network and list them in "Discovered Local Devises" window.
        If there are no devices found the window is cleared.
        """
        # Clear content of "Local Devices List" window
        self.discoveredLocalDev.clear()
        
        # Clear content of "Interface Detail" window
        self.detailsLocalDev.clear()

        # Search for local devices
        devices = self.ntd.doLocalScan()
               
        if devices is False:
            # Clear list of local devices if not found any device
            self.localDevicesList = []
            self.localDevicesList.insert(0, "None")

        else:
            # Update list of local devices
            self.localDevicesList = devices.splitlines()

        # Print list of discovered devices in "Discovered Local Devices" window
        self.updateDiscoveredDeviceList(self.discoveredLocalDev)

    def printInfo(self, device, window):
        """
        Print eth and fifo details in "Device Interface Details" window
        """
        # if device is None:
            # dev = self.discoveredLocalDev.currentItem().text()
        # # Text from selected line in "Discovered Local Devices"
        # else:
            # dev = device.text()
            
        # Obtain name of selected device
        dev = device.text()        
        
        # Check in which window (local or remote) device is selected 
        windowName =  window.objectName()
        
        if windowName is self.detailsLocalDev.objectName():
            # Obtain local device name "DEV-?"
            self.selectedLocalDevice = dev.split(' ', 1)
            selected = self.selectedLocalDevice
       
        else:
            # Obtain remote device name "DEV-?"
            self.selectedRemoteDevice = dev.split(' ', 1)
            selected = self.selectedRemoteDevice
            
        #print unicode(selected[0])
        
        if "DEV" in selected[0]:           
            results = self.ntd.do_print(unicode(selected[0]))
            print results
            window.setText(results)
        else:
            window.clear()

    def updateLocalDevice(self):
        """
        Send selected configure .xml file to local device
        Refresh details in local "Device Interface Details" window
        """
        if "DEV" in self.selectedLocalDevice[0]:
            self.ntd.do_lcfg(unicode(self.selectedLocalDevice[0]),str(self.localConfigFile))
            self.printInfo(self.discoveredLocalDev.currentItem(), self.detailsLocalDev)
    
    def updateRemoteDevice(self):
        """
        Send selected configure .xml file to remote device
        Refresh details in remote "Device Interface Details" window
        """            
        if "DEV" in self.selectedRemoteDevice[0]:
            self.ntd.do_rcfg(unicode(self.selectedRemoteDevice[0]), unicode(self.selectedRemoteDevice[1]), str(self.remoteConfigFile))
            self.printInfo(self.discoveredRemoteDev.currentItem(), self.detailsRemoteDev)
            
    @waiting_effects
    def scanRemote(self):
        """
        Search for remote devices on a network and list them in "Discovered Remote Devises" window.
        If there are no devices found the window is cleared.
        """
        # Clear List
        self.remoteDevicesList = []
        
        # Clear content of "Local Devices List" window
        self.discoveredRemoteDev.clear()
        
        # Clear content of "Interface Detail" window
        self.detailsRemoteDev.clear()

        # Get selected devices from combo box
        selectedDeviceInComboBox  = unicode(self.localDevicesComboBox.currentText())              
        
        # Obtain device name "DEV-?"
        dev = selectedDeviceInComboBox.split(' ', 1)       
        
        # Search for remote devices for DEV-?
        if "DEV" in dev[0]:           
            devices = self.ntd.doRemoteScan(unicode(dev[0]))
            
            # Clear list of local devices if not found any device 
            if devices is False:                             
                self.remoteDevicesList.insert(0, "None")

            else:
                # Create a list of all devices (including local)
                allDevices = devices.splitlines()
                
                # For testing only, remove when using real modems
                allDevices.append("DEV-99 00:04:00:00:00:00 140.110.1.28 ELEC MODEM") 
                
                # Remove local devices from list and copy remote devices to remoteDevicesList
                self.remoteDevicesList = list((set(allDevices) - set(self.localDevicesList)))
                
                # If no remote devices found, add "None" to remoteDeviceList
                if len(self.remoteDevicesList) is 0:
                    self.remoteDevicesList.insert(0, "None")               
        
        else: 
            # Clear list of local devices if not found any device              
            self.remoteDevicesList.insert(0, "None")
            
        # Update window with remote devices        
        self.discoveredRemoteDev.addItems(self.remoteDevicesList)       
        
       
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

        self.discoveredLocalDev = QtGui.QListWidget(self.tab)
        self.discoveredLocalDev.setGeometry(QtCore.QRect(30, 95, 410, 71))
        self.discoveredLocalDev.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.discoveredLocalDev.setObjectName(_fromUtf8("discoveredLocalDev"))
        self.discoveredLocalDev.setSpacing(2)
        self.discoveredLocalDev.itemClicked.connect(lambda: self.printInfo(self.discoveredLocalDev.currentItem(), self.detailsLocalDev))

        self.browseButton = QtGui.QPushButton(self.tab)
        self.browseButton.setGeometry(QtCore.QRect(354, 385, 85, 28))
        self.browseButton.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.browseButton.clicked.connect(self.browseLocalFolder)

        self.updateLocalButton = QtGui.QPushButton(self.tab)
        self.updateLocalButton.setGeometry(QtCore.QRect(115, 435, 325, 28))
        self.updateLocalButton.setEnabled(False)
        self.updateLocalButton.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.updateLocalButton.setObjectName(_fromUtf8("updateLocalButton"))
        self.updateLocalButton.clicked.connect(self.updateLocalDevice)

        self.configFileLabel = QtGui.QLabel(self.tab)
        self.configFileLabel.setGeometry(QtCore.QRect(32, 390, 77, 16))
        self.configFileLabel.setObjectName(_fromUtf8("configFileLabel"))

        self.detailsLocalDevLabel = QtGui.QLabel(self.tab)
        self.detailsLocalDevLabel.setGeometry(QtCore.QRect(32, 175, 411, 20))
        self.detailsLocalDevLabel.setStyleSheet(_fromUtf8("background-color: rgba(198, 225, 255, 0);"))
        self.detailsLocalDevLabel.setObjectName(_fromUtf8("detailsLocalDevLabel"))

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

        self.detailsLocalDev = QtGui.QLabel(self.tab)
        self.detailsLocalDev.setGeometry(QtCore.QRect(30, 195, 410, 170))
        self.detailsLocalDev.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        # self.detailsLocalDev.setReadOnly(True)
        self.detailsLocalDev.setAlignment(QtCore.Qt.AlignLeft)
        self.detailsLocalDev.setMargin(5)
        self.detailsLocalDev.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse)
        self.detailsLocalDev.setObjectName(_fromUtf8("detailsLocalDev"))

        self.detailsLocalDevScrollArea = QtGui.QScrollArea(self.tab)
        self.detailsLocalDevScrollArea.setGeometry(QtCore.QRect(30, 195, 410, 170))
        self.detailsLocalDevScrollArea.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.detailsLocalDevScrollArea.setWidgetResizable(True)
        self.detailsLocalDevScrollArea.setWidget(self.detailsLocalDev)

        self.detailsLocalDevLabel.raise_()
        self.discoveredDevicesLable.raise_()
        self.browseButton.raise_()
        self.updateLocalButton.raise_()
        self.configFileLabel.raise_()
        self.scanButton.raise_()
        self.discoveredLocalDev.raise_()
        self.configFileBrowse.raise_()
        #self.updateRemoteButton.raise_()
        self.detailsLocalDev.raise_()
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName(_fromUtf8("tab_2"))

        self.discoveredRemoteDev = QtGui.QListWidget(self.tab_2)
        self.discoveredRemoteDev.setGeometry(QtCore.QRect(30, 95, 410, 71))
        self.discoveredRemoteDev.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.discoveredRemoteDev.setFrameShadow(QtGui.QFrame.Sunken)
        self.discoveredRemoteDev.setSpacing(2)
        self.discoveredRemoteDev.setObjectName(_fromUtf8("discoveredRemoteDev"))
        self.discoveredRemoteDev.itemClicked.connect(lambda: self.printInfo(self.discoveredRemoteDev.currentItem(), self.detailsRemoteDev))

        self.browseButtonRemote = QtGui.QPushButton(self.tab_2)
        self.browseButtonRemote.setGeometry(QtCore.QRect(353, 385, 85, 28))
        self.browseButtonRemote.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.browseButtonRemote.setObjectName(_fromUtf8("browseButtonRemote"))
        self.browseButtonRemote.clicked.connect(self.browseRemoteFolder)
        
        self.updateRemoteButton = QtGui.QPushButton(self.tab_2)
        self.updateRemoteButton.setGeometry(QtCore.QRect(115, 435, 325, 28))
        self.updateRemoteButton.setEnabled(False)
        self.updateRemoteButton.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.updateRemoteButton.setObjectName(_fromUtf8("updateRemoteButton"))
        self.updateRemoteButton.clicked.connect(self.updateRemoteDevice)

        self.configFileLabelRemote = QtGui.QLabel(self.tab_2)
        self.configFileLabelRemote.setGeometry(QtCore.QRect(32, 390, 77, 16))
        self.configFileLabelRemote.setObjectName(_fromUtf8("configFileLabelRemote"))

        self.detailsRemoteDevLabel = QtGui.QLabel(self.tab_2)
        self.detailsRemoteDevLabel.setGeometry(QtCore.QRect(32, 175, 411, 20))
        self.detailsRemoteDevLabel.setObjectName(_fromUtf8("detailsRemoteDevLabel"))
        
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

        self.scanButtonRemote = QtGui.QPushButton(self.tab_2)
        self.scanButtonRemote.setGeometry(QtCore.QRect(330, 60, 110, 28))
        self.scanButtonRemote.setStyleSheet(_fromUtf8("background-color: rgba(224, 231, 245, 255);"))
        self.scanButtonRemote.setObjectName(_fromUtf8("scanButtonRemote"))
        self.scanButtonRemote.clicked.connect(self.scanRemote)

        self.localDevicesComboBox = QtGui.QComboBox(self.tab_2)
        self.localDevicesComboBox.setGeometry(QtCore.QRect(30, 35, 200, 28))
        self.localDevicesComboBox.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.localDevicesComboBox.setStyleSheet(_fromUtf8("selection-background-color: rgb(164, 205, 255);"))
        self.localDevicesComboBox.setObjectName(_fromUtf8("localDevicesComboBox"))

        self.label = QtGui.QLabel(self.tab_2)
        self.label.setGeometry(QtCore.QRect(32, 14, 131, 21))
        self.label.setObjectName(_fromUtf8("label"))

        self.configRemoteFileBrowse = QtGui.QLineEdit(self.tab_2)
        self.configRemoteFileBrowse.setGeometry(QtCore.QRect(115, 385, 231, 28))
        self.configRemoteFileBrowse.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.configRemoteFileBrowse.setText(_fromUtf8(""))
        self.configRemoteFileBrowse.setReadOnly(True)
        self.configRemoteFileBrowse.setObjectName(_fromUtf8("configRemoteFileBrowse"))
        
        # self.lineEdit_3 = QtGui.QLineEdit(self.tab_2)
        # self.lineEdit_3.setGeometry(QtCore.QRect(30, 195, 410, 170))
        # self.lineEdit_3.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 205);"))
        # self.lineEdit_3.setReadOnly(True)
        # self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))      
        
        self.detailsRemoteDev = QtGui.QLabel(self.tab_2)
        self.detailsRemoteDev.setGeometry(QtCore.QRect(30, 195, 410, 170))
        self.detailsRemoteDev.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        # self.detailsRemoteDev.setReadOnly(True)
        self.detailsRemoteDev.setAlignment(QtCore.Qt.AlignLeft)
        self.detailsRemoteDev.setMargin(5)
        self.detailsRemoteDev.setTextInteractionFlags(
            QtCore.Qt.TextSelectableByKeyboard | QtCore.Qt.TextSelectableByMouse)
        self.detailsRemoteDev.setObjectName(_fromUtf8("detailsRemoteDev"))
               
        self.detailsRemoteDevScrollArea = QtGui.QScrollArea(self.tab_2)
        self.detailsRemoteDevScrollArea.setGeometry(QtCore.QRect(30, 195, 410, 170))
        self.detailsRemoteDevScrollArea.setStyleSheet(_fromUtf8("background-color: rgb(255, 255, 255);"))
        self.detailsRemoteDevScrollArea.setWidgetResizable(True)
        self.detailsRemoteDevScrollArea.setWidget(self.detailsRemoteDev)
        
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        MainWindow.setCentralWidget(self.centralwidget)   
        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "GraphNetdisc", None))
        self.browseButton.setText(_translate("MainWindow", "Browse", None))
        self.updateLocalButton.setText(_translate("MainWindow", "Update Local Device", None))
        self.configFileLabel.setText(_translate("MainWindow", "Confige File", None))
        self.detailsLocalDevLabel.setText(_translate("MainWindow", "Device Interface Details", None))
        self.discoveredDevicesLable.setText(_translate("MainWindow", "Discovered Local Devices", None))
        self.scanButton.setText(_translate("MainWindow", "Scan Network", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "   Local Devices", None))
        self.browseButtonRemote.setText(_translate("MainWindow", "Browse", None))
        self.updateRemoteButton.setText(_translate("MainWindow", "Update Remote Device", None))
        self.configFileLabelRemote.setText(_translate("MainWindow", "Confige File", None))
        self.detailsRemoteDevLabel.setText(_translate("MainWindow", "Device Interface Details", None))
        self.discoveredDevicesLable_2.setText(_translate("MainWindow", "Discovered Remote Devices", None))
        self.scanButtonRemote.setText(_translate("MainWindow", "Scan Network", None))
        self.label.setText(_translate("MainWindow", "Select Local Device", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2),
                                  _translate("MainWindow", "   Remote Devices", None))


def mainFunc():
    import sys

    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.updateDiscoveredDeviceList(ui.discoveredLocalDev)
    # ui.showDiscoveredDevice("Dev 2", ui.discoveredLocalDev)
    MainWindow.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    mainFunc()
