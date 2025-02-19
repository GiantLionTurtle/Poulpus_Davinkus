from PyQt6.QtGui import QColor, QIcon, QPixmap
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import QSize
from functools import partial

class ColorPicker:
    def __init__(self, window):
        self.window = window
        self.color_container = QWidget()
        color_layout = QHBoxLayout()
        colors = ["red", "cyan", "#deac2c", "yellow", "black", "magenta", "blue", "gray", "white"]
        for color in colors:
            button = QPushButton()
            button.setIcon(self.create_color_icon(color, 25))
            button.setIconSize(QSize(25, 25))
            button.setFixedSize(35, 35)
            button.clicked.connect(partial(self.set_pen_color, color))
            color_layout.addWidget(button)
        self.color_container.setLayout(color_layout)

    def create_color_icon(self, color, size=30):
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(color))
        return QIcon(pixmap)

    def set_pen_color(self, color):
        self.window.current_color = QColor(color)
        self.window.pen.setColor(self.window.current_color)
