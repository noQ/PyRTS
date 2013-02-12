'''
Created on Jul 3, 2012

@author: Adrian Costia
'''
import sys
import glob
import time
import os
import imp
import logging
import traceback

''' store all plugins in dict '''
LOADED_PLUGINS = dict()

class PluginHandler(object):
    '''
        Plugins Handler - manipulate plugins: load/unload
    '''
    PY_EXT          = ".py"
    ALL_PY_FILES    = "*.py"
    ALL_PYC_FILES   = "*.pyc"

    def __init__(self, path, logevent=False):
        self.log_event = logevent
        self.plugin_path = path
        sys.path.append(self.plugin_path)
        if self.log_event:
            logging.basicConfig(level=logging.INFO,
                                format='%(asctime)s - %(message)s',
                                datefmt='%Y-%m-%d %H:%M:%S')
            logging.info("Start running plugin moniotor")
    
    @staticmethod
    def get_plugin(name):
        if LOADED_PLUGINS.has_key(name):
            return LOADED_PLUGINS.get(name)
        return None
    
    def load_class(self, clazz_name):
        clazz = __import__(clazz_name)
        LOADED_PLUGINS[clazz_name] = getattr(clazz, clazz_name)()
        return LOADED_PLUGINS[clazz_name]
    
    def reload_class(self,clazz_name):
        if self.class_is_loaded(clazz_name):
            clazz = reload(sys.modules[clazz_name])
            LOADED_PLUGINS[clazz_name] = getattr(clazz, clazz_name)()
            return LOADED_PLUGINS[clazz_name]
        else:
            return self.load_class(clazz_name)
    
    def remove_class(self,clazz_name):
        if self.class_is_loaded(clazz_name):
            try:
                del LOADED_PLUGINS[clazz_name]
                del sys.modules[clazz_name]
            except KeyError:
                traceback.print_exc()
    
    def clean_plugin_folder(self):
        _path = self.plugin_path + "/" + PluginHandler.ALL_PYC_FILES
        _pyc_files = glob.glob(_path)
    
    def class_is_loaded(self,clazz_name):
        if LOADED_PLUGINS.has_key(clazz_name):
            return True
        return False
    
    def is_py_file(self,filename):
        if filename.endswith(PluginHandler.PY_EXT):
            return True
        return False
    
    def __whatis(self, event):
        what = 'directory' if event.is_directory else 'file'
        return what

    def get_class_name(self, src_path):
        plugin_name = os.path.basename(src_path)                
        clazz_name, ext = os.path.splitext(plugin_name)
        return clazz_name

    def load_plugins(self):
        ''' Called when handler is initialized '''
        _path = self.plugin_path + "/" + PluginHandler.ALL_PY_FILES
        _plugins = glob.glob(_path)
        if len(_plugins) > 0:
            for plugin in _plugins:
                plugin_name = os.path.basename(plugin)                
                if plugin_name != "__init__.py": 
                    try:
                        if self.is_py_file(plugin_name):
                            clazz_name,ext = os.path.splitext(plugin_name)
                            if not self.class_is_loaded(clazz_name):
                                if self.log_event:
                                    logging.info("Class not in cache.Try to load clazz")
                                ''' load clazz '''
                                clazz = self.load_class(clazz_name)
                                if self.log_event:
                                    logging.info("Plugin %s loaded", str(plugin_name))
                    except Exception as exc:
                        traceback.print_exc()
                        if self.log_event:
                            logging.info("Unable to load plugin : " + str(exc))        
        return LOADED_PLUGINS
    
    def on_moved(self, event):
        """Called when a file or a directory is moved or renamed. """
        raise NotImplemented()

    def on_created(self, event):
        """Called when a file or directory is created."""
        raise NotImplemented()
    
    def on_deleted(self, event):
        ''' Called when a file or directory is deleted. '''
        raise NotImplemented()
    
    def on_modified(self, event):
        ''' Called when a file or directory is modified. '''
        raise NotImplemented()


class plugin_session:
    ''' Get plugin session '''
    def __init__(self):
        self.info = None

class plugin_dict(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.modified = False
        
    def __setitem__(self, *args, **kwargs):
        self.modified = True
        return dict.__setitem__(self, *args, **kwargs)