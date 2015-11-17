from piGPS import GPS
from time import sleep,strftime
from sense_hat import SenseHat



try:
    s = SenseHat()
    sense=True
    
except OSError:
    sense=False    


gps = GPS(log=True)

def display(sat,fix):
    if fix:
        col=(0,255,0)
        image =[]
        for x in range(sat):
            image.append(col)
        for x in range(64-sat):
            image.append([0,0,0])
        if s.get_pixels() != image:
            s.set_pixels(image)
    else:
        s.show_letter("!",(255,0,0))



while True:
    if sense:
        sleep(1)
        display(gps.sat,gps.fix)
        sleep(1)
        s.clear()
    else:
        sleep(2)
