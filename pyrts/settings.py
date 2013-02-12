'''
Created on Jun 1, 2012

@author: Adrian Costia
'''

import traceback
from mongoengine import * #@UnusedWildImport
from pyrts.datastore.store import DataStore
from pyrts.datastore.models import SecretWords
from pyrts.core.logs import Logger
from pyrts.core.configparser import Config
from pyrts.core.restexception import RestException, ServerException, ConfigException
from pyrts.core.cache import *
from pyrts.core.cache.memory import *
from pyrts.core.util import to_bool
from pyrts.core.net import portIsOpen

''' Set enviroment: production or development '''
try:
    RUN_MODE    = Config.getValue("ENV", "environment")
except:
    raise ServerException("Enviroment not specified in .cfg file")

''' Get log level '''
DEBUG_LEVEL = False
try:
    log_level = Config.getValue("LOGGER", "LOG_LEVEL")
    if 'DEBUG' in log_level:
        DEBUG_LEVEL = True 
except:
    pass

''' Init logger '''
logger      = Logger("controller_handler").log

cert_path   = Config.getValue("PUSH", "cert_path")
cert_dev    = Config.getValue("PUSH", "cert_dev")=="YES"

''' Init support email '''
try:
    support_email = Config.getValue("WEB_APPLICATION", "SUPPORT_EMAIL")
except:
    raise ConfigException("[SUPPORT EMAIL] value not defined in section [WEB_APPLICATION] . See web.cfg!")

try:
    mail_server = Config.getValue("MAIL", "SERVER_ADDR")
except:
    raise ConfigException("[SERVER_ADDR] value not defined in section [MAIL] . See web.cfg!")

''' Read PLUGINS path '''
try:
    PLUGINS_PATH   = Config.getValue("PLUGINS", "path")
except:
    raise ConfigException("[path] value not defined in section [PLUGINS] . See web.cfg!")


''' Load default cache '''
try:
    ''' get backend and hosts from cfg file '''
    CACHE_BACKEND = Config.getValue("CACHE", "BACKEND")
    CACHE_HOST    = Config.getValue("CACHE", "HOST")
    ''' init default cache '''
    CACHE = get_cache(CACHE_BACKEND, **{
            'LOCATION': CACHE_HOST, 'TIMEOUT': 30,
    })
except:
    raise ConfigException("[BACKEND] value not defined in section [CACHE] . See web.cfg!")


SERVER_PID  = PID = "/var/run/pyrts.pid"
SERVER_PORT = 4949
''' check server port '''
#if portIsOpen(SERVER_PORT):
#    raise ServerException("Server port " + str(SERVER_PORT) + " is in use!")

try:
    DATABASE_NAME =  Config.getValue("DB", "database")
except Exception as exc:
    raise ConfigException("[database] value not defined in section [DB] . See web.cfg!")

''' Init DB connection '''
DATABASE  = DataStore(DATABASE_NAME).connect()

