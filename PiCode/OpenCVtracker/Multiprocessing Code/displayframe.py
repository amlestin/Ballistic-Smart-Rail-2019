import cv2
import imutils
from imutils.video import FPS
import numpy
import time

f = FPS()

class DisplayFrame:
    def __init__(self, q=None):
        self.xyDoneQueue = q
        self.stopped = False  # indicates if thread should be stopped
        self.currentFrame = None

    def show(self):
        #print("DF started")
        while not self.stopped:
            if not (self.xyDoneQueue.empty()):
                self.currentFrame = self.xyDoneQueue.get()
                # self.frame = imutils.resize(self.currentFrame, width=1000)
                #print("DF1: {:.2f} Got frame {} from xyDoneQueue".format((time.time() * 1000), self.currentFrame.name))
                cv2.imshow("HUD Preview", self.currentFrame.frame)
                key = cv2.waitKey(1) & 0xFF
                # f.start()
                # for x in range(30):
                #     cv2.imshow("HUD Preview", self.currentFrame.frame)
                #     key = cv2.waitKey(1) & 0xFF
                #     f.update()
                # f.stop()
                # print(f.fps())
                #print("DF2: {:.2f} Imshowed frame {} ".format((time.time() * 1000), self.currentFrame.name))
            # f._numFrames = 0
            # else:
            # 	#print("DF: {:.2f} xyDoneQueue empty".format(time.time()*1000))
            if cv2.waitKey(1) == ord("q"):
                #print("waitKey(1) or q was pressed so stopping DF")
                self.stopped = True

    def stop(self):
        self.stopped = True