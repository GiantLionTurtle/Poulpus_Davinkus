from PyQt6.QtGui import QPainter, QBrush
from PyQt6.QtCore import Qt

from Shapes import draw_circle, draw_splatter, draw_square, draw_star, draw_triangle

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