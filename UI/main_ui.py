from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import Qt
import sys

#Class pour upload une image
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Poulpus Davinkus")
        self.image_label = QLabel("En attente d'une image", self)
        self.image_label.setScaledContents(True)
        #Voir size avec Vidieu/Théo
        self.image_label.setFixedSize(400, 600) 

        # Bounton pour upload, pas comme ça dans le vrai UI, mais bien en attendent que le reste soit fait
        self.upload_button = QPushButton("Upload Image", self)
        self.upload_button.clicked.connect(self.upload_image)

        # Ajouter les widgets
        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.upload_button)
        self.setLayout(layout)

    def upload_image(self):
        file_dialog = QFileDialog(self)
        file_path, _ = file_dialog.getOpenFileName(
            self, "Open Image File", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            # Load the image
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Scale the image while keeping its aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

                # Create a new pixmap with the label's exact size
                final_pixmap = QPixmap(self.image_label.size())
                final_pixmap.fill(Qt.GlobalColor.transparent)

                # Center the scaled image within the final pixmap
                painter = QPainter(final_pixmap)
                x_offset = (self.image_label.width() - scaled_pixmap.width()) // 2
                y_offset = (self.image_label.height() - scaled_pixmap.height()) // 2
                painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
                painter.end()

                # Display the final pixmap
                self.image_label.setPixmap(final_pixmap)
            else:
                self.image_label.setText("Failed to load image!")

            #Scaledpixmap = pixmap.scaled(self.image_label.width(), self.image_label.height(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            #self.image_label.setPixmap(Scaledpixmap)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    uploader = MainWindow()
    uploader.show()
    sys.exit(app.exec())
