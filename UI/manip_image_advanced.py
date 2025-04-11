import numpy as np
import cv2 as cv
from PIL import Image, ImageDraw
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt
from dataclasses import dataclass
from matplotlib import pyplot as plt
import os
from typing import List, Dict
import itertools
import array as arr
import math

class ManipImageAdvanced:
    def __init__(self, pixmap=None, file_path=None):
        self.image = None
        #Obtained as arguments when instancing the class
        self.pixmap = pixmap
        self.file_path = file_path
        #To draw circles, for tests purposes only, remove once tests have been done
        self.circles = []

    # @dataclass
    # class AnalysisData:
    #     circles: list
    #     circles_shape: list
    #     circles_color: list

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
            return os.path.basename(os.path.normpath(self.file_path)) #returns following this format: heart.png
        except Exception as e:
            print(f"Error occured trying to get image name as:{e}")

    def initalizeImageFromPixmap(self):
        try:
            image = self._convertPixmapToCvImage(self.pixmap)
            #Convert to HSV format
            image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
            self.image = image_hsv

            plt.figure()
            plt.imshow(image_hsv)
            plt.show()

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
                mask_white = cv.inRange(image_hsv, lower_bound, upper_bound)
                masked_image = cv.bitwise_not(mask_white)
            elif(self.getImageName() == "canadien_logo.png"):
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

            plt.figure()
            plt.imshow(masked_image)
            plt.show()

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
            cv.drawContours(img_bgr, contours, -1, (0, 0, 255), 3)
            plt.figure()
            plt.imshow(img_bgr)
            plt.show()

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
            img = self.image
            img_bgr = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            cv.drawContours(img_bgr, contours_list, -1, (0, 0, 255), 3)
            plt.figure()
            plt.imshow(img_bgr)
            plt.show()
            return contours_list
        except Exception as e:
            print(f"Error occured trying to filter the contours:{e}")
    
    def reassembleContours(self, contours):
        try:          
            # We'll process contours into groups that should be connected
            contour_groups = []
            
            for current_contour in contours:
                matched = False
                
                # Check against existing groups
                for group in contour_groups:
                    # Get all endpoints in this group
                    group_endpoints = []
                    for contour in group:
                        group_endpoints.append(contour[0][0])  # start point
                        group_endpoints.append(contour[-1][0])  # end point
                    
                    # Get current contour's endpoints
                    current_start = current_contour[0][0]
                    current_end = current_contour[-1][0]
                    
                    # Check if any endpoint is close to any in the group, change 5 for threshold to look around
                    for point in group_endpoints:
                        if (np.linalg.norm(point - current_start) < 5 or 
                            np.linalg.norm(point - current_end) < 5):
                            group.append(current_contour)
                            matched = True
                            break
                    if matched:
                        break
                
                # If no match found, create a new group
                if not matched:
                    contour_groups.append([current_contour])
            
            # Now merge contours within each group
            merged_contours = []
            for group in contour_groups:
                if len(group) == 1:
                    merged_contours.append(group[0])
                else:
                    # Start with first contour in group
                    merged = group[0]
                    
                    for contour in group[1:]:
                        merged_start = merged[0][0]
                        merged_end = merged[-1][0]
                        contour_start = contour[0][0]
                        contour_end = contour[-1][0]
                        
                        # Find best connection
                        dists = {
                            'start-end': np.linalg.norm(merged_start - contour_end),
                            'end-start': np.linalg.norm(merged_end - contour_start),
                            'start-start': np.linalg.norm(merged_start - contour_start),
                            'end-end': np.linalg.norm(merged_end - contour_end)
                        }
                        
                        min_key = min(dists, key=dists.get)
                        
                        if min_key == 'start-end':
                            merged = np.concatenate([contour[::-1], merged])
                        elif min_key == 'end-start':
                            merged = np.concatenate([merged, contour])
                        elif min_key == 'start-start':
                            merged = np.concatenate([contour[::-1], merged])
                        elif min_key == 'end-end':
                            merged = np.concatenate([merged, contour[::-1]])
                    
                    merged_contours.append(merged)

            print(f'Nombre de contours desormais:{len(merged_contours)}')

            #Semble pas vraiment aider maintenant que trace les contours, pas l'interieur
            #Adjustments specific for each picture:
            # if self.getImageName() == "heart.png":
            #     contour1 = merged_contours[0]
            #     contour2 = merged_contours[3]

            #     merged = np.concatenate([contour1,contour2[::-1]])
                
            #     merged_contours[0] = merged
            #     del merged_contours[3]
               
            #     if len(merged_contours) >3:
            #         i = len(merged_contours)-1
            #         while len(merged_contours) != 3:
            #             del merged_contours[i]
            #             i = i-1
            # if self.getImageName() == "shrek.png":
            #     contour0 = merged_contours[0]
            #     contour1 = merged_contours[1]

            #     merged = np.concatenate([contour1[::-1],contour0])

            #     merged_contours[0] = merged
            #     del merged_contours[1]
            
            #Test if contours reassemble correctly
            img = self.image
            img_bgr = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            cv.drawContours(img_bgr, merged_contours, -1, (0, 0, 255), 3)
            plt.figure()
            plt.imshow(img_bgr)
            plt.show()

            return merged_contours
            
        except Exception as e:
            print(f"Error occurred trying to reassemble contours: {e}")
            return []

    def _convertMm2Px(self,page_size,image_size,measure_to_convert):
        try:
            page_height, page_width = page_size
            image_height, image_width = image_size
            x_conversion = image_width/page_width
            y_conversion = image_height/page_height
            #Want to take the smallest between the two so that at worst some overlapping, but not outside
            #the range of the sheet on the robot or creating a weird shape
            if x_conversion > y_conversion:
                return y_conversion*measure_to_convert
            return x_conversion*measure_to_convert
        except Exception as e:
            print("Error occured while trying to convert the measurement from mm to px: {e}")
    
    
    def placeCircles(self, contours, circle_diameter, min_spacing):
        try:
            #Initialize list of circle centers
            circles_data = []
            gcode_list = []

            #Convert the circle radius in mm to px
            circle_stamp_radius = round(self._convertMm2Px([195,175], [445,400], circle_diameter)/2)

            #Determine the minimum distance between the circle centers, in px
            min_distance = round(circle_stamp_radius + min_spacing, None)

            #Go through each contour in the list of all contours reassembled
            i=0
            for contour in contours:
                #print(f"Index du contour:{i}")
                #Go through all coordinates for a contour
                for val in contour:
                    x = val[0,0]
                    #print(f"X:{x}")
                    y = val[0,1]
                    #print(f"Y:{y}")
                    if x+circle_stamp_radius >= 400:
                        x = 400 - circle_stamp_radius
                    if x-circle_stamp_radius <=0:
                        x = circle_stamp_radius
                    if y+circle_stamp_radius >= 445:
                        y = 445-circle_stamp_radius
                    if y-circle_stamp_radius <= 0:
                        y = circle_stamp_radius
                    #Can change the second argument if want less circles
                    if self._isValueAlreadyPresent(x,y,min_spacing,circles_data):
                        continue
                    center = (x,y)
                    circles_data.append(center)

                    x_center = x
                    y_center = y
                    circle_shape = 'Cercle'
                    circle_color = 'Noir'
                    gcode_list.append((x_center,y_center,circle_shape,circle_color))

                i = i+1
            self.circles = circles_data
            self.draw_circles([400,445],'white')

            return gcode_list

        except Exception as e:
            print(f"Error occured trying to place circles: {e}")

    def _isValueAlreadyPresent(self,value_x, value_y,value_look_around,list):
        try:
            for point in list:
                #print(f"X dans fct:{point[0]}")
                # temp = value_look_around
                # while temp >= -value_look_around:
                #     if point[0] - temp == value_x:
                #         return True
                #     if point[1] - temp == value_y:
                #         return True
                #     temp = temp-1
                norme = (value_x-point[0])**2 + (value_y-point[1])**2
                print(f"Valeur de Max:{norme}")
                if (norme <= value_look_around**2):
                    return True
            return False
        except Exception as e:
            print(f"Error occured while trying to find if the value is already present: {e}")

    def draw_circles(self, image_size, background, ):
        output_image = Image.new("RGB", image_size, background)
        draw = ImageDraw.Draw(output_image)
        circle_radius = self._convertMm2Px([195,175], [445,400], 20.0)/2

        for x, y in self.circles:
            draw.ellipse(
                [x - circle_radius, y - circle_radius, x + circle_radius, y + circle_radius],
                outline="red",
                width=2
            )

        plt.figure()
        plt.imshow(output_image)
        plt.show()