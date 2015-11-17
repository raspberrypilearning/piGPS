##!/usr/bin/env python
          
      
import time
import serial
from pynmea import nmea          
      
ser = serial.Serial(
  port='/dev/ttyAMA0',
  baudrate = 9600,
  parity=serial.PARITY_NONE,
  stopbits=serial.STOPBITS_ONE,
  bytesize=serial.EIGHTBITS,
  timeout=1
  )
          
gp = nmea.GNGGA()
      
while True:
  x=ser.readline()
  try:
    pass    

#x=x.decode('utf-8')
#    x=x.replace("GNGGA","GPGGA")
  except UnicodeDecodeError:
    pass
  print(x[0:6])
  if x[0:6] == "GNGGA":
    print("FOUND")
    gps = gp.parse(x)
    #print(gps.latitude,gps.longitude)
  print(x)
