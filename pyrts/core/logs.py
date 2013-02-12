import logging
import os.path
from pyrts.core.configparser import Config

class Logger:
    def __init__(self,loggerName=None):
        # if the logger name is not specified then set default logger name
        if loggerName is None:
            self.DEFAULT_LOGGER = Config.getValue("LOGGER", "DEFAULT_LOGGER_NAME") 
        else:
            self.DEFAULT_LOGGER = loggerName
        
        # set logger
        self.log = logging.getLogger(self.DEFAULT_LOGGER)
        # set file. for more details view web.cfg
        self.logFile   =  Config.getValue("LOGGER", "LOG_FILE")
        
        self.hdlr      = logging.FileHandler(os.path.join(os.path.dirname(__file__), '..', 'web', self.logFile))
        # define log format: 2012-02-19 11:30:26,618 - empathy - DEBUG - web.py - 234 - debug test message
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
        # set file handler. will write in the file defined by handler.
        self.hdlr.setFormatter(self.formatter)
        # set log handler
        self.log.addHandler(self.hdlr)
        # set level for logger
        self.logLevel   =  Config.getValue("LOGGER", "LOG_LEVEL")
        self.log.setLevel(logging._levelNames[self.logLevel])
