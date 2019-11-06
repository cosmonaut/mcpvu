#import sys

# Base plugin. All plugins should inherit this class.

class BasePlugin(object):
    def __init__(self):
        print("BasePlugin loaded...")
        self._config = PluginConfig()

    def start(self):
        """Start plugin"""
        pass

    def stop(self):
        """Stop plugin"""
        pass

    def get_config(self):
        """Get plugin configuration (of type PluginConfig)"""
        return(self._config)


class PluginConfig(object):
    def __init__(self):
        self.xbits = 8
        self.ybits = 8
        self.pbits = 8


        
def load_plugin():
    p = BasePlugin()
    return(p)
