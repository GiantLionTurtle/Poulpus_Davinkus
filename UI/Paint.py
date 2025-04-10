from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QToolBar, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QPalette, QLinearGradient, QIcon, QAction
from PyQt6.QtCore import Qt, QPoint, QSize
from functools import partial
import sys
import os
from Uploader import Uploader
from manip_image_advanced import ManipImageAdvanced
from manip_image_simple import ManipImage
from Shapes import draw_circle, draw_splatter, draw_square, draw_star, draw_triangle
from Colors import ColorPicker
from Canvas import Canvas
from Communication import Communication
import random
import re
import pathlib
import time

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        #Création de la fenêtre principal
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
        self.drwing_path = None
        self.workspace_path = pathlib.Path(__file__).parent.resolve()

        #Paths des différentes images disponibles dans la banque
        self.image_paths = {
    "Shrek": "{}/Images/shrek".format(self.workspace_path),
    "Coeur": "{}/Images/heart.png".format(self.workspace_path),
    "Canadiens": "{}/Images/canadien_logo".format(self.workspace_path),
    "Capybara": "{}/Images/capybara".format(self.workspace_path),
    "Poulpe": "{}/Images/Poulpus_Davinkus".format(self.workspace_path),
}
        #path des différents dessins disponibles dans la banque
        self.drawing_paths = {
    "Foret": "{}/drawings/foret.txt".format(self.workspace_path),
    "Chat": "{}/drawings/chat.txt".format(self.workspace_path),
    "Voiture": "{}/drawings/voiture.txt".format(self.workspace_path)
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

        # toolbar = QToolBar("Option")
        # self.addToolBar(toolbar)
    
        menu = self.menuBar()
        option_menu = menu.addMenu("Options")
        save_drawing_button = QAction("Save drawing", self)
        save_drawing_button.setStatusTip("Save the current drawing")
        save_drawing_button.triggered.connect(self.save_drawing)
        option_menu.addAction(save_drawing_button)

        # Boutons des différentes couleurs
        self.color_picker = ColorPicker(self)
        main_layout.addWidget(self.color_picker.color_container, 0, 1, 1, 2, Qt.AlignmentFlag.AlignCenter & Qt.AlignmentFlag.AlignJustify)
  
        # Boutons des différentes formes
        self.side_buttons_container = QWidget()
        side_buttons_layout = QVBoxLayout()
        shapes = ["Carré", "Triangle", "Cercle", "Fleur", "Étoile"]
        for shape in shapes:
            btn = QPushButton(shape)
            btn.setFixedSize(80, 30)
            btn.clicked.connect(partial(self.set_shape, shape))
            side_buttons_layout.addWidget(btn)
        self.side_buttons_container.setLayout(side_buttons_layout)
        main_layout.addWidget(self.side_buttons_container, 1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter & Qt.AlignmentFlag.AlignJustify)

        #Toile de gauche
        self.left_canvas = Canvas(self)
        self.left_label = self.left_canvas.canevas_label
        self.left_label.setFixedSize(400, 600)
        main_layout.addWidget(self.left_label, 1, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)

        #Toile de droite
        self.right_canvas = Canvas(self)
        self.right_label = self.right_canvas.canevas_label
        self.right_label.setFixedSize(400, 600)
        main_layout.addWidget(self.right_label, 1, 4, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # coutainer du bouton en dessous de la toile de gauche
        button_container = QWidget()
        button_layout = QHBoxLayout()

        # Bouton pour effacer l'entiereté de la toile 
        self.clear_button = QPushButton("Nettoyer la toile")
        self.clear_button.clicked.connect(self.clear_canvas)
        self.clear_button.setFixedSize(150, 40)
        button_layout.addWidget(self.clear_button)

        # Bouton pour annuler la dernière action
        self.undo_button = QPushButton("Retour vers l'arrière")
        self.undo_button.clicked.connect(self.undo)
        self.undo_button.setFixedSize(150, 40)
        button_layout.addWidget(self.undo_button)

        # Bouton pour exporter les formes en G-code
        self.export_button = QPushButton("Envoyer le dessin au robot")
        self.export_button.clicked.connect(self.export_drawing)
        self.export_button.setFixedSize(150, 40)
        button_layout.addWidget(self.export_button)

        button_container.setLayout(button_layout)
        main_layout.addWidget(button_container, 2, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # Bouton qui permet de changer le mode d'utilisation de l'intertface
        mode_button = QPushButton("Changer de mode")
        mode_button.clicked.connect(self.change_mode)
        mode_button.setFixedSize(150, 40)
        main_layout.addWidget(mode_button, 0, 5, 1, 1)

        # Add this with your other buttons
        test_btn = QPushButton("Test Progression")
        test_btn.clicked.connect(self.test_progression)
        test_btn.setFixedSize(150, 40)
        button_layout.addWidget(test_btn)

        #self.manip_image = ManipImage()
        #self.analyze_button = QPushButton("Appuie pour 5 big BOOMS")
        self.analyze_button = QPushButton()
        self.analyze_button.setIcon(QIcon("{}/UI/Bouton.png".format(self.workspace_path)))
        self.analyze_button.setIconSize(QSize(150, 40))
        self.analyze_button.clicked.connect(self.test_analyze)
        self.analyze_button.setFixedSize(150, 40)
        main_layout.addWidget(self.analyze_button, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)
        self.analyze_button.hide()

        #Bouton pour choisir dans la banque d'image
        self.image_selector = QComboBox()
        self.image_selector.setFixedSize(200, 50)
        self.image_selector.addItem("Choisir une image")
        self.image_selector.addItem(QIcon(self.image_paths.get("Shrek")), "Shrek")
        self.image_selector.addItem(QIcon(self.image_paths.get("Heart")), "Coeur")
        self.image_selector.addItem(QIcon(self.image_paths.get("Canadiens")), "Canadiens")
        self.image_selector.addItem(QIcon(self.image_paths.get("Capybara")), "Capybara")
        self.image_selector.addItem(QIcon(self.image_paths.get("Poulpe")), "Poulpe")
        main_layout.addWidget(self.image_selector, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)
        self.image_selector.hide()
        self.image_selector.currentTextChanged.connect(self.image_change)
        self.uploader = Uploader(self.left_label)

        #Boutons pour choisir un dessin de la banque
        self.drawing_selector = QComboBox()
        self.drawing_selector.setFixedSize(200, 50)
        self.drawing_selector.addItems(["Choisissez un dessin","Foret", "Chat", "Voiture"])
        main_layout.addWidget(self.drawing_selector, 0, 3, 1, 1, Qt.AlignmentFlag.AlignHCenter)
        self.drawing_selector.currentTextChanged.connect(self.drawing_change)

        # Add this with your other UI elements
        self.connection_status = QLabel()
        self.update_connection_status(False)  # Initialize as disconnected
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Robot Status:"))
        status_layout.addWidget(self.connection_status)
        status_container = QWidget()
        status_container.setLayout(status_layout)
        main_layout.addWidget(status_container, 3, 3)  # Adjust position as needed

        self.communication = Communication(self)

        self.pen = QPen(QColor("black"))
        self.pen.setWidth(6)

    def closeEvent(self, event):
        self.communication = None

    #Fonction pour afficher l'image sélectionné dans la banque
    def image_change(self, s):
        if s == "Choisir une image":
            self.clear_canvas()
        self.image_path = self.image_paths.get(s)
        if self.image_path:
            self.uploader.upload_image(self.image_path)

    def drawing_change(self, s):
        if s == "Choisissez un dessin":
            self.clear_canvas()
        self.drawing_path = self.drawing_paths.get(s)
        if self.drawing_path:
            self.load_drawing()

    #Lance l'analyse d'image sur l'image présente sur la toile de gauche
    def test_analyze(self):
        output_path = os.path.abspath("{}/output.png".format(self.workspace_path))
        output_path2 = os.path.abspath("{}/outputgcode.txt".format(self.workspace_path))
        
        # Accède à la pixmap de uploader
        pixmap = self.uploader.get_pixmap()
        if pixmap is None:
            print("Error: No image uploaded.")
            return
        cv_img = ManipImageAdvanced(pixmap=pixmap, file_path=self.image_path)
        cv_img.initalizeImageFromPixmap()
        cv_img.applyMaskOnImage()
        contours = cv_img.findContours()
        new_contours = cv_img.contourFiltering(contours)
        final_contours = cv_img.reassembleContours(new_contours)
        coordinates = cv_img.fillContours(final_contours, 20.0, 0.0)
        #cv_img.draw_circles(output_path, (400, 600), "white")
        #cv_img.convert_gcode(output_path2, (216, 279), (400, 600))
        
        print("Analysis completed, outputs saved.")

    def save_drawing(self):
        if not self.shapes:
            print("No shapes to save.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Drawing", "", "Text Files (*.txt)")
        
        if not file_path:
            print("Save canceled.")
            return

        with open(file_path, "w") as f:
            for shape, position, color in self.shapes:
                x = position.x()
                y = position.y()
                #color_str = color.name()  
                f.write(f"SHAPE {shape} X{x} Y{y} COLOR {color}\n")

        print(f"Drawing saved to '{file_path}'")

    #Charge un dessin préalablement enregistré
    def load_drawing(self):
        if not self.drawing_path or not os.path.exists(self.drawing_path):
            print("Invalid drawing path")
            return

        self.shapes.clear()
        
        with open(self.drawing_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                match = re.search(r'SHAPE (\w+) X(-?\d+) Y(-?\d+) COLOR (#\w+)', line)
                if match:
                    shape, x, y, color = match.groups()
                    position = QPoint(int(x), int(y))
                    qcolor = QColor(color) 
                    self.shapes.append((shape, position, qcolor))

        self.redraw_canvas()


    #Création de l'arrière plan de type "Océan" avec un gradient de différentes teintes de bleu
    def set_ocean_gradient_background(self):
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 105, 148))
        gradient.setColorAt(1, QColor(0, 191, 255))  

        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))

        self.setPalette(palette)
    
    #Fonction pour ajouter les bulles dans l'arrière plan
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        self.draw_bubbles(painter)

    #Création des bulles pour l'arrière plan
    def draw_bubbles(self, painter):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(173, 216, 230, 150)))  # Bleu pale pour faire comme transparent

        for _ in range(25): 
            diameter = random.randint(20, 50)
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            painter.drawEllipse(x, y, diameter, diameter)

    #Fonction pour que la fenêtre reste stable quand elle est ajustée en plein écran
    def resizeEvent(self, event):
        self.set_ocean_gradient_background()
        super().resizeEvent(event)

    #Changement de mise en plan lors du changement de mode
    def change_mode(self):
        self.clear_canvas()
        if self.current_mode == "Drawing":
            self.current_mode = "Image"
            self.side_buttons_container.setVisible(False)
            self.color_picker.color_container.setVisible(False)
            self.undo_button.setVisible(False)
            #self.export_button.setVisible(False)
            self.image_selector.setVisible(True)
            self.analyze_button.setVisible(True)
            self.image_path = None
            self.image_selector.setCurrentIndex(0)
            self.drawing_selector.setVisible(False)
            self.drawing_selector.setCurrentIndex(0)
            
        else:
            self.current_mode = "Drawing"
            self.side_buttons_container.setVisible(True)
            self.color_picker.color_container.setVisible(True)
            self.undo_button.setVisible(True)
            #self.export_button.setVisible(True)
            self.image_selector.setVisible(False)
            self.analyze_button.setVisible(False)
            self.image_path = None
            self.drawing_selector.setVisible(True)
            
    #Ajuste la bonne forme à utiliser en fonction du choix de l'utilisateur
    def set_shape(self, shape):
        self.current_shape = shape

    #Efface l'entierté des formes/images sur la toile de gauche
    def clear_canvas(self):
        self.left_canvas.fill_canvas()
        self.right_canvas.fill_canvas()
        self.shapes.clear()
        self.history.clear()

    #Envoie les coordonnée et les informations des formes sur un dessin
    def export_drawing(self):
        print(self.shapes)
        self.communication.gcode_logic(self.shapes)


    #Efface la dernière forme placé par l'utilisateur
    def undo(self):
        if self.shapes:  
            self.shapes.pop()  
            self.redraw_canvas()

    #Redessine la toile de gauche après une modification
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

    #Ajoute une forme lorsque l'utilisateur appuis dans une zone de la toile de gauche uniquement
    def mousePressEvent(self, event):
        if self.current_mode == "Drawing":
            position = self.left_label.mapFrom(self, event.pos())
            painter = QPainter(self.left_canvas.canvas)
            self.pen.setColor(self.current_color)
            painter.setPen(self.pen)
            painter.setBrush(QBrush(self.current_color, Qt.BrushStyle.SolidPattern))

            if self.current_shape in ["Cercle", "Carré", "Triangle", "Étoile", "Fleur"]:
                x = position.x()
                y = position.y()
                self.shapes.append((x, y, self.current_shape,self.current_color.name()))
                self.draw_shape(self.current_shape, position, painter)

            painter.end()
            self.left_label.setPixmap(self.left_canvas.canvas)

    def draw_shape(self, shape, position, painter):
        if shape == "Cercle":
            draw_circle(position, painter, 50)
        elif shape == "Carré":
            draw_square(position, painter, 50)
        elif shape == "Triangle":
            draw_triangle(position, painter, 50)
        elif shape == "Étoile":
            draw_star(position, painter, 50)
        elif shape == "Fleur":
            draw_splatter(position, painter)


    def draw_progression(self, shape: str, position: QPoint, color: QColor):
        painter = QPainter(self.right_canvas.canvas)
        try:
            self.pen.setColor(color)
            painter.setPen(self.pen)
            painter.setBrush(QBrush(color, Qt.BrushStyle.SolidPattern))
            self.draw_shape(shape, position, painter)
        finally:
            painter.end()
        
        self.right_label.setPixmap(self.right_canvas.canvas)
        self.update()  # Force UI refresh


    def test_progression(self):
        if not self.shapes:
            print("No shapes to draw ")
            return
        
        self.right_canvas.fill_canvas()
        self.right_label.setPixmap(self.right_canvas.canvas)
        
        for shape, pos, color in self.shapes:
            self.draw_progression(shape, pos, color)
            QApplication.processEvents()  # Mise èa jour du UI
            time.sleep(0.5)

    def update_connection_status(self, connected: bool):
        color = "green" if connected else "red"
        text = "Connected" if connected else "Disconnected"
        
        # Create a colored dot icon
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 20, 20)
        painter.end()
        
        self.connection_status.setPixmap(pixmap)
        self.connection_status.setToolTip(f"SSH Connection: {text}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())