import time
import threading
import queue
import cv2
import base64
import os
from PIL import Image

class CustomThread (threading.Thread):
    def __init__(self, handler, delay=1):
        threading.Thread.__init__(self)
        self.__handler = handler
        self.__deplay = delay
        self.__stop = False
    
    def set_stop(self, stop):
        self.__stop = stop

    def set_delay(self, delay):
        self.__deplay = delay

    #override thread method
    def run(self):
        while not self.__stop:
            self.__handler()
            time.sleep(self.__deplay)


class CameraThread(threading.Thread):
    def __init__(self, cam_index=0):
        threading.Thread.__init__(self)
        self.__cam_index = cam_index
        self.cap = cv2.VideoCapture(cam_index)
        self.frame_queue = queue.Queue(maxsize=1)  # Only store one frame at a time
        self.daemon = True

    def run(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:  # If reading fails
                print("Error reading video stream.")
                break

            # Empty the queue before adding new frame
            while not self.frame_queue.empty():
                self.frame_queue.get()

            self.frame_queue.put(frame)

    def get_latest_frame(self):
        return self.frame_queue.get()