from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog
from PyQt6.QtGui import QPixmap
import sys

#Class pour upload une image
class ImageUploader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Poulpus Davinkus")
        self.image_label = QLabel("En attente d'une image", self)
        self.image_label.setScaledContents(True)
        #Voir size avec Vidieu/Théo
        self.image_label.setFixedSize(800, 600) 

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
            # Montrer image
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    uploader = ImageUploader()
    uploader.show()
    sys.exit(app.exec())
