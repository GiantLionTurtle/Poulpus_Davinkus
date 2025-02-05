import numpy as np
import cv2 as cv

class ManipImage:
    def __init__(self, image):
        self.image = image

    def getCvImage(self,file_path):
        try:
            self.image = cv.imread(file_path)
            return self.image
        except Exception as e:
            print(f"Error occured as e:{e}")

    def imageAnalysis(self,file_path, stampDiameter=None, threshold=None):
        try:
            self.image = cv.imread(file_path, cv.IMREAD_GRAYSCALE)
            print(self.image.data)
            print(self.image.shape)
            return self.image
        except Exception as e:
            print(f"Error occured while trying to analyze the image: {e}")