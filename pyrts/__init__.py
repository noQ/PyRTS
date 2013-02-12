STATUS_CODE_TEXT = {
    'SUCCESS' : 0,
    'JSON_PROTOCOL_ERROR' : 1,
    'METHOD_NOT_DEFINED' : 2,
    'REST_METHOD_ERROR' : 3,
    'JSON_INVALID' : 4,
    'HTTPS_NOT_USED' : 5,
    100: 'CONTINUE',
    101: 'SWITCHING PROTOCOLS',
    200: 'OK',
    201: 'CREATED',
    202: 'ACCEPTED',
    203: 'NON-AUTHORITATIVE INFORMATION',
    204: 'NO CONTENT',
    205: 'RESET CONTENT',
    206: 'PARTIAL CONTENT',
    300: 'MULTIPLE CHOICES',
    301: 'MOVED PERMANENTLY',
    302: 'FOUND',
    303: 'SEE OTHER',
    304: 'NOT MODIFIED',
    305: 'USE PROXY',
    306: 'RESERVED',
    307: 'TEMPORARY REDIRECT',
    400: 'BAD REQUEST',
    401: 'UNAUTHORIZED',
    402: 'PAYMENT REQUIRED',
    403: 'FORBIDDEN',
    404: 'NOT FOUND',
    405: 'METHOD NOT ALLOWED',
    406: 'NOT ACCEPTABLE',
    407: 'PROXY AUTHENTICATION REQUIRED',
    408: 'REQUEST TIMEOUT',
    409: 'CONFLICT',
    410: 'GONE',
    411: 'LENGTH REQUIRED',
    412: 'PRECONDITION FAILED',
    413: 'REQUEST ENTITY TOO LARGE',
    414: 'REQUEST-URI TOO LONG',
    415: 'UNSUPPORTED MEDIA TYPE',
    416: 'REQUESTED RANGE NOT SATISFIABLE',
    417: 'EXPECTATION FAILED',
    500: 'INTERNAL SERVER ERROR',
    501: 'NOT IMPLEMENTED',
    502: 'BAD GATEWAY',
    503: 'SERVICE UNAVAILABLE',
    504: 'GATEWAY TIMEOUT',
    505: 'HTTP VERSION NOT SUPPORTED',
}

STR_ZERO = "0"

''' error code name '''
STATUS_SUCCESS         = 0
STATUS_ERROR           = 1
REST_EXCEPTION         = -1
CONFIG_EXCEPTION       = -2
SAVE_ERROR             = -3
PARAMETER_NOT_FOUND    = -4
DATA_NOT_FOUND         = -5
READ_ERROR             = -6
DELETE_ERROR           = -7
PROTOCOL_ERROR         = -8
HOST_ID_DOWN           = -9
TOKEN_INVALID          = -10
TOKEN_EXPIRED          = -11
UID_INVALID            = -12
AUTHENTICATION_ERROR   = -13
AUTHORIZED             = -18
NOT_AUTHORIZED         = -19
ACCOUNT_NOT_ACTIVATED  = -20
PLUGIN_NOT_FOUND       = -21
GENERAL_ERROR          = -22
INVALID_DATA           = -23
PARAMETER_LENGTH_ZERO  = -24
NO_MEDIA_FOUND         = -25
NOT_IMPLEMENTED        = -26
PARAMETER_INVALID      = -27
INVALID_EMAIL          = -28
USER_EXIST             = -29
USER_NOT_EXIST         = -30
INVALID_LOCALE         = -31
DB_ERROR               = -32
COLLECTION_ERROR       = -37
GAME_SESSION_ERROR     = -38
PLUGIN_NOT_FOUND       = -39
CONTROLLER_ERROR       = -40

SUCCESS            = "OK"
FAILED             = "NOK"

''' error messages '''
REST_EXCEPTION_MSG         = ""
CONFIG_EXCEPTION_MSG       = "Config parameter not found"
PARAMETER_NOT_FOUND_MSG    = "Parameter not found"
TOKEN_INVALID_MSG          = "Token invalid"
TOKEN_EXPIRED_MSG          = "Token expired!"
AUTHENTICATION_ERROR_MSG   = "Authentication error"
SAVE_ERROR_MSG             = "Unable to save data"
DATA_NOT_FOUND_MSG         = "Data not found"
READ_ERROR_MSG             = "Unable to read data"
DELETE_ERROR_MSG           = "Unable to delete data"
HOST_ID_DOWN_MSG           = "Host is down!"
NOT_AUTHORIZED_MSG         = "Permission Denied! Authorization failed."
INVALID_DATA_MSG           = "Invalid data"
NO_MEDIA_FOUND_MSG         = "No media file found"
NOT_IMPLEMENTED_MSG        = "Not Implemented!"
UID_INVALID_MSG            = "UID is invalid!"
INVALID_DATA_MSG           = "Invalid data"
INVALID_LOCALE_MSG         = "Invalid locale"
USER_EXIST_MSG             = "User already registered!"
INVALID_POI_MSG            = "Invalid POI"
FRIEND_ERROR_MSG           = "User has no friend"
COLLECTION_ERROR_MSG       = "Collection exists"
CONTROLLER_ERROR_MSG       = "Controller  error"

GAME_SESSION_MSG           = "Unable to create/join game session. Maybe game session is full. Please, try again later!"
PLUGIN_NOT_FOUND_MSG       = "Plugin not found or loaded."


''' store all errors '''
WEB_ERROR = {
    STATUS_SUCCESS        : SUCCESS,
    STATUS_ERROR          : FAILED,
    REST_EXCEPTION        : REST_EXCEPTION_MSG,
    PARAMETER_NOT_FOUND   : PARAMETER_NOT_FOUND_MSG,
    CONFIG_EXCEPTION      : CONFIG_EXCEPTION_MSG,
    SAVE_ERROR            : SAVE_ERROR_MSG,
    TOKEN_INVALID         : TOKEN_INVALID_MSG,
    AUTHENTICATION_ERROR  : AUTHENTICATION_ERROR_MSG,
    DATA_NOT_FOUND        : DATA_NOT_FOUND_MSG,
    READ_ERROR            : READ_ERROR_MSG,
    DELETE_ERROR          : DELETE_ERROR_MSG,
    HOST_ID_DOWN          : HOST_ID_DOWN_MSG,
    NOT_AUTHORIZED        : NOT_AUTHORIZED_MSG,
    NO_MEDIA_FOUND        : NO_MEDIA_FOUND_MSG,
    NOT_IMPLEMENTED       : NOT_IMPLEMENTED_MSG,
    TOKEN_EXPIRED         : TOKEN_EXPIRED_MSG,
    INVALID_DATA          : INVALID_DATA_MSG,
    INVALID_LOCALE        : INVALID_LOCALE_MSG,
    USER_EXIST            : USER_EXIST_MSG,
    UID_INVALID           : UID_INVALID_MSG,
    COLLECTION_ERROR      : COLLECTION_ERROR_MSG,
    GAME_SESSION_ERROR    : GAME_SESSION_MSG,
    PLUGIN_NOT_FOUND      : PLUGIN_NOT_FOUND_MSG,
    CONTROLLER_ERROR      : CONTROLLER_ERROR_MSG

}

def get_error(code):
    if WEB_ERROR.has_key(code):
        return WEB_ERROR.get(code)
    ''' return general error : -1 '''
    return REST_EXCEPTION
