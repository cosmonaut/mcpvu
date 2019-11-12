import sys

import numpy as np

import importlib

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox
from PyQt5.QtCore import QTimer
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

        # Currently loaded plugin
        self._plugin = None
        
        # todo populate at init with real plugins...
        # file that holds names..? search dir? config file?
        self.plugin_list = ["skeletonplugin", "baseplugin"]

        # Counter for count rate
        self._cr_counts = 0

        # Data acquisition timer.
        self._dat_timer = QTimer()
        self._dat_timer.setInterval(0)
        self._dat_timer.setSingleShot(False)
        self._dat_timer.stop()
        # run function get_data() on timeout
        self._dat_timer.timeout.connect(self.get_data)

        # Replot timer
        # Note replot timing vs data speed...
        self._plot_timer = QTimer()
        self._plot_timer.setInterval(500)
        self._plot_timer.setSingleShot(False)
        self._plot_timer.stop()
        # Run replot() on timeout
        self._plot_timer.timeout.connect(self.replot)

        # Count rate timer
        self._cr_timer = QTimer()
        self._cr_timer.setInterval(1000)
        self._cr_timer.setSingleShot(False)
        self._cr_timer.stop()
        # Run whatever on timeout
        self._cr_timer.timeout.connect(self.count_rate)



        # TODO:
        # * remove implotcanvas native from ui in designer.
        # * add dynamic plot loading and placement per plugin config
        # * text file that contains loadable plugins for menu... (with gen script?)
        # * real detector plugin...
        # * Track master photon list and allow fits file save (one bin table per det segment?)
        # * Generate phd plot
        # * Generate count rate history plot
        # * Live count rate
        # * Spectrum plot (configurable box per image plot?)
        # * Image plot adjustable zoom and colormaps?
        # * implot log scale, rebinning
        # * Dynamic data vs plot timing adjustment for fast data???

        
        # File/quit
        self.actionQuit.triggered.connect(self.do_quit)

        # Load Plugin
        self.actionLoad_Plugin.triggered.connect(self.plugin_menu)
        self.actionUnload_Plugin.triggered.connect(self.unload_plugin)

        self.actionLoad_Plugin.setEnabled(True)
        self.actionUnload_Plugin.setDisabled(True)

        
        # A test button...

        self.startButton.clicked.connect(self.unpause_plugin)
        self.pauseButton.clicked.connect(self.pause_plugin)
        
        #self.pushButton_1.clicked.connect(self.widget.plot)
        #self.pushButton_1.clicked.connect(self.load_plugin)
        
    
    def closeEvent(self, event):
        # safely close anything left...
        pass

    def do_quit(self, action):
        print("quitting...")
        # Make sure plugin is unloaded...
        self.unload_plugin()
        print("plugin closed")
        # Close it down
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
            self._plugin = my_plugin

            # Get configuration data from plugin
            plugin_config = self._plugin.get_config()
            print(plugin_config.segments)
            # Configure GUI items here...
            # Load plots etc...

            self.actionLoad_Plugin.setDisabled(True)
            self.actionUnload_Plugin.setEnabled(True)
            self._plugin.start()
        except ModuleNotFoundError:
            print("Module not found...")
            # Warning window
            QMessageBox.warning(self, "Warning", "Error loading plugin...")

    def unload_plugin(self):
        if (self._plugin != None):
            self.pause_plugin()
            self._plugin.stop()
            # clean up other stuff...?
            del self._plugin
            self._plugin = None

            self.actionUnload_Plugin.setDisabled(True)
            self.actionLoad_Plugin.setEnabled(True)

    def pause_plugin(self):
        """Pause plugin"""
        if (self._plugin != None):
            self._plugin.pause()
            #self.widget.clear()
            self._dat_timer.stop()
            self._plot_timer.stop()
            self._cr_timer.stop()
            self._cr_counts = 0
            print("plugin paused...")

    def unpause_plugin(self):
        """Unpause plugin"""
        if (self._plugin != None):
            self._plugin.unpause()
            self._dat_timer.start()
            self._plot_timer.start()
            self._cr_timer.start()
            print("plugin running...")

    def get_data(self):
        """Get data from plugin. Called from a GUI timer on a regular
        interval"""
        # Get expected amount of data in queue
        n = self._plugin.get_data_len()

        if (n == 0):
            return

        # Try to get as much as possible without spending too long in
        # get_data()
        if (n > 10):
            n = 10

        for i in range(n):
            d = self._plugin.get_data()
            if (d != None):
                self.widget.append_data(d)
                self._cr_counts += d.len
            else:
                # Just quit if we got a None data -- that implies empty queue
                return

    def replot(self):
        """Handle refreshing all active plots"""
        self.widget.plot()

    def count_rate(self):
        """Display count rate"""
        n = self._plugin.get_data_len()
        print("countrate: {0:d}, pak: {1:d}".format(self._cr_counts, n))
        self._cr_counts = 0
        
        
        
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

        
