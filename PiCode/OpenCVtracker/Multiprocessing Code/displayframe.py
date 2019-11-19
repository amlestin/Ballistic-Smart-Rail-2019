import cv2
import imutils
from imutils.video import FPS
import numpy
import time

class DisplayFrame:
    def __init__(self, q=None, file5=None, done=None):
        self.resizeDoneQueue = q
        self.stopped = False  # indicates if thread should be stopped
        self.currentFrame = None
        self.file5 = file5  # used for file logging
        self.done = done

    def show(self):
        #print("DF started")
        self.file5.write('testy mcTestFace')
        while not self.stopped:
            if not self.resizeDoneQueue.empty():
                self.currentFrame = self.resizeDoneQueue.get()
                # print("DF1: {:.2f} Got frame {} from resizeDoneQueue.\n".format((time.time() * 1000),
                #                                                                            self.currentFrame.name))
                self.file5.write("DF1: {:.2f} Got frame {} from {} via resizeDoneQueue.\n".format((time.time() * 1000), self.currentFrame.name, self.currentFrame.worker))
                cv2.imshow('Video Preview', self.currentFrame.frame)
                key = cv2.waitKey(1) & 0xFF
                self.file5.write("DF2: {:.2f} Imshowed frame {} \n".format((time.time() * 1000), self.currentFrame.name))

            # else:
            # 	#print("DF: {:.2f} resizeDoneQueue empty".format(time.time()*1000))
            if cv2.waitKey(1) == ord("q"):
                print("waitKey(1) or q was pressed so stopping DF")
                self.stopped = True
                self.done.set()

    def stop(self):
        self.stopped = True