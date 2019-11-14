import cv2
import imutils
from imutils.video import FPS
import numpy
import time

class DisplayFrame:
    def __init__(self, q=None, file1=None, done=None):
        self.resizeDoneQueue = q
        self.stopped = False  # indicates if thread should be stopped
        self.currentFrame = None
        self.file1 = file1 #used for file logging
        self.done = done

    def show(self):
        #print("DF started")
        while not self.stopped:
            if not self.resizeDoneQueue.empty():
                self.currentFrame = self.resizeDoneQueue.get()
                self.file1.write("DF1: {:.2f} Got frame {} from resizeDoneQueue.\n".format((time.time() * 1000), self.currentFrame.name))
                cv2.imshow('Video Preview', self.currentFrame.frame)
                key = cv2.waitKey(1) & 0xFF
                self.file1.write("DF2: {:.2f} Imshowed frame {} \n".format((time.time() * 1000), self.currentFrame.name))

            # else:
            # 	#print("DF: {:.2f} resizeDoneQueue empty".format(time.time()*1000))
            if cv2.waitKey(1) == ord("q"):
                print("waitKey(1) or q was pressed so stopping DF")
                self.stopped = True
                # self.file1.close()
                self.done.set()

    def stop(self):
        self.stopped = True