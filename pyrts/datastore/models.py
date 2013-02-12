'''
Created on Apr 20, 2012

@author: Adrian Costia
'''

import traceback
import datetime
from mongoengine import * #@UnusedWildImport


class AccessWhiteList(Document):
    '''192.168.190.18'''
    address     = StringField(required=True,unique=True)

class AccessBlackList(Document):
    address     = StringField(required=True,unique=True)

class AccessToken(Document):
    address     = StringField(required=True, unique=True)
    token       = StringField(required=True, unique_with='address')
    expire_at   = IntField(required=True)
    never_expire= BooleanField(required=False, default=False)
    is_valid    = BooleanField(required=True, default=True)
    
    meta = {
        'indexes': ['address','token'],
        'ordering' : ['expire_at']
    }

class SecretWords(Document):
    word    = StringField(required=True,unique=True)
    meta = {
        'indexes'  : ['word'],
    }


class Plugin(Document):
    name            = StringField(required=True,unique=True)
    leaderboards    = DictField(required=False)
    score           = DictField(required=False)
    stats           = DictField(required=False)

    meta = {
        'indexes'  : ['name'],
    }


'''
    Store info about applications (games)
'''
class Application(EmbeddedDocument):
    '''
        application_name = game_name
    '''
    name                = StringField(required=True)
    load                = IntField(required=False)
    info                = DictField(required=False)
    last_ping           = DateTimeField(default=datetime.datetime.now)
    is_active           = BooleanField(required=False)
    register_at         = DateTimeField(default=datetime.datetime.now)

    meta = {
                'index' : ['name'],
                'ordering' : ['name','-load']
           }

'''
    Create game session
    
    1. incompleted - create session
    2. completed (start game)
    3. terminated (end game + results) 
    4. canceled (timeout etc)
    
'''
SESSION_STATUS = ['INCOMPLETED','COMPLETED','TERMINATED','CANCELED','FULL']

class User(EmbeddedDocument):
    name        = StringField(required=False)
    uid         = StringField(required=True)
    rtid        = StringField(required=True)
    ready       = BooleanField(required=True,default=False)
    info        = DictField(required=True)

class Team(EmbeddedDocument):
    name        = StringField(required=False)
    users       = ListField(StringField(),required=False)
    info        = DictField(required=False,default={})

class Session(Document):
    name        = StringField(required=True)
    owner       = StringField(required=True)
    game_type   = StringField(required=False)
    application_name = StringField(required=True)
    teams       = SortedListField(EmbeddedDocumentField(Team), required=False)
    users       = SortedListField(EmbeddedDocumentField(User), required=True)
    rtserver    = DictField(required=True, default={})
    status      = StringField(required=True)
    is_active   = BooleanField(required=False)
    info        = DictField(required=True, default={})
    created_at  = DateTimeField(default=datetime.datetime.now)
    expired_at  = IntField(required=True)
    
    def __str__(self):
        return "Session for "+self.application_name
    
''' 
    Define cluster nodes
'''
class Node(Document):
    address         = StringField(required=True)
    machine_name    = StringField(required=True, unique_with='address')
    ports           = DictField(required=True)
    system          = DictField(required=False)
    register_at     = DateTimeField(default=datetime.datetime.now)
    last_ping       = DateTimeField(required=True)
    is_active       = BooleanField(required=True)
    applications    = ListField(EmbeddedDocumentField(Application), required=False)
    
    meta = {
            'index' : ['address','access_token'],
            'ordering' : ['-last_ping','-load']
            }    


''' 
    Define controller property - for internal use only
    server_type:
        1. controller
        2. router
'''
class ControllerServer(Document):
    name          = StringField(required=True)
    address       = StringField(required=True)
    created_at    = DateTimeField(default=datetime.datetime.now)
    is_controller = BooleanField(required=True)
    ''' server type: controller/router '''
    server_type   = StringField(required=False)
    nodes         = ListField(ReferenceField(Node), required=False)
    
    meta = {
        'indexes'  : ['name'],
    }
