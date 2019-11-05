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
    def __init__(self, parent = None, width = 6, height = 4, dpi = 150):

        fig = Figure(figsize = (width, height), dpi = dpi)

        self.data = np.zeros((100,100), dtype = np.uint32)

        self.axes = fig.add_subplot()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        #         FigureCanvas.setSizePolicy(self,
        #                 QSizePolicy.Expanding,
        #                 QSizePolicy.Expanding)
        #         FigureCanvas.updateGeometry(self)

        
        self.im = self.axes.imshow(self.data)
        self.draw()

    def plot(self):
        rn = np.random.randint(low=1, high=100, size=(self.data.shape))
        self.data[:] = rn[:]
        self.im.set_data(self.data)
        self.im.autoscale()
        self.draw()

    def append(self, newdata):
        pass

    def clear(self):
        pass

    
