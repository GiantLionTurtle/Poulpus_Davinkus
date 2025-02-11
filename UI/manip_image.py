import numpy as np
import cv2 as cv
from PIL import Image, ImageDraw
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt

class ManipImage:
    def __init__(self, circle_radius=10, file_path=None, pixmap=None):
        self.image = None
        self.file_path = file_path
        self.pixmap = pixmap
        self.circle_radius = circle_radius
        self.circles = []

    def _convertPixmapToCvImage(self, pixmap:QPixmap) -> np.ndarray:
        try:
            # image = []
            # for pixel in pixmap.trueMatrix(,pixmap.width(),pixmap.height()):
            #     image.append(pixel)
            # return np.array(image)
            # qimage = QPixmap.toImage(pixmap)
            # return self._convertQtImageToCvImage(qimage)
            print("A developper")
            print("test")
        except Exception as e:
            print(f"Error occured as e:{e}")

    def _convertQtImageToCvImage(self, qimage: QImage) -> np.ndarray:
        try:
            # image = []
            # for pixel in qimage.pixelColor():
            #     image.append([pixel.red(), pixel.green(), pixel.blue()])
            # return np.array(image)
            print("A developper")
        except Exception as e:
            print(f"Error occured as e:{e}")
    
    def setCvImage(self):
        try:
            self.image = cv.imread(self.file_path)
            return self.image
        except Exception as e:
            print(f"Error occured as e:{e}")

    # def imageAnalysis(self):
    #     try:
    #         self.image = cv.imread(self.file_path, cv.IMREAD_GRAYSCALE)
    #         return self.image
    #     except Exception as e:
    #         print(f"Error occured while trying to analyze the image: {e}")

    def load_image(self):
        if self.file_path is None:
            self.image = self._convertPixmapToCvImage(self.pixmap)
        elif self.pixmap is None:
            self.image = Image.open(self.file_path).convert("L")
        return self.image

    def analyze_image(self):
        if self.image is None:
            raise ValueError("Image not loaded. Call load_image() first.")
        
        # Convert the image to a NumPy array with type uint8
        img_array = np.array(self.image.convert("L"), dtype=np.uint8)
        
        # Apply a binary threshold to isolate the shape (heart)
        _, binary_img = cv.threshold(img_array, 50, 255, cv.THRESH_BINARY)

        # Grid sampling (convert analog to discrete image) to detect areas to stamp
        height, width = binary_img.shape
        step = self.circle_radius * 2  # Distance between circle centers

        for y in range(0, height, step):
            for x in range(0, width, step):
                # Check if the grid has white pixels (sum=0)
                if binary_img[y:y + step, x:x + step].sum() > 0:
                    self.circles.append((x, y))


    def draw_circles(self, output_path="output.png"):
        if self.image is None:
            raise ValueError("Image not loaded, call load_image() first")

        output_image = self.image.convert("RGB")
        draw = ImageDraw.Draw(output_image)

        # Draw the circles to visualize the detected positions
        for x, y in self.circles:
            draw.ellipse(
                [x - self.circle_radius, y - self.circle_radius, x + self.circle_radius, y + self.circle_radius],
                outline="red",
                width=2
            )

        # Save the output
        output_image.save(output_path)
    
    def convert_gcode(self, output_path):
        gcode = []
        for circle in self.circles:
            x, y = circle
            gcode.append(f"G1 X{x} Y{y}")

        with open(output_path, "w") as txt_file:
            for line in gcode:
                txt_file.write("".join(line) + "\n")