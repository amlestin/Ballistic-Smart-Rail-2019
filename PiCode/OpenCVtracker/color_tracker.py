import numpy as np
import cv2
import imutils
#import struct #I'm not sure what I need this for so delete later if it proves unecessary
from threading import Thread
import queue as Q
import serial

# serial connection to the Arduino
arduino = serial.Serial('/dev/ttyUSB0', 115200)

class ColorTracker:
	# define the lower and upper boundaries of the "green"
	# ball in the HSV color space, then initialize the
	# list of tracked points
	greenLower = (29, 86, 6)
	greenUpper = (64, 255, 255)
	
	def __init__(self, q=None):
		#instance vars
		self.q = q
		self.stopped = False
		self.cnts=(0,)
		self.xOffset=0
		self.yOffset=0
		
	def start(self):
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self
		
	def update(self):
		# keep looping
		while not self.stopped:
			currentFrame = self.q.get()
			try:
				# blur frame, and convert it to the HSV color space
				blurred = cv2.GaussianBlur(currentFrame.frame, (11, 11), 0)
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
					# find the largest contour in the mask, then use
					# it to compute the minimum enclosing circle and
					# centroid
					c = max(self.cnts, key=cv2.contourArea)
					((x, y), radius) = cv2.minEnclosingCircle(c)
					M = cv2.moments(c)
					center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
					self.xOffset = float((x-(resWidth/2))/(resWidth/2)) #float representing distance from screen center to face center
					self.yOffset = float(((resLength/2)-int(y))/(resLength/2))
					arduino.write(offsetStr.encode("{:.3f},{:.3f},{}".format(xOffset, yOffset, getTrackingStatus)))
				else:
					self.cnts = None
				print("tracker ready for ", currentFrame.name)
				currentFrame.trackerReady = True
			except:
				pass
		
	def stop(self):
		self.stopped = True
		
	def getTrackingStatus(self):
		if len(cnts)>0:
			return 1
		else:
			return 0
