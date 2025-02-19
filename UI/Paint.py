from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QIcon, QBrush, QPolygon, QPainterPath
from PyQt6.QtCore import Qt, QSize, QPoint
from functools import partial
import sys
import math
from Uploader import Uploader
from Shapes import draw_circle, draw_splatter, draw_square, draw_star, draw_triangle
from Colors import ColorPicker
from Canvas import Canvas

class Window(QMainWindow):
    SHAPE_SIZE = 50  # Fixed shape size

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Poulpus Davinkus")
        self.setGeometry(100, 100, 800, 600)
        self.current_shape = "Line"
        self.current_mode = "Drawing"
        self.current_color = QColor("black")
        self.previousPoint = None

        # Main container for widgets
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QGridLayout()
        central_widget.setLayout(main_layout)

        
        self.color_picker = ColorPicker(self)
        main_layout.addWidget(self.color_picker.color_container, 0, 1, 1, 2)
        

        # Shape buttons
        self.side_buttons_container = QWidget()
        side_buttons_layout = QVBoxLayout()
        shapes = ["Line", "Square", "Triangle", "Circle", "Ink", "Star"]
        for shape in shapes:
            btn = QPushButton(shape)
            btn.setFixedSize(80, 30)
            btn.clicked.connect(partial(self.set_shape, shape))
            side_buttons_layout.addWidget(btn)
        self.side_buttons_container.setLayout(side_buttons_layout)
        main_layout.addWidget(self.side_buttons_container, 1, 0, 4, 1)
        
        #left_canvas
        self.left_canvas = Canvas(self)
        self.left_label = self.left_canvas.canevas_label
        main_layout.addWidget(self.left_label, 1, 2, 4, 1)
        
        #right_canvas
        self.right_canvas = Canvas(self)
        self.right_label = self.right_canvas.canevas_label
        main_layout.addWidget(self.right_label, 1, 4, 4, 2)
        
        # Clear button
        clear_button = QPushButton("Clear Canvas")
        clear_button.clicked.connect(self.left_canvas.fill_canvas)
        clear_button.setFixedSize(150, 40)
        main_layout.addWidget(clear_button, 5, 2, 1, 1)
        
        self.pen = QPen(QColor("black"))
        self.pen.setWidth(6)

        #Mode button
        mode_button = QPushButton("Change mode")
        mode_button.clicked.connect(self.change_mode)
        mode_button.setFixedSize(150, 40)
        main_layout.addWidget(mode_button, 0, 5, 1, 1)

        #Upload image button
        self.uploader = Uploader(self.left_label)
        main_layout.addWidget(self.uploader,0,2,1,1)
        self.uploader.hide()

    def change_mode(self):
        self.left_canvas.fill_canvas()
        if self.current_mode == "Drawing":
            self.current_mode = "Image"
            self.side_buttons_container.hide()
            self.color_picker.color_container.hide()
            self.uploader.show()
        else:
            self.current_mode = "Drawing"
            self.side_buttons_container.show()
            self.color_picker.color_container.show()
            self.uploader.hide()

    def set_shape(self, shape):
        self.current_shape = shape

    #Action of adding shapes when the mouse is clicked on the canevas
    def mousePressEvent(self, event):
        if self.current_mode == "Drawing":
            position = self.left_label.mapFrom(self, event.pos())
            painter = QPainter(self.left_canvas.canvas)
            self.pen.setColor(self.current_color)
            painter.setPen(self.pen)
            painter.setBrush(QBrush(self.current_color, Qt.BrushStyle.SolidPattern))  # Ensure the fill color is set

            if self.current_shape == "Circle":
                draw_circle(position,painter,self.SHAPE_SIZE)
            elif self.current_shape == "Square":
                draw_square(position,painter,self.SHAPE_SIZE)
            elif self.current_shape == "Triangle":
                draw_triangle(position,painter,self.SHAPE_SIZE)
            elif self.current_shape == "Star":
                draw_star(position,painter,self.SHAPE_SIZE)
            elif self.current_shape == "Ink":
                draw_splatter(position,painter)
            elif self.current_shape == "Line":
                self.previousPoint = position

            painter.drawPoint(position)
            painter.end()
            self.left_label.setPixmap(self.left_canvas.canvas)


    def mouseMoveEvent(self, event):
        if self.current_mode == "Drawing" and self.current_shape == "Line" and self.previousPoint:
            position = self.left_label.mapFrom(self, event.pos())
            painter = QPainter(self.left_canvas.canvas)
            self.pen.setColor(self.current_color)
            painter.setPen(self.pen)
            painter.drawLine(self.previousPoint, position)
            painter.end()
            self.left_label.setPixmap(self.left_canvas.canvas)
            self.previousPoint = position


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
