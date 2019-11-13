from baseplugin import BasePlugin
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
        self._config.segments = 1
        self._config.xbits = [IM_BITS]
        self._config.ybits = [IM_BITS]
        self._config.pbits = [PHD_BITS]

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
            s = np.zeros(244, dtype = np.uint8)

            # Populate data object
            self._data.x[:] = x[:]
            self._data.y[:] = y[:]
            self._data.p[:] = p[:]
            self._data.seg[:] = s[:]
            self._data.len = 244
            
            # Queue up the data...
            self._q.put(self._data)
            
            time.sleep(0.01)


def load_plugin():
    p = SkeletonPlugin()
    return(p)
