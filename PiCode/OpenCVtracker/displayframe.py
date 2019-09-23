#this module is referenced via a symlink in the py3cv4 virtualenv site-packages folder so that it can be actually located within the Git repo for backing up to GitHub

from threading import Thread
import cv2
import imutils
#will I need numpy?

class displayFrame:
	def __init__(self):
		self.frame = None
		self.stopped = False #indicates if thread should be stopped
		
	def start(self):
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self
		
	def update(self, frame):
			frame = imutils.resize(frame, width=600)
			cv2.imshow("Scope View", frame)
			key = cv2.waitKey(1) & 0xFF
			return
