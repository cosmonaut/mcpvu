import threading
import queue
import time
import numpy as np
from implotwidget import ImplotWidget



# Photon data. Using fixed size numpy arrays right now.
class PhotonData(object):
    def __init__(self, chunksize = 244):
        # x, y, and pulse height
        self.x = np.zeros(chunksize, dtype = np.uint16)
        self.y = np.zeros(chunksize, dtype = np.uint16)
        self.p = np.zeros(chunksize, dtype = np.uint16)
        #self.seg = np.zeros(chunksize, dtype = np.uint8)
        # index of detector segment (one segment per photondata chunk)
        self.segment = 0
        # Number of valid items in data
        self.len = 0


class PluginConfig(object):
    def __init__(self):
        """Configuration for each detector segment
        xbits, ybits, and pbits must have length that matches segments"""

        # Segment configurations
        self.segment_configs = [SegmentConfig(xbit = 8, ybit = 8, pbit = 8, segment = 0)]

        # Plot configurations
        self.plots = [PluginPlotItem()]

        # # Number of X bits per segment
        # self.xbits = [8]
        # # Number of Y bits per segment
        # self.ybits = [8]
        # # Number of pulse height bits per segment
        # self.pbits = [8]
        # # Number of detector segments
        # self.segments = 1

        # # Plot item config
        # #self.plots = [PluginPlotItem(row = 0, column = 0, row_span = 1, column_span = 1, segment = 0)]
        # self.plot = []


class SegmentConfig(object):
    def __init__(self, xbit = 8, ybit = 8, pbit = 8, segment = 0):
        """Configuration for a detector segment"""
        self.xbit = xbit
        self.ybit = ybit
        self.pbit = pbit
        self.segment = segment


class PlotConfig(object):
    def __init__(self, xbit = 8, ybit = 8, pbit = 8, segment = 0):
        """Configuration for a single plot"""
        self.xbit = xbit
        self.ybit = ybit
        self.pbit = pbit
        self.segment = segment


class PluginPlotItem(object):
    def __init__(self, plot_config = PlotConfig(), name = ImplotWidget, row = 0, column = 0, row_span = 1,
                 column_span = 1, segment = 0):
        """Plot item configuration"""
        self.name = ImplotWidget
        self.row = row
        self.column = column
        self.row_span = row_span
        self.column_span = column_span
        self.plot_config = plot_config


# Base plugin. All plugins should inherit this class.
class BasePlugin(object):
    def __init__(self):
        """Base plugin class"""
        self._config = PluginConfig()
        #self._config = config

        # Data
        self._data = PhotonData()
        # Data queue
        self._q = queue.SimpleQueue()

        # Event used to signal pause/unpause
        self._lock = threading.Event()
        # Start thread as paused
        self._lock.set()
        self._sample_thread = threading.Thread(target = self._run)
        # Flag for thread close (don't change in thread)
        self._flag = False

        print("BasePlugin loaded...")

    def start(self):
        """Start plugin"""
        if (not self._sample_thread.is_alive()):
            self._sample_thread.start()

    def stop(self):
        """Stop plugin"""
        if (self._sample_thread.is_alive()):
            # signal to stop thread...
            self._flag = True
            self.pause()
            self._sample_thread.join()
            print("thread closed...")

    def pause(self):
        """Pause sampler"""
        if (self._sample_thread.is_alive()):
            self._lock.set()

    def unpause(self):
        """Unpause sampler"""
        if (self._sample_thread.is_alive()):
            # Check that lock is locked...
            self._lock.clear()

    def get_config(self):
        """Get plugin configuration (of type PluginConfig)"""
        return(self._config)

    def _run(self):
        """Thread function -- primary sampling thread function"""
        while(True):
            if (self._lock.is_set()):
                # Search for quit flag
                if (self._flag):
                    print("Closing sampling thread")
                    return

                continue

            # Fill data object with test fake data
            #print("baseplugin sampler running...")
            for i in range(244):
                self._data.x[i] = i
                self._data.y[i] = i
                self._data.p[i] = i
                self._data.segment = 0
            self._data.len = 244
            # Queue up the data...
            self._q.put(self._data)
            
            time.sleep(0.1)

    def get_data(self):
        """Get sampler data
        Return data if available
        Return None if no data available
        """
        if (not self._q.empty()):
            try:
                d = self._q.get_nowait()
            except queue.Empty:
                d = None
            return(d)
        else:
            return(None)

    def get_data_len(self):
        """Get amount of data in queue"""
        return(self._q.qsize())

        
def load_plugin():
    p = BasePlugin()
    return(p)
