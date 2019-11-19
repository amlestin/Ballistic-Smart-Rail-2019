from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import time

class CurrentFrame:
    def __init__(self, frame=None):
        self.frame = frame
        self.name = 0
        self.timeStamp = 0
        self.xOffset = 0
        self.yOffset = 0
        self.contours = 0
        self.worker = ''


class PiVideoStream:
    def __init__(self, q=None, file1=None):
        self.mainQueue = q  # pull mainQueue from shared memory
        self.stopped = False
        self.time1 = time.time() * 1000
        self.file1 = file1

    # def start(self):
    #     # start the thread to read frames from the video stream
    #     self.p = Process(target=self.update, args=())
    #     self.p.daemon = True
    #     self.p.start()
    #     return self

    def update(self, resolution=(320, 240), framerate=32, awb_mode='auto'):
        self.camera = PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.awb_mode = awb_mode
        self.rawCapture = PiRGBArray(self.camera, size=resolution)
        self.stream = self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True)
        i = 0  # used for naming frames
        for f in self.stream:  # keep looping infinitely until the thread is stopped
            # grab the frame from the stream then clear the stream in preparation for the next frame
            frame = CurrentFrame()  # instantiate new CurrentFrame object for each frame
            frame.frame = f.array
            frame.timeStamp = (time.time() * 1000)
            self.file1.write("VS1: {:.2f} Got a frame from stream.\n".format(frame.timeStamp))
            # print("VS1: {:.2f} Got a frame from stream.\n".format(frame.timeStamp))
            self.rawCapture.truncate(0)
            frame.name = i
            i = i + 1
            if not self.mainQueue.full():
                self.mainQueue.put(frame)
                self.file1.write("VS2: {:.2f} Put frame {} from stream into mainQueue (mainQueue size: {})\n".format(
                    frame.timeStamp, frame.name, self.mainQueue.qsize()))
                # print("VS2: {:.2f} Put frame {} from stream into mainQueue (mainQueue size: {})\n".format(
                #     frame.timeStamp, frame.name, self.mainQueue.qsize()))
            else:
                self.file1.write("VS3: {:.2f} mainQueue full. Deleted oldest then put frame {} (mainQueue size: {})\n".format(
                    frame.timeStamp, frame.name, self.mainQueue.qsize()))
                self.mainQueue.get()
                self.mainQueue.put(frame)
            # if the thread indicator variable is set, stop the thread and resource camera resources
            if self.stopped:
                self.stream.close()
                self.rawCapture.close()
                self.camera.close()
                return

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
