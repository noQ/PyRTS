# Copyright (C) 2013 Costia Adrian
# Created on January 14, 2013
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from hashlib import sha1
from random import randrange
from socket import error, socket, AF_INET, SOCK_STREAM
from time import time
import imp
import inspect
import itertools
import os
import platform
import random
import re
import string
import sys
import types
import uuid
from pyrts.core.const import *
from pyrts.core.restexception import RestException, NotBoolean

class GeoData:
    pass

def checkHost(host,port):
    s = socket(AF_INET, SOCK_STREAM)
    try:
        try:
            s.connect((host, port))
            return True
        except (IOError, error):
            return False
    finally:
        s.close()

def parse_hosts(srv_list):
    servers = srv_list.split(COMMA)
    print "Checking host(s)...Please wait few moments."
    for server in servers:
        (host,port) = server.split(":")
        if port is None:
            port = 20000
        # check host
        print "Host %s:%s " % (host,port)
        if not checkHost(host,int(port)):
            print "Host %s:%s is down! " % (host,port)
            sys.exit(2)
        else:
            print "Host %s:%s is up! " % (host,port)
    return servers


def create_file(name, content):
    if os.path.isdir(name):
        raise IOError("%s must be a file instance not a directory!" % name)
    fd = None
    while True:
        try:
            ''' open file in "w" mode '''
            fd = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_BINARY', 0))
            try:
                ''' write file content '''
                os.write(fd, content)
            finally:
                os.close(fd)
        except OSError, e:
            raise IOError("File exists!")
        else:
            '''
                The file saved worked. Exit now!
            '''
            break
    ''' set file permission '''
    os.chmod(name, 0644)
    ''' return unique file id '''
    return fd
    

def checkFile(file):
    '''
        Check file
    '''
    if not os.path.isfile(file):
        raise IOError("Can't find file " + str(file))

def path_exists(path):
    '''
        Check path
    '''
    if os.path.exists(path):
        return True
    return False
   

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

def logical_drives():
    import string
    from ctypes import windll

    logical_drives = []
    bmask = windll.kernel32.GetLogicalDrives() 
    for drv in string.uppercase:
        if bmask & 1:
            logical_drives.append(drv)
        bmask >>= 1
    return logical_drives


def whereis(find_file):
    '''
        Locate file on drive
    '''
    drives = logical_drives()
    for drv in drives:
        print "Reading drive >> " + drv + "...Please wait few seconds."
        for path, dirs, files in os.walk(drv+":\\"):
            for file in files:
                if find_file in file:
                    # set file location in config file
                    return path

def validate_email(email):
    '''
        Validate email address:
            Exemplu: validate_email('test@csign.com')
    '''
    if len(email) > 6:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", email) != None:
            return True
    return False

class Options(object):
    pass


def _resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in xrange(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level "
                              "package")
    return "%s.%s" % (package[:dot], name)

def import_module(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    """
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]


def load_class(clazz):
    pass

def has_method(clazz,method):
    class_methods = inspect.getmembers(clazz, inspect.ismethod)
    if not isinstance(class_methods, list):
        raise TypeError,"clazz method must be a List instance"

    if len(class_methods) > 0:
        for class_method in class_methods:
            if method in class_method[0]: # where "method" is the method in clazz
                return True
    return False

def get_clazz_methods(clazz):
    return inspect.getmembers(clazz, inspect.ismethod)

def inspect_clazz(clazz):
    methods = get_clazz_methods(clazz)
    methods_map = {}
    for method in methods:
        methods_map[method[0]]=method[1]
    return methods_map    

def dict2Class(data):
    '''
        Transform dictionary in class 
    '''
    if isinstance(data, list):
        data = [dict2Class(val) for val in data]
    if not isinstance(data, dict):
        return data
    
    options = Options()
    for key in data:
        options.__dict__[key] = dict2Class(data[key])
    return options

class dict2object(object):
    def __init__(self, d):
        self.__dict__['d'] = d

    def __getattr__(self, key):
        value = self.__dict__['d'][key]
        if type(value) == type({}):
            return dict2object(value)
        return value
  
def dict2GeoLocation(data):
    '''
        Transform dictionary in class 
    '''
    if isinstance(data, list):
        data = [dict2GeoLocation(val) for val in data]
    if not isinstance(data, dict):
        return data
    
    locations = GeoData()
    for key in data:
        locations.__dict__[key] = dict2GeoLocation(data[key])
    return locations

def attr2Class(clazz,data):
    '''
        Transform dictionary in class 
    '''
    if isinstance(data, list):
        data = [attr2Class(clazz,val) for val in data]
    if not isinstance(data, dict):
        return data
    
    for key in data:
        clazz.__dict__[key] = attr2Class(clazz,data[key])
    return clazz

def class2Dict(clazz):
    if isinstance(clazz, object):
        delattr(clazz, "__doc__")
        delattr(clazz, "__module__")
        return clazz.__dict__

def setParam(params,key,value=True):
    if to_bool(value):
        setattr(params,key,value)
    else:
        delattr(params, key)
    

def to_unicode(string):
    """
        Converts a 'string' to unicode
    """
    if not isinstance(string, unicode):
        if not isinstance(string,str):
            raise TypeError('You are required to pass either unicode or string here, not: %r (%s)' % (type(string), string))
        try:
            string = string.decode("UTF-8")
        except UnicodeDecodeError, exc:
            raise TypeError(str(exc))
    return string

def to_utf8(string):
    return to_unicode(string).encode("UTF-8")

def to_bool(value):
    """
       Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if isinstance(value,bool):
        return value
    if str(value).lower() in ("yes", "y", "true",  "t", "1"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
    raise NotBoolean(value='Invalid value for boolean conversion: ' + str(value))


def to_param(param,value):
    return "".join(["--",param,"=",value])

def to_option(param):
    return "".join(["--",param])

def capitalize_word(param):
    if UNDERSCORE in param:
        words = param.lower().split("_")
        param = ''.join('%s' % (word.lower().capitalize()) for word in words)
    else:
        ''' remove whitespace and capitalize string '''
        param = param.lower().capitalize().strip()
    return param
    
def list_to_str(array):
    if len(array) > 0:
        _elements = 1
        _str = ''
        for elem in array:
            if _elements == len(array):
                _str += '%s' % (elem)
            else:
                _str += '%s,' % (elem)
            _elements += 1
        return _str

def extract_parameters(clazz):
    _params = []
    clazz_params = clazz.__dict__
    if len(clazz_params) > 0:
        for (key,value) in clazz_params.items():
            param = None
            if isinstance(value, bool):
                if value:
                    param = to_option(key)                
            else:
                param = to_param(key, str(value))
            if param is not None:
                _params.append(param)
    return _params
    

def array2params(array):
    '''
        Transform a dictionary to param 
    '''
    return ''.join(' %s' % (param) for param in array)

def getParamValue(arg,search_key):
    try:
        if arg.find(search_key) != -1:
            if arg.find(EQUAL) == -1:
                raise Exception(" '=' not found in key! Please use key=value ")
            uargs = arg.split("=")
            return uargs[1]
        else:
            return arg
    except Exception:
        return None

def generate_simple_token(nchars=16):
    chars   =  'azertyupqsdfghjkmwxcvbn1234567890AZERTYUPQSDFGHJKMWXCVBN'
    hash    = ''
    for char in xrange(nchars):
        rand_char = random.randrange(0, len(chars))
        hash += chars[rand_char]
    return hash

def generate_random_name():
    return generate_simple_token(nchars=7)

def generate_words(*args):
    return ("".join(letters) for letters in itertools.product(*args))

def generate_id_by_uuid():
    ''' Generate random UUID. Return UUID in HEX format ''' 
    tmp_uuid = uuid.uuid4()
    return tmp_uuid.hex
    
def generate_id():
    return sha1(str(time()) + str(randrange(1000000))).hexdigest()[:10]
