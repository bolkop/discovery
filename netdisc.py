from __future__ import print_function
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pccontrol import pccontrol
import textwrap
import time
import sys
import os
from datetime import datetime


#
# Class for scanning network using netdisc
#
class netdisc:
    __pcControl = pccontrol()

    def __init__(self):
        # Check PC MAC and IP address. 
        self.MacAddress = self.get_MAC()
        print(self.MacAddress)
        self.IpAddress = self.get_IP()
        print(self.IpAddress)
        self.subnetMask = self.get_SubnetMask()
        print (self.subnetMask)
        self.defaultGateway = self.get_DefaultGateway()
        
        # Update 00000000000.xml file with PC MAC and IP address       
        self.set_pcXML(self.MacAddress, self.IpAddress, self.subnetMask)

    def __do_action(self, cmd1, cmd2="", cmd3="", cmd4=""):
        """
        Execute the netdisc command
        Return response from netdisc after command is executed
        IN: cmd as a string:
        OUT: netdisc response as string
        """
        cmd = "C:\\ModemConfig\\netdisc" + " " + cmd1 + " " + cmd2 +" "+ cmd3 +" "+cmd4
        with tempfile.TemporaryFile() as tempf:
            proc = subprocess.Popen(cmd, stdout=tempf)
            proc.wait()
            tempf.seek(0)
            return tempf.read()

    def do_start(self):
        """
        Start netdisc
        OUT: True if successfull
        Raise exception if not able to start netdisc
        """
        # Response from netdisc
        try:
            readback = self.__do_action("start")
        except Exception as e:
            return e

        if "running" in readback:
            return True
        else:
            return False
           # raise Exception("Can't start netdisc")

    def do_stop(self):
        """
        Stop netdisc
        OUT: True if successfull
        Raise exception if not able to stop netdisc
        """
        # Response from netdisc
        try:
            readback = self.__do_action("stop")
        except Exception as e:
            return e
        if "stopped" in readback or "not running" in readback:
            return True
        else:
            return False
            #raise Exception("Can't stop netdisc")

    def do_ldisc(self):
        """
        Send a Local-Discovery
        OUT: True if successfull
        Raise exception if not able to execute command
        """
        # Response from netdisc
        readback = self.__do_action("ldisc")
        if "Sent LOCAL-DISCOVERY" in readback:
            return True
            # if "Received LOCAL-DISCOVERY" in readback:
            # return True
            # else:
            # raise Exception("There are no devices discovered")
        else:
            return False
            #raise Exception("Local discovery not sent")

    def do_rdisc(self, device):
        """
        Send a Remote-Discovery using device name and "fifo0" 
        IN: devie as string
        OUT: True if successfull
        Raise exception if not able to execute command
        """
            
        # Response from netdisc
        readback = self.__do_action("rdisc", device.upper(), "fifo0")
        if "sent REMOTE-DISCOVERY" in readback:
            return True
            # if "Received DISCOVERY-REPLY" in readback:
                # return True
            # else:
                # raise Exception("There are no remote devices discovered")
        else:
            return False
            #raise ValueError("Remote discover not sent", readback)

    def do_lcfg(self, device, configFile):
        """
        Send a Local-Config
        IN: Device name (e.g. DEV-1 or IP address) and directory of config .xml file
        OUT: True if successfull
        Raise exception if not able to execute command
        """
        try:
            configs = open(configFile, "rb")
        except:
            raise ValueError("Cannot open the config file")

        # Response from netdisc
        readback = self.__do_action("lcfg", device, "'"+configFile+"'")

        if "Sent LOCAL-CONFIG" in readback:
            # if "Received CONFIG-ACK" in readback:
            #     return True
            # else:
            #     raise Exception("No response from local device")
            return True
        else:
            raise ValueError("Config file not sent", readback)

    def do_rcfg(self, device, macAddress, configFile):
        """
        Send a Remote-Config
        IN: Device name (e.g. DEV-1 or IP address), MAC address and directory of config .xml file
        OUT: True if successfull
        Raise exception if not able to execute command
        """
        try:
            configs = open(configFile, "rb")
        except:
            raise ValueError("Cannot open the config file")
        # Response from netdisc
        readback = self.__do_action("rcfg", device.upper(), macAddress, "'"+configFile+"'")
        if "sent REMOTE-CONFIG" in readback:
            if "Received CONFIG-ACK" in readback:
                return True
            else:
                raise Exception("No response from local device")
        else:
            raise ValueError("Config file not sent", readback)

    def do_delete(self):
        """
        Delete devices from devices dir
        OUT: True if successfull
        Raise exception if not able to execute command
        """
        # Response from netdisc
        readback = self.__do_action("del")
        if "Devices deleted" in readback:
            return True
        else:
            return False
            #raise Exception("Can't delete devices")

    def do_print(self, dev=None):
        """
        Prints a summary of discovered devices or a single devices configuration
        OUT: List of discovered devices
        """

        #This is only for testing
        tmpDev = "TestDEV-8: 00:04:00:00:00:00 140.10.10.2 ELEC MODEM 247 00:02:00:00:00:00 192.168.0.150 \n" \
                 "TestDEV-7: 00:aa:de:00:00:52 192.168.0.150 ELEC MODEM 246 ff:ff:ff:ff:ff:ff 255.255.255.255"
        
        tmpSummary = "Device Summary - DEV-7 192.168.0.150 00:aa:de:00:00:52 \n" \
                     "Interfaces: Name IP Address MAC Address \n" \
                     "eth0 192.168.0.150 00:aa:de:00:00:52 \n" \
                     "fifo0 140.10.10.1 00:02:00:00:00:00 \n" \
                     "fifo1 140.11.10.1 00:02:00:00:00:00"
        
        # Check the modified time has changed for the devlist.xml file
        c = 0
        while c<8:
            try:
                newTime = (os.path.getmtime('C:\\ModemConfig\\devlist.xml'))
               
                # Extra time to make sure the devlist.xml file is fully modified    
                time.sleep(0.5)
                break
                
            except Exception:
                time.sleep(0.1)
                c += 1
                      
        if dev is None:

            # #Get info about discovered devices
            # readback = self.__do_action("print")
            
            # #Wait for readback for less than 2s
            # t1 = datetime.now()
            # while len(readback)== 0:
                # if (datetime.now() - t1).seconds > 1:
                    # break
            # #    time.sleep(0.8)
                # readback = self.__do_action("print")
            
            # Send command netdisc print
           
           # time.sleep(2)
          # print(os.path.getmtime("C:\\ModemConfig\\devlist.xml"))
            readback = self.__do_action("print")   
            
            
            # Check if any devices was discovered
            if "DEV" in readback:

                # Remove four first lines; only list of discovered devices will be shown
                devicesList = '\n'.join(readback.split('\n')[4:])
                
                # Remove indent from text
                devicesList = textwrap.dedent(devicesList)
                return devicesList
            else:
                return False #tmpDev #False

        else:
            readback = self.__do_action("print", dev)
          #  print(readback)
            if "eth" in readback:
                return readback
            else:
                return False #tmpSummary #False

    def get_MAC(self):
        """
        Obtain MAC address of host PC, checks number of active NIC and raise an error if more than one or none
        OUT: MAC address of active NIC
        Raise exception if not able to execute command
        """
        
        # Collect MAC addreses from all active NIC
        macList = self.__pcControl.getMacAddresses()
        macCount = len(macList)
        
        # Check how many is active
        if macCount >1:
            raise ValueError("More than one NIC is active")
        elif macList[0] == None:
            raise ValueError("There is no active Network Interface Controllers")
        else:
            return macList[0]       

    def get_IP(self):
        """
        Obtain IP address for provide macAddress
        IN: macAddress as string
        OUT: IP address
        Raise exception if not able to execute command
        """
   
        # Obtain IP addresses from active MAC address
        ipList = self.__pcControl.getIp(self.MacAddress) 
            
        # Check is there at least one IP address   
        if ipList!= None:
            return ipList[0]
        else:
            raise ValueError("There is no IP address")
            
    def get_SubnetMask(self):
        
        ip = self.get_IP()
        return self.__pcControl.getSubnet(ip)
    
    def get_DefaultGateway(self):
        ip = self.get_IP()
        return self.__pcControl.getDefaultGateway(ip)

    def set_pcXML(self, mac, ip=None, mask=None):
        """
        Set MAC and IP in the 000000000.xml file. If ip is None, the ip address is not changed
        IN: mac as string, ip as string
        OUT: True/False
        Raise exception if not able to execute command
        """
        tree = ET.parse('C:\\ModemConfig\\000000000000.xml')
        root = tree.getroot()
        name = None

        # Change MAC address within 000000000000.xml file
        for inface in root.iter('INTERFACE'):
            name = inface.find('NAME').text
            if name == 'Eth0':
                inface.find('MAC').text = mac

                # Change IP address if is provided as ip
                if ip != None:
                    inface.find('ADDRESS').text = ip

                # Change netmask if is provided as mask
                if mask != None:
                    inface.find('NETMASK').text = mask

                # Save changes to .xml file
                tree.write('C:\\ModemConfig\\000000000000.xml')
                return True

        # MAC address not change and return False
        return False

    def doLocalScan(self):
        """
        Scan local network for any devices
        IN: None
        OUT: List of found devices class device
        Raise exception if not able to execute command
        """
        # Stop netdisc        
        self.do_stop()
        
        # Start nedtisc
        self.do_start()
        
        # Delete remaining discovered devices 
        self.do_delete()
        
        # Scan for local devices
        self.do_ldisc()    
        
        # Return list of found devices
        return self.do_print()

    def doRemoteScan(self, device):
        """
        Scan local network for any devices
        IN: None
        OUT: List of found devices class device
        Raise exception if not able to execute command
        """              
        # Scan for local devices
        self.do_rdisc(device)    
        
        # Return list of found devices
        return self.do_print()
# ********************** End of class netdisc ********************************

class scanning:
    __localIP = None
    __localMAC = None
    __pcControl = pccontrol()

    def __init__(self):
        None
        # self.__localMAC = self.get_MAC()
        # self.__localIP = self.get_IP()

        # Set MAC address in 000000000000.xml file


# ********************** End of class scanning ********************************

class device:
    __name = None
    __macAddress = None
    __ipAddress = None
    __type = None

    # def __init__(self, xmlFile):
    # self.xmlFile = xmlFile

    def getName(self):
        return self.__name

    def get_MAC(self):
        return self.__macAddress

    def get_IP(self):
        return self.__ipAddress

    def get_Type(self):
        return self.__type

    def set_MAC(self, mac):
        self.__macAddress = mac

    def set_IP(self, ip):
        self.__ipAddress = ip

    def set_Type(self, type):
        self.__type = type


# ********************** End of class device ********************************
if __name__ == "__main__":
    # t = "Interfaces: Name IP Address MAC Address\n          eth0      192.168.0.150 00:aa:de:00:00:52\n         fifo0      140.10.10.1 00:02:00:00:00:00\n         fifo1      140.11.10.1 00:02:00:00:00:00"
    # for line in t.split('\n'):
    # if "fifo0" in line:

    # ipAddress = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line)
    # print(ipAddress)

    ##TEST##
    # try:
    netd = netdisc()
   # print(netd.doLocalScan())
   # netd.do_stop()
   # netd.do_start()
   # netd.do_start()

  #  netd.do_delete()

    #time.sleep(2)

   # netd.do_ldisc()
  #  time.sleep(2)
  #  dev = netd.do_print()
  #  print(dev)


    dev = netd.doLocalScan()
    print(dev)
   
# print(netd.do_stop())
# print(netd.do_start())
# netd.do_ldisc()
# print(netd.do_scan_network())

# print(netd.do_ldisc())
# #print (netd.do_lcfg("DEV-1", "C:\\ModemConfig\\CPSModemPIUA.xml"))
# #print (netd.do_lcfg("DEV-1", "C:\\ModemConfig\\CPSModemPIUA.xml"))
# print(netd.do_print())
# print (netd.do_stop())
# except Exception as e:
#     print(e)
