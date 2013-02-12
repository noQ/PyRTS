'''
Created on Jun 25, 2012

@author: Adrian Costia
'''

import traceback
import time
import random
import socket
import struct
from pyrts.datastore.models import *
from pyrts.core.util import generate_simple_token 
from pyrts.core.restexception import DataNotFound, ReadDataException
from pyrts.core.controller.pluginmonitor import PluginHandler
from pyrts.core.params import *

def connect_to_rts():
    pass

class ControllerPlugin(object):
    """
        All games (applications) must extend this class
    """
    def can_start_game(self, session):
        raise NotImplementedError("Please implement me!")
    
    def setup_teams(self, team_type):
        raise NotImplementedError("Please implement me!")
    
    def set_team(self, name, uid):
        raise NotImplementedError("Please implement me!")
    
    def get_joinable_team(self, teams, uid, name=None):
        raise NotImplementedError("Please implement me!")


class RTNode(object):
    """
        Real Time Node 
    """
    def __init__(self, addr, load, ports):
        self.addr = addr
        self.load = load
        self.ports = ports
        
    def __repr__(self):
        return repr((self.addr, self.load, self.ports))


class GameSession:
    """ 
        Create game session
    """
    def __init__(self, **kwargs):
        if kwargs.has_key(PARAM_APPLICATION):
            self.application_name = kwargs[PARAM_APPLICATION]
        if kwargs.has_key(PARAM_UID):            
            self.uid = kwargs[PARAM_UID]
        if kwargs.has_key(PARAM_SESSION):
            self.session_name = kwargs[PARAM_SESSION]
        self.game_type  = None
        self.auto_team  = False
        self.auto_ready = False 
    
    def expire_in(self, seconds=300):    
        '''return a UNIX style timestamp representing +5 min from now'''
        return int(time.time() + seconds)
    
    def is_expired(self, session_time):
        if int(time.time()) > session_time:
            return True
        return False
    
    def get_or_create_session_name(self):
        ''' get or create session '''
        if hasattr(self, self.session_name):
            return self.session_name
        return self._create_session()
              
    def __create_session(self):
        ''' create session '''
        self.session_name =  generate_simple_token(nchars=5) 

        return self.session_name
    
    def __generate_rts_token(self):
        ''' Generate real time server (rts) token for current user id '''
        return generate_simple_token(5)

    def create_rt_session(self, session):
        ''' Create session on real time server '''
        def get_user_real_time_id(users, uid):
            for user in users:
                if user.uid == uid:
                    return user.rtid
            return None
            
        server_address = session.rtserver[PARAM_ADDRESS]
        server_port    = session.rtserver[PARAM_UDP]
        sid            = session.name
        game           = session.application_name
        teams          = session.teams
        users          = session.users
        
        msg = 'c' + chr(len(game)) + game + sid + chr(len(teams))
        for team in teams:
            msg += chr(len(team.name)) + team.name + chr(len(team.users))
            for uid in team.users:
                rt_uid = get_user_real_time_id(users, uid)
                if rt_uid is None:
                    return None
                msg += rt_uid
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((server_address,server_port))
        s.send(struct.pack("!I"+str(len(msg))+"s", len(msg), str(msg)))
        dataSz = struct.unpack("!I", s.recv(4))
        response = s.recv(dataSz[0])
        if response == RESPONSE_SERVER_OK:
            ''' activate session'''
            session.is_active = True
            session.status = SESSION_STATUS[1] # status = COMPLETED
        return session

    def get_available_slots(self):
        return self.app.slots
    
    def get_rtserver(self):
        ''' check application was registered '''
        nodes = Node.objects(applications__name=self.application_name, is_active=True)
        if len(nodes) == 0:
            error = "%s not found on server.", self.application_name
            raise DataNotFound(error)
        
        ''' extract server with less connexions '''
        _rtnodes = []
        for node in nodes:
            ''' search for rts server '''
            app = filter(lambda f: f.name == self.application_name, node.applications)
            if len(app) == 1:
                _rtnodes.append(RTNode(node.address, app[0].load, node.ports))
        ''' sort nodes by load '''
        if len(_rtnodes) > 0:
            _rtnodes = sorted(_rtnodes, key = lambda _n: _n.load)
            rt_server = dict(addr=_rtnodes[0].addr,
                             udp=_rtnodes[0].ports["udp"],
                             tcp=_rtnodes[0].ports["tcp"],
                             http=_rtnodes[0].ports["http"]
                             )
            return rt_server 

    def find_session(self):
        return Session.objects(name=self.session_name, is_active=False).first()

    @staticmethod
    def check_session(session_name):
        user_session = Session.objects(name=session_name, is_active=False).first()
        return user_session
    
    def get_awaiting_sessions(self):
        ''' Get session list for user '''
        sessions = Session.objects(
                                   application_name=self.application_name,
                                   is_active=False,
                                   users__uid=self.uid
                                   )
        return sessions
    
    def get_user(self):
        ''' TODO: Get user by uid from "social connector" framework '''

        ''' create user token. used by the real time server '''
        rt_token = self.__generate_rts_token()
        user = User(
                    uid=self.uid,
                    rtid=rt_token,
                    ready=False,
                    info={}
                    )
        return user
    
    def set_auto_ready(self, boolean):
        self.auto_ready = boolean
    
    def user_is_ready(self, session):
        for user in session.users:
            if user.uid == self.uid:
                user.ready = True
                break
        return session
    
    def set_game_type(self, gametype):
        self.game_type = gametype
    
    def auto_set_team(self, boolean):
        self.auto_team = boolean
    
    def get_session(self, **kwargs):
        '''
            Create new game session on controller with status 
            1. Incomplete if no of users < game available slots
            2. Complete (start game) if no of users = game available slots
            3. if no of users > game available slots then create new session
            
        '''

        ''' get session for game '''
        session = Session.objects(
                                  application_name=self.application_name,
                                  status=SESSION_STATUS[0],
                                  is_active=False
                                  ).first()
        ''' if session not found then create new session with status INCOMPLETE '''
        if session is None:
            session_owner = self.get_user()
            session = Session(
                              name=self.__create_session(),
                              application_name = self.application_name,
                              owner = session_owner.uid,
                              users = [session_owner],
                              status = SESSION_STATUS[0],
                              is_active=False,
                              expired_at=self.expire_in()
                              )
        else:
            user_exist = False
            if self.is_expired(session.expired_at):
                session.delete(safe=True)
                return None
            
            ''' if session exists then join in session '''
            if len(session.users) == 0:
                session.users = []
            else:
                if any(user.uid == self.uid for user in session.users):
                    user_exist = True
            if not user_exist:                 
                session.users.append(self.get_user())
                
        ''' create teams if not exists'''
        game = PluginHandler.get_plugin(self.application_name)
        if len(session.teams) == 0:
            if self.game_type is not None:
                teams = game.setup_teams(self.game_type)
                if not isinstance(teams, list) or len(teams) == 0:
                    raise Exception("Not instance of list or list is empty!")
                session.teams = []
                for team in teams:
                    session.teams.append(Team(name=team))
                session.game_type = self.game_type

        ''' add user in any team is flag is autosetteam'''
        if self.auto_team:
            team_name = game.get_joinable_team(session.teams, self.uid, name=None)
            for team in session.teams:
                if team.name == team_name:
                    team.users.append(self.uid)
                    break
            ''' set flag auto_ready = True and start the game '''
            if self.auto_ready:
                for user in session.users:
                    if user.uid == self.uid:
                        user.ready = True
                        break
        ''' save session '''
        session.save()
        return session
    