from PyQt6.QtCore import QPoint
from PyQt6.QtGui import QPolygon, QPainter
import math

def draw_circle(position, painter, size):
    """
    Dessine un cercle centré sur la position donnée.
    
    Args:
        position (QPoint): Centre du cercle
        painter (QPainter): Objet pour dessiner
        size (int): Diamètre du cercle
    """
    painter.drawEllipse(position.x() - size // 2, position.y() - size // 2, size, size)

def draw_square(position, painter, size):
    """
    Dessine un carré centré sur la position donnée.
    
    Args:
        position (QPoint): Centre du carré  
        painter (QPainter): Objet pour dessiner
        size (int): Longueur du côté du carré
    """
    painter.drawRect(position.x() - size // 2, position.y() - size // 2, size, size)

def draw_triangle(position, painter, size):
    """
    Dessine un triangle équilatéral centré sur la position donnée.
    
    Args:
        position (QPoint): Centre du triangle
        painter (QPainter): Objet pour dessiner
        size (int): Hauteur du triangle
    """
    points = [QPoint(position.x(), position.y() - size // 2),
              QPoint(position.x() + size // 2, position.y() + size // 2),
              QPoint(position.x() - size // 2, position.y() + size // 2)]
    painter.drawPolygon(*points)

def draw_star(position, painter, size):
    """
    Dessine une étoile à 5 branches centrée sur la position donnée.
    
    Args:
        position (QPoint): Centre de l'étoile
        painter (QPainter): Objet pour dessiner  
        size (int): Taille globale de l'étoile
    """
    points = [
        QPoint(position.x(), position.y() - size // 2),  # Pointe du haut
        QPoint(position.x() + size // 6, position.y() - size // 6),
        QPoint(position.x() + size // 2, position.y() - size // 6), 
        QPoint(position.x() + size // 4, position.y() + size // 10),
        QPoint(position.x() + size // 3, position.y() + size // 2),  # Pointe droite
        QPoint(position.x(), position.y() + size // 4),  
        QPoint(position.x() - size // 3, position.y() + size // 2),  # Pointe gauche
        QPoint(position.x() - size // 4, position.y() + size // 10),
        QPoint(position.x() - size // 2, position.y() - size // 6),  
        QPoint(position.x() - size // 6, position.y() - size // 6),
    ]
    
    painter.drawPolygon(*points)

def draw_splatter(position, painter):
    """
    Dessine une forme d'éclaboussure autour de la position donnée.
    
    Args:
        position (QPoint): Centre de l'éclaboussure
        painter (QPainter): Objet pour dessiner
    """
    num_points = 12  # Nombre de points autour du centre
    radius = 25      # Rayon de l'éclaboussure
    
    for i in range(num_points):
        # Calcul de la position de chaque sous-élément
        angle = 2 * math.pi * i / num_points
        offset_x = int(radius * math.cos(angle))
        offset_y = int(radius * math.sin(angle))

        # Position du sous-élément
        splatter_position = QPoint(position.x() + offset_x, position.y() + offset_y)
        
        # Définition de la forme de chaque sous-élément (petite étoile)
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