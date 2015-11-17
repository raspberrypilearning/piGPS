import serial
#import pynmea2

def parseGPS(str):
    if str.find('GGA') > 0:
#        msg = pynmea2.parse(str)
 #       lat = pynmea2.dm_to_sd(msg.lat)
  #      lon = pynmea2.dm_to_sd(msg.lon)
#        print(msg.sat)
        print(str)



serialPort = serial.Serial("/dev/ttyAMA0", 9600, timeout=0.5)

while True:
    str = serialPort.readline().decode("utf-8")
    parseGPS(str)

  #  except:
   #   print("error decoding")        



