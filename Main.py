from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QApplication, QCursor

from netdisc import netdisc
from pccontrol import pccontrol

import ModSetupWithTree as ms

class MyQtApp(ms.Ui_MainWindow, QtGui.QMainWindow):
    __ntd = netdisc() # object class netdisc
    
    __localPc = None
    __localDevicesList = ["Dev10 24323, fdsfs, fsdfs, fssdf", "Dev1 54881 dsfdf gsdjkls ds;djfk sdlkf;"]   # Global list to hold all discovered local devices
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
                QApplication.restoreOverrideCursor()
                self.showdialog(e.args[0])
               # self.clearDevicesFromTree()
                raise e                         
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
        self.__localPc = QtGui.QTreeWidgetItem(['Local PC ' + pcIpAddress])
        self.treeWidget.addTopLevelItem(self.__localPc)
        self.lineEditPcPhysicalAddress.clear()
        self.lineEditPcPhysicalAddress.setText((unicode(self.__ntd.get_MAC())))
        self.lineEditPcIpAddress.setText(unicode(pcIpAddress))
        self.lineEditPcSubnetMask.setText(unicode(self.__ntd.get_SubnetMask()))
        self.lineEditPcDefaultGateway.setText(unicode(self.__ntd.get_DefaultGateway()))
        self.stackedWidget.setCurrentIndex(0)
    
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
            # self.__localDevicesList = []
            # self.__localDevicesList.insert(0, "None")
            raise ValueError("Unable to find local devices")
        else:
            # Update list of local devices
            #self.__localDevicesList = []
            lineSplited = devices.splitlines()
            
            for dev in lineSplited:
                devSplited = dev.split()
                tmpList = " ".join([devSplited[index] for index in [0,2,3,4]])
                self.__localDevicesList.append(tmpList)
            
            print (self.__localDevicesList)
            self.addLocalDevicesToTree(self.__localDevicesList)

        # Print list of discovered devices in Tree window
        #self.updateDiscoveredDeviceList()
        
    # def updateDiscoveredDeviceList(self):
        # """
        # Add discovered devices to Tree window from global __localDevicesList.
        # """
        # print (self.__localDevicesList[0])
        # if self.__localDevicesList[0] == "None":
            # self.clearDevicesFromTree()
        # else:
            # self.addLocalDevicesToTree(self._localDevicesList)
            

    def addLocalDevicesToTree(self, devicesList):
      #  allDevices = devicesList.splitlines()
        
        #add all dev from list before updates
        for dev in self.__localDevicesList:
           # devSplited = dev.split()
            #tmpList = " ".join([devSplited[index] for index in [0,2,3,4]])
            localDev = QtGui.QTreeWidgetItem(self.__localPc)
            localDev.setText(0, dev)
            
        # update __localDevicesList list and remove not existing devices
      #  self.__localDevicesList = list((set(allDevices) - set(self.__localDevicesList)))   
        
        # add updated list to tree
    #    for dev in self.__localDevicesList:
           # devSplited = dev.split()
           # tmpList = " ".join([devSplited[index] for index in [0,2,3,4]])
     #       localDev = QtGui.QTreeWidgetItem(self.__localPc)
     #       localDev.setText(0, dev)
        
      #  print(dev)
        
        # findQWidget = QtGui.QTreeWidgetItem(self.__localPc)    
        # findQWidget.setText(0, dev) 
        # print(findQWidget.text(0))
        
        #for index in range(self.treeWidget.topLevelItemCount()):
        for index in range(self.__localPc.childCount()):
            print ("from tree", self.__localPc.child(index).text(0))
           # print("first item in list ",  tmpList[0])
            print("from list", self.__localDevicesList[0])
          #  if self.__localDevicesList[0] != self.__localPc.child(index).text(0):
          #      self.__localPc.takeChild(index)
            
       
       # for ch in treeChild:
        #    print (ch.text(0))
            
            
            # if findQWidget is self.treeWidget.itemWidget(self.__localPc, index):
                # print (findQWidget)
                
                
        self.treeWidget.expandToDepth(0)  
       # for dev in self.treeWidget.
        
    def clearDevicesFromTree(self):
        print ("All deviced removed from tree")
        None
            
    def showdialog(self, text):
        """
        Display window message type info.
        Text parameter as string is displayed
        Message window includes OK button
        """
        msg = QtGui.QMessageBox()
        msg.setWindowTitle("Info")
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText(text+"\t\n\n")
        msg.setStandardButtons(QtGui.QMessageBox.Ok)   
        msg.exec_()
    

def mainFunc():
    import sys

    app = QtGui.QApplication(sys.argv)
    qtApp = MyQtApp()
    qtApp.show()
    app.exec_()

if __name__ == '__main__':
    mainFunc()
