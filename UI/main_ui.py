from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt
from manip_image import ManipImage
import cv2 as cv
import sys
import os

#Class pour upload une image
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Poulpus Davinkus")
        self.setFixedSize(1200, 800)
        self.image_label = QLabel("En attente d'une image", self)
        self.image_label.setScaledContents(True)
        #Voir size avec Vidieu/Théo
        self.image_label.setFixedSize(400, 600) 

        # Bounton pour upload, pas comme ça dans le vrai UI, mais bien en attendent que le reste soit fait
        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.clicked.connect(self.upload_image)

        #Button to test image analysis from pixmap
        self.test_analysis_button = QPushButton("Test", self)
        self.test_analysis_button.clicked.connect(self.test_analysis)

        # Ajouter les widgets
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.test_analysis_button)
        self.setLayout(layout)

    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
           self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        #file_path = os.path.expanduser("~/Documents/School/S4/Projet/lesun.jpg")
        if file_path:
            # Load the image and convert it to a QPixmap from a cv image (numpy array))
            #pixmap = QPixmap(file_path)
            cv_img = ManipImage(file_path=file_path)
            cv_img = cv_img.setCvImage()
            qImg = convertCvImageToQtImage(cv_img)
            pixmap = QPixmap.fromImage(qImg)
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
    
    def test_analysis(self):
        output_path = os.path.expanduser("~/Documents/School/S4/Projet/output.png")
        output_path2 = os.path.expanduser("~/Documents/School/S4/Projet/gcode.txt")
        cv_img = ManipImage(pixmap=self.final_pixmap)
        cv_img.load_image()
        cv_img.analyze_image()
        cv_img.draw_circles(output_path)
        cv_img.convert_gcode(output_path2)

def convertCvImageToQtImage(cv_img:cv.Mat) -> QImage:
    height, width = cv_img.shape[:2]
    cv_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)
    bytesPerLine = 3 * width
    qImg = QImage(cv_img.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
    return qImg

if __name__ == "__main__":
    app = QApplication(sys.argv)
    uploader = MainWindow()
    uploader.show()
    sys.exit(app.exec())
    # filepath = os.path.expanduser("~/Documents/School/S4/Projet/heart.png")
    # output_path = os.path.expanduser("~/Documents/School/S4/Projet/output.png")
    # output_path2 = os.path.expanduser("~/Documents/School/S4/Projet/gcode.txt")
    # cv_img = ManipImage(filepath)
    # cv_img.load_image()
    # cv_img.analyze_image()
    # cv_img.draw_circles(output_path)
    # cv_img.convert_gcode(output_path2)