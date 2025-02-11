from PyQt6.QtWidgets import QPushButton, QFileDialog, QLabel
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt
import cv2 as cv

class Uploader(QPushButton):
    def __init__(self, image_label, parent=None):
        super().__init__("Upload an image", parent)
        self.setFixedSize(150, 40)
        self.image_label = image_label  # QLabel where the image will be displayed
        self.clicked.connect(self.upload_image)  # Connect button click to function

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            cv_img = cv.imread(file_path)  # Load image as OpenCV format
            qImg = self.convertCvImageToQtImage(cv_img)
            pixmap = QPixmap.fromImage(qImg)

            if not pixmap.isNull():
                # Keep aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

                # Create a final image with padding to avoid distortion
                final_pixmap = QPixmap(self.image_label.size())
                final_pixmap.fill(Qt.GlobalColor.transparent)

                painter = QPainter(final_pixmap)
                x_offset = (self.image_label.width() - scaled_pixmap.width()) // 2
                y_offset = (self.image_label.height() - scaled_pixmap.height()) // 2
                painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
                painter.end()

                self.image_label.setPixmap(final_pixmap)
            else:
                self.image_label.setText("Failed to load image!")

    def convertCvImageToQtImage(self, cv_img):
        """Converts an OpenCV image (BGR) to a QImage"""
        height, width = cv_img.shape[:2]
        cv_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
        bytesPerLine = 3 * width
        return QImage(cv_img.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
