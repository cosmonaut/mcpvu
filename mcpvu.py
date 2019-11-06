import sys

import numpy as np

import importlib

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox
from PyQt5 import QtWidgets
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

        # todo populate at init with real plugins...
        # file that holds names..? search dir? config file?
        self.plugin_list = ["baseplugin"]

        # File/quit
        self.actionQuit.triggered.connect(self.do_quit)

        # Load Plugin
        self.actionLoad_Plugin.triggered.connect(self.plugin_menu)
        
        # A test button...
        self.pushButton_1.clicked.connect(self.widget.plot)
        #self.pushButton_1.clicked.connect(self.load_plugin)
        
    
    def closeEvent(self, event):
        # safely close anything left...
        #print("close event")
        pass

    def do_quit(self, action):
        print("quitting...")
        self.close()

    def plugin_menu(self):
        """Menu to select and load a plugin"""
        plugin_name, ok = QInputDialog.getItem(self, "Plugin Menu","Plugin:", self.plugin_list, 0, False)
        if ok and plugin_name:
            print("Loading plugin: {0:s}".format(plugin_name))
            # load...
            self.load_plugin(plugin_name)

    def load_plugin(self, plugin_name):
        print("Loading plugin...")
        try:
            baseplugin = importlib.import_module(plugin_name)
            my_plugin = baseplugin.load_plugin()
        except ModuleNotFoundError:
            print("Module not found...")
            # Warning window
            QMessageBox.warning(self, "Warning", "Plugin not found...")
        
        
# Load the UI
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

        
