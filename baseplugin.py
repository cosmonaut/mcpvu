import threading
import time

# Base plugin. All plugins should inherit this class.

class BasePlugin(object):
    def __init__(self):
        """Base plugin class"""
        print("BasePlugin loaded...")
        self._config = PluginConfig()

        self._lock = threading.Event()
        # Start thread as paused
        self._lock.set()
        self._sample_thread = threading.Thread(target = self._run)
        self._flag = False

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

            print("baseplugin sampler running...")
            time.sleep(0.5)


class PluginConfig(object):
    def __init__(self):
        self.xbits = 8
        self.ybits = 8
        self.pbits = 8

        
def load_plugin():
    p = BasePlugin()
    return(p)
