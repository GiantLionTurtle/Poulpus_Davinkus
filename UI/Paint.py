from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QComboBox, QToolBar, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QPalette, QLinearGradient, QIcon, QAction
from PyQt6.QtCore import Qt, QPoint, QSize
from functools import partial
import sys
import os
from Uploader import Uploader
from manip_image_advanced import ManipImageAdvanced
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

        # Création de la fenêtre principale
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

        # Chemins des différentes images disponibles dans la banque
        self.image_paths = {
            "Shrek": "{}/Images/shrek.png".format(self.workspace_path),
            "Coeur": "{}/Images/heart.png".format(self.workspace_path),
            "Canadiens": "{}/Images/canadien_logo.png".format(self.workspace_path),
            "Capybara": "{}/Images/capybara.png".format(self.workspace_path),
            "Poulpe": "{}/Images/Poulpus_Davinkus.jpg".format(self.workspace_path),
            "Pikachu": "{}/Images/fat_pikachu.png".format(self.workspace_path),
        }
        # Chemins des différents dessins disponibles dans la banque
        self.drawing_paths = {
            "Foret": "{}/drawings/foret.txt".format(self.workspace_path),
            "Chat": "{}/drawings/chat.txt".format(self.workspace_path)
        }
        
        # Mise en page principale
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QGridLayout()
        central_widget.setLayout(main_layout)

        # Ajustement des colonnes/rangées pour avoir une belle mise en page facile à comprendre
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
        save_drawing_button = QAction("Sauvegarder le dessin", self)
        save_drawing_button.setStatusTip("Sauvegarder le dessin actuel")
        save_drawing_button.triggered.connect(self.save_drawing)
        option_menu.addAction(save_drawing_button)

        # Boutons des différentes couleurs
        self.color_picker = ColorPicker(self)
        main_layout.addWidget(self.color_picker.color_container, 0, 1, 1, 2, Qt.AlignmentFlag.AlignCenter & Qt.AlignmentFlag.AlignJustify)
  
        # Boutons des différentes formes
        self.side_buttons_container = QWidget()
        side_buttons_layout = QVBoxLayout()
        shapes = ["Carre", "Triangle", "Cercle", "Fleur", "Etoile"]
        for shape in shapes:
            btn = QPushButton(shape)
            btn.setFixedSize(80, 30)
            btn.clicked.connect(partial(self.set_shape, shape))
            side_buttons_layout.addWidget(btn)
        self.side_buttons_container.setLayout(side_buttons_layout)
        main_layout.addWidget(self.side_buttons_container, 1, 0, 1, 1, Qt.AlignmentFlag.AlignCenter & Qt.AlignmentFlag.AlignJustify)

        # Toile de gauche
        self.left_canvas = Canvas(self)
        self.left_label = self.left_canvas.canevas_label
        self.left_label.setFixedSize(400, 445)
        main_layout.addWidget(self.left_label, 1, 1, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # Toile de droite
        self.right_canvas = Canvas(self)
        self.right_label = self.right_canvas.canevas_label
        self.right_label.setFixedSize(400, 445)
        main_layout.addWidget(self.right_label, 1, 4, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # Container du bouton en dessous de la toile de gauche
        button_container = QWidget()
        button_layout = QHBoxLayout()

        # Bouton pour effacer l'intégralité de la toile 
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

        # Bouton qui permet de changer le mode d'utilisation de l'interface
        mode_button = QPushButton("Changer de mode")
        mode_button.clicked.connect(self.change_mode)
        mode_button.setFixedSize(150, 40)
        main_layout.addWidget(mode_button, 0, 5, 1, 1)

        # Ajout avec les autres boutons
        test_btn = QPushButton("Progression du robot")
        test_btn.clicked.connect(self.test_progression)
        test_btn.setFixedSize(150, 40)
        button_layout.addWidget(test_btn)

        #self.manip_image = ManipImage()
        self.analyze_button = QPushButton("Analyser l'image")
        self.analyze_button.clicked.connect(self.test_analyze)
        self.analyze_button.setFixedSize(150, 40)
        main_layout.addWidget(self.analyze_button, 0, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)
        self.analyze_button.hide()

        # Bouton pour choisir dans la banque d'image
        self.image_selector = QComboBox()
        self.image_selector.setFixedSize(200, 50)
        self.image_selector.addItem("Choisir une image")
        self.image_selector.addItem(QIcon(self.image_paths.get("Shrek")), "Shrek")
        self.image_selector.addItem(QIcon(self.image_paths.get("Heart")), "Coeur")
        self.image_selector.addItem(QIcon(self.image_paths.get("Canadiens")), "Canadiens")
        self.image_selector.addItem(QIcon(self.image_paths.get("Capybara")), "Capybara")
        self.image_selector.addItem(QIcon(self.image_paths.get("Poulpe")), "Poulpe")
        self.image_selector.addItem(QIcon(self.image_paths.get("Pikachu")), "Pikachu")
        main_layout.addWidget(self.image_selector, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter)
        self.image_selector.hide()
        self.image_selector.currentTextChanged.connect(self.image_change)
        self.uploader = Uploader(self.left_label)

        # Boutons pour choisir un dessin de la banque
        self.drawing_selector = QComboBox()
        self.drawing_selector.setFixedSize(200, 50)
        self.drawing_selector.addItems(["Choisissez un dessin","Foret", "Chat"])
        main_layout.addWidget(self.drawing_selector, 0, 3, 1, 1, Qt.AlignmentFlag.AlignHCenter)
        self.drawing_selector.currentTextChanged.connect(self.drawing_change)

        # Label pour afficher l'état de la connexion
        self.connection_status = QLabel()
        self.update_connection_status(False) 
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("Connexion au robot:"))
        status_layout.addWidget(self.connection_status)
        status_container = QWidget()
        status_container.setLayout(status_layout)
        main_layout.addWidget(status_container, 2, 5)  

        self.communication = Communication(self)

        self.pen = QPen(QColor("black"))
        self.pen.setWidth(6)

    def closeEvent(self, event):
        """
        Gère l'événement de fermeture de la fenêtre.

        Args:
            event: L'événement de fermeture.
        """
        self.communication = None

    def image_change(self, s):
        """
        Affiche l'image sélectionnée dans la banque.

        Args:
            s (str): Le nom de l'image sélectionnée.
        """
        if s == "Choisir une image":
            self.clear_canvas()
        self.image_path = self.image_paths.get(s)
        if self.image_path:
            self.uploader.upload_image(self.image_path)

    def drawing_change(self, s):
        """
        Charge le dessin sélectionné dans la banque.

        Args:
            s (str): Le nom du dessin sélectionné.
        """
        if s == "Choisissez un dessin":
            self.clear_canvas()
        self.drawing_path = self.drawing_paths.get(s)
        if self.drawing_path:
            self.load_drawing()

    def test_analyze(self):
        """
        Lance l'analyse d'image sur l'image présente sur la toile de gauche.
        """
        # Accède à la pixmap de uploader
        pixmap = self.uploader.get_pixmap()
        if pixmap is None:
            print("Erreur : Aucune image chargée.")
            return
        cv_img = ManipImageAdvanced(pixmap=pixmap, file_path=self.image_path)
        cv_img.initalizeImageFromPixmap()
        cv_img.applyMaskOnImage()
        contours = cv_img.findContours()
        new_contours = cv_img.contourFiltering(contours)
        coordinates = cv_img.placeCircles(new_contours, 20.0, 25.0)
        self.shapes = coordinates
        self.communication.gcode_logic(coordinates)
        
        print("Analyse terminée, sorties sauvegardées.")

    def save_drawing(self):
        """
        Sauvegarde le dessin actuel dans un fichier.
        """
        if not self.shapes:
            print("Aucune forme à sauvegarder.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Sauvegarder le dessin", "", "Fichiers texte (*.txt)")
        
        if not file_path:
            print("Sauvegarde annulée.")
            return

        with open(file_path, "w") as f:
            for x, y, shape, color in self.shapes:
                f.write(f"SHAPE {shape} X{x} Y{y} COLOR {color}\n")

        print(f"Dessin sauvegardé dans '{file_path}'")

    def load_drawing(self):
        """
        Charge un dessin préalablement enregistré.
        """
        if not self.drawing_path or not os.path.exists(self.drawing_path):
            print("Chemin du dessin invalide")
            return

        self.shapes.clear()
        
        with open(self.drawing_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                match = re.search(r'SHAPE (\w+) X(-?\d+) Y(-?\d+) COLOR (#\w+)', line)
                if match:
                    shape, x, y, color = match.groups()
                    # Stocke comme (x, y, shape, color) pour correspondre au format de dessin manuel
                    self.shapes.append((int(x), int(y), shape, color))

        self.redraw_canvas()

    def set_ocean_gradient_background(self):
        """
        Crée l'arrière-plan de type "Océan" avec un gradient de différentes teintes de bleu.
        """
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(0, 105, 148))
        gradient.setColorAt(1, QColor(0, 191, 255))  

        palette = self.palette()
        palette.setBrush(QPalette.ColorRole.Window, QBrush(gradient))

        self.setPalette(palette)
    
    def paintEvent(self, event):
        """
        Gère l'événement de peinture pour ajouter les bulles dans l'arrière-plan.

        Args:
            event: L'événement de peinture.
        """
        super().paintEvent(event)
        painter = QPainter(self)
        self.draw_bubbles(painter)

    def draw_bubbles(self, painter):
        """
        Crée les bulles pour l'arrière-plan.

        Args:
            painter (QPainter): L'objet peintre pour dessiner.
        """
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(173, 216, 230, 150)))  # Bleu pâle pour faire comme transparent

        for _ in range(25): 
            diameter = random.randint(20, 50)
            x = random.randint(0, self.width())
            y = random.randint(0, self.height())
            painter.drawEllipse(x, y, diameter, diameter)

    def resizeEvent(self, event):
        """
        Gère l'événement de redimensionnement pour que la fenêtre reste stable.

        Args:
            event: L'événement de redimensionnement.
        """
        self.set_ocean_gradient_background()
        super().resizeEvent(event)

    def change_mode(self):
        """
        Change le mode d'utilisation de l'interface entre dessin et image.
        """
        self.clear_canvas()
        if self.current_mode == "Drawing":
            self.current_mode = "Image"
            self.side_buttons_container.setVisible(False)
            self.color_picker.color_container.setVisible(False)
            self.undo_button.setVisible(False)
            self.export_button.setVisible(False)
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
            self.export_button.setVisible(True)
            self.image_selector.setVisible(False)
            self.analyze_button.setVisible(False)
            self.image_path = None
            self.drawing_selector.setVisible(True)
            
    def set_shape(self, shape):
        """
        Définit la forme à utiliser en fonction du choix de l'utilisateur.

        Args:
            shape (str): Le nom de la forme sélectionnée.
        """
        self.current_shape = shape
        if shape == "Triangle" or "Carre":
            self.current_color = QColor(Qt.GlobalColor.black)
        if shape == "Etoile":
            self.current_color = QColor(Qt.GlobalColor.yellow)
        if shape == "Cercle":
            self.current_color = QColor(Qt.GlobalColor.blue)

    def clear_canvas(self):
        """
        Efface l'intégralité des formes/images sur la toile de gauche.
        """
        self.left_canvas.fill_canvas()
        self.right_canvas.fill_canvas()
        self.shapes.clear()
        self.history.clear()

    def export_drawing(self):
        """
        Envoie les coordonnées et les informations des formes sur un dessin au robot.
        """
        print(self.shapes)
        self.communication.gcode_logic(self.shapes)

    def undo(self):
        """
        Efface la dernière forme placée par l'utilisateur.
        """
        if self.shapes:  
            self.shapes.pop()  
            print("Self shapes: {}".format(self.shapes))
            self.redraw_canvas()

    def redraw_canvas(self):
        """
        Redessine la toile de gauche après une modification.
        """
        self.left_canvas.fill_canvas() 
        painter = QPainter(self.left_canvas.canvas)
        for x, y, shape, color in self.shapes:
            self.pen.setColor(QColor(color))
            painter.setPen(self.pen)
            painter.setBrush(QBrush(QColor(color), Qt.BrushStyle.SolidPattern))
            position = QPoint(x, y)
            self.draw_shape(shape, position, painter)
        painter.end()
        self.left_label.setPixmap(self.left_canvas.canvas)

    def mousePressEvent(self, event):
        """
        Gère l'événement de clic de souris pour ajouter une forme.

        Args:
            event: L'événement de clic de souris.
        """
        if self.current_mode == "Drawing":
            abs_position = event.pos()
            position = self.left_label.mapFrom(self, event.pos())
            painter = QPainter(self.left_canvas.canvas)
            self.pen.setColor(self.current_color)
            painter.setPen(self.pen)
            painter.setBrush(QBrush(self.current_color, Qt.BrushStyle.SolidPattern))

            if self.current_shape in ["Cercle", "Carre", "Triangle", "Etoile", "Fleur"]:
                x = position.x()
                y = position.y()
                self.shapes.append((x, y, self.current_shape, self.current_color.name()))
                self.draw_shape(self.current_shape, position, painter)

            painter.end()
            self.left_label.setPixmap(self.left_canvas.canvas)

    def _convertMm2Px(self, page_size, image_size, measure_to_convert):
        """
        Convertit une mesure de millimètres en pixels.

        Args:
            page_size (list): Dimensions de la page en mm [hauteur, largeur].
            image_size (list): Dimensions de l'image en pixels [hauteur, largeur].
            measure_to_convert (float): Mesure à convertir.

        Retour:
            float: La mesure convertie en pixels.
        """
        try:
            page_height, page_width = page_size
            image_height, image_width = image_size
            x_conversion = image_width/page_width
            y_conversion = image_height/page_height
            # Prend le plus petit des deux pour éviter les débordements
            if x_conversion > y_conversion:
                return y_conversion*measure_to_convert
            return x_conversion*measure_to_convert
        except Exception as e:
            print(f"Erreur lors de la conversion de la mesure de mm en px: {e}")

    def draw_shape(self, shape, position, painter):
        """
        Dessine une forme à la position spécifiée.

        Args:
            shape (str): Le nom de la forme à dessiner.
            position (QPoint): La position où dessiner.
            painter (QPainter): L'objet peintre pour dessiner.
        """
        shape_size = round(self._convertMm2Px([195,175], [445,400], 20))
        if shape == "Cercle":
            draw_circle(position, painter, shape_size)
        elif shape == "Carre":
            draw_square(position, painter, shape_size)
        elif shape == "Triangle":
            draw_triangle(position, painter, shape_size)
        elif shape == "Etoile":
            draw_star(position, painter, shape_size)
        elif shape == "Fleur":
            draw_splatter(position, painter)

    def draw_progression(self, shape: str, x: int, y: int, color: QColor):
        """
        Dessine la progression du robot sur la toile de droite.

        Args:
            shape (str): La forme à dessiner.
            x (int): Position x.
            y (int): Position y.
            color (QColor): Couleur de la forme.
        """
        painter = QPainter(self.right_canvas.canvas)
        try:
            self.pen.setColor(color)
            painter.setPen(self.pen)
            painter.setBrush(QBrush(color, Qt.BrushStyle.SolidPattern))
            position = QPoint(x, y)
            self.draw_shape(shape, position, painter)
        finally:
            painter.end()
        
        self.right_label.setPixmap(self.right_canvas.canvas)
        self.update()  # Force le rafraîchissement de l'interface

    def test_progression(self):
        """
        Teste la progression du robot en dessinant les formes une par une.
        """
        if not self.shapes:
            print("Aucune forme à dessiner")
            return
        
        self.right_canvas.fill_canvas()
        self.right_label.setPixmap(self.right_canvas.canvas)
        
        for x, y, shape, color_name in self.shapes:
            color = QColor(color_name)
            self.draw_progression(shape, x, y, color)
            QApplication.processEvents()  # Met à jour l'interface
            time.sleep(1)

    def update_connection_status(self, connected: bool):
        """
        Met à jour l'état de la connexion au robot.

        Args:
            connected (bool): True si connecté, False sinon.
        """
        color = "green" if connected else "red"
        text = "Connecté" if connected else "Déconnecté"
        
        # Crée une icône de point coloré
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setBrush(QColor(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(0, 0, 20, 20)
        painter.end()
        
        self.connection_status.setPixmap(pixmap)
        self.connection_status.setToolTip(f"Connexion SSH: {text}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())