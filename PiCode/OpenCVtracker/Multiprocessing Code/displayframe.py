import cv2
import imutils
from imutils.video import FPS
import numpy
import time

class DisplayFrame:
    def __init__(self, q=None, file=None):
        self.resizeDoneQueue = q
        self.stopped = False  # indicates if thread should be stopped
        self.currentFrame = None
        self.file = file #used for file logging
        self.done = False

    def show(self):
        #print("DF started")
        while not self.stopped:
            # print('resizeDoneQueue size: {}'.format(self.resizeDoneQueue.qsize()))
            if not self.resizeDoneQueue.empty():
                try:
                    self.currentFrame = self.resizeDoneQueue.get()
                    # print('DF0: resizeDoneQueue size: {}'.format(self.resizeDoneQueue.qsize()))
                    # print("DF1: {:.2f} Got frame {} from resizeDoneQueue. (resizeDoneQueue size: {})".format((time.time() * 1000), self.currentFrame.name, self.resizeDoneQueue.qsize()))
                    cv2.imshow('Video Preview', self.currentFrame.frame)
                    key = cv2.waitKey(1) & 0xFF
                except:
                    # print('displayframe error')
                    pass
                #print("DF2: {:.2f} Imshowed frame {} ".format((time.time() * 1000), self.currentFrame.name))
            # else:
            # 	#print("DF: {:.2f} resizeDoneQueue empty".format(time.time()*1000))
            if cv2.waitKey(1) == ord("q"):
                #print("waitKey(1) or q was pressed so stopping DF")
                self.stopped = True
                # self.file.close()
                self.done = True

    def stop(self):
        self.stopped = True