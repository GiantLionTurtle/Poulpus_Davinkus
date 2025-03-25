from PyQt6.QtWidgets import QPushButton, QFileDialog, QLabel
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt
from manip_image_simple import ManipImage
import cv2 as cv
class Uploader:
    def __init__(self, image_label):
         self.image_label = image_label
    #class Uploader(QPushButton):
    # def __init__(self, image_label, parent=None):
    #     #super().__init__("Upload an image", parent)
    #     self.setFixedSize(150, 35)
    #     self.image_label = image_label  # QLabel where the image will be displayed
    #     self.clicked.connect(self.upload_image)  # Connect button click to function

    def convertCvImageToQtImage(cv_img):

        height, width = cv_img.shape[:2]
        cv_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        bytesPerLine = 3 * width
        return QImage(cv_img.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)

    def upload_image(self,image_path):
                #file_dialog = QFileDialog(self)
                # file_path, _ = file_dialog.getOpenFileName(
                #    self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
                # )
            file_path = image_path
                #file_path = os.path.expanduser("~/Documents/School/S4/Projet/lesun.jpg")
            if file_path:
                    # Load the image and convert it to a QPixmap from a cv image (numpy array)) test
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                        # Garde le aspect ratio
                    scaled_pixmap = pixmap.scaled(
                        self.image_label.width(),
                        self.image_label.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )

                        # Mettre le vrai size de l'image en premier
                    final_pixmap = QPixmap(self.image_label.size())
                    final_pixmap.fill(Qt.GlobalColor.transparent)

                        # Permet de fill les cotées avec du blanc pour que l'image ne soit pas déformer
                    painter = QPainter(final_pixmap)
                    x_offset = (self.image_label.width() - scaled_pixmap.width()) // 2
                    y_offset = (self.image_label.height() - scaled_pixmap.height()) // 2
                    painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
                    painter.end()

                        # Display the final pixmap
                    self.image_label.setPixmap(final_pixmap) 
                    self.final_pixmap = final_pixmap       
                else:
                    self.image_label.setText("Failed to load image!")

    def get_pixmap(self):
         return self.final_pixmap

    
