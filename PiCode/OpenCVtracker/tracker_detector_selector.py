#this object lets you easily adjust how much object detection vs tracking is performed
#using more detection might give better acuracy, but using more tracking might give better speed

class TrackerDetectorSelector:
	def __init__(self):
		self.frame = frame
		self.framesBetweenDetector = 30 #how many frames the tracker runs before momentarily switching to detector for one correction frame
		self.useDetector = False
		

	def start(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.update, args=())
		t.daemon = True
		t.start()
		return self

	def update(self):
		while not self.stopped:
			if vs.mainQueue[0].name % self.framesBetweenDetector = 0:
				self.frame = detector.getXY
			else:
				self.frame = tracker.getXY

	def getXY(self):
		# return the frame most recently read
		return self.frame

	def stop(self):
		# indicate that the thread should be stopped
		self.stopped = True
