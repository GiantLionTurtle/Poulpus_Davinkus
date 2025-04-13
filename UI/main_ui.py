from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QImage
from PyQt6.QtCore import Qt
from manip_image_simple import ManipImage
from manip_image_advanced import ManipImageAdvanced
import cv2 as cv
import sys
import os
import pathlib

#Class pour upload une image
class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.initUI()
        self.workspace_path = pathlib.Path(__file__).parent.resolve()

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

        #Button to test advanced image analysis from pixmap
        self.test_analysis_button_2 = QPushButton("Test2", self)
        self.test_analysis_button_2.clicked.connect(self.testAnalysis2)

        # Ajouter les widgets
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.test_analysis_button)
        layout.addWidget(self.test_analysis_button_2)
        self.setLayout(layout)

    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
           self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
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
    
    def test_analysis(self):
        output_path = os.path.abspath("{}/output.png".format(self.workspace_path))
        output_path2 = os.path.abspath("{}/outputgcode.txt".format(self.workspace_path))
        cv_img = ManipImage(pixmap=self.final_pixmap)
        cv_img.load_image()
        cv_img.analyze_image()
        cv_img.draw_circles(output_path, (400, 600), "white")
        cv_img.convert_gcode(output_path2, (216, 279), (400, 600))

    def testAnalysis2(self):
        output_path = os.path.expanduser("{}/output.png".format(self.workspace_path))
        output_path2 = os.path.expanduser("{}/gcode.txt".format(self.workspace_path))

        cv_img = ManipImageAdvanced(pixmap=self.final_pixmap)
        cv_img.initalizeImageFromPixmap()
        cv_img.findContours()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    uploader = MainWindow()
    uploader.show()
    sys.exit(app.exec())