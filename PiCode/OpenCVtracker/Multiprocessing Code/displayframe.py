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
        standbyList = []  # used for holding frames if they're out of order
        i = 0
        j = 0
        failed = 0  # used to decide to skip a frame if certain num of failures occur

        #print("DF started")
        while not self.stopped:
            if not self.resizeDoneQueue.empty():
                self.currentFrame = self.resizeDoneQueue.get()
                # print("DF1: {:.2f} Got frame {} from resizeDoneQueue.\n".format((time.time() * 1000),
                #                                                                            self.currentFrame.name))
                self.file5.write("DF1: {:.2f} Got frame {} from {} via resizeDoneQueue.\n".format((time.time() * 1000), self.currentFrame.name, self.currentFrame.worker))
                self.file5.write("{}={}? ... ".format(int(self.currentFrame.name), i))
                if int(self.currentFrame.name) == i:
                    self.file5.write("yes\n")
                    self.file5.write("currentFrame.name:{} = i = {}\n".format(self.currentFrame.name, i))
                    cv2.imshow('Video Preview', self.currentFrame.frame)
                    key = cv2.waitKey(1) & 0xFF
                    self.file5.write("DF2: {:.2f} Imshowed frame {} \n".format((time.time() * 1000),
                                                                               self.currentFrame.name))
                    i += 1
                    while j != i:  # I'm essentially using j like a "new frame displayed" event
                        j = i
                        if len(standbyList) != 0:  # if standbyList isn't empty
                            z = 0
                            for x in standbyList:
                                self.file5.write("Checking standbyList[{}], frame {} in standbyList\n".format(z, x.name))
                                if int(x.name) == i:
                                    self.file5.write("x.name = i (({} = {}))\n".format(x.name, i))
                                    cv2.imshow('Video Preview', x.frame)
                                    key = cv2.waitKey(1) & 0xFF
                                    self.file5.write("DF2: {:.2f} Imshowed frame {} \n".format((time.time() * 1000),
                                                                                               x.name))
                                    standbyList.remove(x)
                                    i += 1
                                    self.file5.write("i+=1: i={}\n".format(i))
                                    break
                                z += 1
                else:
                    standbyList.append(self.currentFrame)
                    failed += 1
                    self.file5.write("no. failed++\n")
                    self.file5.write("Placed frame {} in standbyList\n".format(self.currentFrame.name))
                    if failed >= 4:
                        i = int(self.currentFrame.name)  # reset frame index (sorry this isn't more object oriented) :P
                        self.file5.write("i = {}\n".format(i))
                        failed = 0  # reset failure counter

            # else:
            # 	#print("DF: {:.2f} resizeDoneQueue empty".format(time.time()*1000))
            if cv2.waitKey(1) == ord("q"):
                print("waitKey(1) or q was pressed so stopping DF")
                self.stopped = True
                self.done.set()
                self.file5.close()

    def stop(self):
        self.stopped = True