from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGridLayout, QWidget, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QIcon
from PyQt6.QtCore import Qt, QSize
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
        self.canvas = QPixmap(400, 400)
        self.canvas.fill(QColor("white"))
        self.label.setPixmap(self.canvas)

        layout.addWidget(self.label, 1, 1)

        layout.setRowStretch(0, 1)
        layout.setRowStretch(2, 1)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(2, 1)

        self.pen = QPen(QColor("black"))
        self.pen.setWidth(6)
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        # Function to generate colored icons
        def create_color_icon(color, size=40):
            pixmap = QPixmap(size, size)
            pixmap.fill(QColor(color))
            return QIcon(pixmap)

        # Button container
        buttonContainer = QWidget()
        buttonLayout = QHBoxLayout()

        colors = {
            "Rouge": "red",
            "Bleu": "cyan",
            "Vert": "green",
            "Jaune": "yellow",
            "Noir": "black",
            "Mauve": "magenta",
            "Bleu fonce": "blue",
            "Gris": "gray",
            "Blanc": "white"
        }

        for name, color in colors.items():
            button = QPushButton()
            button.setIcon(create_color_icon(color))
            button.setIconSize(QSize(40, 40))
            button.setFixedSize(50, 50)
            button.clicked.connect(lambda checked, c=color: self.pen.setColor(QColor(c)))
            buttonLayout.addWidget(button)

        buttonContainer.setLayout(buttonLayout)
        layout.addWidget(buttonContainer, 0, 1)

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
