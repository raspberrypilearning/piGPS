from __future__ import print_function
import serial, io

addr  = '/dev/ttyAMA0'  # serial port to read data from
baud  = 9600            # baud rate for serial port
fname = 'gps-log.dat'   # log file to save data in
fmode = 'a'             # log file mode = append

with serial.Serial(addr,9600) as pt, open(fname,fmode) as outf:
    spb = io.TextIOWrapper(io.BufferedRWPair(pt,pt,1),
        encoding='ascii', errors='ignore', newline='\r',line_buffering=True)
    spb.readline()  # throw away first line; likely to start mid-sentence (incomplete)
    while (1):
        x = spb.readline()  # read one line of text from serial port
        print (x,end='')    # echo line of text on-screen
        outf.write(x)       # write line of text to file
        outf.flush()        # make sure it actually gets written out
