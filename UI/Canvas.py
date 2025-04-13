from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QBrush, QPixmap
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPainter, QPen, QColor


class Canvas:
    """Classe représentant une toile de dessin pour l'application."""
    
    def __init__(self, window):
        """
        Initialise la toile de dessin.
        
        Args:
            window (QMainWindow): La fenêtre principale de l'application
        """
        self.window = window
        # Crée une pixmap blanche de 400x445 pixels
        self.canvas = QPixmap(400, 445)
        self.canvas.fill(QColor("white"))
        # Crée un QLabel pour afficher la pixmap
        self.canevas_label = QLabel()
        self.canevas_label.setPixmap(self.canvas)
        self.canevas_label.setFixedSize(400, 445)

    def fill_canvas(self):
        """Réinitialise la toile en la remplissant de blanc."""
        self.canvas.fill(QColor("white"))
        self.canevas_label.setPixmap(self.canvas)

    def paintEvent(self, event):
        """
        Gère l'événement de peinture de la toile.
        
        Args:
            event (QPaintEvent): L'événement de peinture
        """
        painter = QPainter(self)
        
        # Ne redessine que la partie qui doit être mise à jour
        painter.drawPixmap(0, 0, self.canvas)  # Dessiner la toile

        # Dessiner les formes vectorielles (couche de formes)
        self.shape_layer.draw_shapes(painter)
        
        painter.end()
    
    def update_canvas(self, rect):
        """
        Met à jour une zone rectangulaire de la toile.
        
        Args:
            rect (QRect): La zone rectangulaire à mettre à jour
        """
        self.update(rect)