from __future__ import print_function
import wmi


class pccontrol:
      
    def __init__(self):
        self.localInterfaces = []
        self.getNicDetis()
    
    
    def getNicDetis(self):
        """
        Obtain MAC, IP Mask and Default Gateway from host PC
        """
        connection = wmi.WMI () 
        for interface in connection.Win32_NetworkAdapterConfiguration (IPEnabled=1):
            for ip in interface.IPAddress:            
                self.localInterfaces.append(nic(interface.MACAddress, interface.IPAddress, interface.IPSubnet, interface.DefaultIPGateway))
        else:
            self.localInterfaces.append(nic())
    def getMacAddresses(self):
        """
        Obtain MAC addresses of host PC
        OUT: List of MAC addresses of active NIC
        """
        macAddresses = []     
        for i in self.localInterfaces:            
            macAddresses.append(i.macAddress)
            return macAddresses
      
    def getIp(self, mac):
        """
        Obtain IP address for provided MAC Address
        IN: MAC Address as string
        OUT: IP address
        """          
        for i in self.localInterfaces:
            if i.macAddress == mac:
                return i.ipAddress
               
    def getSubnet(self, ip):
        """
        Obtain subnet mask for provided IP address
        IN: IP Address as string
        OUT: Subnet Mask
        """  
        for i in self.localInterfaces:
            for index, t in enumerate(i.ipAddress):
                if t == ip:
                    return i.subnetMask[index]
                
    def getDefaultGateway(self, ip):
        """
        Obtain default gateway for provided IP address
        IN: IP Address as string
        OUT: Default Gateway
        """  
        for i in self.localInterfaces:
            for index, t in enumerate(i.ipAddress):
                if t == ip:                       
                    return i.defaultGateway[index]
              
    
    def setIp(self, mac, ip = None, subnetmask = "255.255.255.0", gateway = None):
        """
        NIC with MACAddress is set to IP address as provided value ip. 
        If ip is None, IP address is set automatically, DHCP is enabled      
        IN: macAddress, ip and subnetMask as string. Only MACAddress is mandatory
        OUT: True
        Raise exception if not able to execute command
        """            
        try:  
            connection = wmi.WMI () 
            for interface in connection.Win32_NetworkAdapterConfiguration (IPEnabled=1):
                if interface.MACAddress == mac:                     
                    if ip is None:
                        interface.EnableDHCP() 
                        self.getNicDetis()
                        
                    # Set IP address, subnetmask and default gateway
                    # Note: EnableStatic() and SetGateways() methods require *lists* of values to be passed
                    else:                        
                        interface.EnableStatic(IPAddress=[ip],SubnetMask=[subnetmask])
                        if gateway is True:
                            interface.SetGateways(DefaultIPGateway=[gateway])
                        else:
                            interface.SetGateways(DefaultIPGateway=["0.0.0.0"])
                    
                        self.getNicDetis()            
                                           
        except Exception as e:
            return e
    
   
 #********************** End of class pccontrol ********************************          

 
class nic:
    
    def __init__(self, mac=None, ip=None, mask=None, gateway=None):
        self.macAddress = mac
        self.ipAddress = ip
        self.subnetMask = mask
        self.defaultGateway = gateway        
                
 #********************** End of class nic ********************************            


if __name__ == "__main__": 
    import time
    def temp(mac, ip=None):
        hostPC.setIp(mac, ip)
        hostPC.getNicDetis()
        print (hostPC.getIp(mac))        
     
     
    hostPC = pccontrol()
    print (hostPC.getMacAddresses()[0])
    mac = hostPC.getMacAddresses()[0]
    hostPC.setIp(mac)
  #  time.sleep(8)
  #  print (hostPC.getIp(mac))
  #  print (hostPC.getSubnet("144.179.171.66"))
    print (hostPC.getDefaultGateway("144.179.171.66"))
   # temp(mac)


            


    #print (hostPC.get_IP("CC:3D:82:85:BC:77"))
    #print (hostPC.get_IP("48:0F:CF:69:3B:2F"))
    #print (hostPC.get_MACIP())  
    #print(hostPC.set_IP(u"48:0F:CF:69:3B:2F", u"192.168.1.1", u"255.255.255.0"))
    #print(hostPC.set_IP("48:0F:CF:69:3B:2F"))

        
    #print(set_IP(u"48:0F:CF:69:3B:2F", u"192.168.1.114", u"255.255.255.0"))

    # c = wmi.WMI () 
    # interface_name = []
    # mac_addresses = []
    # ip_addresses = []
    # mac_ip = {}

    # network_devices = c.Win32_NetworkAdapterConfiguration (IPEnabled=1)
    # if len(network_devices) == 0:
        # print("No active network devices")

    # if len(network_devices) > 1:
        # print ("More than one network device is active")
        
    # nic = network_devices[0]
    # print (nic)
    # for ip_address in nic.IPSubnet:
        # print (ip_address)
        # ip_addresses.append(ip_address)
           
    # mac_ip[nic.MACAddress] = ip_addresses
    # print(mac_ip)
        
    # for key in mac_ip:
        # if len(mac_ip[key])>1:
            # print ("mac address: %s has more than one IP address: %s" %(key, mac_ip[key]))
    # mac_ip
    # ip_addresses
