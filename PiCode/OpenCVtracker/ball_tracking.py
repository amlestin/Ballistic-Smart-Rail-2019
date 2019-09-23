# USAGE
# python ball_tracking.py --video ball_tracking_example.mp4
# python ball_tracking.py

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from imutils.video import displayFrame #custom threaded module
import numpy as np
import argparse
import cv2
import imutils
import time
import serial
import struct

Xoffset = 0 #global ints
Yoffset = 0
trackingStatus = 0
frame = None #I suspect this is needed since frame isn't declared before the displayFrame class is instantiated
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
	df = displayFrame().start() #instantiate frame display thread (using a comma inside the argument parentheses because frame is an np array)

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

		# resize the frame, blur it, and convert it to the HSV
		# color space
		#frame = imutils.resize(frame, width=600) #moved this to its own threaded module to increase speed
		time2=time.time()
		blurred = cv2.GaussianBlur(frame, (11, 11), 0)
		hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

		# construct a mask for the color "green", then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, greenLower, greenUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		# find contours in the mask and initialize the current
		# (x, y) center of the ball
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = imutils.grab_contours(cnts)
		center = None
		#timeCheck2=(time.time()-time2)
		timeCheckB.insert(i,int((time.time()-time2)*1000))
		avgTimeB=(sum(timeCheckB))/(len(timeCheckB))
		print("Avg ImgProcess Time: {:.2f}ms".format(avgTimeB))
		#print("ImgProcess Time:{:.2f}ms".format(timeCheck2*1000))

		time3=time.time()
		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			trackingStatus = 1
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
			

			# only proceed if the radius meets a minimum size
			if radius > 10:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				# then print x/y offset from center and FPS -Jesse Moody
				cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
				cv2.circle(frame, center, 5, (0, 0, 255), -1)
				
				Xoffset = float((x-(resWidth/2))/(resWidth/2)) #float representing distance from screen center to face center
				Yoffset = float(((resLength/2)-int(y))/(resLength/2))
				
				#cv2.putText(frame, currentFPSstr, (30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
				#cv2.putText(frame, averageFPSstr, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 2)
				#print(currentFPSstr)
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
		df.update(frame,) #(display frame). Comma appended because np array
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
