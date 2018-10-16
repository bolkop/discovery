from __future__ import print_function
import wmi


class pccontrol:
    
    
    def __init__(self):
        None
    
    
    def get_MACIP(self):
        """
        Obtain MAC addresses and associated IP addresses for host PC
        OUT: Dictionary of MAC addresses as key and IP addresses as value. Only active NIC are searched
        Raise exception if not able to execute command
        """
        macIP = {}
        ipAddresses = []
        try:
            connection = wmi.WMI () 
            for interface in connection.Win32_NetworkAdapterConfiguration (IPEnabled=1):
                for ip in interface.IPAddress:
                    ipAddresses.append(ip)
                macIP[interface.MACAddress] = ipAddresses
            return macIP
        except Exception as e:
            return e
    
    def get_MAC(self):
        """
        Obtain MAC addresses of host PC
        OUT: List of MAC addresses of active NIC
        Raise exception if not able to execute command
        """
        #macAddresses = []
        try:
            #connection = wmi.WMI () 
            #network_devices = connection.Win32_NetworkAdapterConfiguration (IPEnabled=1)
            # if len(network_devices) == 0:
                # raise ValueError("No active network devices")
            
            # if len(network_devices) > 1:
                # raise ValueError("More than one network device is active")
            
          
            # for interface in connection.Win32_NetworkAdapterConfiguration (IPEnabled=1):
                # macAddresses.append(interface.MACAddress)
                
            #print (macAddresses)
            
            return self.get_MACIP().keys()
        except Exception as e:
            return e
    
    
        
    def get_IP(self, macAddress):
        """
        Obtain IP address for provide macAddress
        IN: macAddress as string
        OUT: List of IP addresses
        Raise exception if not able to execute command
        """
        #ipAddresses = []
        try:
            # connection = wmi.WMI ()     
            # for interface in connection.Win32_NetworkAdapterConfiguration (IPEnabled=1):
                # print(interface.MACAddress)
                # if interface.MACAddress == macAddress:
                    # for ip in interface.IPAddress:
                        # ipAddresses.append(ip)
            
            # Obtain all active MAC addresses            
            macIP = self.get_MACIP()
            for mac in macIP.keys():
            # Return all IP addresses for the matching MAC address   
                if mac == macAddress:    
                    return macIP[mac]
        except Exception as e:
            return e
    
    def set_IP(self, mac, ip = None, subnetmask = None, gateway = None):
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
                print(interface.MACAddress)
                if interface.MACAddress == mac:       
                    if ip is None:
                        return interface.EnableDHCP()                                                        
                    # Set IP address, subnetmask and default gateway
                    # Note: EnableStatic() and SetGateways() methods require *lists* of values to be passed
                    else:
                        interface.EnableStatic(IPAddress=[ip],SubnetMask=[subnetmask])
                        if gateway is True:
                            interface.SetGateways(DefaultIPGateway=[gateway])
                        else:
                            interface.SetGateways(DefaultIPGateway=["0.0.0.0"])
                    return self.get_IP(mac)
                    
        except Exception as e:
            return e
    
 #********************** End of class pccontrol ********************************          

 
#hostPC = pccontrol()
#print (hostPC.get_MAC())

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
# for ip_address in nic.IPAddress:
  # #  print (ip_address)
    # ip_addresses.append(ip_address)
       
# mac_ip[nic.MACAddress] = ip_addresses
# print(mac_ip)
    
# for key in mac_ip:
    # if len(mac_ip[key])>1:
        # print ("mac address: %s has more than one IP address: %s" %(key, mac_ip[key]))
# mac_ip
# ip_addresses