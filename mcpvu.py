import sys

import numpy as np

import importlib

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5.uic import loadUiType

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

UIFILE = "mcpvu.ui"
UiMainWindow, QMainWindow = loadUiType(UIFILE)


class Main(QMainWindow, UiMainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        # File/quit
        self.actionQuit.triggered.connect(self.nn_quit)
        # A test button...
        #self.pushButton_1.clicked.connect(self.widget.plot)
        self.pushButton_1.clicked.connect(self.load_plugin)
        
    
    def closeEvent(self, event):
        # safely close anything left...
        #print("close event")
        pass

    def nn_quit(self, action):
        print("quitting...")
        self.close()

    def load_plugin(self):
        print("Loading plugin...")
        try:
            baseplugin = importlib.import_module("baseplugin")
            my_plugin = baseplugin.load_plugin()
        except ModuleNotFoundError:
            print("Module not found...")

        
        

class Ui(QMainWindow):
    def __init__(self):
        # Call the inherited classes __init__ method
        super(Ui, self).__init__()
        # Load the .ui file
        uic.loadUi(UIFILE, self)
        # Show the GUI
        self.show()

        

def main():
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

        
