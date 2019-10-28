import numpy as np
import cv2
import imutils
from threading import Thread
import threading
import queue as Q
import serial
import time

# serial connection to the Arduino
arduino = serial.Serial('/dev/ttyUSB0', 115200)

# define the lower and upper boundaries of the "green"
# ball in the HSV color space, then initialize the
# list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
# set video resolution
resWidth = 320
resLength = 240

class ColorTracker:

	def __init__(self, q=None):
		# instance vars
		self.stopped = False
		self.cnts = (0,)
		self.xOffset = 0
		self.yOffset = 0
		self.xyDoneQueue = Q.Queue(maxsize=50)  # put processed frames in here for the next object (HUD/serial) to use
		self.currentFrame = None
		self.q = q  # mainQueue

	def start(self):
		self.t = Thread(target=self.update, args=())
		self.t.daemon = True
		self.t.start()
		return self

	def update(self):
		# keep looping
		# cv2.namedWindow("HUD Preview", 0)  # only used for testing
		while not self.stopped:
			if not self.q.empty():
				time1 = time.time()
				self.currentFrame = self.q.get()
				print("{:.2f} | CT: Got frame {} from mainQueue".format(currentFrame.name))
				# print("processing frame")
				# blur frame, and convert it to the HSV color space
				blurred = cv2.GaussianBlur(self.currentFrame.frame, (11, 11), 0)
				hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
				# construct a mask for the color "green", then perform
				# a series of dilations and erosions to remove any small
				# blobs left in the mask
				mask = cv2.inRange(hsv, greenLower, greenUpper)
				mask = cv2.erode(mask, None, iterations=2)
				mask = cv2.dilate(mask, None, iterations=2)

				# find contours in the mask and initialize the current
				# (x, y) center of the ball
				self.cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
					cv2.CHAIN_APPROX_SIMPLE)
				self.cnts = imutils.grab_contours(self.cnts)
				center = None

				# only proceed if at least one contour was found
				if len(self.cnts) > 0:
					# print("Contours found")
					# find the largest contour in the mask, then use
					# it to compute the minimum enclosing circle and
					# centroid
					c = max(self.cnts, key=cv2.contourArea)
					((x, y), radius) = cv2.minEnclosingCircle(c)
					M = cv2.moments(c)
					center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
					self.xOffset = float((x-(resWidth/2))/(resWidth/2))  # float representing distance from screen center to face center
					self.yOffset = float(((resLength/2)-int(y))/(resLength/2))
					self.currentFrame.xOffset = self.xOffset
					self.currentFrame.yOffset = self.yOffset
					if not self.xyDoneQueue.full():
						# print("putting currentFrame into xyDoneQueue")
						self.xyDoneQueue.put(self.currentFrame, block=True)  # Block is true so it will wait for other thread to finish
					else: #xyDoneQueue is full
						self.xyDoneQueue.get() #remove the oldest frame to make room for the new frame
						self.xyDoneQueue.put(self.currentFrame, block=True)
					# arduino.write(offsetStr.encode("{:.3f},{:.3f},{}".format(self.xOffset, self.yOffset, getTrackingStatus))) #need to implement this elsewhere
				else:
					self.cnts = None
				# print("CT: Get/process took {:.2f}s".format(time.time()-time1))
					# print("No contours found")
				# cv2.imshow("HUD Preview", self.currentFrame.frame)
				# key = cv2.waitKey(1) & 0xFF
				# time2 = time.time()
				# fps = 1/(time2 - time1)
				# print("time elapsed: {:.2f}".format(1/fps))
				# print("fps: {:.2f}".format(fps))
			# elif int(time.time()) % 2 == 0:
			# 	print("mainQueue empty")

	def stop(self):
		self.stopped = True
		
	def getTrackingStatus(self):
		if len(cnts)>0:
			return 1
		else:
			return 0
