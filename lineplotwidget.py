import numpy as np

from PyQt5.QtCore import QTimer

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# line plot widget
# Todo
# * multiple segments?
class LineplotWidget(FigureCanvas):
    def __init__(self, plugin_config, plot_config, parent = None, width = 3, height = 3, dpi = 100):

        self.fig = Figure(figsize = (width, height), dpi = dpi)
        #self.fig.tight_layout()

        # Count rate timer
        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.setSingleShot(False)
        self._timer.timeout.connect(self.count_rate)
        self._timer.start()
        
        self.segment = plot_config.segment

        self.c = 0
        
        # Plot data object
        self.data = np.zeros(120, dtype = np.uint32)
        self.xdata = np.arange(119, -1, -1)

        self.axes = self.fig.add_subplot()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        #         FigureCanvas.setSizePolicy(self,
        #                 QSizePolicy.Expanding,
        #                 QSizePolicy.Expanding)
        #         FigureCanvas.updateGeometry(self)

        # Line plot
        self.lplot = self.axes.plot(self.xdata, self.data, color = 'black', ds = 'steps-mid')
        self.axes.set_xlim(120, 0)
        #self.axes.set_ylim(0, 1)

        #self.lplot.set_grid(True)
        self.axes.grid(True)
        
        # Handle mouse button presses
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        #self.plot()
        self.draw()

    def plot(self):
        """Update plot data and redraw plot"""
        # Normal plot()
        self.lplot[0].set_ydata(self.data)
        # would be nice to use set_clim() for cleared data
        #self.lplot[0].autoscale()
        self.axes.relim()
        self.axes.autoscale_view()
        self.draw()

    def append_data(self, newdata):
        """Add new plot data but don't redraw/replot"""
        # Add photon by photon...

        if (newdata.segment == self.segment):
            #self.c += self.data.len
            self.c += newdata.len
        
    def count_rate(self):
        #self.c = 0
        self.data = np.roll(self.data, -1)
        self.data[-1] = self.c
        self.c = 0

    def clear(self):
        """Clear plot data and replot"""
        self.data[:] = 0
        #self.plot()
        # Manual replot allows for better initial scaling...
        self.lplot[0].set_ydata(self.data)
        #self.axes.set_ylim(0, 1)
        #self.im.set_clim(0, 1)
        self.draw()

    def on_click(self, event):
        #print(event)
        # Print event in plot
        if (event.inaxes == self.axes):
            print(int(event.xdata), int(event.ydata))

