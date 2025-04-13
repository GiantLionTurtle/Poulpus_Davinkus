from PyQt6.QtWidgets import QPushButton, QFileDialog, QLabel
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt
import cv2 as cv

class Uploader:
    """
    Classe pour charger et afficher des images dans l'application.
    Gère la conversion et l'adaptation des images au format Qt.
    """
    
    def __init__(self, image_label):
        """
        Initialise l'uploader avec un label pour afficher l'image.
        
        Args:
            image_label (QLabel): Le widget QLabel où afficher l'image
        """
        self.image_label = image_label
        self.final_pixmap = None  # Stocke la dernière image chargée

    @staticmethod
    def convertCvImageToQtImage(cv_img):
        """
        Convertit une image OpenCV (numpy array) en QImage Qt.
        
        Args:
            cv_img (numpy.ndarray): L'image OpenCV à convertir
            
        Retour:
            QImage: L'image convertie au format Qt
        """
        height, width = cv_img.shape[:2]
        cv_img = cv.cvtColor(cv_img, cv.COLOR_BGR2RGB)  # Conversion BGR vers RGB
        bytesPerLine = 3 * width  # Calcul du stride (3 canaux RGB)
        return QImage(cv_img.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)

    def upload_image(self, image_path):
        """
        Charge une image depuis un fichier et l'affiche dans le label.
        
        Args:
            image_path (str): Chemin vers le fichier image à charger
        """
        file_path = image_path
        if file_path:
            # Charge l'image et la convertit en QPixmap
            pixmap = QPixmap(file_path)
            
            if not pixmap.isNull():
                # Redimensionne en conservant le ratio d'aspect
                scaled_pixmap = pixmap.scaled(
                    self.image_label.width(),
                    self.image_label.height(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

                # Crée une pixmap de la taille du label avec fond transparent
                final_pixmap = QPixmap(self.image_label.size())
                final_pixmap.fill(Qt.GlobalColor.transparent)

                # Centre l'image redimensionnée
                painter = QPainter(final_pixmap)
                x_offset = (self.image_label.width() - scaled_pixmap.width()) // 2
                y_offset = (self.image_label.height() - scaled_pixmap.height()) // 2
                painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
                painter.end()

                # Affiche l'image finale
                self.image_label.setPixmap(final_pixmap)
                self.final_pixmap = final_pixmap  # Sauvegarde la pixmap
            else:
                self.image_label.setText("Échec du chargement de l'image!")

    def get_pixmap(self):
        """
        Récupère la dernière pixmap chargée.
        
        Retour:
            QPixmap: La dernière image chargée ou None si aucune image
        """
        return self.final_pixmap

    
