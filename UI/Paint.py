from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QIcon, QBrush, QPolygon, QPainterPath
from PyQt6.QtCore import Qt, QSize, QPoint
from functools import partial
import sys
import math

class Window(QMainWindow):
    SHAPE_SIZE = 50  # Fixed shape size

    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Paint Poulpus Davinkus")
        self.setGeometry(100, 100, 800, 600)
        self.current_shape = "Line"
        self.current_color = QColor("black")
        self.previousPoint = None

        # Main container 
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        
        main_layout = QGridLayout()
        central_widget.setLayout(main_layout)
        
        # Color buttons
        colors = ["red", "cyan", "#deac2c", "yellow", "black", "magenta", "blue", "gray", "white"]
        color_container = QWidget()
        color_layout = QHBoxLayout()
        for color in colors:
            button = QPushButton()
            button.setIcon(self.create_color_icon(color, 25))
            button.setIconSize(QSize(25, 25))
            button.setFixedSize(35, 35)
            button.clicked.connect(partial(self.set_pen_color, color))
            color_layout.addWidget(button)
        color_container.setLayout(color_layout)
        main_layout.addWidget(color_container, 0, 1, 1, 2)

        # Shape buttons
        side_buttons_container = QWidget()
        side_buttons_layout = QVBoxLayout()
        shapes = ["Line", "Square", "Triangle", "Circle", "Ink", "Star"]
        for shape in shapes:
            btn = QPushButton(shape)
            btn.setFixedSize(80, 30)
            btn.clicked.connect(partial(self.set_shape, shape))
            side_buttons_layout.addWidget(btn)
        side_buttons_container.setLayout(side_buttons_layout)
        main_layout.addWidget(side_buttons_container, 1, 0, 4, 1)
        
        # Left canvas
        self.left_canvas = QPixmap(400, 400)
        self.left_canvas.fill(QColor("white"))
        self.left_label = QLabel()
        self.left_label.setPixmap(self.left_canvas)
        self.left_label.setFixedSize(400, 400)
        main_layout.addWidget(self.left_label, 1, 2, 4, 1)
        
        # Right canvas
        self.right_canvas = QPixmap(400, 400)
        self.right_canvas.fill(QColor("white"))
        self.right_label = QLabel()
        self.right_label.setPixmap(self.right_canvas)
        self.right_label.setFixedSize(400, 400)
        main_layout.addWidget(self.right_label, 1, 4, 4, 2)
        
        # Clear button
        clear_button = QPushButton("Clear Canvas")
        clear_button.clicked.connect(self.clear_canvas)
        clear_button.setFixedSize(150, 40)
        main_layout.addWidget(clear_button, 5, 2, 1, 1)
        
        self.pen = QPen(QColor("black"))
        self.pen.setWidth(6)

        self.splatterImage = QPixmap("C:/S4-Projet/Poulpus_Davinkus/UI/Splatter")

    def draw_splatter(self, position, painter):
        num_points = 12  # Number of splatter points in the burst pattern
        radius = 25  # Radius of the burst

        for i in range(num_points):
            angle = 2 * math.pi * i / num_points  # Evenly spaced points around the circle
            offset_x = int(radius * math.cos(angle))  # X offset based on angle
            offset_y = int(radius * math.sin(angle))  # Y offset based on angle
            
            splatter_position = QPoint(position.x() + offset_x, position.y() + offset_y)
            
            # Define a consistent shape for splatter (e.g., small circles or stars)
            points = QPolygon([
                QPoint(splatter_position.x(), splatter_position.y() - 5),
                QPoint(splatter_position.x() + 2, splatter_position.y() - 2),
                QPoint(splatter_position.x() + 5, splatter_position.y() - 2),
                QPoint(splatter_position.x() + 2, splatter_position.y() + 2),
                QPoint(splatter_position.x() + 3, splatter_position.y() + 5),
                QPoint(splatter_position.x(), splatter_position.y() + 3),
                QPoint(splatter_position.x() - 3, splatter_position.y() + 5),
                QPoint(splatter_position.x() - 2, splatter_position.y() + 2),
                QPoint(splatter_position.x() - 5, splatter_position.y() - 2),
                QPoint(splatter_position.x() - 2, splatter_position.y() - 2),
            ])
            painter.drawPolygon(points)

    def create_color_icon(self, color, size=30):
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(color))
        return QIcon(pixmap)

    def set_pen_color(self, color):
        self.current_color = QColor(color)
        self.pen.setColor(self.current_color)

    def set_shape(self, shape):
        self.current_shape = shape

    def clear_canvas(self):
        self.left_canvas.fill(QColor("white"))
        self.right_canvas.fill(QColor("white"))
        self.left_label.setPixmap(self.left_canvas)
        self.right_label.setPixmap(self.right_canvas)

    def mousePressEvent(self, event):
        position = self.left_label.mapFrom(self, event.pos())
        painter = QPainter(self.left_canvas)
        self.pen.setColor(self.current_color)
        painter.setPen(self.pen)
        painter.setBrush(QBrush(self.current_color, Qt.BrushStyle.SolidPattern))  # Ensure the fill color is set

        if self.current_shape == "Circle":
            # Draw the circle centered on the mouse click position
            painter.drawEllipse(position.x() - self.SHAPE_SIZE // 2, position.y() - self.SHAPE_SIZE // 2, self.SHAPE_SIZE, self.SHAPE_SIZE)
        elif self.current_shape == "Square":
            # Draw the square centered on the mouse click position
            painter.drawRect(position.x() - self.SHAPE_SIZE // 2, position.y() - self.SHAPE_SIZE // 2, self.SHAPE_SIZE, self.SHAPE_SIZE)
        elif self.current_shape == "Triangle":
            # Draw the triangle centered on the mouse click position
            points = QPolygon([
                QPoint(position.x(), position.y() - self.SHAPE_SIZE // 2),
                QPoint(position.x() + self.SHAPE_SIZE // 2, position.y() + self.SHAPE_SIZE // 2),
                QPoint(position.x() - self.SHAPE_SIZE // 2, position.y() + self.SHAPE_SIZE // 2)
            ])
            painter.drawPolygon(points)
        elif self.current_shape == "Star":
            # Draw a single point at the mouse click position
            points = QPolygon([
                QPoint(position.x(), position.y() - 25),
                QPoint(position.x() + 10, position.y() - 10),
                QPoint(position.x() + 25, position.y() - 10),
                QPoint(position.x() + 15, position.y() + 5),
                QPoint(position.x() + 20, position.y() + 20),
                QPoint(position.x(), position.y() + 10),
                QPoint(position.x() - 20, position.y() + 20),
                QPoint(position.x() - 15, position.y() + 5),
                QPoint(position.x() - 25, position.y() - 10),
                QPoint(position.x() - 10, position.y() - 10),
            ])
            painter.drawPolygon(points)
        elif self.current_shape == "Ink":
             self.draw_splatter(position, painter)


            
        elif self.current_shape == "Line":
            self.previousPoint = position

        painter.drawPoint(position)

        painter.end()
        self.left_label.setPixmap(self.left_canvas)


    def mouseMoveEvent(self, event):
        if self.current_shape == "Line" and self.previousPoint:
            position = self.left_label.mapFrom(self, event.pos())
            painter = QPainter(self.left_canvas)
            self.pen.setColor(self.current_color)
            painter.setPen(self.pen)
            painter.drawLine(self.previousPoint, position)
            painter.end()
            self.left_label.setPixmap(self.left_canvas)
            self.previousPoint = position

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())
