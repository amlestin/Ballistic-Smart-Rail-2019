# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread
import cv2
import time
import queue as Q
import random

class CurrentFrame:
	def __init__(self, frame=None):
		self.frame = frame
		self.hudReady = False
		self.trackerReady = False
		self.name = 0
		self.xyOffset = (0, 0)
		
	def frameReady(self):
		return (self.hudReady and self.trackerReady)

class PiVideoStream:
	def __init__(self, resolution=(320, 240), framerate=32, awb_mode='auto'):
		# initialize the camera and stream
		self.camera = PiCamera()
		self.camera.resolution = resolution
		self.camera.framerate = framerate
		self.camera.awb_mode = awb_mode
		self.rawCapture = PiRGBArray(self.camera, size=resolution)
		self.stream = self.camera.capture_continuous(self.rawCapture,
			format="bgr", use_video_port=True)

		# initialize the frame and the variable used to indicate
		# if the thread should be stopped
		self.frame = CurrentFrame()
		self.stopped = False
		self.mainQueue = Q.Queue(maxsize=50)

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		i=0
		# keep looping infinitely until the thread is stopped
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame.frame = f.array
			self.rawCapture.truncate(0)
			if not self.mainQueue.full():
				print("VS: mainQueue size: {}".format(self.mainQueue.qsize()))
				self.mainQueue.put(self.frame)
				#  number (i.e. name) each frame in the queue
				if (i <= 30):
					self.frame.name = i
					i=i+1
				elif (i>30):
					i=0

			# if the thread indicator variable is set, stop the thread
			# and resource camera resources
			if self.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

	def read(self):
		# return the frame most recently read
		return self.frame
		
	def more(self):
		#return True if there are still frames in the queue
		return self.mainQueue.qsize() > 0

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True

	def getQueue(self): #I don't think this works. Delete it later.
		return self.mainQueue.get()
