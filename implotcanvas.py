import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
#import matplotlib.pyplot as plt

# image widget
# Todo
# * Log scaling
# * Toolbar or pan/zoom
# * Colormap options
class implotCanvas(FigureCanvas):
    def __init__(self, parent = None, xbit = 10, ybit = 10, width = 6, height = 6, dpi = 150):

        self.fig = Figure(figsize = (width, height), dpi = dpi)

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
                                   vmin = 0, vmax = 1)
        self.fig.colorbar(self.im)

        # Handle mouse button presses
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        #self.plot()
        self.draw()

    def plot(self):
        """Update plot data and redraw plot"""
        # Normal plot()
        self.im.set_data(self.data)
        # would be nice to use set_clim() for cleared data
        self.im.autoscale()
        self.draw()

    def append_data(self, newdata):
        """Add new plot data but don't redraw/replot"""
        # Add photon by photon...
        for i in range(newdata.len):
            self.data[newdata.y[i], newdata.x[i]] += 1
            # ignore p etc...

    def clear(self):
        """Clear plot data and replot"""
        self.data[:] = 0
        # or manually replot to set better initial scale
        self.plot()

    def on_click(self, event):
        #print(event)
        # In the actual image plot
        if (event.inaxes == self.axes):
            print(int(event.xdata), int(event.ydata))

