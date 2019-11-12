import cv2
import imutils
from imutils.video import FPS
import numpy
import time

f = FPS()

class DisplayFrame:
    def __init__(self, q=None, file=None):
        self.hudDoneQueue = q
        self.stopped = False  # indicates if thread should be stopped
        self.currentFrame = None
        self.file = file #used for file logging
        self.done = False

    def show(self):
        #print("DF started")
        while not self.stopped:
            if not (self.hudDoneQueue.empty()):
                self.currentFrame = self.hudDoneQueue.get()
                self.currentFrame.frame = imutils.resize(self.currentFrame.frame, width=1000)
                # print('DF0: hudDoneQueue size: {}'.format(self.hudDoneQueue.qsize()))
                #print("DF1: {:.2f} Got frame {} from hudDoneQueue".format((time.time() * 1000), self.currentFrame.name))
                cv2.imshow("HUD Preview", self.currentFrame.frame)
                key = cv2.waitKey(1) & 0xFF
                # self.file.write('{}\n'.format(self.currentFrame.timeStamp)) #uncomment for logging timestamps
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
            # 	#print("DF: {:.2f} hudDoneQueue empty".format(time.time()*1000))
            if cv2.waitKey(1) == ord("q"):
                #print("waitKey(1) or q was pressed so stopping DF")
                self.stopped = True
                # self.file.close()
                self.done = True

    def stop(self):
        self.stopped = True