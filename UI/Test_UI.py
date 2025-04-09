from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QGridLayout, QLineEdit, QComboBox
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtCore import Qt
import sys
import os

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumSize(400, 150)

        parentLayout = QVBoxLayout()

        self.combox = QComboBox()
        self.combox.addItem("Charlotte")
        self.combox.addItem("la")
        self.combox.addItem("thug")
        self.combox.addItem(QIcon("{}/lebron".format(self.workspace_path)), "LBJ")

        self.button = QPushButton("I am a button")

        self.button.clicked.connect(self.clickBouton)
 
        parentLayout.addWidget(self.combox)
        parentLayout.addWidget(self.button)

        centerWidget = QWidget()
        centerWidget.setLayout(parentLayout)
        self.setCentralWidget(centerWidget)
    
    def clickBouton(self):
        print("Ça marche")
        

       
#setting up window

app = QApplication(sys.argv)
window = Window()



window.show()
app.exec()