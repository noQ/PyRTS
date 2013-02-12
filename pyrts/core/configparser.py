'''
Created on Jan 20, 2012

@author: Adrian Costia
'''
import ConfigParser
import os.path

class Config:

    _init_config          = False
    _config               = None
    _default_web_cfg_file = os.path.join(os.path.dirname(__file__), '..', 'web', 'web.cfg')
    
    @staticmethod
    def init():
        
        # check for web.cfg
        if os.path.isfile(Config._default_web_cfg_file):
            baseFilename = os.path.abspath(Config._default_web_cfg_file)
            
            # load config file
            Config._config = ConfigParser.RawConfigParser()
            Config._config.read(baseFilename)
            
            Config._init_config = True
            return Config._config
        else:
            # raise exception
            raise Exception("Config file web.cfg not found in package")

    @staticmethod
    def getConfig():
        if Config._init_config == False:
            Config.init()
        
        return Config._config

    # read value from section
    @staticmethod
    def getValue(section,key):
        if Config._init_config == False:
            Config.init()
            
        if Config._config is None:
            raise Exception("Config object not initialized")
        return Config._config.get(section, key);
