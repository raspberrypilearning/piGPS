#!/usr/bin/python3

from datetime import datetime
import threading
import serial
from time import sleep,strftime
import re
from signal import pause
import sys
from math import sin,cos,radians,degrees,log,tan,pi,atan2,asin,sqrt

class GPS(object):
    """
    The GPS object reads NMEA sentence data from a serial connected GPS device. Once created the GPS object stores the current stores the current gps data and makes this data available via property methods.

    :param bool log:
        If 'True' the GPS object will write a csv logfile of all valid lat/lon data recieved, by default this is 'False'
        
    :param str logfile:
        Specifies the filename of any GPS logfile to be written, if no filename is specified then a file name gpsLog-{utc timestamp}.csv is used.
        
    :param str dev:
        Specifies the tty device on which the GPS device is connected, the defualt is '/dev/ttyACM0'
        
    :param int baud:
        Set the baud rate (speed) of the communication with the GPS device, default is '9600'
        
    :param bool debug:
        Determines whether debuging information is printed to the console, default is 'False'    
    """

    def __init__(self, **kwargs):
        self._log = kwargs.get('log',False)
        self._logfile = kwargs.get('logfile','gpsLog-{0}.csv'.format(datetime.utcnow()))
        self._dev = kwargs.get('dev', '/dev/ttyACM0')
        self._baud = kwargs.get('baud', 9600)
        self._debug = kwargs.get('debug', False)
        self.datastream = serial.Serial(self._dev, self._baud, timeout=0.5)
        self._gpsData = [0,0,0,0,0,0]
        
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    @property
    def debug(self):
        return self._debug

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
        """
        Takes a valid NMEA sentence as a parameter, the checksum is then striped and compared to the remainder of the sentence.
        If the checksum can't be extracted or is invalid then 'False' is returned, if the checksum matches then the function returns 'True'.
        """
        sentence = sentence.rstrip('\n').lstrip('$')
        try: 
            data,cs1 = re.split('\*', sentence)
        except ValueError:
            with open("errorLog",'a') as f:
                f.write(",".join(str(value) for value in [self.time,sentence]+ "\n"))
            
            return False
    
        cs2 = 0
        for c in data:
            cs2 ^= ord(c)

        if int(cs1,16)==cs2:
            return True
        else:
            return False

    def altCheck(self,alt):
        """
        Checks for a valid alt and 
        """
        if not alt or alt == '':
            return 0.
        else :
            return float(alt)
 
    def nmeaToDec(self,dm,dir):
        """
        Converts a NMEA formatted position to a position in Decimal notation.
        """
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


    
    def distanceToTarget(self,target):
        """
        Takes a tuple (lon, lat) and calculates straightline distance to target from current location
        """
        if int(self.sat) > 4:
            # convert decimal degrees to radians 
            lat1,lon1,lat2,lon2 = map(radians, [self.lat, self.lon, target[0],target[1]])

            # haversine formula 
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371 # Radius of earth in kilometers. Use 3956 for miles
            return c * r
        else:
            return None
        
    def parseGGA(self,ggaString):
        """
        Takes a NMEA GGA string and splits out the data fields storing them in a List object called 'gpsList', converting the data to appropriate data types before storing.
        
        gpsList[0] : The UTC time from the GPS device as a 'datetime.time()' object.
        gpsList[1] : The current decimal Latitude from GPS as a float.
        gpsList[2] : The current decimal Londitude from GPS as a float.
        gpsList[3] : The current Altitude in metres from GPS as a float.
        gpsList[4] : The current number of satelites from which data is being received
        gpsList[5] : A boolean value indicating whether the GPS receiver currently has a fix, meaning it is receiving data from at least 4 satelites.
        """
        gpsList = self._gpsData
        print(gpsList)
        rawList = ggaString.split(",")
        if self.debug:
            print("Parsing...\n",rawList)
        time = rawList[1][0:2]+":"+rawList[1][2:4]+":"+rawList[1][4:6]
        print(time)
        if time != "::":
            gpsList = [datetime.strptime(time,'%H:%M:%S').time() ,self.nmeaToDec(rawList[2],rawList[3]),self.nmeaToDec(rawList[4],rawList[5]),self.altCheck(rawList[9]),int(rawList[7]),rawList[6]]
        
        return gpsList

    def logdata(self):
        """
        The logdata function adds the latest data (seperated by commas) to the logfile.
        """
        with open(self._logfile,'a') as f:
            f.write(",".join(str(value) for value in self._gpsData)+ "\n")
            
                                            
    def run(self):
        """
        The run function runs as a background thread once a GPS object is created, it:
        
            - Reads NMEA lines from serial input
            - Checks whether it is a GGA NMEA sentence
            - Validates GGA sentence using it's checksum
            - If valid the GGA sentence is parsed and stored in the GPS object's 'gpsData' structure.
            - If logging is enabled then the latest GPS data is written to the log file.
        """
        if self._log:
            with open(self._logfile,'a') as f:
                f.write("UTC Time, Latitude, Londitude,Altitude,Satelites,GPS Fix")
        while True:
            # Do something
            byteSentence = self.datastream.readline()
            try:
                nmeaSentence = byteSentence.decode("utf-8")
            except:
                nmeaSentence = "Decode Error"

            if nmeaSentence[3:6] == "GGA":
                
                if self.checksum(nmeaSentence):
                    self._gpsData = self.parseGGA(nmeaSentence)
                if self.debug:
                    print(self._gpsData)
                    print(self.fix)
                if self._log and self.fix:
                    self.logdata()
            sleep(0.2)

if __name__ == "__main__":

    if len(sys.argv) > 1:
        device = sys.argv[1]
    
    if len(sys.argv) > 2:
        try:
            baud_rate = int(sys.argv[2])
        except ValueError as e:
            print(e)
            baud_rate = 9600
    
    gps = GPS()
    pause()
