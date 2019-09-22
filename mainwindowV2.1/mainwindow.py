from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QApplication, QCursor
from PyQt4.QtCore import QSettings

from netdisc import netdisc
from pccontrol import pccontrol
from ftplib import FTP

import socket 
import struct
import time
import os
import treegui as gui

__version__ = "2.0.1"

class MyQtApp(gui.Ui_MainWindow, QtGui.QMainWindow):

    __ntd = netdisc() # object class netdisc
    
    __localPc = None
    __localDevicesList = []#"Dev10 24323, fdsfs, fsdfs, fssdf"\
                            #, "Dev1 54881 dsfdf gsdjkls ds;djfk sdlkf;"\
                           # ,"TestDEV-8: 00:04:00:00:00:00 140.10.10.2 ELEC MODEM 247 00:02:00:00:00:00 192.168.0.150"]  # Global list to hold all discovered local devices                             
    __remoteDevicesList = []   # Global list to hold all discovered remote devices
    __selectedLocalDevice = None  # Global variable for selected local device 
    __selectedRemoteDevice = None  # Global variable for selected global device 
    __localConfigXmlFile = ""   # Configuration .xml File for local device
    __remoteConfigXmlFile = ""   # Configuration .xml File for remote device
    __localConfigFtpFile = ""   # Configuration .ftp File for local device
    __remoteConfigFtpFile = ""   # Configuration .ftp File for remote device
    __ipPcDetails = {"mac": "0", "ip": "0", "mask": "0", "gateway": "0"}
  
    __testList = ["Dev10 24323, fdsfs, fsdfs, fssdf"\
                            , "Dev1 54881 dsfdf gsdjkls ds;djfk sdlkf;"\
                            ,"TestDEV-88: 140.10.10.2 ELEC MODEM"]  
    __deviceType = {"PC":0, "local":0, "remote":2}
    
    def __init__(self):
        super(MyQtApp, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("mainwindow -  Build 2.1")     
        self.initTree()
        self.treeWidget.itemClicked.connect(lambda: self.printInfo(self.treeWidget.currentItem()))
        self.pushButtonPc.clicked.connect(self.scanLocal)       
        self.pushButtonLocalXmlBrowse.clicked.connect(self.browseLocalXmlFolder)
        self.pushButtonLocalXmlApply.setEnabled(False)
        self.pushButtonLocalFtpBrowse.clicked.connect(self.browseLocalFtpFolder)
        self.pushButtonLocalFtpApply.setEnabled(False)     
        self.pushButtonLocalXmlApply.clicked.connect(lambda: self.xmlConfigDl(self.treeWidget.currentItem(), self.__localConfigXmlFile))
        self.pushButtonLocalFtpApply.clicked.connect(lambda: self.ftpConfigDl(self.treeWidget.currentItem(), self.__localConfigFtpFile))        
        self.pushButtonRemoteXmlBrowse.clicked.connect(self.browseRemoteXmlFolder)
        self.pushButtonRemoteXmlApply.setEnabled(False)
        self.pushButtonRemoteFtpBrowse.clicked.connect(self.browseRemoteFtpFolder)
        self.pushButtonRemoteFtpApply.setEnabled(False)
        self.pushButtonRemoteXmlApply.clicked.connect(lambda: self.xmlConfigDl(self.treeWidget.currentItem(), self.__remoteConfigXmlFile))
        self.pushButtonRemoteFtpApply.clicked.connect(lambda: self.ftpConfigDl(self.treeWidget.currentItem(), self.__remoteConfigFtpFile))      
        self.pushButtonRefreshPcIp.clicked.connect(self.refreshPcIpDetails)
        self.pushButtonApplyPcIp.clicked.connect(self.applyPcIp)
        self.pushButtonCancelPcIp.clicked.connect(self.cancelIpChanges)
        self.lineEditPcIpAddress.textEdited.connect(self.editPcIpDetails)
        self.lineEditPcDefaultGateway.textEdited.connect(self.editPcIpDetails)
        self.lineEditPcSubnetMask.textEdited.connect(self.editPcIpDetails)
        self.lineEditPcIpAddress.returnPressed.connect(self.pushButtonApplyPcIp.click)
        self.lineEditPcSubnetMask.returnPressed.connect(self.pushButtonApplyPcIp.click)
        self.lineEditPcDefaultGateway.returnPressed.connect(self.pushButtonApplyPcIp.click)
        self.pushButtonReset.clicked.connect(lambda: self.reset(self.treeWidget.currentItem()))
        self.pushButtonResetRemote.clicked.connect(lambda: self.reset(self.treeWidget.currentItem()))
        self.pushButtonScanRemote.clicked.connect(self.scanRemote)
        self.radioButtonDhcpIp.clicked.connect(self.setDhclIp)
        self.radioButtonDefaultIp.clicked.connect(self.setDefaultIp)
        self.radioButtonManualIp.clicked.connect(self.setManualIp)
        
        settings = QSettings()
        self.recentFiles = settings.value("RecentFiles").toStringList()
    
    def waiting_effects(function):
        def new_function(*args, **kwargs):
            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            try:
                return function(*args, **kwargs)
            except ValueError as e:
                print("exceptoin in waiting_effects function")
                QApplication.restoreOverrideCursor()
                self.showdialog(e.args[0])                       
            finally:
                QApplication.restoreOverrideCursor()
        return new_function        
                 
    def initTree(self):
        """
        Clear Items in Tree Widget.
        Check details TCP/IP details of host PC.
        Update Tree and Widget with host PC details.       
        """
        self.treeWidget.takeTopLevelItem(0)
        self.treeWidget.setHeaderLabels(["Network Devices"])
        self.__localPc = QtGui.QTreeWidgetItem(['Local PC '])
        self.treeWidget.addTopLevelItem(self.__localPc)
        
        # Select Host PC in tree list
        self.treeWidget.setCurrentItem(self.__localPc)
        
        self.refreshPcIpDetails()
        self.stackedWidget.setCurrentIndex(0)
     
        #self.treeWidget.itemClicked.connect(lambda: self.printInfo(self.treeWidget.currentItem()))
    
    def browseLocalXmlFolder(self):
        """
        Select a config file for local device after button Browse is clicked
        and display filer path in text field
        """
        selectFile = None
        
        # Set file filter
        filter = "xml(*.xml)"  
        
        # Obtain path of the last config file
        dir = (os.path.dirname(self.__localConfigXmlFile))
       
        # Obtain the selected .xml file
        selectFile = str(QtGui.QFileDialog.getOpenFileName(self, "Choose config .xml file", dir, filter))
        
        if selectFile != "":
            self.__localConfigXmlFile = selectFile
            print("xml file", self.__localConfigXmlFile)
               
        # Show path to .xml file in Text Window
        self.lineEditLocalXmlBrowse.setText(self.__localConfigXmlFile)
        
        
        #Enable or disable "Apply" button
        if self.lineEditLocalXmlBrowse.text() != "":
            self.pushButtonLocalXmlApply.setEnabled(True)
        else:
            self.pushButtonLocalXmlApply.setEnabled(False)
            
    def browseRemoteXmlFolder(self):
        """
        Select a config file for remote device after button Browse is clicked
        and display filer path in text field
        """
        selectFile = None
        
        # Set file filter
        filter = "xml(*.xml)"        
        
        # Obtain path of the last config file
        dir = (os.path.dirname(self.__remoteConfigXmlFile))
                 
        # Obtain the selected .xml file
        selectFile = str(QtGui.QFileDialog.getOpenFileName(self, "Choose config .xml file", dir, filter))
        
        if selectFile != "":
            self.__remoteConfigXmlFile = selectFile
            print("xml file", self.__remoteConfigXmlFile)
            
        # Show path to .xml file in Text Window
        self.lineEditRemoteXmlBrowse.setText(self.__remoteConfigXmlFile)

        #Enable or disable "Update Local Device" button
        if self.lineEditRemoteXmlBrowse.text() != "":
            self.pushButtonRemoteXmlApply.setEnabled(True)
        else:
            self.pushButtonRemoteXmlApply.setEnabled(False)

    def browseLocalFtpFolder(self):
        """
        Select a config file for local device after button Browse is clicked
        and display filer path in text field
        """
        selectFile = None
        
        # Set file filter
        filter = "Config File(*.ftp;*.h8)"
        
        # Obtain path of the last config file
        dir = os.path.dirname(self.__localConfigFtpFile)
        
        # Obtain the selected .ftp file
        selectFile = str(QtGui.QFileDialog.getOpenFileName(self, "Choose config .ftp file", dir, filter))
       
        if selectFile != "":
            self.__localConfigFtpFile = selectFile
            print("xml file", self.__localConfigFtpFile)
            
        # Show path to .ftp file in Text Window
        self.lineEditLocalFtpBrowse.setText(self.__localConfigFtpFile)

        #Enable or disable "Apply" button
        if self.lineEditLocalFtpBrowse.text() != "":
            self.pushButtonLocalFtpApply.setEnabled(True)
        else:
            self.pushButtonLocalFtpApply.setEnabled(False)
            
    def browseRemoteFtpFolder(self):
        """
        Select a config file for remote device after button Browse is clicked
        and display filer path in text field
        """
        selectFile = None
        
        # Set file filter
        filter = "Config File(*.ftp;*.h8)"

        # Obtain path of the last config file
        dir = os.path.dirname(self.__remoteConfigFtpFile)
        
        # Obtain the selected .ftp file
        selectFile = str(QtGui.QFileDialog.getOpenFileName(self, "Choose config .ftp file", dir, filter))
       
        if selectFile != "":
            self.__remoteConfigFtpFile = selectFile
            print("xml file", self.__remoteConfigFtpFile)
        
        # Show path to .ftp file in Text Window
        self.lineEditRemoteFtpBrowse.setText(self.__remoteConfigFtpFile)

        #Enable or disable "Update Local Device" button
        if self.lineEditRemoteFtpBrowse.text() != "":
            self.pushButtonRemoteFtpApply.setEnabled(True)
        else:
            self.pushButtonRemoteFtpApply.setEnabled(False)
    
    def refreshPcIpDetails(self):
        # """
        # Get the current IP settings for the local PC
        # Update info in the Tree and TCP/IP Details windows
        # Update info in the 0000000000.xml file
        # """
       
        # Get the current IP settings for an active NIC
        nic = self.__ntd.refreshNicDetails()
        
        self.__ipPcDetails["mac"] = self.__ntd.get_MAC()
        self.__ipPcDetails["ip"] = self.__ntd.get_IP()
        self.__ipPcDetails["mask"] = self.__ntd.get_SubnetMask()
        self.__ipPcDetails["gateway"] = self.__ntd.get_DefaultGateway()
      
        # Update info in Tree Window
        self.__localPc.setText(0,  'Local PC ' + self.__ipPcDetails["ip"])
        
        # Update info in TCP/IP Window
        self.lineEditPcPhysicalAddress.setText(self.__ipPcDetails["mac"])
        self.lineEditPcIpAddress.setText(self.__ipPcDetails["ip"])
        self.lineEditPcSubnetMask.setText(self.__ipPcDetails["mask"])
        self.lineEditPcDefaultGateway.setText(self.__ipPcDetails["gateway"])
        
        # Update IP details in the 0000000000.XML file
        if self.__ntd.set_pcXML(self.__ipPcDetails["mac"], self.__ipPcDetails["ip"],\
                            self.__ipPcDetails["mask"]) == False:
            
            self.showdialog("Unable to modify 0000000000.XML file")
            return 
    @waiting_effects
    def setDhclIp(self, arg=None):
        # """
        # Make IP, mask and gateway fields read only 
        # Change ip address of host PC as per DHCL server
        # Radio Button DHCL IP address is selected
        # """
        
        # Change colour and read only values for fields in TCP/IP Window
        self.lineEditPcIpAddress.setReadOnly(True)
        self.lineEditPcIpAddress.setStyleSheet((""))
        self.lineEditPcSubnetMask.setReadOnly(True)
        self.lineEditPcSubnetMask.setStyleSheet((""))
        self.lineEditPcDefaultGateway.setReadOnly(True)
        self.lineEditPcDefaultGateway.setStyleSheet((""))
       
        # Set ip address to DHCL value
        
        self.__ntd.setIp(self.__ipPcDetails["mac"])
        
     #   QtCore.QTimer.singleShot(1000, self.refreshPcIpDetails())
        self.refreshPcIpDetails()
        
        
        # Update info in Tree and TCP/IP Window
     #   self.refreshPcIpDetails()
    
    def setDefaultIp(self):
        # """
        # Make IP, mask and gateway fields read only 
        # Radio Button Default IP address is selected
        # """
        
        # Change colour and read only values for fields in TCP/IP Window
        self.lineEditPcIpAddress.setReadOnly(True)
        self.lineEditPcIpAddress.setStyleSheet((""))
        self.lineEditPcSubnetMask.setReadOnly(True)
        self.lineEditPcSubnetMask.setStyleSheet((""))
        self.lineEditPcDefaultGateway.setReadOnly(True)
        self.lineEditPcDefaultGateway.setStyleSheet((""))
        
    def setManualIp(self):
        # """
        # Make IP, mask and gateway fields active (editable)
        # IP address can be set manualy in TCP/IP Window
        # Radio Button Manual IP address is selected
        # """
        
        # Make IP, mask and gateway fields active (editable)
        self.lineEditPcIpAddress.setReadOnly(False)
        self.lineEditPcIpAddress.setStyleSheet(("background-color: rgb(255, 255, 255);"))
        self.lineEditPcSubnetMask.setReadOnly(False)
        self.lineEditPcSubnetMask.setStyleSheet(("background-color: rgb(255, 255, 255);"))
        self.lineEditPcDefaultGateway.setReadOnly(False)
        self.lineEditPcDefaultGateway.setStyleSheet(("background-color: rgb(255, 255, 255);"))
    
    def isIpInNetwork(self, ip, hostIp, netmask): 
        """
        Check if ip is in a network
        Return True or False
        """
        ipAddr = struct.unpack('!L',socket.inet_aton(ip))[0]    
        hostIpAddr = struct.unpack('!L',socket.inet_aton(hostIp))[0]
        mask = struct.unpack('!L',socket.inet_aton(netmask))[0]
        
        return ipAddr & mask == hostIpAddr & mask    
        
    def defaultIp(self, deviceIp, deviceNetmask):
        # """
        # Calculate default ip address for host PC
        # Default ip address is in network of local device
        # IN - ip address of local device as deviceIP
        # IN - netmask of loacal device as deviceNetmask
        # Out - free ip address on network for host PC
        # """
    
        # Convert network and ip address from string to int
        intNetmask = struct.unpack('!L',socket.inet_aton(deviceNetmask))[0]  
        intDeviceIp = struct.unpack('!L',socket.inet_aton(deviceIp))[0]
        
        # Calculate network address for local device
        network = intNetmask & intDeviceIp
        
        # Calculate max number of devices in network of local device
        iter = 2**32 - intNetmask -1
        
        # First ip address on local network
        ipaddr = network + 1
        
        # Check is ipaddr free on network
        for i in xrange(iter):        
                       
            # Convert ip address from int to string
            pcIP = socket.inet_ntoa(struct.pack('!L', ipaddr))
            
            # Check is this ip adderss used by local device         
            for dev in self.__localDevicesList:
                devSplited = dev.split(' ', 3)                
              
                # IP address is used; increment IP value by 1 and check again
                if pcIP == devSplited[2]:                     
                    ipaddr+= 1
                    break
            else: 
                return pcIP               
        
        # Print message if unbable to find free ip address    
        else:
            print("Unable to find free IP address")
            return False         
        
    def editPcIpDetails(self):
        # """
        # Change IP, mask or gateway by user when mouse clicked on their fields 
        # """
       
        self.pushButtonApplyPcIp.setEnabled(True)
        self.pushButtonApplyPcIp.setDefault(True)        
        
        regExp = QtCore.QRegExp('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        validator = QtGui.QRegExpValidator(regExp)
        self.lineEditPcIpAddress.setValidator(validator)
        self.lineEditPcSubnetMask.setValidator(validator)
        self.lineEditPcDefaultGateway.setValidator(validator)
        #self.pushButtonApplyPcIp.setFocus()
    
    @waiting_effects
    def applyPcIp(self, arg=None):
        # """
        # Check that data provided by user are correct. 
        # If correct, show new values for IP, mask, or gateway
        # If not correct, display window with error message
        # """
        
        if not self.isIpFormatCorrect(self.lineEditPcIpAddress):
            self.showdialog("Incorrect IP Address %s" %self.lineEditPcIpAddress.text())
        
        elif not self.isIpFormatCorrect(self.lineEditPcSubnetMask):
            self.showdialog("Incorrect Subnet Mask %s" %self.lineEditPcSubnetMask.text())
        
        elif not self.isIpFormatCorrect(self.lineEditPcDefaultGateway):
            self.showdialog("Incorrect Gateway Address %s" %self.lineEditPcDefaultGateway.text())
        
        else:
        
            # result = self.__ntd.setIp(self.__ipPcDetails["mac"], self.__ipPcDetails["ip"],\
                           # self.__ipPcDetails["mask"], self.__ipPcDetails["gateway"])
            result = self.__ntd.setIp(unicode(self.lineEditPcPhysicalAddress.text()), unicode(self.lineEditPcIpAddress.text()),\
                           unicode(self.lineEditPcSubnetMask.text()), unicode(self.lineEditPcDefaultGateway.text()))

            if result == 0:               
                # Update info in Tree Window
                self.__localPc.setText(0,  'Local PC ' + self.lineEditPcIpAddress.text())
            
                # Save new IP Details
                self.__ipPcDetails["ip"] = unicode(self.lineEditPcIpAddress.text())
                self.__ipPcDetails["mask"] = unicode(self.lineEditPcSubnetMask.text())
                self.__ipPcDetails["gateway"] = unicode(self.lineEditPcDefaultGateway.text())
                self.pushButtonApplyPcIp.setEnabled(False)
                return True
            else:
                self.cancelIpChanges()
                self.showdialog("Unable to change IP addres, error code %s" %result)
                return False                            
          
           # self.framePcAddressDetails.focusWidget().clearFocus()
            
        
    
    def cancelIpChanges(self):
        print("cancel pc ip changes")

        self.lineEditPcPhysicalAddress.setText(self.__ipPcDetails["mac"])
        self.lineEditPcIpAddress.setText(self.__ipPcDetails["ip"])
        self.lineEditPcSubnetMask.setText(self.__ipPcDetails["mask"])
        self.lineEditPcDefaultGateway.setText(self.__ipPcDetails["gateway"])
        self.pushButtonApplyPcIp.setEnabled(False)
        

    def isIpFormatCorrect(self, qIpLine):
    
        splitedIp = unicode(qIpLine.text()).split('.')
            
        try:
            if len(splitedIp) != 4: 
                #self.showdialog("Incorrect IP Address %s" %ustr)
                qIpLine.selectAll()
                qIpLine.setFocus()
                return False
            for item in splitedIp:
                if not 0 <= int(item) <= 255:
                   # self.showdialog("Incorrect IP Address %s" %ustr)
                    qIpLine.selectAll()
                    qIpLine.setFocus()
                    return False
        except ValueError:
            qIpLine.selectAll()
            qIpLine.setFocus()
            return False
        
        return True 
    
    def setPcIpInLocalNetwork(self):
                 
        localDeviceIp = unicode(self.lineEditLocalEth0Ip.text())
        localDeviceNetmask = unicode(self.lineEditLocalEth0Mask.text())
        pcIp = unicode(self.lineEditPcIpAddress.text())
        pcNetmask =  unicode(self.lineEditPcSubnetMask.text())
        
        # Check is ip address of host PC in network of local device
        if self.isIpInNetwork(localDeviceIp, pcIp, pcNetmask) and\
                self.isIpInNetwork(pcIp, localDeviceIp, localDeviceNetmask):
            return True
        
        # Check is Default IP address option selected
        elif self.radioButtonDefaultIp.isChecked():
        
            # Change PC IP to default value
            pcIp = self.defaultIp(localDeviceIp, localDeviceNetmask)
            if pcIp != False:
                self.lineEditPcIpAddress.setText(pcIp)
                self.lineEditPcSubnetMask.setText(localDeviceNetmask)
                self.lineEditPcDefaultGateway.setText(localDeviceIp)
                return self.applyPcIp()                 
                # Wait 2s until IP is changed
                # loop = QtCore.QEventLoop() 
                # QtCore.QTimer.singleShot(2000, loop.quit)
                # loop.exec_()
                #return True
            else:
                QApplication.restoreOverrideCursor()
                self.showdialog("Unable to set default IP address")
                return False
        else:
            # PC IP has to be changed manualy
            QApplication.restoreOverrideCursor()
            self.showdialog("Host PC has different network. Please change IP address")
            return False
        
    @waiting_effects
    def scanLocal(self, arg=None):
        """
        Search for local devices on a network and list them in Tree Widget window.
        If there are no devices found the Tree window is cleared.
        """
        # Search for local devices
        devices = self.__ntd.doLocalScan()       
        print ("local devices", devices)
        
       # Did not find local devices    
        if devices is False:
            # Remove all devices from tree
            self.__localPc.takeChildren()
            
            # Show PC details window
            self.stackedWidget.setCurrentIndex(0)
            
            # Select Host PC in tree list
            self.treeWidget.setCurrentItem(self.__localPc)
                       
            # Display message window
            QApplication.restoreOverrideCursor()
            self.showdialog("Unable to find local devices")
            
            # except ValueError as e:
                # QApplication.restoreOverrideCursor()
                # self.showdialog(e.args[0])
            return False
                       
        else:
            newLocalDevices = []
            oldList = self.__localDevicesList
            self.__localDevicesList = devices
                   
            for dev in self.__localDevicesList:
                if dev not in oldList:                                 
                    newLocalDevices.append(dev)
                       
            self.addLocalDevicesToTree(newLocalDevices)   
            self.printInfo(self.treeWidget.currentItem())      
            return True

    def addLocalDevicesToTree(self, devicesList):        
        """
        Add new devices to tree widget
        Remove not existing devices from tree widget
        IN list of devices to be added
        """
        
        # Add all dev from list before updates     
        for dev in devicesList:              
            localDev = QtGui.QTreeWidgetItem(self.__localPc, 1)
            localDev.setText(0, dev)
       
       # Remove all non-existing local devices from tree   
        childRange = range(self.__localPc.childCount())       
        
        for chindex in childRange:            
            for index in range(self.__localPc.childCount()):              
                if unicode(self.__localPc.child(index).text(0)) not in str(self.__localDevicesList).strip():
                    self.__localPc.takeChild(index)                 
                    childRange.pop()
                    break
        
        # Show all branches         
        self.treeWidget.expandAll()  
    
    @waiting_effects
    def scanRemote(self, arg=None):
        """
        Search for remote devices on a network and list them in Tree Widget window.
        If there are no devices found the Tree window is cleared or remaining remote devices.
        """   
        if self.setPcIpInLocalNetwork() == False:
            return
        # Search for remote devices for DEV-?
        if "DEV" in self.__selectedLocalDevice[0]:           
            devices = self.__ntd.doRemoteScan(self.__selectedLocalDevice[0]) 
            print("remote dev", devices)
            
            # # For testing only, remove when using real modems
            # if len(self.__remoteDevicesList)<1:
                # devices.append("DEV-99 00:04:00:00:00:00 140.110.1.28 ELEC MODEM") 
            # else:
                # self.__remoteDevicesList.pop()
                
         #   print("all devices", devices)
        
        # Did not find local devices    
        if devices is False:
            # Remove all remote devices from tree
            self.treeWidget.currentItem().takeChildren()
            
            # Display message window
            QApplication.restoreOverrideCursor()
            self.showdialog("Unable to find remote devices")
            return
                       
        else:
            newRemoteDevices = []
            oldList = self.__remoteDevicesList
            
            self.__remoteDevicesList = list((set(devices) - set(self.__localDevicesList)))
                   
            for dev in self.__remoteDevicesList:
                if dev not in oldList:  
                    print("new remote dev", dev)
                    newRemoteDevices.append(dev)                            
            self.addRemoteDevicesToTree(newRemoteDevices) 
            
    def addRemoteDevicesToTree(self, devicesList):        
        """
        Add new remote devices to tree widget
        Remove not existing devices from tree widget
        IN list of devices to be added
        """
    
        # Add all dev from list before updates     
        for dev in devicesList:              
            remoteDev = QtGui.QTreeWidgetItem(self.treeWidget.currentItem(), self.__localPc, 2)
            remoteDev.setText(0, dev)
       
        # Remove all non-existing local devices from tree   
        childRange = range(self.treeWidget.currentItem().childCount())       
        
        for chindex in childRange:            
            for index in range(self.treeWidget.currentItem().childCount()):              
                if unicode(self.treeWidget.currentItem().child(index).text(0)) not in str(self.__remoteDevicesList).strip():
                    self.treeWidget.currentItem().takeChild(index)                 
                    childRange.pop()
                    break
        
    @waiting_effects
    def printInfo(self, device):
        """
        Print eth and fifo details in "Device Details" window
        """
        
        # Obtain type of selected device and open correct window
        if device == None:
            return
        devType = device.type()
        self.stackedWidget.setCurrentIndex(devType)
     
        # Local Device is type 1
        if devType == 1:
            # Obtain local device name "DEV-?"
            self.__selectedLocalDevice = unicode(device.text(0)).split(' ', 3)
            
            selected = self.__selectedLocalDevice
  #          print(selected)
        elif devType == 2:
            # Obtain remote device name "DEV-?"
            self.__selectedRemoteDevice = unicode(device.text(0)).split(' ', 3)
            selected = self.__selectedRemoteDevice
                      
        else:
            selected = "None"
            return
                  
        if "DEV" in selected[0]:           
            results = self.__ntd.do_print(unicode(selected[0]))
         #   print results
            self.updateWindow(devType, results)
        else:
            #print("clear window")
            self.clearWindow(devType)
    

    def updateWindow(self, type, details):
        
        if details:
            if type == 1:
                lineSplited = details.splitlines()
                #print(lineSplited)
                for index, line in enumerate(lineSplited):
                   # print (line)
                    #print(index)
                    if "eth0" in line:
                        splited = line.split()
                        tmp = "".join(splited[1])
                        self.lineEditLocalEth0Ip.setText(tmp)
                        tmp = "".join(splited[2])
                        self.lineEditLocalEth0MacAddress.setText(tmp)
                        tmp = "".join(splited[4])
                        self.lineEditLocalEth0Mask.setText(tmp) 
                   
                    elif "fifo0" in line:
                        splited = line.split()
                        tmp = "".join(splited[1])
                        self.lineEditFifo0IpAddress.setText(tmp)
                        tmp = "".join(splited[2])
                        self.lineEditLocalFifo0MacAddress.setText(tmp)
                    
                    elif "fifo1" in line:
                        splited = line.split()
                        tmp = "".join(splited[1])
                        self.lineEditFifo1IpAddress.setText(tmp)
                        tmp = "".join(splited[2])
                        self.lineEditLocalFifo1MacAddress.setText(tmp)   
                     
                    elif line.strip().startswith("Route"):
                        i = index+4     
                        text = ""
                        while len(lineSplited[i].strip()) != 0:
                            text += lineSplited[i]+"\n"                            
                            i +=1 
                        #print(text)
                        self.textEditLocalRoute.setText("\n"+text)    
                    
                    elif line.strip().startswith("Backup"):
                        i = index+4     
                        text = ""
                        while len(lineSplited[i].strip()) != 0:
                            text += lineSplited[i]+"\n"                            
                            i +=1 
                        #print(text)
                        self.textEditLocalBackRoute.setText("\n"+text) 
                        
            elif type == 2:
                lineSplited = details.splitlines()
                #print(lineSplited)
                for index, line in enumerate(lineSplited):
                   # print (line)
                    #print(index)
                    if "eth0" in line:
                        splited = line.split()
                        tmp = "".join(splited[1])
                        self.lineEditRemoteEth0Ip.setText(tmp)
                        tmp = "".join(splited[2])
                        self.lineEditRemoteEth0MacAddress.setText(tmp)
                        tmp = "".join(splited[4])
                        self.lineEditRemoteEth0Mask.setText(tmp) 
                   
                    elif "fifo0" in line:
                        splited = line.split()
                        tmp = "".join(splited[1])
                        self.lineEditRemoteFifo0IpAddress.setText(tmp)
                        tmp = "".join(splited[2])
                        self.lineEditRemoteFifo0MacAddress.setText(tmp)
                    
                    elif "fifo1" in line:
                        splited = line.split()
                        tmp = "".join(splited[1])
                        self.lineEditRemoteFifo1IpAddress.setText(tmp)
                        tmp = "".join(splited[2])
                        self.lineEditRemoteFifo1MacAddress.setText(tmp)   
                     
                    elif line.strip().startswith("Route"):
                        i = index+4     
                        text = ""
                        while len(lineSplited[i].strip()) != 0:
                            text += lineSplited[i]+"\n"                            
                            i +=1 
                        #print(text)
                        self.textEditRemoteRoute.setText("\n"+text)    
                    
                    elif line.strip().startswith("Backup"):
                        i = index+4     
                        text = ""
                        while len(lineSplited[i].strip()) != 0:
                            text += lineSplited[i]+"\n"                            
                            i +=1 
                        #print(text)
                        self.textEditRemoteBackRoute.setText("\n"+text)              
        
    def clearWindow(self, type):
            if type == 1:              
                self.lineEditLocalEth0Ip.clear()
                self.lineEditLocalEth0MacAddress.clear()                                
                self.lineEditFifo0IpAddress.clear()                
                self.lineEditLocalFifo0MacAddress.clear()                      
                self.lineEditFifo1IpAddress.clear()               
                self.lineEditLocalFifo1MacAddress.clear()  
                self.textEditLocalRoute.clear()
                self.textEditLocalBackRoute.clear()
            elif type == 2:
                self.lineEditRemoteEth0Ip.clear()
                self.lineEditRemoteEth0MacAddress.clear()                                
                self.lineEditRemoteFifo0IpAddress.clear()                
                self.lineEditRemoteFifo0MacAddress.clear()                      
                self.lineEditRemoteFifo1IpAddress.clear()               
                self.lineEditRemoteFifo1MacAddress.clear()  
                self.textEditRemoteRoute.clear()
                self.textEditRemoteBackRoute.clear()
            

    @waiting_effects
    def xmlConfigDl(self, device, file):
        """
        Download configure .xml file to selected device
        Refresh details in local "Device Details" window
        """
        # Obtain type of selected device and open correct window  
        if device == None:
            # Display message window
            QApplication.restoreOverrideCursor()
            self.showdialog("None device selected")
            return
            
        # Local Device is type 1
        elif device.type() == 1:           
            if "DEV" in self.__selectedLocalDevice[0]:
                try:
                    self.__ntd.do_lcfg(self.__selectedLocalDevice[0],file)
                except ValueError as e:
                    QApplication.restoreOverrideCursor()
                    self.showdialog(e.args[0])
                    return
          #  time.sleep(5)
            # if self.scanLocal():
                # print("reset", self.__selectedLocalDevice[2])
                # self.reset(device) 
                
            # Wait 2s until IP is changed
            loop = QtCore.QEventLoop() 
            QtCore.QTimer.singleShot(1000, loop.quit)
            loop.exec_()   
            self.scanLocal()              
            return 
                
        if device.type() == 2:           
            parent = device.parent()
            # Obtain parent (local) device name "DEV-?" 
            parentSplited = unicode(parent.text(0)).split(' ', 3)
            
            if "DEV" in parentSplited[0]:
                try:                                               
                    self.__ntd.do_rcfg(parentSplited[0],unicode(self.lineEditRemoteFifo0MacAddress.text()), file)                 
                except ValueError as e:
                    QApplication.restoreOverrideCursor()
                    self.showdialog(e.args[0])
                    return
                
                self.treeWidget.setCurrentItem(parent, True)
                print("current item", unicode(self.treeWidget.currentItem().text(0)))
                self.scanRemote()
              #  self.treeWidget.setCurrentItem(parent, False)
              #  print("device after xmlDl", device.text(0))
             #   self.treeWidget.setCurrentItem(parent.child(0), True)
             #   self.treeWidget.setItemSelected(device, True)
                self.printInfo(parent)
                
              
             #   print("current item", unicode(self.treeWidget.currentItem().text(0)))
               
                                                 
    @waiting_effects
    def ftpConfigDl(self, device, fileName):
        """
        Download configure .ftp file to selected device
        Refresh details in local "Device Details" window
        """           
        if self.setPcIpInLocalNetwork() == False:
            return
        
        splited = unicode(device.text(0)).split(' ', 3)
         
        # Get ip address of selected device
        ipAddress = splited[2]   
        print("FTP connection to: ", ipAddress)
        destName = "config.h8"
        dlftp = None  

        #ftmp = "C:\Temp\DSPModemSoftware27\ElectricalInstalls\ElectricalInstalls\modem configs\config_cs.h8"
                     
        try:               
            file =  open(fileName, 'rb')
        except IOError as e:
            QApplication.restoreOverrideCursor()
            self.showdialog("File {0}: {1}". format(fileName, e.strerror))
            return
       
        try:              
            # Create connection 
            dlftp = FTP(ipAddress, timeout = 4)
            
            #DSP Modem does not support passive mode
            dlftp.set_pasv(False)         
           
            dlftp.login(user='kop', passwd='kop')           
            result = dlftp.storlines('STOR ' + destName, file)           
      
        except socket.timeout:
            QApplication.restoreOverrideCursor()
            self.showdialog("Unable to connect with IP {0}. \nReset device and try again.". format(ipAddress))
            return 
        except IOError as e:
            if dlftp != None:
                dlftp.quit()
            QApplication.restoreOverrideCursor()
            self.showdialog("FTP connection error({0}): {1}. \nReset device and try again.". format(e.errno, e.strerror))
            return 
            
        self.scanLocal()
           # print("reset", self.__selectedLocalDevice[2])
           # self.reset(device) 
        self.printInfo(device)  

    @waiting_effects
    def reset(self, device):
                                            
        if self.setPcIpInLocalNetwork() == False:
            return
            
        if device == None:
            return
        elif device.type()== 1:
            network = "eth0"
        elif device.type() == 2:
            network = "fifo0"
        else:
            return 
            
        selected = unicode(device.text(0)).split(' ', 1)

        if not self.__ntd.reset(selected[0], network):
            QApplication.restoreOverrideCursor()
            self.showdialog("Unable to reset device %s" %selected[0])
        

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
    app.setOrganizationName("AS")
    app.setOrganizationDomain("as.co.uk")
    app.setApplicationName("Modem Config")
    qtApp = MyQtApp()
    qtApp.show()
    app.exec_()

if __name__ == '__main__':
    mainFunc()