#this module is referenced via a symlink in the py3cv4 virtualenv site-packages folder so that it can be actually located within the Git repo for backing up to GitHub

from threading import Thread
import cv2
import imutils
from imutils.video import FPS
import numpy
#will I need numpy?
import queue as Q

f = FPS()

class DisplayFrame:
	def __init__(self, q=None):
		self.q = q
		self.stopped = False #indicates if thread should be stopped
		self.currentFrame = None
		
	def start(self):
		t = Thread(target=self.show, args=())
		t.daemon = True
		t.start()
		return self

	def show(self):
		cv2.namedWindow("HUD Preview", 0)
		f.start()
		while not self.stopped:
			if not (self.q.empty()):
				f.start()
				for x in range(30):
					self.currentFrame = self.q.get()
					# self.frame = imutils.resize(self.currentFrame, width=1000)
					# print("Showing frame: " + str(self.currentFrame.name))
					cv2.imshow("HUD Preview", self.currentFrame.frame)
					key = cv2.waitKey(1) & 0xFF
					f.update()
				f.stop()
				print("fps: {:.2f}".format(f.fps()))
				f._numFrames = 0
			if cv2.waitKey(1) == ord("q"):
				self.stopped = True

	def stop(self):
		self.stopped = True
