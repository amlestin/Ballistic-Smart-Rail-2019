# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from threading import Thread, Lock
import cv2
import time
import datetime
import queue as Q
import random

class CurrentFrame:
	def __init__(self, frame=None):
		self.frame = frame
		self.name = 0
		self.timeStamp = 0
		self.xOffset = 0
		self.yOffset = 0

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
		self.frame = CurrentFrame
		self.stopped = False
		self.mainQueue = Q.Queue(maxsize=100)
		self.time1 = time.time()*1000

	def start(self):
		# start the thread to read frames from the video stream
		self.t = Thread(target=self.update, args=())
		self.t.daemon = True
		self.t.start()
		return self

	def update(self):
		i=1
		# keep looping infinitely until the thread is stopped
		for f in self.stream:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			self.frame.frame = f.array
			self.frame.timeStamp = (time.time() * 1000)
			self.rawCapture.truncate(0)
			if not self.mainQueue.full():
				# time1 = time.time()
				self.mainQueue.put(self.frame)
				# print("VS: mainQueue.put() took {:.2f}s".format(time.time()-time1))
				#  number (i.e. name) each frame in the queue
				if (i <= 100):
					self.frame.name = i
					i=i+1
				elif (i>100):
					i=1
				print("VS: {:.2f} Put frame {} from stream into mainQueue (mainQueue size: {})".format(self.frame.timeStamp, self.frame.name, self.mainQueue.qsize()))
			else:
				self.mainQueue.get()
				self.mainQueue.put(self.frame)
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

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True