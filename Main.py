from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QApplication, QCursor

from netdisc import netdisc
from pccontrol import pccontrol

import ModSetupWithTree as ms

class MyQtApp(ms.Ui_MainWindow, QtGui.QMainWindow):
    __ntd = netdisc() # object class netdisc
    
    __localDevicesList = []   # Global list to hold all discovered local devices
    __remoteDevicesList = []   # Global list to hold all discovered remote devices
    __selectedLocalDevice = None  # Global variable for selected local device 
    __selectedRemoteDevice = None  # Global variable for selected global device 
    __localConfigXmlFile = None   # Configuration .xml File for local device
    __remoteConfigXmlFile = None   # Configuration .xml File for remote device
    __localConfigFtpFile = None   # Configuration .ftp File for local device
    __remoteConfigFtpFile = None   # Configuration .ftp File for remote device
  
    
    def __init__(self):
        super(MyQtApp, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Network Scanner -  Build 01")     
        self.initTree()
        self.treeWidget.itemClicked.connect(self.showWidgetDetails)
        self.pushButtonPc.clicked.connect(self.scanLocal)
       
    
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
        
    def showWidgetDetails(self, it, col):
      #  print(it, col, it.text(col))
  
        self.stackedWidget.setCurrentIndex(col)
         
                 
    def initTree(self):
        """
        Clear Items in Tree Widget.
        Check details TCP/IP details of host PC.
        Update Tree and Widget with host PC details.       
        """
        self.treeWidget.clear()
        self.treeWidget.setHeaderLabels(["Network Devices"])
        pcIpAddress = self.__ntd.get_IP()
        localPc = QtGui.QTreeWidgetItem(['Local PC\t' + pcIpAddress])
        self.treeWidget.addTopLevelItem(localPc)
        self.lineEditPcPhysicalAddress.clear()
        self.lineEditPcPhysicalAddress.setText((unicode(self.__ntd.get_MAC())))
        self.lineEditPcIpAddress.setText(unicode(pcIpAddress))
        self.lineEditPcSubnetMask.setText(unicode(self.__ntd.get_SubnetMask()))
        self.lineEditPcDefaultGateway.setText(unicode(self.__ntd.get_DefaultGateway()))
        self.showdialog()
    
    def pcDetals(self):
        print "pc details"
        
        
    @waiting_effects
    def scanLocal(self):
        """
        Search for local devices on a network and list them in Tree Widget window.
        If there are no devices found the Tree window is cleared.
        """
        # Clear content of "Local Devices List" window
        #self.discoveredLocalDev.clear()
        
        # Clear content of "Interface Detail" window
        #self.detailsLocalDev.clear()

        # Search for local devices
        devices = self.__ntd.doLocalScan()
               
        if devices is False:
            # Clear list of local devices if not found any device
            self.__localDevicesList = []
            self.__localDevicesList.insert(0, "None")

        else:
            # Update list of local devices
            self.__localDevicesList = devices.splitlines()

        # Print list of discovered devices in Tree window
        self.updateDiscoveredDeviceList()
        
    def updateDiscoveredDeviceList(self):
        """
        Add discovered devices to Tree window from global __localDevicesList.
        """
        print (self.__localDevicesList[0])
        if self.__localDevicesList[0] == "None":
            None
            
    def showdialog(self):
        msg = QtGui.QMessageBox()
        #msg.setIcon(QtGui.QMessageBox.Information)

        msg.setText("This is a message box")
        msg.exec_()

        # if ret == QtGui.QMessageBox.Yes:
            # print( "Yes" )
            # return
        # else:
            # print( "No" )
            # return
        # msg.setInformativeText("This is additional information")
        # msg.setWindowTitle("MessageBox demo")
        # msg.setDetailedText("The details are as follows:")
        # msg.setStandardButtons(QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel)     
        
        # listView.clear()
        # listView.addItems(self.localDevicesList)
        # self.updateComboBox()
 
 # for parent in plist:
 # pitems=QTreeWidgetItem(treeWidget)
 # pitems.setText(0,parent)
 # for child in clist:
 # citems=QTreeWidgetItem(pitems)
 # citems.setText(0,child)
    
    

def mainFunc():
    import sys

    app = QtGui.QApplication(sys.argv)
    qtApp = MyQtApp()
    qtApp.show()
    app.exec_()

if __name__ == '__main__':
    mainFunc()
