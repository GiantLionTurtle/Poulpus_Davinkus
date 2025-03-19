import numpy as np
import cv2 as cv
from PIL import Image, ImageDraw
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt
from dataclasses import dataclass
from matplotlib import pyplot as plt

class ManipImageAdvanced:
    def __init__(self, pixmap=None):
        self.image = None
        self.pixmap = pixmap

    def _convertPixmapToCvImage(self, pixmap:QPixmap) -> np.ndarray:
        try:
            qimage = pixmap.toImage()
            qimage = qimage.convertToFormat(QImage.Format.Format_BGR888) #format for opencv
            width, height = qimage.width(), qimage.height()
            ptr = qimage.bits()
            ptr.setsize(qimage.sizeInBytes())
            arr = np.frombuffer(ptr, dtype=np.uint8)
            arr = np.reshape(arr,(height, width, 3))
            return arr
        except Exception as e:
            print(f"Error occured as e:{e}")

    def initalizeImage(self):
        image = self._convertPixmapToCvImage(self.pixmap)
        image_rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
        image_hsv = cv.cvtColor(image_rgb, cv.COLOR_RGB2HSV)
        image_gray = cv.cvtColor(image_rgb, cv.COLOR_RGB2GRAY)
        contours,hierarchy = cv.findContours(image_gray, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        cv.drawContours(image_rgb, contours, -1, (0,255,0), 3)
        #edges = cv.Canny(image_hsv, 1, 200)

        #Hough Transform
        # lines = cv.HoughLinesP(edges, 1, np.pi/180, 68, minLineLength=1, maxLineGap=250)
        # # Draw lines on the image
        # for line in lines:
        #     x1, y1, x2, y2 = line[0]
        #     cv.line(image_hsv, (x1, y1), (x2, y2), (255, 255, 255), 3)

        self.image = image_hsv

        plt.figure()
        plt.imshow(image_rgb)
        plt.show()

    
    
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

        #Peut-etre utile dans le futur
        # #Bounds to change with sliders, but static for now
        # lower_bound = np.array([0, 0, 50])
        # upper_bound = np.array([10, 120, 150])
        # #Use different masks depending on the different colors in an image generated automatically?
        # mask = cv.inRange(image_hsv, lower_bound, upper_bound)