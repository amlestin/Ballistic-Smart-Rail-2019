from colortracker import ColorTracker
from resizeframe import ResizeFrame
from hud import Hud
import numpy as np
import argparse
import cv2
# from imutils.video import FPS
from pivideostream import PiVideoStream
from displayframe import DisplayFrame
import time
import struct
from multiprocessing import Process, Queue
import os

# serial connection to the Arduino
# arduino = serial.Serial('/dev/ttyUSB0', 115200)
# print("connecting to serial port")
# time.sleep(2) #let it initialize

# set video parameters
resolution = (320, 240)
framerate = 30
awb_mode = 'sunlight'
file = open("timeStamps5.txt", "w+")

if __name__ == '__main__':
    # create queues in shared memory so each process can access it
    mainQueue = Queue(maxsize=70)
    xyDoneQueue = Queue(maxsize=70)
    hudDoneQueue = Queue(maxsize=70)
    resizeDoneQueue = Queue(maxsize=70)

    # start VideoStream process
    vs = PiVideoStream(mainQueue, file)
    time.sleep(1)  # allow pi camera to "warm up"
    vsP1 = Process(target=vs.update, args=(resolution, framerate, awb_mode))  # passing these parameters here because
    # passing to PiVideoStream instantiation causes pi camera to be accessed by two different processes which breaks it
    vsP1.daemon = True
    vsP1.start()

    # start ColorTracker process
    tracker = ColorTracker(mainQueue, xyDoneQueue, file)  # pass shared queues
    trackerP1 = Process(target=tracker.update, args=())
    trackerP1.daemon = True
    trackerP1.start()

    # start Hud process
    hud = Hud(resolution, xyDoneQueue, hudDoneQueue, file)
    hudP1 = Process(target=hud.draw, args=())
    hudP1.daemon = True
    hudP1.start()

    # start ResizeFrame process
    resize = ResizeFrame(hudDoneQueue, resizeDoneQueue, file)
    resizeP1 = Process(target=resize.resize, args=())
    resizeP1.daemon = True
    resizeP1.start()

    # start DisplayFrame process
    display = DisplayFrame(resizeDoneQueue, file)
    displayP1 = Process(target=display.show, args=())
    displayP1.daemon = True
    displayP1.start()

    while not display.done:
        continue

    # vsP1.join()
    # trackerP1.join()
    # hudP1.join()
    # df1.p.join()
    # file.close()
