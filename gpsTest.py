from piGPS import GPS
from time import sleep,strftime
from sense_hat import SenseHat



try:
    s = SenseHat()
    sense=True
    s.show_letter("!",(255,0,0))
except OSError:
    sense=False    


gps = GPS()

def display(sat,fix):
    if fix:
        col=(0,255,0)
    else:
        col=(255,0,0)

    image =[]
    for x in range(sat):
        image.append(col)
    for x in range(64-sat):
        image.append([0,0,0])
    if s.get_pixels() != image:
        s.set_pixels(image)

while not(gps.fix):
    pass

date = strftime("%d-%m-%Y")
time = gps.time[0:2]+":"+gps.time[2:4]


print("Time:" + time)
filename = 'gpsLog-%s-%s' % (time,date)
while True:
    if gps.fix:
        line = '%s,%s,%s,%s,%s' % (gps.time,gps.lat,gps.lon,gps.alt,gps.sat)
        with open(filename,'a') as file:
            file.write(line+ "\n")
                        
    if sense:
        display(gps.sat,gps.fix)                
    sleep(1)
