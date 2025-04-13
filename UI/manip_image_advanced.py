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
        """Initialise la classe avec une image (QPixmap) et/ou un chemin de fichier.
        
        Args:
            pixmap (QPixmap): Image au format QPixmap
            file_path (str): Chemin vers le fichier image
        """
        self.image = None
        self.pixmap = pixmap
        self.file_path = file_path
        #Utile pour tests internes si la fonction pour tracer les cercles fonctionne
        self.circles = []

    def _convertPixmapToCvImage(self, pixmap:QPixmap) -> np.ndarray:
        """Convertit un QPixmap en image OpenCV (numpy array).
        
        Args:
            pixmap (QPixmap): Image source à convertir
            
        Retourne:
            np.ndarray: Image convertie au format BGR (3 canaux)
        """
        try:
            qimage = pixmap.toImage()
            qimage = qimage.convertToFormat(QImage.Format.Format_BGR888)
            width, height = qimage.width(), qimage.height()
            ptr = qimage.bits()
            ptr.setsize(qimage.sizeInBytes())
            arr = np.frombuffer(ptr, dtype=np.uint8)
            arr = np.reshape(arr,(height, width, 3))
            return arr
        except Exception as e:
            print(f"Error occured as e:{e}")

    def getImageName(self):
        """Extrait le nom du fichier image à partir du chemin complet.
        
        Returns:
            str: Le nom du fichier (ex: "heart.png")
        """
        try:
            return os.path.basename(os.path.normpath(self.file_path)) #returns following this format: heart.png
        except Exception as e:
            print(f"Error occured trying to get image name as:{e}")

    def initalizeImageFromPixmap(self):
        """Initialise l'image interne en convertissant le QPixmap en format HSV."""
        try:
            image = self._convertPixmapToCvImage(self.pixmap)
            image_hsv = cv.cvtColor(image, cv.COLOR_BGR2HSV)
            self.image = image_hsv

            #Test pour voir si l'image est bien en HSV
            plt.figure()
            plt.imshow(image_hsv)
            plt.show()

        except Exception as e:
            print(f"Error occured as:{e}")

    def applyMaskOnImage(self):
        """Applique un masque spécifique à l'image selon son nom.
        
        "Retourne" l'image binaire (une fois le masque appliqué) par l'entremise de l'attribut de la classe
        """

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

            #Visualiser les resultats pour confirmer le bon comportement de la fonction
            plt.figure()
            plt.imshow(masked_image)
            plt.show()

            self.image = masked_image
        except Exception as e:
            print(f"Error occured trying to apply mask on image:{e}")

    def findContours(self):
        """Détecte les contours dans l'image masquée.
        
        Retourne:
            list: Liste des contours détectés
        """
        try:
            img = self.image
            edges = cv.Canny(img, 100, 200)
            contours, _ = cv.findContours(edges, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
            #L'image masquée à une "shape" de 2 comme une image GRAY, utilise pour visualiser le résultat
            img_bgr = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            cv.drawContours(img_bgr, contours, -1, (0, 0, 255), 3)
            plt.figure()
            plt.imshow(img_bgr)
            plt.show()

            return contours
        except Exception as e:
            print(f"Error occured trying to find contours:{e}")

    def contourFiltering(self,contours):
        """Filtre les contours selon des critères spécifiques à chaque image.
        
        Args:
            contours: Liste des contours à filtrer
            
        Retourne:
            list: Contours filtrés
        """
        try:
            if(self.getImageName() == "heart.png"):
                contours_list = contours
            elif(self.getImageName() == "shrek.png"):
                contours_list = [contour for contour in contours if (len(contour) > 8 and cv.contourArea(contour) > 6)]
            elif(self.getImageName() == "canadien_logo.png"):
                contours_list = [contour for contour in contours if (cv.contourArea(contour) > 140)]
            elif(self.getImageName() == "capybara.png"):
                contours_list = contours
            elif(self.getImageName() == "Poulpus_Davinkus.jpg"):
                contours_list = []
                for contour in contours:
                    if (len(contour) >= 40 and cv.contourArea(contour) > 10):
                        contours_list.append(contour)
            elif(self.getImageName() == "fat_pikachu.png"):
                contours_list = [contour for contour in contours if (len(contour) >= 10 and cv.contourArea(contour) > 2)]

            #Visualise le résultat pour s'assurer que le filtrage s'est bien passé
            img = self.image
            img_bgr = cv.cvtColor(img, cv.COLOR_GRAY2RGB)
            cv.drawContours(img_bgr, contours_list, -1, (0, 0, 255), 3)
            plt.figure()
            plt.imshow(img_bgr)
            plt.show()
            return contours_list
        except Exception as e:
            print(f"Error occured trying to filter the contours:{e}")

    def _convertMm2Px(self,page_size,image_size,measure_to_convert):
        """Convertit une mesure en mm en pixels selon les dimensions de la page et de l'image.
        
        Args:
            page_size: Dimensions de la page en mm [hauteur, largeur]
            image_size: Dimensions de l'image en pixels [hauteur, largeur]
            measure_to_convert: Mesure en mm à convertir
            
        Retourne:
            float: Mesure convertie en pixels
        """
        try:
            page_height, page_width = page_size
            image_height, image_width = image_size
            x_conversion = image_width/page_width
            y_conversion = image_height/page_height
            #Utilise la plus petite conversion afin d'avoir au pire de la superposition, mais éviter d'être
            #en dehors des limites de la page
            if x_conversion > y_conversion:
                return y_conversion*measure_to_convert
            return x_conversion*measure_to_convert
        except Exception as e:
            print("Error occured while trying to convert the measurement from mm to px: {e}")
    
    
    def placeCircles(self, contours, circle_diameter, min_spacing):
        """Place des cercles le long des contours en respectant un espacement minimal.
        
        Args:
            contours: Liste des contours où placer les cercles
            circle_diameter: Diamètre des cercles en mm
            min_spacing: Espacement minimal entre cercles en mm
            
        Retourne:
            list: Liste des cercles placés au format (x,y,forme,couleur)
        """
        try:
            #Initialize list of circle centers
            circles_data = []
            comm_list = []

            #Convert the circle radius in mm to px
            circle_stamp_radius = round(self._convertMm2Px([195,175], [445,400], circle_diameter)/2)

            #Go through each contour in the list of all contours reassembled
            i=0
            for contour in contours:
                #Passe à travers toutes les coordonnées d'un contour
                for val in contour:
                    x = val[0,0]
                    y = val[0,1]
                    if x+circle_stamp_radius >= 400:
                        x = 400 - circle_stamp_radius
                    if x-circle_stamp_radius <=0:
                        x = circle_stamp_radius
                    if y+circle_stamp_radius >= 445:
                        y = 445-circle_stamp_radius
                    if y-circle_stamp_radius <= 0:
                        y = circle_stamp_radius
                    #Modifie le deuxième argument si désire moins de cercles
                    if self._isValueAlreadyPresent(x,y,min_spacing,circles_data):
                        continue

                    #Manipulation des données pour le visualiser plus tard avec drawCircles
                    center = (x,y)
                    circles_data.append(center)

                    #Format utilisé pour la communication et conversion en g-code
                    x_center = x
                    y_center = y
                    circle_shape = 'Cercle'
                    circle_color = 'Noir'
                    comm_list.append((x_center,y_center,circle_shape,circle_color))

                i = i+1
            
            self.circles = circles_data
            self.draw_circles([400,445],'white')

            return comm_list

        except Exception as e:
            print(f"Error occured trying to place circles: {e}")

    def _isValueAlreadyPresent(self,value_x, value_y,value_look_around,list):
        """Vérifie si un cercle existe déjà à proximité des coordonnées données.
        
        Args:
            value_x: Coordonnée x à vérifier
            value_y: Coordonnée y à vérifier
            value_look_around: Rayon de vérification
            list: Liste des cercles déjà placés
            
        Retourne:
            bool: True si un cercle proche existe déjà, False sinon
        """
        try:
            for point in list:
                norme = (value_x-point[0])**2 + (value_y-point[1])**2
                if (norme <= value_look_around**2):
                    return True
            return False
        except Exception as e:
            print(f"Error occured while trying to find if the value is already present: {e}")

    def draw_circles(self, image_size, background):
        """Dessine les cercles sur une image vierge pour visualisation.
        
        Args:
            image_size: Dimensions de l'image [largeur, hauteur]
            background: Couleur de fond de l'image
        """
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