import numpy as np
import cv2
import imutils
#import struct #I'm not sure what I need this for so delete later if it proves unecessary
import threading

class ColorTracker:
	# define the lower and upper boundaries of the "green"
	# ball in the HSV color space, then initialize the
	# list of tracked points
	greenLower = (29, 86, 6)
	greenUpper = (64, 255, 255)
	
	def __init__(self, frame=None):
		#instance vars
		self.frame = frame
		self.stopped = False
		
	def start(self):
		t = Thread(target=self.getXYoffsets, args=())
		t.daemon = True
		t.start()
		return self
		
	def getXYoffsets(self):
		# keep looping
		while not self.stopped:
			try:
				# blur frame, and convert it to the HSV color space
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
					Xoffset = float((x-(resWidth/2))/(resWidth/2)) #float representing distance from screen center to face center
					Yoffset = float(((resLength/2)-int(y))/(resLength/2))
					return (xOffset, yOffset)
				else:
					trackingStatus = 0
			except:
				pass
		
	def stop(self):
		self.stopped = True
		
	def setFrame(self, value):
		self.frame = value

	def getFrame(self):
		return self.frame
