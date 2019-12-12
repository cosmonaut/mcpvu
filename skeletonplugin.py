from baseplugin import BasePlugin, PluginPlotItem, SegmentConfig, PluginConfig, PlotConfig
from implotwidget import ImplotWidget
from implotwidget import ImplotWidgetCont
from lineplotwidget import LineplotWidget
import numpy as np
import time


IM_BITS = 10
PHD_BITS = 8
PAK_SIZE = 244


# An example of a simple plugin
class SkeletonPlugin(BasePlugin):
    def __init__(self):
        BasePlugin.__init__(self)
        # New config: 10 bit x and y (1024x1024).
        # 8 bit pulse height.
        # One segment

        # Overwrite config
        self._config = PluginConfig()

        # Segment configurations
        self._config.segment_configs = [SegmentConfig(xbit = IM_BITS, ybit = IM_BITS, pbit = PHD_BITS, segment = 0)]

        # Plot configurations
        pc = PlotConfig(xbit = IM_BITS, ybit = IM_BITS, pbit = PHD_BITS, segment = 0)
        print(pc.xbit)
        self._config.plots = [PluginPlotItem(plot_config = pc, name = ImplotWidgetCont, row = 0, column = 0,
                                             row_span = 1, column_span = 1, segment = 0),
                              PluginPlotItem(plot_config = pc, name = LineplotWidget, row = 2, column = 0,
                                             row_span = 1, column_span = 2, segment = 0)]


        # self._config.segments = 1
        # self._config.xbits = [IM_BITS]
        # self._config.ybits = [IM_BITS]
        # self._config.pbits = [PHD_BITS]
        # self._config.plots = [PluginPlotItem(name = ImplotWidget, row = 0, column = 0,
        #                                      row_span = 1, column_span = 1, segment = 0,
        #                                      xbit = 10. ybit = 10, pbit = 8)]

        # For random number generation...
        self._cen = (2**IM_BITS)//2
        self._pcen = (2**PHD_BITS)//2

        print("Skeleton plugin loaded...")

    # Override _run function...
    def _run(self):
        while(True):
            # This portion allows pausing and closing of the thread
            if (self._lock.is_set()):
                # Search for quit flag
                if (self._flag):
                    # End the thread...
                    return

                # while paused do small sleep to keep CPU usage lower
                time.sleep(0.01)

                continue


            # Generate random gaussian data for x, y, p
            x = np.random.normal(self._cen, 40, 244)
            x = x.astype(np.uint16)
            x[(x > 1023)] = 1023
            y = np.random.normal(self._cen, 40, 244)
            y = y.astype(np.uint16)
            y[(y > 1023)] = 1023
            p = np.random.normal(self._pcen, 40, 244)
            p = p.astype(np.uint8)
            #p[(p > 255)] = 255
            #s = np.zeros(244, dtype = np.uint8)
            s = 0

            # Populate data object
            self._data.x[:] = x[:]
            self._data.y[:] = y[:]
            self._data.p[:] = p[:]
            self._data.segment = s
            self._data.len = 244
            
            # Queue up the data...
            self._q.put(self._data)
            
            time.sleep(0.01)


def load_plugin():
    p = SkeletonPlugin()
    return(p)
