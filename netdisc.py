import sys
import subprocess
import tempfile

class netdisc():

    def do_action(self, cmd1, cmd2 = "", cmd3 = "", cmd4 = "", cmd5 = ""):
        with tempfile.TemporaryFile() as tempf:


            proc = subprocess.Popen(["C:\\ModemConfig\\netdisc", cmd1, cmd2, cmd3, cmd4, cmd5], stdout=tempf)

            proc.wait()
            tempf.seek(0)
            return tempf.read()

    def do_stop(self):
        readback = self.do_action("start")
        if "stopped" or "not running" in readback:
            return readback
        else:
            return False

    def do_start(self):
        readback = self.do_action("start")
        if "running" in readback:
                return readback
        else:
            return False

    def do_ldsc(self):
        tmpDev =  "DEV-8: 00:04:00:00:00:00 140.10.10.2 ELEC MODEM 247 00:02:00:00:00:00 192.168.0.150 \n" \
                    "DEV-7: 00:aa:de:00:00:52 192.168.0.150 ELEC MODEM 246 ff:ff:ff:ff:ff:ff 255.255.255.255"
        readback = self.do_action("ldisc")
        if "Received DISCOVERY-REPLY" in readback:
            return readback
        else:
            return tmpDev

    def do_localscan(self):

        self.do_stop()
        self.do_stop()
        self.do_start()
        readback = self.do_ldsc()
        if readback is not False:
            return readback
        else:
            return "Device not found"




if __name__ == "__main__":
    ntd = netdisc()
    # print(ntd.do_action("stop"))
    # print(ntd.do_action("stop"))
    # print(ntd.do_action("start"))
    # print(ntd.do_action("start"))
    # print(ntd.do_action("ldisc"))
    # print(ntd.do_stop())
    # print(ntd.do_stop())
    # print(ntd.do_start())
    # print(ntd.do_ldisc())
    print(ntd.do_localscan())