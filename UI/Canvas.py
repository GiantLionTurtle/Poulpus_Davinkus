from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QBrush, QPixmap
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPainter, QPen, QColor


class Canvas:
    def __init__(self, window):
        self.window = window
        self.canvas = QPixmap(400, 600)
        self.canvas.fill(QColor("white"))
        self.canevas_label = QLabel()
        self.canevas_label.setPixmap(self.canvas)
        self.canevas_label.setFixedSize(400, 600)

    def fill_canvas(self):
        self.canvas.fill(QColor("white"))
        self.canevas_label.setPixmap(self.canvas)

    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Only redraw the part that needs to be updated
        painter.drawPixmap(0, 0, self.canvas)  # Dessiner la toile

        # Dessiner les formes vectorielle
        self.shape_layer.draw_shapes(painter)
        
        painter.end()
    
    def update_canvas(self, rect):
        """
        Update only the specific area where the shape was drawn.
        This method allows selective redrawing by passing the QRect to update.
        """
        self.update(rect)

