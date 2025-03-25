from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QPalette, QLinearGradient
from PyQt6.QtCore import Qt, QPoint
from functools import partial
import sys
from Uploader import Uploader
from Shapes import draw_circle, draw_splatter, draw_square, draw_star, draw_triangle
from Colors import ColorPicker
from Canvas import Canvas
import random

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Poulpus Davinkus")
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen_geometry)

        self.set_ocean_gradient_background()

        self.current_shape = "Line"
        self.current_mode = "Drawing"
        self.current_color = QColor("black")
        self.previousPoint = None
        self.shapes = []  
        self.history = []
        self.image_path = None

        self.image_paths = {
    "Shrek": "C:/S4-Projet/Poulpus_Davinkus/UI/Images/shrek",
    "Heart": "C:/S4-Projet/Poulpus_Davinkus/UI/Images/heart",
    "Nemo": "C:/S4-Projet/Poulpus_Davinkus/UI/Images/nemo",
    "Canadiens": "C:/S4-Projet/Poulpus_Davinkus/UI/Images/canadien_logo",
    "Capybara": "C:/S4-Projet/Poulpus_Davinkus/UI/Images/capybara",
    "Poulpe": "C:/S4-Projet/Poulpus_Davinkus/UI/Images/Poulpus_Davinkus",
}
        
        # Main container
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout()
        central_widget.setLayout(main_layout)

        # Ajustement des colones/rangées pour avoiur une belle mise en page facile à comprendre
        main_layout.setColumnStretch(0, 1)  # Bouton des formes
        main_layout.setColumnStretch(1, 1)  # Boutons de couleurs
        main_layout.setColumnStretch(2, 1)  # Toile de gauche
        main_layout.setColumnStretch(3, 1)  # Espace entre les 2 toiles
        main_layout.setColumnStretch(4, 3)  # Toile de droite
        main_layout.setColumnStretch(5, 2)  # Espace entre la toile de droite et la bordure

        main_layout.setRowStretch(0, 1)  # Boutons de couleurs (Haut)
        main_layout.setRowStretch(1, 4)  # Toiles + formes (milieu)
        main_layout.setRowStretch(2, 1)  # Boutons en bas (bas)

        # Boutons couleur
        self.color_picker = ColorPicker(self)
        main_layout.addWidget(self.color_picker.color_container, 0, 1, 1, 2, Qt.AlignmentFlag.AlignCenter & Qt.AlignmentFlag.AlignJustify)
  
        # Boutons formes
        self.side_buttons_container = QWidget()
        side_buttons_layout = QVBoxLayout()
        shapes = ["Square", "Triangle", "Circle", "Ink", "Star"]
        for shape in shapes:
            btn = QPushButton(shape)
            btn.setFixedSize(80, 30)
            btn.clicked.connect(partial(self.set_shape, shape))
            side_buttons_layout.addWidget(btn)
        self.side_buttons_container.setLayout(side_buttons_layout)
        main_layout.addWidget(self.side_buttons_container, 1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter & Qt.AlignmentFlag.AlignJustify)

        self.left_canvas = Canvas(self)
        self.left_label = self.left_canvas.canevas_label
        self.left_label.setFixedSize(400, 600)
        main_layout.addWidget(self.left_label, 1, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)

        self.right_canvas = Canvas(self)
        self.right_label = self.right_canvas.canevas_label
        self.right_label.setFixedSize(400, 600)
        main_layout.addWidget(self.right_label, 1, 4, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # coutainer du bouton en dessous de la toile de gauche
        button_container = QWidget()
        button_layout = QHBoxLayout()

        # Bouton pour effacer l'entiereté de la toile 
        self.clear_button = QPushButton("Clear Canvas")
        self.clear_button.clicked.connect(self.clear_canvas)
        self.clear_button.setFixedSize(150, 40)
        button_layout.addWidget(self.clear_button)

        # Bouton pour annuler la dernière action
        self.undo_button = QPushButton("Undo")
        self.undo_button.clicked.connect(self.undo)
        self.undo_button.setFixedSize(150, 40)
        button_layout.addWidget(self.undo_button)

        # Bouton pour exporter les formes en G-code
        self.export_button = QPushButton("Export G-code")
        self.export_button.clicked.connect(self.export_gcode)
        self.export_button.setFixedSize(150, 40)
        button_layout.addWidget(self.export_button)

        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container, 2, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # Bouton qui permet de changer le mode d'utilisation de l'intertface
        mode_button = QPushButton("Change mode")
        mode_button.clicked.connect(self.change_mode)
        mode_button.setFixedSize(150, 40)
        main_layout.addWidget(mode_button, 0, 5, 1, 1)

        # Bouton qui permet de télécharger une image
        # self.uploader = Uploader(self.left_label)
        # main_layout.addWidget(self.uploader, 0, 1, 1, 2, Qt.AlignmentFlag.AlignHCenter)
        # self.uploader.hide()

        self.image_selector = QComboBox()
        self.image_selector.addItems(["Select an image", "Shrek", "Heart", "Nemo", "Canadiens", "Capybara", "Poulpe"])
        main_layout.addWidget(self.image_selector, 0, 0, 1, 2, Qt.AlignmentFlag.AlignHCenter)
        self.image_selector.hide()
        self.image_selector.currentTextChanged.connect(self.text_change)
        self.uploader = Uploader(self.left_label)

        self.pen = QPen(QColor("black"))
        self.pen.setWidth(6)

    def text_change(self, s):
        self.image_path = self.image_paths.get(s)
        if self.image_path:
            self.uploader.upload_image(self.image_path)



    def set_ocean_gradient_background(self):
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 105, 148))
        gradient.setColorAt(1, QColor(0, 191, 255))  

        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(palette)

    def paintEvent(self, event):

        super().paintEvent(event)
        painter = QPainter(self)
        self.draw_bubbles(painter)

    def draw_bubbles(self, painter):

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(173, 216, 230, 150)))  # Bleu pale pour faire comme transparent

        for _ in range(25): 
            diameter = random.randint(20, 50)
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            painter.drawEllipse(x, y, diameter, diameter)

    def resizeEvent(self, event):
        self.set_ocean_gradient_background()
        super().resizeEvent(event)

    def change_mode(self):
        self.clear_canvas()
        if self.current_mode == "Drawing":
            self.current_mode = "Image"
            self.side_buttons_container.setVisible(False)
            self.color_picker.color_container.setVisible(False)
            #self.uploader.setVisible(True)
            self.undo_button.setVisible(False)
            self.export_button.setVisible(False)
            self.image_selector.setVisible(True)
        else:
            self.current_mode = "Drawing"
            self.side_buttons_container.setVisible(True)
            self.color_picker.color_container.setVisible(True)
            #self.uploader.setVisible(False)
            self.undo_button.setVisible(True)
            self.export_button.setVisible(True)
            self.image_selector.setVisible(False)
            

    def set_shape(self, shape):
        self.current_shape = shape

    def clear_canvas(self):
        self.left_canvas.fill_canvas()
        self.shapes.clear()
        self.history.clear()

    def export_gcode(self):
        gcode_commands = []
        for shape, position, color in self.shapes:
            x = position.x()
            y = position.y()
            gcode_commands.append(f"SHAPE {shape} X{x} Y{y} COLOR {color}")

        with open("output.gcode", "w") as f:
            f.write("\n".join(gcode_commands))
        print("G-code exported to output.gcode")

    def undo(self):
        if self.shapes:  
            self.shapes.pop()  
            self.redraw_canvas()

    def redraw_canvas(self):
        self.left_canvas.fill_canvas() 
        painter = QPainter(self.left_canvas.canvas)
        for shape, position, color in self.shapes:
            self.pen.setColor(QColor(color))
            painter.setPen(self.pen)
            painter.setBrush(QBrush(QColor(color), Qt.BrushStyle.SolidPattern))
            self.draw_shape(shape, position, painter)
        painter.end()
        self.left_label.setPixmap(self.left_canvas.canvas)

    def mousePressEvent(self, event):
        if self.current_mode == "Drawing":
            position = self.left_label.mapFrom(self, event.pos())
            painter = QPainter(self.left_canvas.canvas)
            self.pen.setColor(self.current_color)
            painter.setPen(self.pen)
            painter.setBrush(QBrush(self.current_color, Qt.BrushStyle.SolidPattern))

            if self.current_shape in ["Circle", "Square", "Triangle", "Star", "Ink"]:
                self.shapes.append((self.current_shape, position, self.current_color.name()))
                self.draw_shape(self.current_shape, position, painter)

            painter.end()
            self.left_label.setPixmap(self.left_canvas.canvas)

    def draw_shape(self, shape, position, painter):
        if shape == "Circle":
            draw_circle(position, painter, 50)
        elif shape == "Square":
            draw_square(position, painter, 50)
        elif shape == "Triangle":
            draw_triangle(position, painter, 50)
        elif shape == "Star":
            draw_star(position, painter, 50)
        elif shape == "Ink":
            draw_splatter(position, painter)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())