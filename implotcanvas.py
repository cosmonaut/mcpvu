import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# image widget
# Todo
# * Log scaling
# * Toolbar or pan/zoom
# * Colormap options
class implotCanvas(FigureCanvas):
    def __init__(self, parent = None, xbit = 8, ybit = 8, width = 6, height = 4, dpi = 150):

        fig = Figure(figsize = (width, height), dpi = dpi)

        self.xsize = 2**xbit
        self.ysize = 2**ybit

        self.data = np.zeros((self.xsize, self.ysize), dtype = np.uint32)

        self.axes = fig.add_subplot()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        #         FigureCanvas.setSizePolicy(self,
        #                 QSizePolicy.Expanding,
        #                 QSizePolicy.Expanding)
        #         FigureCanvas.updateGeometry(self)

        
        self.im = self.axes.imshow(self.data, origin = 'lower')
        self.draw()

        #self.d1 = np.arange(4096*4096) % 65535
        #self.d1 = np.arange(4096*4096).reshape((4096,4096)) % 65535
        #self.d1 = self.d1.astype(np.uint32)

        #self.d2 = (self.d1 + 65535//2) % 512

        #self.d = [self.d1, self.d2]
        #self.i = 0

    def plot(self):
        #rn = np.random.randint(low=1, high=100, size=(self.data.shape))
        #rn = np.zeros(self.data.shape, dtype = np.uint32)
        #rn = rn + 10
        #self.data[:] = rn[:]
        #self.data[:] = self.d[self.i]
        #self.i = (self.i + 1) % 2

        # Normal plot()
        self.im.set_data(self.data)
        self.im.autoscale()
        self.draw()

    def append_data(self, newdata):
        # Add photon by photon...
        for i in range(newdata.len):
            self.data[newdata.y[i], newdata.x[i]] += 1
            # ignore p etc...

    def clear(self):
        self.data[:] = 0
        self.plot()

    
