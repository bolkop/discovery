from __future__ import print_function
import wmi

__version__ = "2.0.0"

class pccontrol:
      
    def __init__(self):
        self.localInterfaces = []
        #self.getNicDetails()
    
    
    def getNicDetails(self):
        """
        Obtain MAC, IP Mask and Default Gateway from host PC
        """
        self.localInterfaces = []
        connection = wmi.WMI () 
        for interface in connection.Win32_NetworkAdapterConfiguration (IPEnabled=1):
            for ip in interface.IPAddress:            
                self.localInterfaces.append(nic(interface.MACAddress, interface.IPAddress, interface.IPSubnet, interface.DefaultIPGateway))
        else:
            self.localInterfaces.append(nic())
            
        return self.localInterfaces
        
    def getMacAddresses(self):
        """
        Obtain MAC addresses of host PC
        OUT: List of MAC addresses of active NIC
        """
        macAddresses = []     
        for i in self.localInterfaces:            
            macAddresses.append(i.macAddress)
            return macAddresses
        else:
            return ("0.0.0.0.0.0")
    def getIp(self, mac):
        """
        Obtain IP address for provided MAC Address
        IN: MAC Address as string
        OUT: IP address
        """          
        for i in self.localInterfaces:
            if i.macAddress == mac:
                return i.ipAddress
        
        else:
            return ("0.0.0.0")
               
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
        else:
            return ("255.255.255.255")
                
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
        else:
            return ("0.0.0.0")    
              
    
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
                        self.getNicDetails()
                        
                    # Set IP address, subnetmask and default gateway
                    # Note: EnableStatic() and SetGateways() methods require *lists* of values to be passed
                    else:                        
                        interface.EnableStatic(IPAddress=[ip],SubnetMask=[subnetmask])
                        
                        if gateway:
                            print("in pccontrol gateway", gateway)
                            interface.SetGateways(DefaultIPGateway=[gateway])
                        else:
                            interface.SetGateways(DefaultIPGateway=["0.0.0.0"])
                    
                        self.getNicDetails()            
                                           
        except Exception as e:
            return e
    
   
 #********************** End of class pccontrol ********************************          

 
class nic:
    
    def __init__(self, mac="0", ip="0", mask="0", gateway="0"):
        if mac:
            self.macAddress = mac
        else:
            self.macAddress = "0"
        if ip:
            self.ipAddress = ip
        else:
            self.ipAddress = "0"
        if mask:
            self.subnetMask = mask
        else:
            self.subnetMask = "0"
        if gateway:
            self.defaultGateway = gateway        
        else:
            self.defaultGateway = "0"
                
 #********************** End of class nic ********************************            


if __name__ == "__main__":     
     
    hostPC = pccontrol()
    print (hostPC.getNicDetails()[0].ipAddress)
    print (hostPC.getMacAddresses()[0])
    mac = hostPC.getMacAddresses()[0]
    hostIp = hostPC.getIp(mac)
    print(hostIp)
    print (hostPC.getDefaultGateway(hostIp))



            

