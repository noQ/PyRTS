'''
Created on Apr 27, 2012

@author: Adrian Costia
'''

import web
import time
import random
import datetime
import uuid
import hashlib
from hmac import *
from pyrts import NOT_AUTHORIZED, get_error
from pyrts.settings import RUN_MODE
from pyrts.datastore.store import DataStore
from pyrts.datastore.models import * #@UnusedWildImport
from pyrts.core.configparser import *
from pyrts.core.net import *
from pyrts.core.const import *
from pyrts.core.decorators.security import *
from pyrts.core.cachemanipulator import get_from_cache
from pyrts.core.restexception import NotAuthorized,SaveDataException
from pyrts.core.serializers.base import MongoObject


try:
    from hashlib import sha1
    sha = sha1
except:
    import sha

'''
    Generate token
'''

def read_web_data(web_data,**kwargs):
    return (kwargs["code"], kwargs["address"],web_data) 

class token_handler:
    '''
        Generate token for node server
            
            - Call example:
                http://192.168.190.29:8080/token/
            - METHOD: GET
            - Response:
                {
                    'token': 'ae05666ca8318a3ade92f8313bcd297fbaa15d0e', 
                    'is_valid': True, 
                    'id': '4fe4937a6ee7221e14000000',
                    'expire_at': 1371936952, 
                    'address': '192.168.190.29'
                }
                
    '''
    def GET(self):
        web.header('Content-Type', 'application/json')
        ''' read data from web and return web code '''
        response_code, remote_addr, response_data = read_web_data(web)
        
        ''' raise exception if authorization fail '''
        if response_code == NOT_AUTHORIZED:
            return dict(error=get_error(NOT_AUTHORIZED))
        if remote_addr is None or len(remote_addr) == 0:
            return dict(error=get_error(NOT_AUTHORIZED))
            
        ''' generate and save access token '''
        access_token = generate_access_token()
        try:
            token_obj = AccessToken(address=remote_addr,
                        token=access_token,
                        expire_at = int(time.time() + one_year_in_seconds),
                        is_valid = True
                        )
            token_obj.save()
            ''' convert mongo object in json '''
            json_obj =  MongoObject.to_json(token_obj)
            return json_obj
        except Exception as error:
            return  {"error" : str(error)}

class AuthToken(object):
    '''
        Generate AuthToken
    '''    
    def __init__(self, key=None, secret=None, iface='eth0'):
        self.key = key
        self.secret = secret
        self.iface = iface
    
    def expire_in_24h(self):
        '''return a UNIX style timestamp representing 24 hours from now'''
        return int(time.time() + one_day_in_seconds)
    
    def shuffle_word(self,word):
        ''' shuffle word '''
        return ''.join(random.sample(word, len(word)))
    
    def sha_key(self,key,secret_word):
        crypted_string = self.shuffle_word(key + str(time.time()) + secret_word)
        return sha(crypted_string).hexdigest()
    
    def generate_uuid(self, tip=None):
        '''
            generate unique ID
        '''
        current_time = long(round(time.time() * 1000))
        if tip is None:
            tip = random.random()
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(current_time)+str(tip))

    @staticmethod
    def get_random_uuid():
        return AuthToken().generate_uuid()

    def simple_hash(self, nchars=16):
        chars   =  'azertyupqsdfghjkmwxcvbn1234567890AZERTYUPQSDFGHJKMWXCVBN'
        hash    = ''
        for char in range(nchars):
            rand_char = random.randrange(0, len(chars))
            hash += chars[rand_char]
        return hash

    @staticmethod
    def password_hash(password, algorithm='sha512'):
        return hashlib.new(algorithm, password).hexdigest()
    
    def generate_auth_token(self):
        net = Network()
        ''' Get web server MAC address for default iface eth0''' 
        mac = net.getHwAddr(self.iface)
        return self._compose_key(mac)
    
    def _get_from_config(self, what):
        if Config.getConfig().has_section("TOKEN"):
            key = Config.getValue("TOKEN", what)
            if key is None:
                raise Exception("KEY/SECRET WORD not found in .cfg file, section [TOKEN] ")
            return key
        raise Exception("Section [TOKEN] not found in .cfg file!")
    
    def _compose_key(self, mac):
        # get secret key (word)
        if self.key is None:
            secret_words = SECRET_WORDS
            if len(secret_words) > 0:
                rand = random.randrange(0, len(secret_words))
                try:
                    secret_word = secret_words[rand]
                    if secret_word:
                        self.key = secret_word.word
                except ValueError:
                    self.key = self._get_from_config("key")
            else:
                self.key = self._get_from_config("key")

        # create secret key
        key = "%s%s%s" % (self.key, mac, str(self.expire_in_24h()))
        # shuffle key
        key = self.shuffle_word(key)
        if self.secret is None:
            self.secret = self._get_from_config("secret")
        sha_key = self.sha_key(key, self.secret)
        return sha_key
    
def generate_access_token():
    token = AuthToken()
    return token.generate_auth_token()

def test_token():
    token = AuthToken()
    otoken = token.generate_auth_token()
    print "Generated token: " + str(otoken)

if __name__ == "__main__":
    test_token()
