from vision.ssd.config.fd_config import define_img_size
from vision.ssd.mb_tiny_RFB_fd import create_Mb_Tiny_RFB_fd, create_Mb_Tiny_RFB_fd_predictor
import cv2
import numpy as np

import os
ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))

class FaceDetector(object):

    def __init__(self):

        self.__inputSize = 320
        self.__candidateSize = 100
        self.__threshold = 0.7

        define_img_size(self.__inputSize)

        numClasses = 2
        testDevice = "cuda:0"
        modelPath = "models/version-RFB-320.pth"
        modelPath = os.path.join(ABSOLUTE_PATH, modelPath)

        net = create_Mb_Tiny_RFB_fd(numClasses, is_test=True, device=testDevice)
        self.__predictor = create_Mb_Tiny_RFB_fd_predictor(
            net, candidate_size=self.__candidateSize, device=testDevice)

        net.load(modelPath)

    def predict(self, orig_image):
        face_box = []
        
        image = cv2.cvtColor(orig_image, cv2.COLOR_BGR2RGB)
        boxes, labels, probs = self.__predictor.predict(image, 
                            self.__candidateSize / 2, self.__threshold)
        num_face = boxes.size(0)
        
        height, width = orig_image.shape[:2]
        center_x = width / 2
        center_y = height / 2
        most_center_distance = np.sqrt(height*height + width*width)
        offset = 10
        for i in range(num_face):
            box = boxes[i, :]
            x1 = int(max(0, min(box[0] - offset, width)))
            y1 = int(max(0, min(box[1] - offset, height)))
            x2 = int(max(0, min(box[2] + offset, width)))
            y2 = int(max(0, min(box[3] + offset, height)))

            h = (y1+y2/2) - center_y
            w = (x1+x2/2) - center_x
            center_distance = np.sqrt(h*h + w*w)
            if center_distance < most_center_distance:
                most_center_distance = center_distance
                face_box = [y1, x2, y2, x1]

        return face_box