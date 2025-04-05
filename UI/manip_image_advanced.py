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

    #Might not be useful afterall
    def transparentBackground(self):
        if self.image is None:
            raise ValueError("Must run intializeImageFromPixmap first")
        #If the image has 4 channels, it has an alpha channel (means transparent background)
        if self.image.shape[2] == 4:
            return 1
        else:
            return 0

    def applyMaskOnImage(self):
        if self.image is None:
            raise ValueError("Must run intializeImageFromPixmap first")
        try:
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
                lower_bound = np.array([0, 0, 0])
                upper_bound = np.array([180, 0, 255])
                mask_black = cv.inRange(image_hsv, lower_bound, upper_bound)
                masked_image = cv.bitwise_not(mask_black)
            elif(self.getImageName() == "nemo.png"):
                lower_bound = np.array([0, 0, 0])
                upper_bound = np.array([180, 0, 255])
                lower_bound2 = np.array([0, 0, 0])
                upper_bound2 = np.array([180, 0, 55])
                mask_white = cv.inRange(image_hsv, lower_bound, upper_bound)
                mask_white2 = cv.inRange(image_hsv, lower_bound2, upper_bound2)
                masked_image = cv.bitwise_not(mask_white2)
            elif(self.getImageName() == "canadien_logo.png"):
                #Make sure when we apply the stamps we dont put a stamp for the little circle
                lower_bound = np.array([0, 0, 0])
                upper_bound = np.array([180, 0, 255])
                mask_white = cv.inRange(image_hsv, lower_bound, upper_bound)
                masked_image = cv.bitwise_not(mask_white)
            elif(self.getImageName() == "capybara.png"):
                lower_bound = np.array([0, 0, 0])
                upper_bound = np.array([180, 0, 255])
                mask_white = cv.inRange(image_hsv, lower_bound, upper_bound)
                masked_image = cv.bitwise_not(mask_white)
            elif(self.getImageName() == "Poulpus_Davinkus.jpg"):
                lower_bound = np.array([160, 50, 50])
                upper_bound = np.array([180, 255, 255])
                mask_pink = cv.inRange(image_hsv, lower_bound, upper_bound)
                lower_bound2 = np.array([109, 73, 225])
                upper_bound2 = np.array([180, 255, 255])
                mask_pink_light = cv.inRange(image_hsv, lower_bound2, upper_bound2)
                masked_image = cv.subtract(mask_pink, mask_pink_light)
            elif(self.getImageName() == "fat_pikachu.png"):
                lower_bound = np.array([0, 0, 0])
                upper_bound = np.array([180, 0, 255])
                mask_white = cv.inRange(image_hsv, lower_bound, upper_bound)
                masked_image = cv.bitwise_not(mask_white)

            # plt.figure()
            # plt.imshow(masked_image)
            # plt.show()

            self.image = masked_image
        except Exception as e:
            print(f"Error occured trying to apply mask on image:{e}")

    def findContours(self):
        try:
            img = self.image
            edges = cv.Canny(img, 100, 200)
            contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
            print(f"Number of contours: {len(contours)}")
            #Let us see the contours, masked image has shape == 2 just as grayscale
            img_bgr = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            # cv.drawContours(img_bgr, contours, -1, (0, 0, 255), 2)

            # plt.figure()
            # plt.imshow(img_bgr)
            # plt.show()

            return contours
        except Exception as e:
            print(f"Error occured trying to find contours:{e}")
    
    def _isNearBackground(self, contour, mask, pixel_tolerance):
        try:
            # Create a temporary mask to check neighborhood
            temp_mask = np.zeros_like(mask, dtype=np.uint8)

            # Get coordinates of contour pixels
            ys, xs = np.where(temp_mask == 255)
            
            for y, x in zip(ys, xs):
                # Check surrounding pixels in a square of size (2*tolerance + 1)
                x_min = max(0, x - pixel_tolerance)
                x_max = min(mask.shape[1] - 1, x + pixel_tolerance)
                y_min = max(0, y - pixel_tolerance)
                y_max = min(mask.shape[0] - 1, y + pixel_tolerance)
                
                # Extract the neighborhood region
                neighborhood = mask[y_min:y_max+1, x_min:x_max+1]
                
                # Check if any background pixel exists nearby
                if np.any(np.all(neighborhood == [0, 0, 0], axis=-1)):
                    return True
            return False
        except Exception as e:
            print(f"Error occured trying to check if contour is near background:{e}")

    def contourFiltering(self,contours):
        try:
            if(self.getImageName() == "heart.png"):
                contours_list = contours
            elif(self.getImageName() == "shrek.png"):
                for contour in contours:
                    print(f"Contour area: {cv.contourArea(contour)}")
                    print(f"Contour length: {len(contour)}")
                contours_list = [contour for contour in contours if (len(contour) > 8 and cv.contourArea(contour) > 6)]
                print(f"Number of contours after filtering: {len(contours_list)}")
                for contour in contours_list:
                    print(f"Contour area: {cv.contourArea(contour)}")
                    print(f"Contour length: {len(contour)}")
            #Skipped pour l'instant
            elif(self.getImageName() == "nemo.png"):
                for contour in contours:
                    print(f"Contour area: {cv.contourArea(contour)}")
                    print(f"Contour length: {len(contour)}")
                contours_list = [contour for contour in contours if (len(contour) >= 8)]
                print(f"Number of contours after filtering: {len(contours_list)}")
            elif(self.getImageName() == "canadien_logo.png"):
                for contour in contours:
                    print(f"Contour area: {cv.contourArea(contour)}")
                    print(f"Contour length: {len(contour)}")
                contours_list = [contour for contour in contours if (cv.contourArea(contour) > 140)]
                print(f"Number of contours after filtering: {len(contours_list)}")
                for contour in contours_list:
                    print(f"Contour area: {cv.contourArea(contour)}")
                    print(f"Contour length: {len(contour)}")
            elif(self.getImageName() == "capybara.png"):
                contours_list = contours
            #Skipped pour l'instant
            elif(self.getImageName() == "Poulpus_Davinkus.jpg"):
                contours_list = []
                for contour in contours:
                    if (len(contour) >= 40 and cv.contourArea(contour) > 10) or (self._isNearBackground(contour, self.image,1)):
                        contours_list.append(contour)
                for contour in contours_list:
                    print(f"Contour area: {cv.contourArea(contour)}")
                    print(f"Contour length: {len(contour)}")
                print(f"Number of contours after filtering: {len(contours_list)}")
            elif(self.getImageName() == "fat_pikachu.png"):
                contours_list = [contour for contour in contours if (len(contour) >= 10 and cv.contourArea(contour) > 2)]
                for contour in contours_list:
                    print(f"Contour area: {cv.contourArea(contour)}")
                    print(f"Contour length: {len(contour)}")
                print(f"Number of contours after filtering: {len(contours_list)}")

            #Test if the filtering is correct
            # img = self.image
            # img_bgr = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            # cv.drawContours(img_bgr, contours_list, -1, (0, 0, 255), 3)
            # plt.figure()
            # plt.imshow(img_bgr)
            # plt.show()
            return contours_list
        except Exception as e:
            print(f"Error occured trying to filter the contours:{e}")
    
    def reassembleContours(self, contours):
        try:
            valid_contours = [contour for contour in contours if len(contour) > 0]
            
            if not valid_contours:
                print("Warning: No valid contours found!")
                return np.array([])

            one_contour = np.concatenate(valid_contours)

            #Test if contour reassembles correctly
            img = self.image
            img_bgr = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            cv.drawContours(img_bgr, one_contour, -1, (0, 0, 255), 3)
            plt.figure()
            plt.imshow(img_bgr)
            plt.show()
            return one_contour
        except Exception as e:
            print(f"Error occured trying to reassemble contours:{e}")
    
    def fillContours(self, contours):
        try:
            print('Hello')
        except Exception as e:
            print(f"Error occured trying to fill contours with stamps:{e}")

        #Hough Transform
        # lines = cv.HoughLinesP(edges, 1, np.pi/180, 68, minLineLength=1, maxLineGap=250)
        # # Draw lines on the image
        # for line in lines:
        #     x1, y1, x2, y2 = line[0]
        #     cv.line(image_hsv, (x1, y1), (x2, y2), (255, 255, 255), 3)