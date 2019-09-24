#this module is referenced via a symlink in the py3cv4 virtualenv site-packages folder so that it can be actually located within the Git repo for backing up to GitHub

from threading import Thread
import cv2
import imutils
import numpy
#will I need numpy?

class displayFrame:
	def __init__(self, frame=None):
		self.frame = frame
		self.stopped = False #indicates if thread should be stopped
		
	def start(self):
		t = Thread(target=self.show, args=())
		t.daemon = True
		t.start()
		return self
		
	def show(self):
		while not self.stopped:
			try:
				self.frame = imutils.resize(self.frame, width=1000)
				cv2.imshow("Scope View", self.frame)
			except:
				pass
			if cv2.waitKey(1) == ord("q"):
				self.stopped = True

	def stop(self):
		self.stopped = True
		
	def setFrame(self, value):
		self.frame = value

	def getFrame(self):
		return self.frame
