import json
from pyrts import *

def rest_error(message, code=STATUS_ERROR):
    return json.dumps({'e': code , 'm': message })    

class RestException(Exception):
    def __init__(self, value, code=-1):
        self.value = value
        self.code = code
    def __str__(self):
        return repr(self.value)

class ControllerException(RestException):
    def __init__(self,value=get_error(CONTROLLER_ERROR)):
        RestException.__init__(self, value, code=CONTROLLER_ERROR) 

class NotNode(RestException):
    def __init__(self):
        self.message = "Is not node"

class ProtocolError(RestException):
    def __init__(self,value=get_error(PROTOCOL_ERROR)):
        RestException.__init__(self, value, code=PROTOCOL_ERROR) 

class ConfigException(RestException):
    def __init__(self,value=get_error(CONFIG_EXCEPTION)):
        RestException.__init__(self, value, code=CONFIG_EXCEPTION) 

class HostIsDown(RestException):
    def __init__(self,value=get_error(HOST_ID_DOWN)):
        RestException.__init__(self, value, code=HOST_ID_DOWN) 
    
class ServerException(RestException):
    pass

class ImportModuleException(Exception):
    pass

class FileNotFound(Exception):
    pass

class NotBoolean(RestException):
    def __init__(self, value="Not instance of boolean!"):
        RestException.__init__(self, value)        

class NotList(RestException):
    def __init__(self, value="Not instance of list!"):
        RestException.__init__(self, value)        

class NotDictionary(RestException):
    def __init__(self,value="Not instance of dictionary!"):
        RestException.__init__(self, value)        

class NotInt(RestException):
    def __init__(self,value="Not instance of int!"):
        RestException.__init__(self, value)        

class DBError(RestException):
    def __init__(self,value="Database error"):
        RestException.__init__(self, value)

class ServerParametersNotFound(RestException):
    def __init__(self, value=get_error(PARAMETER_NOT_FOUND)):
        RestException.__init__(self, value, code=PARAMETER_NOT_FOUND)

class AuthTokenException(RestException):
    '''
        Authorization required
    '''
    def __init__(self,value=get_error(TOKEN_INVALID)):
        RestException.__init__(self, value, code=TOKEN_INVALID)        

class AuthTokenExpired(RestException):
    '''
        Authorization token expired
    '''
    def __init__(self,value=get_error(TOKEN_EXPIRED)):
        RestException.__init__(self, value, code=TOKEN_EXPIRED)        

class AuthenticationError(RestException):
    def __init__(self,value=get_error(NOT_AUTHORIZED)):
        RestException.__init__(self, value, code=NOT_AUTHORIZED)        

class NotAuthorized(RestException):
    def __init__(self,value=get_error(NOT_AUTHORIZED)):
        RestException.__init__(self, value, code=NOT_AUTHORIZED)        

class SaveDataException(RestException):
    def __init__(self, value=get_error(SAVE_ERROR)):
        RestException.__init__(self, value, code=SAVE_ERROR)

class DeleteDataException(RestException):
    def __init__(self, value=get_error(DELETE_ERROR)):
        RestException.__init__(self, value, code=DELETE_ERROR)

class ReadDataException(RestException):
    def __init__(self, value=get_error(READ_ERROR)):
        RestException.__init__(self, value, code=READ_ERROR)

class DataNotFound(RestException):
    def __init__(self, value=get_error(DATA_NOT_FOUND)):
        RestException.__init__(self, value, code=DATA_NOT_FOUND)

class InvalidDataException(RestException):
    def __init__(self, value=get_error(INVALID_DATA)):
        RestException.__init__(self, value, code=INVALID_DATA)

class InvalidLocaleException(RestException):
    def __init__(self, value=get_error(INVALID_LOCALE)):
        RestException.__init__(self, value, code=INVALID_LOCALE)
    
class UserExists(RestException):
    def __init__(self, value=get_error(USER_EXIST)):
        RestException.__init__(self, value, code=USER_EXIST)

class UserException(RestException):
    def __init__(self, value=get_error(UID_INVALID)):
        RestException.__init__(self, value, code=UID_INVALID)

class CollectionException(RestException):
    def __init__(self, value=get_error(COLLECTION_ERROR)):
        RestException.__init__(self, value, code=COLLECTION_ERROR)

class GameSessionException(RestException):
    def __init__(self, value=get_error(GAME_SESSION_ERROR)):
        RestException.__init__(self, value, code=GAME_SESSION_ERROR)

class PluginNotFound(RestException):
    def __init__(self, value=get_error(PLUGIN_NOT_FOUND)):
        RestException.__init__(self, value, code=PLUGIN_NOT_FOUND)
