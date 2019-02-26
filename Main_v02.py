from PyQt4 import QtCore, QtGui, Qt
from PyQt4.QtGui import QApplication, QCursor

from netdisc import netdisc
from pccontrol import pccontrol
from ftplib import FTP

import socket 
import time
import treegui_v02 as gui

#temp text

class MyQtApp(gui.Ui_MainWindow, QtGui.QMainWindow):

    __ntd = netdisc() # object class netdisc
    
    __localPc = None
    __localDevicesList = []#"Dev10 24323, fdsfs, fsdfs, fssdf"\
                            #, "Dev1 54881 dsfdf gsdjkls ds;djfk sdlkf;"\
                           # ,"TestDEV-8: 00:04:00:00:00:00 140.10.10.2 ELEC MODEM 247 00:02:00:00:00:00 192.168.0.150"]  # Global list to hold all discovered local devices                             
    __remoteDevicesList = []   # Global list to hold all discovered remote devices
    __selectedLocalDevice = None  # Global variable for selected local device 
    __selectedRemoteDevice = None  # Global variable for selected global device 
    __localConfigXmlFile = None   # Configuration .xml File for local device
    __remoteConfigXmlFile = None   # Configuration .xml File for remote device
    __localConfigFtpFile = None   # Configuration .ftp File for local device
    __remoteConfigFtpFile = None   # Configuration .ftp File for remote device
    __ipPcDetails = {"mac": "0", "ip": "0", "mask": "0", "gateway": "0"}
  
    __testList = ["Dev10 24323, fdsfs, fsdfs, fssdf"\
                            , "Dev1 54881 dsfdf gsdjkls ds;djfk sdlkf;"\
                            ,"TestDEV-8: 140.10.10.2 ELEC MODEM"]  
    __deviceType = {"PC":0, "local":0, "remote":2}
    def __init__(self):
        super(MyQtApp, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Network Scanner -  Build 02")     
        self.initTree()
        #self.treeWidget.itemClicked.connect(self.showWidgetDetails)
        self.stackedWidget.setCurrentIndex(0)
        self.pushButtonPc.clicked.connect(self.scanLocal)
        self.pushButtonLocalXmlBrowse.clicked.connect(self.browseLocalXmlFolder)
        self.pushButtonLocalXmlApply.setEnabled(False)
        self.pushButtonLocalFtpBrowse.clicked.connect(self.browseLocalFtpFolder)
        self.pushButtonLocalFtpApply.setEnabled(False)
        self.pushButtonLocalXmlApply.clicked.connect(lambda: self.xmlConfigDl(self.__selectedLocalDevice, self.__localConfigXmlFile))
        self.pushButtonLocalFtpApply.clicked.connect(lambda: self.ftpConfigDl(self.__selectedLocalDevice, self.__localConfigFtpFile))
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
        self.pushButtonScanRemote.clicked.connect(self.scanRemote)
    
    def waiting_effects(function):
        def new_function(*args, **kwargs):
            QApplication.setOverrideCursor(QCursor(QtCore.Qt.WaitCursor))
            try:
                function(*args, **kwargs)
            except ValueError as e:
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
     #   pcIpAddress = self.__ntd.get_IP()
        self.__localPc = QtGui.QTreeWidgetItem(['Local PC '])
        self.treeWidget.addTopLevelItem(self.__localPc)
      #  self.lineEditPcPhysicalAddress.clear()
      #  self.lineEditPcPhysicalAddress.setText((unicode(self.__ntd.get_MAC())))
      #  self.lineEditPcIpAddress.setText(unicode(pcIpAddress))
      #  self.lineEditPcSubnetMask.setText(unicode(self.__ntd.get_SubnetMask()))
      #  self.lineEditPcDefaultGateway.setText(unicode(self.__ntd.get_DefaultGateway()))
        self.refreshPcIpDetails()
        self.stackedWidget.setCurrentIndex(0)
        self.treeWidget.itemClicked.connect(lambda: self.printInfo(self.treeWidget.currentItem()))
      
        
        #self.addLocalDevicesToTree(self.__localDevicesList) #only for test purpose
        
    def pcDetals(self):
        print "pc details"

    
    def browseLocalXmlFolder(self):
        """
        Select a config file for local device after button Browse is clicked
        and display filer path in text field
        """
        # Set file filter
        filter = "xml(*.xml)"
        
        # Obain the selected .xml file
        self.__localConfigXmlFile = str(QtGui.QFileDialog.getOpenFileName(None, "", "", filter))
        
        # Show path to .xml file in Text Window
        self.lineEditLocalXmlBrowse.setText(self.__localConfigXmlFile)

        #Enable or disable "Apply" button
        if self.lineEditLocalXmlBrowse.text() != "":
            self.pushButtonLocalXmlApply.setEnabled(True)
        else:
            self.pushButtonLocalXmlApply.setEnabled(False)
            
    # def browseRemoteXmlFolder(self):
        # """
        # Select a config file for remote device after button Browse is clicked
        # and display filer path in text field
        # """
        # # Set file filter
        # filter = "xml(*.xml)"
        
        # # Obain the selected .xml file
        # self.__remoteConfigXmlFile = str(QtGui.QFileDialog.getOpenFileName(None, "", "", filter))
        
        # # Show path to .xml file in Text Window
        # self.lineEdit.setText(self.__remoteConfigXmlFile)

        # #Enable or disable "Update Local Device" button
        # if self.lineEdit.text() != "":
            # self.pushButton_4.setEnabled(True)
        # else:
            # pushButton_4.setEnabled(False)

    def browseLocalFtpFolder(self):
        """
        Select a config file for local device after button Browse is clicked
        and display filer path in text field
        """
        # Set file filter
        filter = "Config File(*.ftp;*.h8)"
        
        # Obain the selected .ftp file
        self.__localConfigFtpFile = str(QtGui.QFileDialog.getOpenFileName(None, "", "", filter))
        
        # Show path to .ftp file in Text Window
        self.lineEditLocalFtpBrowse.setText(self.__localConfigFtpFile)

        #Enable or disable "Apply" button
        if self.lineEditLocalFtpBrowse.text() != "":
            self.pushButtonLocalFtpApply.setEnabled(True)
        else:
            self.pushButtonLocalFtpApply.setEnabled(False)
            
    # def browseRemoteFtpFolder(self):
        # """
        # Select a config file for remote device after button Browse is clicked
        # and display filer path in text field
        # """
        # # Set file filter
        # filter = "xml(*.xml)"
        # self.__remoteConfigFtpFile = str(QtGui.QFileDialog.getOpenFileName(None, "", "", filter))
        # # print(selectedFile)
        # self.configFtpRemoteFileBrowse.setText(self.__remoteFtpConfigXmlFile)

        # #Enable or disable "Update Local Device" button
        # if self.configFtpRemoteFileBrowse.text() != "":
            # self.updateRemoteFtpButton.setEnabled(True)
        # else:
            # self.updateRemoteFtpButton.setEnabled(False)
    
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
        self.__ntd.set_pcXML(self.__ipPcDetails["mac"], self.__ipPcDetails["ip"],\
                            self.__ipPcDetails["mask"])
        
    def editPcIpDetails(self):
        print("edit pc ip")
       
        self.pushButtonApplyPcIp.setEnabled(True)
      #  self.pushButtonApplyPcIp.setAutoDefault(True)
        self.pushButtonApplyPcIp.setDefault(True)
        
        
        regExp = QtCore.QRegExp('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        validator = QtGui.QRegExpValidator(regExp)
        self.lineEditPcIpAddress.setValidator(validator)
        self.lineEditPcSubnetMask.setValidator(validator)
        self.lineEditPcDefaultGateway.setValidator(validator)
        #self.pushButtonApplyPcIp.setFocus()
    
    def applyPcIp(self):
       
        if not self.isIpCorrect(self.lineEditPcIpAddress):
            self.showdialog("Incorrect IP Address %s" %self.lineEditPcIpAddress.text())
        
        elif not self.isIpCorrect(self.lineEditPcSubnetMask):
            self.showdialog("Incorrect Subnet Mask %s" %self.lineEditPcSubnetMask.text())
        
        elif not self.isIpCorrect(self.lineEditPcDefaultGateway):
            self.showdialog("Incorrect Gateway Address %s" %self.lineEditPcDefaultGateway.text())
        
        else:
            print("set ip")
            # Update info in Tree Window
            self.__localPc.setText(0,  'Local PC ' + self.lineEditPcIpAddress.text())
        
            # Save new IP Details
            self.__ipPcDetails["ip"] = unicode(self.lineEditPcIpAddress.text())
            self.__ipPcDetails["mask"] = unicode(self.lineEditPcSubnetMask.text())
            self.__ipPcDetails["gateway"] = unicode(self.lineEditPcDefaultGateway.text())
            self.__ntd.setIp(self.__ipPcDetails["mac"], self.__ipPcDetails["ip"],\
                           self.__ipPcDetails["mask"], self.__ipPcDetails["gateway"])
          
            self.framePcAddressDetails.focusWidget().clearFocus()
            self.pushButtonApplyPcIp.setEnabled(False)
        
    
    def cancelIpChanges(self):
        print("cancel pc ip changes")
       # self.refreshPcIpDetails()
          # Update info in TCP/IP Window
        self.lineEditPcPhysicalAddress.setText(self.__ipPcDetails["mac"])
        self.lineEditPcIpAddress.setText(self.__ipPcDetails["ip"])
        self.lineEditPcSubnetMask.setText(self.__ipPcDetails["mask"])
        self.lineEditPcDefaultGateway.setText(self.__ipPcDetails["gateway"])
        self.pushButtonApplyPcIp.setEnabled(False)
        

    def isIpCorrect(self, qline):
    
        pieces = unicode(qline.text()).split('.')
            
        try:
            if len(pieces) != 4: 
                #self.showdialog("Incorrect IP Address %s" %ustr)
                qline.selectAll()
                qline.setFocus()
                return False
            for item in pieces:
                if not 0 <= int(item) <= 255:
                   # self.showdialog("Incorrect IP Address %s" %ustr)
                    qline.selectAll()
                    qline.setFocus()
                    return False
        except ValueError:
            qline.selectAll()
            qline.setFocus()
            return False
        
        return True 
        
    @waiting_effects
    def scanLocal(self, arg=None):
        """
        Search for local devices on a network and list them in Tree Widget window.
        If there are no devices found the Tree window is cleared.
        """
        # Search for local devices
        devices = self.__ntd.doLocalScan()       
    
       # Did not find local devices    
        if devices is False:
            # Remove all devices from tree
            self.__localPc.takeChildren()
            # Display message window
            QApplication.restoreOverrideCursor()
            self.showdialog("Unable to find local devices")
            
            # except ValueError as e:
                # QApplication.restoreOverrideCursor()
                # self.showdialog(e.args[0])
            return
                       
        else:
            newLocalDevices = []
            oldList = self.__localDevicesList
            self.__localDevicesList = devices
                   
            for dev in self.__localDevicesList:
                if dev not in oldList:                                 
                    newLocalDevices.append(dev)
                       
            self.addLocalDevicesToTree(newLocalDevices)            

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
                    childRange.pop(1)
                    break
        
        # Show all branches         
        self.treeWidget.expandAll()  
    
    @waiting_effects
    def scanRemote(self, arg=None):
        """
        Add new devices to tree widget
        Remove not existing devices from tree widget
        IN list of devices to be added
        """
        print("scan remote pressed")
    
    @waiting_effects
    def printInfo(self, device):
        """
        Print eth and fifo details in "Device Details" window
        """
      
        # Obtain type of selected device and open correct window
        devType = device.type()
        self.stackedWidget.setCurrentIndex(devType)
     
        # Local Device is type 1
        if devType == 1:
            # Obtain local device name "DEV-?"
            self.__selectedLocalDevice = unicode(device.text(0)).split(' ', 3)
            
            selected = self.__selectedLocalDevice
            print(selected)
       
        else:
            selected = "None"
            # # Obtain remote device name "DEV-?"
            # self.selectedRemoteDevice = dev.split(' ', 1)
            # selected = self.selectedRemoteDevice
                  
        if "DEV" in selected[0]:           
            results = self.__ntd.do_print(unicode(selected[0]))
            #print results
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


    @waiting_effects
    def xmlConfigDl(self, device, configFile):
        """
        Download configure .xml file to selected device
        Refresh details in local "Device Details" window
        """
        if "DEV" in device[0]:
            try:
                self.__ntd.do_lcfg(device[0],configFile)
            except ValueError as e:
                QApplication.restoreOverrideCursor()
                self.showdialog(e.args[0])
                return

            self.scanLocal()
            self.printInfo(self.treeWidget.currentItem())  
                
    @waiting_effects
    def ftpConfigDl(self, device, fileName):
        """
        Download configure .ftp file to selected device
        Refresh details in local "Device Details" window
        """      
        # Get ip address of selected device
        ipAddress = device[2]   
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
            dlftp = FTP(ipAddress, timeout = 10)
            
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
        self.printInfo(self.treeWidget.currentItem())  
        print("Ftp File download completed")

    @waiting_effects
    def reset(self, device):
        selected = unicode(device.text(0)).split(' ', 1)

        if not self.__ntd.reset(selected[0]):
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
    qtApp = MyQtApp()
    qtApp.show()
    app.exec_()

if __name__ == '__main__':
    mainFunc()
