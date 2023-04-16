import os
import sys
from Utils import *

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(ABSOLUTE_PATH, "FaceEngines/UltraFacesTorch"))
sys.path.append(os.path.join(ABSOLUTE_PATH, "FaceEngines/AgeitgeyFaces"))

from FaceEngines.UltraFacesTorch.Engine import FaceDetector
from FaceEngines.AgeitgeyFaces.Engine import FaceId

DEBUG_MODE = False

class FaceAI(object):

    def __init__(self, cameraId = 4):
        
        self.model = None
        self.cameraId = cameraId
        print("Capture Webcam Id: ", cameraId)

        self.camThread = CameraThread(cameraId)
        self.camThread.start()

        if DEBUG_MODE:
            cv2.namedWindow("test", cv2.WINDOW_NORMAL)
        
        self.catalogPath = os.path.join(ABSOLUTE_PATH, "FacesFolder/FaceBank")
        self.unknowPath = os.path.join(ABSOLUTE_PATH, "FacesFolder/Unknown")

        if not os.path.exists(self.catalogPath):
            os.makedirs(self.catalogPath)
        if not os.path.exists(self.unknowPath):
            os.makedirs(self.unknowPath)

        self.facedect = FaceDetector()
        self.faceid = FaceId(self.catalogPath)
        self.faceid.loadFacebank(reset=True)

    def addNewGuest(self, name, id):
        try:
            pathFaceFolderGuest = os.path.join(self.catalogPath, name)
            if not os.path.exists(pathFaceFolderGuest):
                os.makedirs(pathFaceFolderGuest)
            originalPath = os.path.join(self.unknowPath, id)
            destinationPath = os.path.join(pathFaceFolderGuest, id)
            os.rename(originalPath, destinationPath)
            self.faceid.loadFacebank(reset=True)
            print("Done to add new guest {0} with image {1}".format(name, id))
        except Exception as e:
            print("addNewGuest error: ", str(e))


    def predictGuest(self):
        
        nameGuest = None
        roiFace = None
        # os.path.join(self.catalogPath, "Tri/Cap1.jpg")
        frame = self.camThread.get_latest_frame()
        if frame is not None:
            boxFace = self.facedect.predict(frame)
            if len(boxFace) == 4:
                [y1, x2, y2, x1] = boxFace #known_face_locations [top, right, bottom, left]
                roiFace = frame[y1:y2, x1:x2].copy()
                nameGuest = self.faceid.infer(frame, [boxFace])[0] 
                frame = cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                frame = cv2.putText(frame, nameGuest, (x1, y2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 3, cv2.LINE_AA)
            
            if DEBUG_MODE:
                cv2.imshow("test", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    pass
        return nameGuest, roiFace