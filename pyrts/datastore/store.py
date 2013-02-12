'''
Created on Jan 20, 2012

@author: Adrian Costia

'''
from pyrts.core.configparser import Config
from mongoengine import connect

class DataStoreConnectionError(Exception):
    pass

class DataStore(object):
    
    _cfgFileDataStore   = "DB"
    _cfgServerAddrOpt   = "server_address"
    _cfgServerPortOpt   = "port"
    _cfgUser            = "username"
    _cfgPassword        = "password"
    
    _defaultServerAddr  = "localhost"
    _defaultServerPort  = 27017
    
    '''
        Initialize data store connection
         - params: collection - database
        Example: DataStore("users") , where users is the collection
         
    '''
    def __init__(self, db):
        self.username   = None
        self.password   = None
        self.has_credentials = False
        self.collection = db
        self.db_connection = None
        
        # loading configuration from web.cfg if section [DB] is present
        if Config.getConfig().has_section("DB"):
            # read option server address
            if Config.getValue(DataStore._cfgFileDataStore, DataStore._cfgServerAddrOpt) is None:
                self.serverAddr = DataStore._defaultServerAddr
            else: # read from config
                self.serverAddr = Config.getValue(DataStore._cfgFileDataStore, DataStore._cfgServerAddrOpt)
            # read option server port
            if Config.getValue(DataStore._cfgFileDataStore, DataStore._cfgServerPortOpt) is None:
                self.serverPort = DataStore._defaultServerPort
            else:
                self.serverPort = Config.getValue(DataStore._cfgFileDataStore, DataStore._cfgServerPortOpt)
        else:
            self.serverAddr = DataStore._defaultServerAddr
            self.serverPort = DataStore._defaultServerPort
        
        try:
            self.username = Config.getValue(DataStore._cfgFileDataStore, DataStore._cfgUser)
        except Exception:
            pass
        
        try:
            self.password = Config.getValue(DataStore._cfgFileDataStore, DataStore._cfgPassword)
        except Exception:
            pass
        
        if self.username is not None and self.password is not None:
            self.has_credentials = True

    def connect(self):
        #init datastore connection
        try:
            if self.has_credentials == True: # connect using credentials
                self.db_connection = connect(
                        self.collection,
                        host=self.serverAddr, port=self.serverPort,
                        username=self.username, password=self.password
                        )
            else:
                self.db_connection = connect(self.collection, host=self.serverAddr, port=int(self.serverPort))
            return self.db_connection
                
        except Exception, e:
            raise DataStoreConnectionError("Cannot connect to the database:\n%s" % e)
    