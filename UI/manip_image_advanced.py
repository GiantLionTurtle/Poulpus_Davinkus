import numpy as np
import cv2 as cv
from PIL import Image, ImageDraw
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt
from dataclasses import dataclass
from matplotlib import pyplot as plt
import os

class ManipImageAdvanced:
    def __init__(self, pixmap=None, file_path=None):
        self.image = None
        #Obtained as arguments when instancing the class
        self.pixmap = pixmap
        self.file_path = file_path

    def _convertPixmapToCvImage(self, pixmap:QPixmap) -> np.ndarray:
        try:
            qimage = pixmap.toImage()
            #format for opencv
            qimage = qimage.convertToFormat(QImage.Format.Format_BGR888)
            width, height = qimage.width(), qimage.height()
            ptr = qimage.bits()
            ptr.setsize(qimage.sizeInBytes())
            arr = np.frombuffer(ptr, dtype=np.uint8)
            #Change to 4 probably if I want alpha, but should check with pixmap doc if possible
            arr = np.reshape(arr,(height, width, 3))
            return arr
        except Exception as e:
            print(f"Error occured as e:{e}")

    def getImageName(self):
        try:
            #print(os.path.basename(os.path.normpath(self.file_path)))
            return os.path.basename(os.path.normpath(self.file_path)) #returns following this format: heart.png
        except Exception as e:
            print(f"Error occured trying to get image name as:{e}")

    def initalizeImageFromPixmap(self):
        try:
            image = self._convertPixmapToCvImage(self.pixmap)
            #Convert to HSV format
            image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
            self.image = image_hsv
        except Exception as e:
            print(f"Error occured as:{e}")

    def transparentBackground(self):
        if self.image is None:
            raise ValueError("Must run intializeImageFromPixmap first")
        #If the image has 4 channels, it has an alpha channel (means transparent background)
        if self.image.shape[2] == 4:
            return 1
        else:
            return 0
        #To implement later if pixmap allows for 4 channels
        # if self.transparentBackground():
        #     #Obtain the alpha channel to use for masks
        #     alpha = self.image[:,:,3]

    def applyMaskOnImage(self):
        if self.image is None:
            raise ValueError("Must run intializeImageFromPixmap first")
        image_hsv = self.image
        if(self.getImageName() == "heart.png"):
            lower_bound = np.array([0, 0, 50])
            upper_bound = np.array([20, 255, 255])
            mask_red = cv.inRange(image_hsv, lower_bound, upper_bound)
            lower_bound2 = np.array([0, 0, 200])
            upper_bound2 = np.array([180, 210, 255])
            mask_white = cv.inRange(image_hsv, lower_bound2, upper_bound2)
            masked_image = cv.subtract(mask_red, mask_white)
        elif(self.getImageName() == "shrek.png"):
            lower_bound = np.array([0, 0, 50])
            upper_bound = np.array([10, 255, 255])
            mask_green = cv.inRange(image_hsv, lower_bound, upper_bound)
            masked_image = cv.bitwise_and(image_hsv, image_hsv, mask=mask_green)
        elif(self.getImageName() == "nemo.png"):
            lower_bound = np.array([0, 0, 50])
            upper_bound = np.array([10, 255, 255])
        elif(self.getImageName() == "canadiens_logo.png"):
            lower_bound = np.array([0, 0, 50])
            upper_bound = np.array([10, 255, 255])
        elif(self.getImageName() == "capybara.png"):
            lower_bound = np.array([0, 0, 50])
            upper_bound = np.array([10, 255, 255])
        elif(self.getImageName() == "Poulpus_Davinkus.jpg"):
            lower_bound = np.array([0, 0, 50])
            upper_bound = np.array([10, 255, 255])
        elif(self.getImageName() == "fat_pikachu.png"):
            lower_bound = np.array([0, 0, 50])
            upper_bound = np.array([10, 255, 255])

        plt.figure()
        plt.imshow(masked_image)
        plt.show()

        self.image = masked_image
    
    
    def convertGcode(self, output_path, paper_size, image_size):
    
        gcode = []

        max_x, max_y = image_size
        paper_width, paper_height = paper_size

        for x, y in self.circles:
            x_mm = (x / max_x) * paper_width
            y_mm = paper_height - (y / max_y) * paper_height

            gcode.append(f"G1 Z{-10}")
            gcode.append(f"G1 X{x_mm:.2f} Y{y_mm:.2f}")
            gcode.append(f"G1 Z{10}")

        with open(output_path, "w") as txt_file:
            for line in gcode:
                txt_file.write("".join(line) + "\n")

        #Hough Transform
        # lines = cv.HoughLinesP(edges, 1, np.pi/180, 68, minLineLength=1, maxLineGap=250)
        # # Draw lines on the image
        # for line in lines:
        #     x1, y1, x2, y2 = line[0]
        #     cv.line(image_hsv, (x1, y1), (x2, y2), (255, 255, 255), 3)