import numpy as np
import cv2
import imutils
from multiprocessing import Process
from multiprocessing import Queue
import time

# define lower/upper boundaries of the "green" ball in the HSV color space, then initialize list of tracked points
greenLower = (29, 86, 6)
greenUpper = (64, 255, 255)
# set video resolution
resWidth = 320
resLength = 240

class ColorTracker:

    def __init__(self, q1=None, q2=None, file1=None):
        # instance vars
        self.stopped = False
        self.cnts = (0,)
        self.xOffset = 0
        self.yOffset = 0
        # self.xyDoneQueue = Queue()  # put processed frames in here for the next object (HUD/serial) to use
        self.currentFrame = None
        self.mainQueue = q1  # mainQueue from shared memory space
        self.xyDoneQueue = q2
        self.file1 = file1

    # def start(self):
    #     self.p = Process(target=self.update, args=())
    #     self.p.daemon = True
    #     self.p.start()
    #     return self

    def update(self):
        while not self.stopped:
            if not self.mainQueue.empty():
                # time1 = time.time()
                self.currentFrame = self.mainQueue.get()
                self.file1.write("CT1: {:.2f} Got frame {} from mainQueue\n".format((time.time() * 1000), self.currentFrame.name))
                # blur frame, and convert it to the HSV color space
                blurred = cv2.GaussianBlur(self.currentFrame.frame, (11, 11), 0)
                hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
                # construct a mask for the color "green", then perform
                # a series of dilations and erosions to remove any small
                # blobs left in the mask
                mask = cv2.inRange(hsv, greenLower, greenUpper)
                mask = cv2.erode(mask, None, iterations=2)
                mask = cv2.dilate(mask, None, iterations=2)

                # find contours in the mask and initialize the current
                # (x, y) center of the ball
                self.cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                self.cnts = imutils.grab_contours(self.cnts)
                center = None

                # only proceed if at least one contour was found
                if len(self.cnts) > 0:
                    # #print("Contours found")
                    # find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
                    c = max(self.cnts, key=cv2.contourArea)
                    ((x, y), radius) = cv2.minEnclosingCircle(c)
                    M = cv2.moments(c)
                    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                    self.xOffset = float((x - (resWidth / 2)) / (
                                resWidth / 2))  # float representing distance from screen center to face center
                    self.yOffset = float(((resLength / 2) - int(y)) / (resLength / 2))
                    self.currentFrame.xOffset = self.xOffset
                    self.currentFrame.yOffset = self.yOffset
                # arduino.write(offsetStr.encode("{:.3f},{:.3f},{}".format(self.xOffset, self.yOffset, getTrackingStatus))) #need to implement this elsewhere
                else:
                    self.cnts = None
                self.currentFrame.contours = self.cnts  # attach contour data to frame
                if not self.xyDoneQueue.full():
                    self.xyDoneQueue.put(self.currentFrame, block=True)  # Block is true so it will wait for other thread/process to finish
                    self.file1.write("CT2: {:.2f} Put frame {} to xyDoneQueue (xyDoneQueue size: {})\n".format((time.time() *
                    1000), self.currentFrame.name, self.xyDoneQueue.qsize()))
                else:  # xyDoneQueue is full
                    self.xyDoneQueue.get()  # remove the oldest frame to make room for the new frame
                    self.xyDoneQueue.put(self.currentFrame, block=True)
                    self.file1.write( "CT2: {:.2f} xyDoneQueue full. Deleted oldest then put frame {} to xyDoneQueue \n"
                                     "xyDoneQueue size: {}".format((time.time() * 1000), self.currentFrame.name, self.xyDoneQueue.qsize()))
            else:
                pass
                #print("CT: {:.2f} mainQueue empty".format((time.time() * 1000)))
            # #print("CT: Get/process took {:.2f}s".format(time.time()-time1))
            # #print("No contours found")
            # cv2.imshow("HUD Preview", self.currentFrame.frame)
            # key = cv2.waitKey(1) & 0xFF
            # time2 = time.time()
            # fps = 1/(time2 - time1)
            # #print("time elapsed: {:.2f}".format(1/fps))
            # #print("fps: {:.2f}".format(fps))
        # elif int(time.time()) % 2 == 0:
        # 	#print("mainQueue empty")

    def stop(self):
        self.stopped = True

    def getTrackingStatus(self):
        if len(cnts) > 0:
            return 1
        else:
            return 0