# USAGE
# python main.py --video ball_tracking_example.mp4
# python main.py

# import the necessary packages
from color_tracker import ColorTracker
from HUD import Hud
import numpy as np
import argparse
import cv2
from imutils.video import VideoStream, FPS, DisplayFrame
import time
import struct
import threading
		
# print("connecting to serial port")
# time.sleep(2) #let it initialize

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

#set video resolution
resWidth = 320
resLength = 240

if not args.get("video", False):


	vs = VideoStream(usePiCamera=True, awb_mode='sunlight', resolution=(resWidth, resLength)).start() # awb_mode=sunlight works well for tracking green object
	print("cam warming up")
	time.sleep(1)
	
	df = DisplayFrame(vs.mainQueue)
	df.start()
	tracker = ColorTracker(vs.mainQueue)
	tracker.start()
	hud = Hud()
	hud.start(tracker.cnts)
	time.sleep(1)

while True:


#vs.release()

## close all windows
#cv2.destroyAllWindows()
