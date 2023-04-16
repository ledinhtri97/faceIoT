import face_recognition
import cv2
import numpy as np
from pathlib import Path

class FaceId(object):
    
    def __init__(self, pathFaceBank):

        self.__pathFaceBank = pathFaceBank
        self.__tolerance = 0.5

    
    def loadFacebank(self, reset=False):

        if reset:
            self.__prepareFacebank()
        else:
            facebank_path = Path(self.__pathFaceBank)/'facebank.npy'
            name_path = Path(self.__pathFaceBank)/'names.npy'
            if facebank_path.is_file() and name_path.is_file():
                self.__targets = np.load(facebank_path)
                self.__names = np.load(name_path)
            else:
                self.__prepareFacebank()

    def __prepareFacebank(self):
    
        print("Prepare Facebank")

        self.__targets = []
        self.__names = []

        facebank_path = Path(self.__pathFaceBank)
        for path in facebank_path.iterdir():
            if path.is_file():
                continue
            else:
                for file in path.iterdir():
                    if not file.is_file():
                        continue
                    else:
                        try:
                            img = face_recognition.load_image_file(file)
                        except:
                            continue
                        facebox = [0, img.shape[1], img.shape[0], 0]
                        face_encodings = face_recognition.face_encodings(img, known_face_locations=[facebox])
                        
                        face_encoding = face_encodings[0]
                        self.__targets.append(face_encoding)
                        self.__names.append(path.name)

        self.__targets = np.array(self.__targets)
        self.__names = np.array(self.__names)
        np.save(facebank_path/'facebank', self.__targets)
        np.save(facebank_path/'names', self.__names)
        
        return self.__targets, self.__names
    
    def infer(self, frame, face_locations):
        '''
        frame : cv mat
        return: #face_names
        '''
        
        # small_frame = cv2.resize(frame, (0, 0), fx=1, fy=1)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.__targets, face_encoding, tolerance=self.__tolerance)
            name = None #Unknown
            # # If a match was found in self.__targets, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(self.__targets, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.__names[best_match_index]

                # print("matches best_match_index: ", best_match_index)
                # print("list __names: ", self.__names)
                # print("list face_distances: ", face_distances)
            face_names.append(name)
        
        return face_names