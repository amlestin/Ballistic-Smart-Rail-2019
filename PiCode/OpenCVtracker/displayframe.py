#this module is referenced via a symlink in the py3cv4 virtualenv site-packages folder so that it can be actually located within the Git repo for backing up to GitHub

from threading import Thread
import cv2
import imutils
import numpy
#will I need numpy?
import queue as Q

class DisplayFrame:
	def __init__(self, q=None):
		self.q = q
		self.stopped = False #indicates if thread should be stopped
		self.currentFrame=None
		
	def start(self):
		t = Thread(target=self.show, args=())
		t.daemon = True
		t.start()
		return self
		
	def show(self):
		cv2.namedWindow("HUD Preview",0)
		while not self.stopped:
			if not (self.q.empty()):
				if (self.q.queue[0].frameReady()):
					self.currentFrame = self.q.get()
			#try:
				#self.frame = imutils.resize(self.frame, width=1000)
				#cv2.imshow("HUD Preview", self.currentFrame.frame)
				
			#except:
				#pass
			if cv2.waitKey(1) == ord("q"):
				self.stopped = True

	def stop(self):
		self.stopped = True
