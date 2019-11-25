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
import multiprocessing
import os
import cProfile, pstats, io

# serial connection to the Arduino
# arduino = serial.Serial('/dev/ttyUSB0', 115200)
# print("connecting to serial port")
# time.sleep(2) #let it initialize

# set video parameters
resolution = (320, 240)
framerate = 32
awb_mode = 'sunlight'
file1 = open("A_videostream.txt", "w+")
file2 = open("A_colortracker.txt", "w+")
file3 = open("A_hud.txt", "w+")
file4 = open("A_resize.txt", "w+")
file4B = open("B_resize.txt", "w+")
file5 = open("A_display.txt", "w+")

done = multiprocessing.Event()
hud_done = multiprocessing.Event()  # resize and display modules will wait


def profile(fnc):
    """A decorator that uses cProfile to profile a function"""

    def inner(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        retval = fnc(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        file2.write(s.getvalue())
        return retval

    return inner

# @profile
def main():
    # create queues in shared memory so each process can access it
    mainQueue = Queue(maxsize=70)
    xyDoneQueue = Queue(maxsize=70)
    hudDoneQueue = Queue(maxsize=70)
    resizeDoneQueue = Queue(maxsize=70)

    # start VideoStream process
    vs = PiVideoStream(mainQueue, file1)
    time.sleep(1)  # allow pi camera to "warm up"
    vsP1 = Process(target=vs.update, name='videoStreamProcess', args=(resolution, framerate, awb_mode))  # passing these parameters here because
    time.sleep(0.5) # put some frames into mainQueue to stop other processes from throwing errors
    # passing to PiVideoStream instantiation causes pi camera to be accessed by two different processes which breaks it
    vsP1.daemon = True
    vsP1.start()

    # start ColorTracker process
    tracker = ColorTracker(mainQueue, xyDoneQueue, file2)  # pass shared queues
    trackerP1 = Process(target=tracker.update, name = 'trackerProcess', args=())
    trackerP1.daemon = True
    trackerP1.start()

    # start Hud process
    hud = Hud(resolution, xyDoneQueue, hudDoneQueue, file3, hud_done)
    hudP1 = Process(target=hud.draw, name='hudProcess', args=())
    hudP1.daemon = True
    hudP1.start()

    # start ResizeFrame process 1
    resize = ResizeFrame(hudDoneQueue, resizeDoneQueue, file4, hud_done, instance_name='resizer1')
    resizeP1 = Process(target=resize.resize, name='resizeProcess', args=())
    resizeP1.daemon = True
    resizeP1.start()

    # start ResizeFrame process 2
    resize2 = ResizeFrame(hudDoneQueue, resizeDoneQueue, file4B, hud_done, instance_name='resizer2')
    resizeP2 = Process(target=resize2.resize, name='resizeProcess2', args=())
    resizeP2.daemon = True
    resizeP2.start()

    # start DisplayFrame process
    display = DisplayFrame(resizeDoneQueue, file5, done)
    displayP1 = Process(target=display.show, name='displayProcess', args=())
    displayP1.daemon = True
    displayP1.start()

    while not done.is_set():
        continue

    else:
        print('Terminating processes')
        file1.close()
        file2.close()
        file3.close()
        file4.close()
        file4B.close()
        vsP1.terminate()
        trackerP1.terminate()
        hudP1.terminate()
        resizeP1.terminate()
        resizeP2.terminate()
        displayP1.terminate()

if __name__ == '__main__':
    main()