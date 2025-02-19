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

