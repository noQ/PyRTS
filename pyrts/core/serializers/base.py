
import calendar
import datetime
import decimal
import json
import re
from StringIO import StringIO
from bson import EPOCH_AWARE
from bson.dbref import DBRef
from bson.max_key import MaxKey
from bson.min_key import MinKey
from bson.objectid import ObjectId
from bson.timestamp import Timestamp
from bson.tz_util import utc
from json import JSONEncoder
from pyrts.core.date import *

try:
    import uuid
    _use_uuid = True
except ImportError:
    _use_uuid = False

_RE_TYPE = type(re.compile("foo"))

class SimpleSerializer(object):
    '''
        How to use:
            class person:
               def __init__(self,name):
                    self.name = name
                    
            me = person('my name is') 
            result = SimpleSerializer.serialize(me)
             >> {"name":"my name is"}
    '''
    
    IS_INSTANCE = 'instance'
    
    @staticmethod
    def encode(o):
        if type(o).__name__ == SimpleSerializer.IS_INSTANCE:
            return o.__dict__
        
    @staticmethod
    def serialize(o):
        return json.dumps(o, default=SimpleSerializer.encode)

class MongoEncoder(JSONEncoder):
    
    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def _dbref_to_obj(self,obj):
        son_obj =  obj.as_doc().to_dict()
        value = {}
        if son_obj:
            _ref = {}
            if son_obj.has_key("$id"):
                _ref["id"] = str(son_obj["$id"])
                value = _ref
        return value

    def default(self, o):
        ret = {}
        
        if isinstance(o, DBRef):
            return self._dbref_to_obj(o)

        attrs = o.__dict__["_data"]
        for obj,value in attrs.iteritems():
            if isinstance(obj,type(None)):
                if isinstance(value, ObjectId):
                    obj = "id"
                    value = str(value)
                else:
                    continue 
            elif isinstance(value, ObjectId):
                value = str(value)
            elif isinstance(value, DBRef):
                return self._dbref_to_obj(value)
            elif isinstance(value, datetime.datetime):
                # TODO share this code w/ bson.py?
                if value.utcoffset() is not None:
                    value = value - value.utcoffset()
                millis = int(calendar.timegm(value.timetuple()) * 1000 +
                             value.microsecond / 1000)
                value = millis
            elif isinstance(value, _RE_TYPE):
                flags = ""
                if value.flags & re.IGNORECASE:
                    flags += "i"
                if value.flags & re.MULTILINE:
                    flags += "m"
                value = {"$regex": value.pattern,"$options": flags}
            elif isinstance(value, MinKey):
                value = {"$minKey": 1}
            elif isinstance(value, MaxKey):
                value = {"$maxKey": 1}
            elif isinstance(value, Timestamp):
                value =  {"t": obj.time, "i": obj.inc}
            elif _use_uuid and isinstance(value, uuid.UUID):
                value = {"$uuid": obj.hex}
            elif isinstance(obj, (list, dict, str, unicode, int, float, bool, type(None))):
                value = value
            else:
                value = ""

            if value:
                ret[obj] = value
        return ret         
    

class MongoObject:
    '''
        How to use encoder :
           MongoObject.to_json(user)
            
    '''
    @staticmethod
    def to_json(o):
        json_str = json.dumps(o,cls=MongoEncoder)
        return json.loads(json_str)
    
