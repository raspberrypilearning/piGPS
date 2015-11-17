from piGPS import GPS
from time import sleep
from sense_hat import SenseHat

s = SenseHat()


while True:
    for sat in range (65):
        image =[]
        col=(255,0,0)
        for x in range(sat):
            image.append(col)
        for x in range(64-sat):
            image.append((0,0,0))
        print(sat,len(image))
        s.set_pixels(image)
        sleep (0.2)

