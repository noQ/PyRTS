'''
Created on Jun 22, 2012

@author: Adrian Costia
'''
import time
import web
import json
import traceback
from pyrts.settings import DEBUG_LEVEL
from pyrts import TOKEN_INVALID,READ_ERROR, AUTHORIZED, NOT_AUTHORIZED
from pyrts.core.cache import *
from pyrts.core.cachemanipulator import get_token_from_cache, get_from_cache, save_token_in_cache, save_in_cache
from pyrts.core.restexception import AuthTokenException, DBError, AuthTokenExpired
from pyrts.datastore.models import *
from pyrts.core.auth.token import *
from pyrts.core.params import PARAM_METHOD, PARAM_IP_ADDR, PARAM_TOKEN, PARAM_EXPIRE_AT

def security_token_required(func):
    """ Security token manipulator
     
        Example:
            @security_token_required()
            def get_controller_details(id, **kwargs):
                ...
                ...
                
    """
    def validate_token(*arg, **kwargs):
        if not kwargs.has_key(PARAM_TOKEN):
            raise AuthTokenException("Invalid token or token not found in the request")
        auth_token = kwargs.get(PARAM_TOKEN)
        if auth_token is None or len(auth_token) == 0:
            raise AuthTokenException("Invalid token or token length is ZERO")

        ''' check token. first check token in cache '''
        token = get_token_from_cache(str(auth_token))
        if token is None:
            ''' if token is none then get user token from db '''
            token = AccessToken.objects(token=str(auth_token), is_valid=True).first()
            if token is None:
                raise AuthTokenException("Token invalid")
            save_token_in_cache(str(auth_token), MongoObject.to_json(token))
            
        if not hasattr(token, PARAM_EXPIRE_AT):
            raise AuthTokenException("Token invalid! Expiration time not set!")
        ''' token is expired ? '''
        if int(time.time()) > token.expire_at:
            raise AuthTokenExpired()
        try:
            ''' delete token '''
            del kwargs[PARAM_TOKEN]
            kwargs["old_token"] = token.token
            ''' return function '''
            result = func(*arg, **kwargs)
            return result
        except Exception as e:
            traceback.print_exc()
            raise e
    validate_token.__doc__ = func.__doc__
    return validate_token


def whitelist_authorization(fn):
    ''' Check if address is in the whitelist '''
    def _is_in_list(web_address):
        address = get_from_cache(web_address)
        if address is None:
            address = AccessWhiteList.objects(address=web_address).first()
        if address:
            return True
        return False        
    
    def check_whitelist(request, **kwargs):
        authorized_code = NOT_AUTHORIZED
        data = None
        address = None
        web_context = web.ctx

        if not web_context.has_key(PARAM_IP_ADDR):
            authorized_code = NOT_AUTHORIZED
        else:
            address = web_context[PARAM_IP_ADDR]        
            if _is_in_list(address):
                authorized_code =  AUTHORIZED
                
        if web_context[PARAM_METHOD] == GET_METHOD:
            data = web.input()
        elif web_context[PARAM_METHOD] == POST_METHOD:
            data = web.data()
        return fn(data, address=address, code=authorized_code)
    return check_whitelist    
