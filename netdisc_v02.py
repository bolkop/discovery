from __future__ import print_function
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pccontrol import pccontrol
import textwrap


#
# Class for scanning network using netdisc
#
class netdisc:
    # capturedLine = ""
    __pcIPAddress = None
    __pcMACAddress = None
    __pcControl = pccontrol()

    def __init__(self):
        # self.IP_address = None
        # self.MAC_address = None
        self.set_pcXML(self.get_MAC())

    def __do_action(self, cmd1, cmd2="", cmd3="", cmd4=""):
        """
        Execute the netdisc command
        Return response from netdisc after command is executed
        IN: cmd as a string:
        OUT: netdisc response as string
        """
        with tempfile.TemporaryFile() as tempf:
            proc = subprocess.Popen(["C:\\ModemConfig\\netdisc", cmd1, cmd2, cmd3, cmd4], stdout=tempf)

            proc.wait()
            tempf.seek(0)
            return tempf.read()
        # proc = subprocess.Popen(["C:\\ModemConfig\\netdisc", cmd1, cmd2, cmd3, cmd4], stdout=subprocess.PIPE,
        #                         stderr=subprocess.STDOUT,
        #                         bufsize=-1)
        #
        # for line in iter(proc.stdout.readline, ''):
        #     None
        #
        # # print (line)
        #
        # return line

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
            raise Exception("Can't start netdisc")

    def do_stop(self):
        """
        Stop netdisc
        OUT: True if successfull
        Raise exception if not able to stop netdisc
        """
        # Response from netdisc
        try:
            readback = self.__do_action("stop")
            # print(readback)
        except Exception as e:
            return e
        print(readback)
        if "stop" in readback or "not running" in readback:
            return True
        else:
            raise Exception("Can't stop netdisc")

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
            raise Exception("Local discovery not sent")

    def do_rdisc(self, device, interfaceName):
        """
        Send a Remote-Discovery
        IN: devie as string, interfaceName as string
        OUT: True if successfull
        Raise exception if not able to execute command
        """
        # Response from netdisc
        readback = self.__do_action("rdisc", device.upper(), interfaceName)
        if "sent REMOTE-DISCOVERY" in readback:
            if "Received DISCOVERY-REPLY" in readback:
                return True
            else:
                raise Exception("There are no remote devices discovered")
        else:
            raise ValueError("Remote discover not sent", readback)

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
        readback = self.__do_action("lcfg", device.upper(), configFile)
        if "sent LOCAL-CONFIG" in readback:
            if "Received CONFIG-ACK" in readback:
                return True
            else:
                raise Exception("No response from local device")
        else:
            raise ValueError("Config file not sent", readback)

    def do_rcfg(self, device, network, configFile):
        """
        Send a Remote-Config
        IN: Device name (e.g. DEV-1 or IP address), network name (e.g Fifo0 or MAC address) and directory of config .xml file
        OUT: True if successfull
        Raise exception if not able to execute command
        """
        try:
            configs = open(configFile, "rb")
        except:
            raise ValueError("Cannot open the config file")
        # Response from netdisc
        readback = self.__do_action("rcfg", device.upper(), network, configFile)
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
            raise Exception("Can't delete devices")

    def do_print(self, dev=None):
        """
        Prints a summary of discovered devices or a single devices configuration
        OUT: List of discovered devices
        """
        tmpDev ="   Network Device Discovery - Device Summary \n" \
                "   ----------------------------------------- \n" \
                "   Name Device MAC Device IP Dev Type Req Discovery MAC Discovery IP \n\n" \
                "   DEV-8: 00:04:00:00:00:00 140.10.10.2 ELEC MODEM 247 00:02:00:00:00:00 192.168.0.150 \n" \
                "   DEV-7: 00:aa:de:00:00:52 192.168.0.150 ELEC MODEM 246 ff:ff:ff:ff:ff:ff 255.255.255.255"
        
        tmpSummary = "Device Summary - DEV-7 192.168.0.150 00:aa:de:00:00:52 \n" \
                     "Interfaces: Name IP Address MAC Address \n" \
                     "eth0 192.168.0.150 00:aa:de:00:00:52 \n" \
                     "fifo0 140.10.10.1 00:02:00:00:00:00 \n" \
                     "fifo1 140.11.10.1 00:02:00:00:00:00"

        if dev is None:
            readback = self.__do_action("print")
            if "DEV" in readback:
                return readback
            else:
                tmpOutput = '\n'.join(tmpDev.split('\n')[4:])
                return textwrap.dedent(tmpOutput)
            
        else:
            readback = self.__do_action("print",dev)
            print (readback)
            if "eth" in readback:
                return readback
            else:
                return tmpSummary
        

    def get_MAC(self):
        """
        Obtain MAC address of host PC, checks number of active NIC and raise an error if more than one or none
        OUT: MAC address of active NIC
        Raise exception if not able to execute command
        """
        try:
            # Collect MAC addreses from all active NIC
            macList = self.__pcControl.get_MAC()
            macCount = len(macList)
            # Check how many is active
            if macCount > 1:
                raise ValueError("More than one NIC is active")
            elif macCount == 0:
                raise ValueError("There is no actie NIC")
            else:
                return macList[0]

        except Exception as e:
            return e

    def get_IP(self):
        """
        Obtain IP address for provide macAddress
        IN: macAddress as string
        OUT: IP address
        Raise exception if not able to execute command
        """

    None

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

    def do_localscan(self):
        """
        Scan local network for any devices
        IN: None
        OUT: List of found devices class device
        Raise exception if not able to execute command
        """
        self.do_start()
        self.do_delete()
        self.do_ldisc()
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
        None

    def get_MAC(self):
        None

    def get_IP(self):
        None

    def get_Type(self):
        None

    def set_MAC(self, mac):
        None

    def set_IP(self, ip):
        None

    def set_Type(self, type):
        None


# ********************** End of class device ********************************
if __name__ == "__main__":
# t = "Interfaces: Name IP Address MAC Address\n          eth0      192.168.0.150 00:aa:de:00:00:52\n         fifo0      140.10.10.1 00:02:00:00:00:00\n         fifo1      140.11.10.1 00:02:00:00:00:00"
# for line in t.split('\n'):
# if "fifo0" in line:

# ipAddress = re.findall( r'[0-9]+(?:\.[0-9]+){3}', line)
# print(ipAddress)

##TEST##
#try:
    netd = netdisc()
    print(netd.do_localscan())
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
