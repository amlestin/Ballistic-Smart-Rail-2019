import cv2
import imutils
from multiprocessing import Process, Queue
import time

class Hud:
	def __init__(self, res, q1=None, q2=None, file=None):
		self.res = res
		self.xyDoneQueue = q1
		self.hudDoneQueue = q2
		self.currentFrame = None
		self.stopped = False  # indicates if thread should be stopped
		self.file = file

	# def start(self):
	# 	t.daemon = True
	# 	t.start()
	# 	return self

	def draw(self):
		while not self.stopped:
			if not self.xyDoneQueue.empty():
				self.currentFrame = self.xyDoneQueue.get()
				# print("HUD1: {:.2f} Got frame {} from xyDoneQueue".format((time.time() * 1000), self.currentFrame.name))
				try:
					# only proceed if at least one contour was found
					# print('Contours found: {}'.format(self.currentFrame.contours))
					if len(self.currentFrame.contours) > 0:
						# find the largest contour in the mask, then use
						# it to compute the minimum enclosing circle and
						# centroid
						c = max(self.currentFrame.contours, key=cv2.contourArea)
						((x, y), radius) = cv2.minEnclosingCircle(c)
						M = cv2.moments(c)
						center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

						# only proceed if the radius meets a minimum size
						if radius > 10:
							# draw the circle and centroid on the frame,
							# then update the list of tracked points
							# then print x/y offset from center and FPS -Jesse Moody
							cv2.circle(self.currentFrame.frame, (int(x), int(y)), int(radius),
								(0, 255, 255), 2)
							cv2.circle(self.currentFrame.frame, center, 5, (0, 0, 255), -1)
							x_offset = float((x-(self.res[0]/2))/(self.res[0]/2))  # float representing distance from screen center to face center
							y_offset = float(((self.res[1]/2)-int(y))/(self.res[1]/2))
							str1 = '(x, y): ({:.3f},{:.3f})'.format(x_offset, y_offset)
							cv2.putText(self.currentFrame.frame, str1, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
							# cv2.putText(currentFrame.frame, currentFPSstr, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1)
							# cv2.putText(frame, averageFPSstr, (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 2)
				except:  # Exception as e:
					# print(e)
					pass
				if cv2.waitKey(1) == ord("q"):
					self.stopped = True
				if not self.hudDoneQueue.full():
					self.hudDoneQueue.put(self.currentFrame,
										 block=True)  # Block is true so it will wait for other thread/process to finish
					# print("HUD2: {:.2f} Put frame {} to hudDoneQueue (hudDoneQueue size: {})".format((time.time() *
					# 																			   1000),
					# 																			  self.currentFrame.name,
					# 																			  self.hudDoneQueue.qsize()))
				else:  # hudDoneQueue is full
					self.hudDoneQueue.get()  # remove the oldest frame to make room for the new frame
					self.hudDoneQueue.put(self.currentFrame, block=True)

	def stop(self):
		self.stopped = True
