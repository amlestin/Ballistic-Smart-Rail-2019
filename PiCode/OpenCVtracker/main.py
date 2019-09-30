# USAGE
# python main.py --video ball_tracking_example.mp4
# python main.py

# import the necessary packages
import color_tracker
import HUD
import numpy as np
import argparse
import cv2
import imutils
import time
import serial
import struct
import threading

timeCheckA=[]
timeCheckB=[]
timeCheckC=[]
timeCheckD=[]
i=0
avgTimeA=0
avgTimeB=0
avgTimeC=0
avgTimeD=0

# serial connection to the Arduino
arduino = serial.Serial('/dev/ttyUSB0', 115200)
print("connecting to serial port")
time.sleep(2) #let it initialize

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
	help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
	help="max buffer size")
args = vars(ap.parse_args())

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)

# if a video path was not supplied, grab the reference
# to the webcam

#set video resolution
resWidth = 320
resLength = 240

if not args.get("video", False):
	vs = VideoStream(usePiCamera=True, awb_mode='sunlight', resolution=(resWidth, resLength)).start() #awb_mode=sunlight works well for tracking green object
	frame = vs.read()
	df = DisplayFrame().start() #instantiate frame display thread (using a comma inside the argument parentheses because frame is an np array)
	tracker = ColorTracker().start()
	
	
# otherwise, grab a reference to the video file
else:
	vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
time.sleep(1.5)

#set up fps vars (I know I probably need to do this differently)
currentFPS = 0
#averageFPS = 0

# keep looping
while True:
	currentFPSstr = 'FPS: {:0.2f}'.format(currentFPS)
	#averageFPSstr = 'AVG FPS: {:0.2f}'.format(averageFPS)
	f = FPS() #instantiate
	f.start() #call start() function thus setting start time for sample period
	for x in range(15): #count 15 frames
    
		# grab the current frame
		time1=time.time()
		frame = vs.read()
		timeCheckA.insert(i,int((time.time()-time1)*1000))
		avgTimeA=(sum(timeCheckA))/(len(timeCheckA))
		print("Avg FrameRead Time: {:.4f}ms".format(avgTimeA))
		f.update() #increment frame counter

		# handle the frame from VideoCapture or VideoStream
		frame = frame[1] if args.get("video", False) else frame

		# if we are viewing a video and we did not grab a frame,
		# then we have reached the end of the video
		if frame is None:
			break

		time2=time.time()
		tracker.setFrame(frame)
		xOffset, yOffset = tracker.getXYoffsets() #how will this work since getXYoffsets() is threaded?
		timeCheckB.insert(i,int((time.time()-time2)*1000))
		avgTimeB=(sum(timeCheckB))/(len(timeCheckB))
		print("Avg ImgProcess Time: {:.2f}ms".format(avgTimeB))
		#print("ImgProcess Time:{:.2f}ms".format(timeCheck2*1000))

		time3=time.time()
		frame = Hud.draw()
				print("FPS: " + currentFPSstr)
				f.stop()
				currentFPS = f.fps()

		else:
			trackingStatus = 0
	
		offsetStr = "[{:0.3f}, {:0.3f}, {}]".format(Xoffset, Yoffset, trackingStatus)
		#print(offsetStr)
		#timeCheck3=(time.time()-time3)
		#print("Draw Time:       {:.2f}ms".format(timeCheck3*1000))
		timeCheckC.insert(i,int((time.time()-time3)*1000))
		avgTimeC=(sum(timeCheckC))/(len(timeCheckC))
		print("Avg Draw Time: {:.2f}ms".format(avgTimeC))
		
		arduino.write(offsetStr.encode())

		#resize/display frame in separate thread (to keep from blocking main loop from going back for another one ASAP since imshow is normally blocking)
		time4=time.time()
		df.setFrame(frame)
		#print("df.frame type:"+str(type(df.frame)))
		timeCheckD.insert(i,int((time.time()-time4)*1000)) #there's probably a better way, but working with lists in Python is weird and I'm not very good at it
		avgTimeD=(sum(timeCheckD))/(len(timeCheckD))
		print("Avg DispFrame Time:{:.2f}ms".format(avgTimeD))
		print("Total Time: {:.2f}ms".format((time.time()-time1)*1000))

		if(i>4):
			i=0
		else:
			i=i+1
		# show the frame to our screen
		#frame = imutils.resize(frame, width=600)
		#cv2.imshow("Frame", frame)
		#key = cv2.waitKey(1) & 0xFF

# if we are not using a video file, stop the camera video stream
if not args.get("video", False):
	vs.stop()

# otherwise, release the camera
else:
	vs.release()

# close all windows
cv2.destroyAllWindows()
