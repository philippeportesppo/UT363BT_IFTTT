#!/usr/bin/env python
#
# Philippe Portes October 2022.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
import sys
import requests
import math
#from bluepy.btle import Scanner, DefaultDelegate
from bluepy.btle import DefaultDelegate, Peripheral
import time
from datetime import datetime
import binascii
import os

class MyDelegate(DefaultDelegate):
        def __init__(self, bluetooth_adr):
                print("Init my delegate")
                self.adr = bluetooth_adr
                #self.s=requests.Session()
                self.windSpeed=0.0
                self.timerStart=0
                self.maxWindSpeed = 0.0
                self.currentDate=datetime.today().strftime("%d")
                self.temp=0.0
                DefaultDelegate.__init__(self)

        def handleNotification(self, cHandle, data):


                if datetime.today().strftime("%d") != self.currentDate:
                        print("Max speed for ",datetime.today().strftime("%d/%m/%y"),": ",self.maxWindSpeed)
                        self.currentDate = datetime.today().strftime("%d")

                if self.windSpeed > self.maxWindSpeed:
                                self.maxWindSpeed = self.windSpeed

                if cHandle == 19:
                        #                   aa  bb  10  0130 2020 33302e3420 a1 e630 30 80 0532
                        # Temp: data:  b'\xaa\xbb\x10\x010  30.4 \xa1\xe600\x80\x052'
                        # wind: data:  b'\xaa\xbb\x10\x017  0.00M/S40\x80\x04\\
                                #print (data)
                                if binascii.b2a_hex(data[0:5]).decode('utf-8') == "aabb100130":
                                        self.temp = float(data[5:11])
                                elif binascii.b2a_hex(data[0:5]).decode('utf-8') == "aabb100137":
                                        self.windSpeed = float(data[5:11])
                                sys.stdout.write ("Wind: %.1f m/s, Max daily wind: %.1f m/s, Temp: %.1f C \r" % (self.windSpeed, self.maxWindSpeed, self.temp))
                                sys.stdout.flush()

                                Headers = { "Content-Type": "application/json;charset=UTF-8","Accept":"text/plain, */*"  }
                                try:
                                        if (self.windSpeed > 4.5):
                                                if (self.timerStart == 0):
                                                        self.timerStart = datetime.now().timestamp()
                                                        print ("Starting timer for 3 seconds")
                                                elif (datetime.now().timestamp() - self.timerStart > 3.0):
                                                        response = requests.post("https://maker.ifttt.com/trigger/wind/with/key/mKD-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXPaM", headers=Headers)
                                                        print("Response: ", response)
                                                        self.timerStart = 0
                                        else:
                                                self.timerStart = 0
                                                print("Stopping timer")
                                except Exception as e:
                                        print("Error sending to IFTT. Retry next time.")
                                        print(e)
                                        pass
def main():: 
        bluetooth_adr = sys.argv[1].lower() # example"fe:ed:fa:ce:fe:ed" 
        hci = sys.argv[1] # hci # to use
        print  ("Will follow broadcasts from:",bluetooth_adr)
        print  ("hci used: ",hci)
        perif = Peripheral()
        perif.setDelegate(MyDelegate(bluetooth_adr))
        while True:
                try:
                        perif.connect(bluetooth_adr, iface=hci) #, addrType=btle.ADDR_TYPE_RANDOM, iface=hci)
                        perif.writeCharacteristic(0x14, b"\x01\x00", True)
                        break;
                except:
                        sys.stdout.write("Connecting... \r")
                        sys.stdout.flush()
                        pass

        retry_counter = 0
        sys.stdout.write("Connected! \r")
        sys.stdout.flush()
        while True:
                try:
                        perif.writeCharacteristic(0x14, b"\x01\x00", True)
                        while True:
                                perif.writeCharacteristic(0x10, b"\x5E", False)
                                time.sleep(2)
                                if perif.waitForNotifications(1):
                                        continue
                except Exception as e:
                        print(e)
                        #exit()
                        if (retry_counter > 100):
                                try:
                                        Headers = { "Content-Type": "application/json;charset=UTF-8","Accept":"text/plain, */*"  }
                                        response = requests.post("https://maker.ifttt.com/trigger/winddisconnect/with/key/mKDXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXPaM", headers=Headers)
                                        print("Response: ", response)
                                        os.system("sudo reboot")
                                except Exception as e:
                                        print("Error sending to IFTT. Retry next time.")
                                        print(e)
                                        pass
                        else:
                                retry_counter=retry_counter+1
                                try:
                                        sys.stdout.write("Re-Connecting \r")
                                        sys.stdout.flush()

                                        perif.connect(bluetooth_adr,iface=hci)
                                        perif.writeCharacteristic(0x14, b"\x01\x00", True)
                                        sys.stdout.write("Re-Connected! \r")
                                        sys.stdout.flush()
                                        pass
                                except:
                                        pass
                        pass

if __name__ == "__main__":
        main()
