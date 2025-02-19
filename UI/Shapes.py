from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QPolygon, QPainter
import math

def draw_circle(position, painter, size):
    painter.drawEllipse(position.x() - size // 2, position.y() - size // 2, size, size)

def draw_square(position, painter, size):
    painter.drawRect(position.x() - size // 2, position.y() - size // 2, size, size)

def draw_triangle(position, painter, size):
    points = [QPoint(position.x(), position.y() - size // 2),
              QPoint(position.x() + size // 2, position.y() + size // 2),
              QPoint(position.x() - size // 2, position.y() + size // 2)]
    painter.drawPolygon(*points)

def draw_star(position, painter, size):
    points = [
        QPoint(position.x(), position.y() - size // 2),
        QPoint(position.x() + size // 4, position.y() - size // 4),
        QPoint(position.x() + size // 2, position.y() - size // 4),
        QPoint(position.x() + size // 8, position.y() + size // 8),
        QPoint(position.x() + size // 4, position.y() + size // 2),
        QPoint(position.x(), position.y() + size // 4),
        QPoint(position.x() - size // 4, position.y() + size // 2),
        QPoint(position.x() - size // 8, position.y() + size // 8),
        QPoint(position.x() - size // 2, position.y() - size // 4),
        QPoint(position.x() - size // 4, position.y() - size // 4),
    ]
    painter.drawPolygon(*points)

def draw_splatter(position, painter):
    num_points = 12
    radius = 25
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        offset_x = int(radius * math.cos(angle))
        offset_y = int(radius * math.sin(angle))

        splatter_position = QPoint(position.x() + offset_x, position.y() + offset_y)
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
