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
            qimage = pixmap.toImage()
            qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)
            width, height = qimage.width(), qimage.height()
    
            ptr = qimage.bits()
            ptr.setsize(qimage.sizeInBytes())
            arr = np.frombuffer(ptr, dtype=np.uint8)
            arr = arr.reshape((height, width, 4))

            return arr
        except Exception as e:
            print(f"Error occured as e:{e}") 

    def load_image(self):
        self.image = self._convertPixmapToCvImage(self.pixmap)
        return self.image

    def analyze_image(self):
        if self.image is None:
            raise ValueError("Image not loaded. Call load_image() first.")
        
        img_array = cv.cvtColor(self.image, cv.COLOR_BGR2GRAY)
        
        # Apply a binary threshold to isolate the shape (heart)
        _, binary_img = cv.threshold(img_array, 50, 255, cv.THRESH_BINARY)

        # Grid sampling (convert analog to discrete image) to detect areas to stamp
        height, width = binary_img.shape
        step = self.circle_radius * 2

        for y in range(0, height, step):
            for x in range(0, width, step):
                # Check if the grid has white pixels (sum=0)
                if binary_img[y:y + step, x:x + step].sum() > 0:
                    self.circles.append((x, y))


    def draw_circles(self, output_path="output.png"):
        if self.image is None:
            raise ValueError("Image not loaded, call load_image() first")

        output_image = cv.cvtColor(self.image, cv.COLOR_BGR2RGB)
        output_image = Image.fromarray(output_image)
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


#Might be useful
def convertCvImageToQtImage(cv_img:cv.Mat) -> QImage:
    height, width = cv_img.shape[:2]
    cv_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
    bytesPerLine = 3 * width
    qImg = QImage(cv_img.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
    return qImg