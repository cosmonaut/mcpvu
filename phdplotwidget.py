import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QFrame, QVBoxLayout

class PHDPlotWidgetCont(QFrame):
    def __init__(self, plugin_config, plot_config, parent = None, width = 4, height = 4, dpi = 100):
        super(PHDPlotWidgetCont, self).__init__(parent = parent)
        # Give it a frame...
        self.setFrameStyle(QFrame.Box | QFrame.Plain);

        self.layout = QVBoxLayout()

        self.setLayout(self.layout)
        # Load plot
        self._plot = PHDPlotWidget(plugin_config, plot_config, parent = parent,
                                   width = width, height = height, dpi = dpi)

        self.layout.addWidget(self._plot)

    def plot(self):
        self._plot.plot()

    def append_data(self, new_data):
        self._plot.append_data(new_data)

    def clear(self):
        self._plot.clear()    


# phd plot widget
# Todo
# * multiple segments?
class PHDPlotWidget(FigureCanvas):
    def __init__(self, plugin_config, plot_config, parent = None, width = 3, height = 3, dpi = 150):

        self.fig = Figure(figsize = (width, height), dpi = dpi)

        # Detector segment
        # TODO: plot all at once -- maybe?
        self.segment = plot_config.segment

        # pulse height bits
        pbit = plot_config.pbit
        self.psize = 2**pbit
        
        # Plot data object
        self.data = np.zeros(self.psize, dtype = np.uint32)
        self.xdata = np.arange(self.psize)
        #self.xdata = np.arange(119, -1, -1)

        self.axes = self.fig.add_subplot()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        #         FigureCanvas.setSizePolicy(self,
        #                 QSizePolicy.Expanding,
        #                 QSizePolicy.Expanding)
        #         FigureCanvas.updateGeometry(self)

        # Line plot
        self.phdplot = self.axes.plot(self.xdata, self.data, color = 'black', ds = 'steps-mid')
        self.axes.set_ylim(0, 1)

        self.axes.grid(True)
        self.axes.set_title("Pulse Height")

        # Enable autoscaling
        self.axes.autoscale(enable = True, axis = 'y')
        
        # Handle mouse button presses
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        #self.plot()
        self.draw()

    def plot(self):
        """Update plot data and redraw plot"""
        # Update data
        self.phdplot[0].set_ydata(self.data)
        # relimit
        self.axes.relim()
        self.axes.autoscale_view()
        self.draw()

    def append_data(self, newdata):
        """Add new plot data but don't redraw/replot"""
        # Add photon by photon...
        if (newdata.segment == self.segment):
            for i in range(newdata.len):
                self.data[newdata.p[i]] += 1

    def clear(self):
        """Clear plot data and replot"""
        self.data[:] = 0

        #self.axes.set_ylim(0, 1)
        
        self.plot()
        # Manual replot allows for better initial scaling...
        #self.lplot[0].set_ydata(self.data)
        #self.axes.set_ylim(0, 1)
        #self.im.set_clim(0, 1)
        #self.draw()

    def on_click(self, event):
        # Print event in plot
        if (event.inaxes == self.axes):
            print(int(event.xdata), int(event.ydata))

