#!/usr/bin/python3

import threading
import serial
from time import sleep,strftime
import re
from signal import pause
import sys

class GPS(object):

    def __init__(self, **kwargs):
        self._log = kwargs.get('log',False)
        self._logfile = kwargs.get('logfile','')
        self._dev = kwargs.get('dev', '/dev/ttyAMA0')
        self._baud = kwargs.get('baud', 9600)
        print(self._log, self._logfile, self._dev, self._baud)
        self.datastream = serial.Serial(self._dev, self._baud, timeout=0.5)
        self._gpsData = [0,0,0,0,0,0]
        
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    @property
    def gpsData(self):
        return self._gpsData

    @gpsData.setter
    def gpsData(self,gpsData):
        self._gpsData = gpsData
        
    @property
    def fix(self):
        if int(self._gpsData[5]) == 0:
            return False
        else:
            return True
    
    @property
    def time(self):
        return self.gpsData[0]
    @property
    def lat(self):
        return self.gpsData[1]
    @property
    def lon(self):
        return self.gpsData[2]
    @property
    def alt(self):
        return self.gpsData[3]
    @property
    def sat(self):
        return self.gpsData[4]
    

    def checksum(self,sentence):
        sentence = sentence.rstrip('\n').lstrip('$')
        try: 
            data,cs1 = re.split('\*', sentence)
        except ValueError:
            with open("errorLog",'a') as f:
                print(sentence)
                #f.write(",".join(str(value) for value in [self.time,sentence]+ "\n"))
            
            return False
    
        cs2 = 0
        for c in data:
            cs2 ^= ord(c)

        if int(cs1,16)==cs2:
            return True
        else:
            return False

    def nmeaToDec(self,dm,dir):
        if not dm or dm == '':
            return 0.
        match = re.match(r'^(\d+)(\d\d\.\d+)$', dm) 
        if match:
            d, m = match.groups()
        if dir == "W":
            sign = -1
        else:
            sign = 1
        return (float(d) + float(m) / 60)*sign


    def parseGGA(self,ggaString):
        rawList = ggaString.split(",")
        print(rawList[1])
        time = rawList[1][0:2]+":"+rawList[1][2:4]+":"+rawList[1][4:6]
        gpsList = [time,self.nmeaToDec(rawList[2],rawList[3]),self.nmeaToDec(rawList[4],rawList[5]),rawList[9],rawList[7],rawList[6]]
        
        return gpsList

    def logdata(self):
        if self._logfile == '':
            self._logfile = 'gpsLog-%s-%s.csv' % (strftime("%d-%m-%Y"),self.time)
            print(self._logfile)
        with open(self._logfile,'a') as f:
            f.write(",".join(str(value) for value in self.gpsData)+ "\n")
            
                                            
    def run(self):
        while True:
            # Do something
            byteSentence = self.datastream.readline()
            try:
                nmeaSentence = byteSentence.decode("utf-8")
            except:
                nmeaSentence = "Decode Error"

            if nmeaSentence[3:6] == "GGA":
                
                if self.checksum(nmeaSentence):
                    self.gpsData = self.parseGGA(nmeaSentence)
                    print(self.gpsData)
                    print(self.fix)
                    if self._log and self.fix:
                        self.logdata()
            sleep(0.2)

if __name__ == "__main__":
    device = '/dev/ttyAMA0'
    baud_rate = 9600

    if len(sys.argv) > 1:
        device = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            baud_rate = int(sys.argv[2])
        except ValueError as e:
            print(e)
            baud_rate = 9600
    
    gps = GPS(log=True, logfile="log.csv", dev=device, baud=baud_rate)
    pause()
