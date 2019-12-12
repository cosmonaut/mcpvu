import sys

import numpy as np
import importlib

from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.uic import loadUiType

import astropy.io.fits as pf
from datetime import datetime
from datetime import timezone


# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt

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

        # Plot objects
        self._plots = []

        # Photon Data container
        self.phot_data = []
        self.phot_tstamps = []
        self.obs_date = datetime.now()

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
        # * text file that contains loadable plugins for menu... (with gen script?)
        # * real detector plugin...
        # * Generate phd plot
        # * Generate count rate history plot
        # * Live count rate
        # * Spectrum plot (configurable box per image plot?)
        # * Image plot adjustable zoom and colormaps?
        # * implot rebinning
        # * Dynamic data vs plot timing adjustment for fast data???

        
        # File/quit
        self.actionQuit.triggered.connect(self.do_quit)

        # Load/Unload Plugin
        self.actionLoad_Plugin.triggered.connect(self.plugin_menu)
        self.actionUnload_Plugin.triggered.connect(self.unload_plugin)

        self.actionLoad_Plugin.setEnabled(True)
        self.actionUnload_Plugin.setDisabled(True)


        # Control Frame (monitor, acquire, save, clear buttons)
        self.control_frame.setEnabled(False)

        self.sav_button.setEnabled(False)

        self.mon_button.clicked.connect(self.monitor)
        self.acq_button.clicked.connect(self.acquire)
        self.sav_button.clicked.connect(self.save)
        self.clr_button.clicked.connect(self.clear)
        
        # A test button...

        #self.startButton.clicked.connect(self.unpause_plugin)
        #self.pauseButton.clicked.connect(self.pause_plugin)
        
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
            self.clear()
            baseplugin = importlib.import_module(plugin_name)
            my_plugin = baseplugin.load_plugin()
            self._plugin = my_plugin

            # Get configuration data from plugin
            plugin_config = self._plugin.get_config()
            #print(plugin_config.segments)
            # Configure GUI items here...
            # Load plots etc...
            for pc in plugin_config.plots:
                # plot object
                plot = pc.name(plugin_config, pc.plot_config)
                self._plots.append(plot)
                self.gridLayout_plots.addWidget(plot, pc.row, pc.column,
                                                pc.row_span, pc.column_span)

            self.actionLoad_Plugin.setDisabled(True)
            self.actionUnload_Plugin.setEnabled(True)
            self._plugin.start()
            self.control_frame.setEnabled(True)

            # Reset buttons
            self.mon_button.setChecked(False)
            self.acq_button.setChecked(False)
            self.sav_button.setChecked(False)

            self.mon_button.setEnabled(True)
            self.acq_button.setEnabled(True)
            self.clr_button.setEnabled(True)
            self.sav_button.setEnabled(False)
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

            for plot in self._plots:
                self.gridLayout_plots.removeWidget(plot)
                plot.deleteLater()
                plot = None

            self._plots = []

            self.actionUnload_Plugin.setDisabled(True)
            self.actionLoad_Plugin.setEnabled(True)
            self.control_frame.setEnabled(False)

            # Reset buttons
            self.mon_button.setChecked(False)
            self.acq_button.setChecked(False)
            self.sav_button.setChecked(False)

            self.mon_button.setEnabled(True)
            self.acq_button.setEnabled(True)
            self.clr_button.setEnabled(True)
            self.sav_button.setEnabled(True)

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
            return(True)

        return(False)

    def unpause_plugin(self):
        """Unpause plugin"""
        if (self._plugin != None):
            self._plugin.unpause()
            self._dat_timer.start()
            self._plot_timer.start()
            self._cr_timer.start()
            print("plugin running...")
            return(True)

        return(False)

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
                #self.widget.append_data(d)
                for plot in self._plots:
                    plot.append_data(d)
                self._cr_counts += d.len

                if (self.acq_button.isChecked()):
                    self.phot_data.append(d)
                    tstamp = datetime.now() - self.obs_date
                    self.phot_tstamps.append(tstamp.total_seconds())
            else:
                # Just quit if we got a None data -- that implies empty queue
                return

    def replot(self):
        """Handle refreshing all active plots"""
        #self.widget.plot()
        for plot in self._plots:
            plot.plot()

    def count_rate(self):
        """Display count rate"""
        n = self._plugin.get_data_len()
        print("countrate: {0:d}, pak: {1:d}".format(self._cr_counts, n))
        self._cr_counts = 0

    def monitor(self):
        """Display data but don't store data for save"""
        if (self.mon_button.isChecked()):
            # unpausing
            status = self.unpause_plugin()
            if (status != True):
                self.mon_button.setChecked(False)
            else:
                self.acq_button.setEnabled(False)
        else:
            # pausing
            status = self.pause_plugin()
            if (status != True):
                self.mon_button.setChecked(True)
            else:
                self.acq_button.setEnabled(True)

    def acquire(self):
        """Display data and hold master photon list for data saving"""

        if (self.acq_button.isChecked()):
            # unpausing

            # Clear data first...
            self.clear()

            status = self.unpause_plugin()
            if (status != True):
                self.acq_button.setChecked(False)
            else:
                self.mon_button.setEnabled(False)
                self.obs_date = datetime.now()
        else:
            # pausing
            status = self.pause_plugin()
            if (status != True):
                self.acq_button.setChecked(True)
            else:
                self.mon_button.setEnabled(True)
                self.sav_button.setEnabled(True)

    def clear(self):
        """Clear all data/plots"""
        # Clear stored photon data
        self.phot_data.clear()
        self.phot_tstamps.clear()

        # Clear plots
        for plot in self._plots:
            plot.clear()

    def save(self):
        """Save acquired detector data in fits format"""
        print("Save  partially implemented")
        print("Total packets: {0:d}".format(len(self.phot_data)))

        # Busy cursor
        QApplication.setOverrideCursor(Qt.WaitCursor)

        # Config with needed info...
        plugin_config = self._plugin.get_config()

        utcobs = self.obs_date.replace(tzinfo = timezone.utc)
        fname = utcobs.strftime("%Y-%m-%d-%H%M%S") + ".fits"

        # Number of binary tables to make (per segment)
        n_segs = len(plugin_config.segment_configs)

        # Sets of arrays to hold photon data per segment
        xarrs = [[] for seg in range(n_segs)]
        yarrs = [[] for seg in range(n_segs)]
        parrs = [[] for seg in range(n_segs)]
        tarrs = [[] for seg in range(n_segs)]

        # Names and units for all table columns
        xname = "X"
        yname = "Y"
        pname = "P"
        tname = "T"

        xform = "1I"
        yform = "1I"
        pform = "1I"
        tform = "1D"

        xunit = "pixels"
        yunit = "pixels"
        punit = "pixels"
        tunit = "seconds"

        # generate data arrays
        for pkt, ts in zip(self.phot_data, self.phot_tstamps):
            idx = pkt.segment
            xarrs[idx].extend(pkt.x[0:pkt.len])
            yarrs[idx].extend(pkt.y[0:pkt.len])
            parrs[idx].extend(pkt.p[0:pkt.len])
            tarrs[idx].extend([ts]*pkt.len)

        # hdu list (add primary at start)
        hdul = []
        hdup = pf.PrimaryHDU()
        hdup.header['PROGRAM'] = ("mcpvu.py -- written by Nicholas Nell (nicholas.nell@colorado.edu)")
        hdup.header['VERSION'] = ("0.1", "program version")
        hdup.header['INSTRMNT'] = ('mcpvu', "Instrument name (not implemented)")
        hdup.header['DETECTOR'] = ("MCP", "Detector type")
        hdup.header['SEGMENTS'] = ("{0:d}".format(n_segs), "Number of segments")
        hdup.header['DATEOBS'] = (utcobs.strftime("%Y-%m-%d %H:%M:%S %Z%z"), "UTC")
        hdup.header['EXPOSURE'] = ("0", "Exposure time (seconds)")

        hdul.append(hdup)

        # Create columns and hdu for each segment
        for seg in range(n_segs):
            # generate column definitions (per segment)
            colx = pf.Column(name = xname, format = xform, unit = xunit, array = xarrs[seg])
            coly = pf.Column(name = yname, format = yform, unit = yunit, array = yarrs[seg])
            colp = pf.Column(name = pname, format = pform, unit = punit, array = parrs[seg])
            colt = pf.Column(name = tname, format = tform, unit = tunit, array = tarrs[seg])
            col_defs = pf.ColDefs([colx, coly, colp, colt])
            # Generate HDU for each segment
            hdul.append(pf.BinTableHDU.from_columns(col_defs))
            hdul[-1].header['SEGMENT'] = ("{0:d}".format(seg), "Detector segment")
            hdul[-1].header['SEGNAME'] = ("{0:d}".format(seg), "Segment name")
            hdul[-1].header['XBITS'] = ("{0:d}".format(plugin_config.segment_configs[idx].xbit), "X bits")
            hdul[-1].header['YBITS'] = ("{0:d}".format(plugin_config.segment_configs[idx].ybit), "Y bits")
            hdul[-1].header['PBITS'] = ("{0:d}".format(plugin_config.segment_configs[idx].pbit), "Pulse height bits")

        # Save fits file
        hdul = pf.HDUList(hdul)
        hdul.writeto(fname)

        # Finish up...
        self.sav_button.setEnabled(False)
        self.sav_button.setChecked(False)

        QApplication.restoreOverrideCursor()

        
        
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

        
