from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QGridLayout, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QSize, QPoint
import sys

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setFixedSize(500, 500)
        self.setWindowTitle("Paint Poulpus Davinkus")

        self.previousPoint = None

        # Main container widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Grid layout to center the canvas
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0) 
        central_widget.setLayout(layout)

        self.label = QLabel()

        # Create the canvas
        self.canvas = QPixmap(QSize(400, 400))
        self.canvas.fill(QColor("white"))
        self.label.setPixmap(self.canvas)

        layout.addWidget(self.label, 1, 1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(2, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)

        self.pen = QPen()
        self.pen.setColor(QColor("black"))
        self.pen.setWidth(6)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        buttonContainer = QWidget()
        buttonLayout = QHBoxLayout()

        redColor = QPushButton("Rouge")
        blueColor = QPushButton("Bleu")
        greenColor = QPushButton("Vert")
        yellowColor = QPushButton("Jaune")
        
        redColor.setFixedSize(50,50)
        blueColor.setFixedSize(50,50)
        greenColor.setFixedSize(50,50)
        yellowColor.setFixedSize(50,50)

        redColor.clicked.connect(self.switchToRed)
        blueColor.clicked.connect(self.switchToBlue)
        greenColor.clicked.connect(self.switchToGreen)
        yellowColor.clicked.connect(self.switchToYellow)

        buttonLayout.addWidget(redColor)
        buttonLayout.addWidget(blueColor)
        buttonLayout.addWidget(greenColor)
        buttonLayout.addWidget(yellowColor)

        buttonContainer.setLayout(buttonLayout)

        layout.addWidget(buttonContainer, 0, 1)

    def switchToRed(self):
        self.pen.setColor(QColor("red"))
    
    def switchToBlue(self):
        self.pen.setColor(QColor("cyan"))
    
    def switchToGreen(self):
        self.pen.setColor(QColor("green"))
    
    def switchToYellow(self):
        self.pen.setColor(QColor("yellow"))


    def getCanvasPos(self, event):
        return self.label.mapFromParent(event.pos())

    def mouseMoveEvent(self, event):
        position = self.getCanvasPos(event)
        painter = QPainter(self.canvas)
        painter.setPen(self.pen) 

        if self.previousPoint:
            painter.drawLine(self.previousPoint, position)
        else:
            painter.drawPoint(position)

        painter.end()
        self.label.setPixmap(self.canvas)
        self.previousPoint = position

    def mouseReleaseEvent(self, event):
        self.previousPoint = None

    def mousePressEvent(self, event):
        position = self.getCanvasPos(event)
        painter = QPainter(self.canvas)
        painter.setPen(self.pen)
        painter.drawPoint(position)
        painter.end()
        self.label.setPixmap(self.canvas)

app = QApplication(sys.argv)
window = Window()
window.show()
app.exec()
