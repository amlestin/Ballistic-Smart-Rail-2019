#this module is referenced via a symlink in the py3cv4 virtualenv site-packages folder so that it can be actually located within the Git repo for backing up to GitHub

from threading import Thread
import cv2
import imutils
from imutils.video import FPS
import numpy
#will I need numpy?
import queue as Q
import time

f = FPS()

class DisplayFrame:
	def __init__(self, q=None):
		self.q = q  # xyDoneQueue
		self.stopped = False #indicates if thread should be stopped
		self.currentFrame = None
		
	def start(self):
		self.t = Thread(target=self.show, args=())
		self.t.daemon = True
		self.t.start()
		return self

	def show(self):
		# f.start()
		print("DF started")
		while not self.stopped:
			if not (self.q.empty()):
				print("DF: xyDoneQueue not empty")
				# f.start()
				# for x in range(30):
				# 	self.currentFrame = self.q.get()
				# 	# self.frame = imutils.resize(self.currentFrame, width=1000)
				# 	# print("Showing frame: " + str(self.currentFrame.name))
				# 	cv2.imshow("HUD Preview", self.currentFrame.frame)
				# 	key = cv2.waitKey(1) & 0xFF
				# 	f.update()
				# f.stop()
				self.currentFrame = self.q.get()
				# self.frame = imutils.resize(self.currentFrame, width=1000)
				# print("Showing frame: " + str(self.currentFrame.name))
				cv2.imshow("HUD Preview", self.currentFrame.frame)
				key = cv2.waitKey(1) & 0xFF
				print("{:.2f} | DF: Got frame {} from xyDoneQueue ({})".format((time.time()*1000), self.currentFrame.name, self.t.getName()))
				# f._numFrames = 0
			else:
				print("DF: xyDoneQueue empty")
			if cv2.waitKey(1) == ord("q"):
				print("waitKey(1) or q was pressed so stopping DF")
				self.stopped = True

	def stop(self):
		self.stopped = True
