import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.colors import LogNorm, PowerNorm, Normalize

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QWidget

class ImplotWidgetCont(QFrame):
    def __init__(self, plugin_config, plot_config, parent = None, width = 6, height = 6, dpi = 150):
        super(ImplotWidgetCont, self).__init__(parent = parent)

        self.setFrameStyle(QFrame.Box | QFrame.Plain);

        self.layout = QVBoxLayout()

        self.setLayout(self.layout)

        self._plot = ImplotWidget(plugin_config, plot_config, parent = parent,
                                  width = width, height = height, dpi = dpi)

        self.layout.addWidget(self._plot)

        btw = QWidget()
        self.bt_layout = QHBoxLayout()
        btw.setLayout(self.bt_layout)

        self.layout.addWidget(btw)

        self.bt_layout.addWidget(QLabel("Colormap: "))
        self.cm_combo = QComboBox()
        self.cm_combo.addItems(["cubehelix", "inferno", "cividis", "viridis", "gist_stern", "gist_heat", "afmhot", "gray"])
        self.bt_layout.addWidget(self.cm_combo)
        self.cm_combo.currentTextChanged.connect(self.cm_update)

        self.bt_layout.addWidget(QLabel("Scale: "))
        self.sc_combo = QComboBox()
        self.sc_combo.addItems(["Sqrt", "Linear", "Log"])
        self.bt_layout.addWidget(self.sc_combo)
        self.sc_combo.currentTextChanged.connect(self.norm_update)

        # TODO -- implement rebin...
        self.bt_layout.addWidget(QLabel("Rebin Factor: "))
        self.rf_combo = QComboBox()
        self.rf_combo.addItems(["1"])
        self.bt_layout.addWidget(self.rf_combo)

        self.bt_layout.addStretch()


        self.norm_update(self.sc_combo.currentText())
        self.cm_update(self.cm_combo.currentText())



    def plot(self):
        self._plot.plot()

    def append_data(self, new_data):
        self._plot.append_data(new_data)

    def clear(self):
        self._plot.clear()

    def cm_update(self, txt):
        self._plot.set_plot_cm(txt)

    def norm_update(self, txt):
        self._plot.set_plot_norm(txt)



# image widget
# Todo
# * Log scaling
# * Toolbar or pan/zoom
# * Colormap options
class ImplotWidget(FigureCanvas):
    def __init__(self, plugin_config, plot_config, parent = None, width = 6, height = 6, dpi = 150):

        self.fig = Figure(figsize = (width, height), dpi = dpi)
        #self.fig.tight_layout()
        
        self.segment = plot_config.segment

        #xbit = plugin_config.xbits[plugin_config.plots]
        #ybit = plugin_config.ybits[plugin_config.segment]
        xbit = plot_config.xbit
        ybit = plot_config.ybit

        self.xsize = 2**xbit
        self.ysize = 2**ybit

        # Plot data object
        self.data = np.zeros((self.xsize, self.ysize), dtype = np.uint32)

        self.axes = self.fig.add_subplot()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        #         FigureCanvas.setSizePolicy(self,
        #                 QSizePolicy.Expanding,
        #                 QSizePolicy.Expanding)
        #         FigureCanvas.updateGeometry(self)

        # image plot
        self.im = self.axes.imshow(self.data, origin = 'lower', cmap = 'cubehelix',
                                   vmin = 0.0, vmax = 1.0, interpolation = 'None')
        self.cm = self.im.get_cmap()
        self.cm.set_bad((0, 0, 0))
        self.cm.set_under((0, 0, 0))
        self.cm.set_over((1, 1, 1))
        
        self.fig.colorbar(self.im)

        self.norm = "Sqrt"

        # Handle mouse button presses
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        #self.plot()
        self.draw()

    def plot(self):
        """Update plot data and redraw plot"""
        # Normal plot()
        self.im.set_data(self.data)
        # would be nice to use set_clim() for cleared data
        #self.im.autoscale(tight = True)
        dmin = self.data.min()
        if (dmin <= 0.0):
            #print(self.norm)
            if (self.norm == "Log"):
                dmin = 0.3
            else:
                dmin = 0.0
        dmax = self.data.max()
        if (dmax < 1.0):
            dmax = 1.0
        self.im.set_clim(dmin, dmax)

        self.draw()

    def append_data(self, newdata):
        """Add new plot data but don't redraw/replot"""
        # Add photon by photon...

        if (newdata.segment == self.segment):
            for i in range(newdata.len):
                self.data[newdata.y[i], newdata.x[i]] += 1
                # ignore p etc...

    def clear(self):
        """Clear plot data and replot"""
        self.data[:] = 0
        #self.plot()
        # Manual replot allows for better initial scaling...
        #self.im.set_data(self.data)
        #self.im.set_clim(0, 1)
        #self.draw()
        self.plot()

    # Capture clicks
    def on_click(self, event):
        #print(event)
        # In the actual image plot
        if (event.inaxes == self.axes):
            print(int(event.xdata), int(event.ydata))

    # Plot colormap
    def set_plot_cm(self, cm_name):
        #mp.set_cmap(cm_name)
        self.im.set_cmap(cm_name)
        self.cm = self.im.get_cmap()
        self.cm.set_bad((0, 0, 0))
        self.cm.set_under((0, 0, 0))
        self.cm.set_over((1, 1, 1))

        self.plot()

    # Plot Normalization
    def set_plot_norm(self, norm_name):
        if (norm_name == "Linear"):
            self.norm = norm_name
            norm = Normalize()
            self.im.set_norm(norm)
            self.plot()
        elif (norm_name == "Log"):
            self.norm = norm_name
            dmax = self.data.max()
            if (dmax <= 1.0):
                dmax = 1.0
            norm = LogNorm(vmin = 0.3, vmax = dmax)
            self.im.set_norm(norm)
            #print(norm.vmin)
            self.plot()

        elif (norm_name == "Sqrt"):
            self.norm = norm_name
            dmax = self.data.max()
            if (dmax <= 1):
                dmax = 1
            norm = PowerNorm(gamma = 0.5)
            self.im.set_norm(norm)
            self.plot()
        else:
            print("Warning: Bad plot norm selected...")
            # go to linear here?
            self.norm = "Linear"
            norm = Normalize()
            self.im.set_norm(norm)
            self.plot()

