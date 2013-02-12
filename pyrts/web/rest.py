'''
Created on Apr 26, 2012

@author: Adrian Costia
'''
import os
import json
import web
import traceback
from pyrts.core.serializers.base import MongoObject
from pyrts.core.restexception import AuthTokenException, DataNotFound, HostIsDown,\
    ServerException, DeleteDataException, ReadDataException, GameSessionException, SaveDataException, \
    PluginNotFound, ServerParametersNotFound
from pyrts import STATUS_SUCCESS, SUCCESS
from pyrts.settings import DEBUG_LEVEL
from pyrts.core.const import DEFAULT_WEB_PORT, DOUBLE_DOT
from pyrts.core.date import date_to_int
from pyrts.core.util import checkHost, dict2Class
from pyrts.core.controller import *
from pyrts.core.controller.session import *
from pyrts.core.decorators.security import * 
from pyrts.core.auth.token import AuthToken
from pyrts.core.controller.pluginmonitor import PluginHandler

def get_remote_ip_address():
    ''' get web context and extract user IP address '''
    web_context = web.ctx
    if not web_context.has_key(PARAM_IP_ADDR):
        raise ServerException("Unable to extract node IP address ")
    return web_context[PARAM_IP_ADDR]

def check_controller(controllerid):
    if controllerid is None:
        raise ServerParametersNotFound("Controller ID not specified!")
    srv_controller = Server(controllerid)
    if srv_controller is None:
        raise DataNotFound("Controller not found!")
    return srv_controller

def check_node(nodeid):
    if nodeid is None:
        raise ServerParametersNotFound("Server node ID not specified!")
    srv_node = ServerNode(nodeid)
    if srv_node is None:
        raise DataNotFound("Node server not found!")
    return srv_node


class REST:
    """Server methods for the PYRTS."""
        
    def is_alive(self):
        """
            Check if server (controller) is alive
        """
        return 0
    
    @security_token_required
    def addcontroller(self, ip_address=None, controller=True, **kwargs):
        """
            Create new server controller
           
                method call: addcontroller(self, ip_address, controller, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token    - auth token
                
                optional parameters:
                    ip_address -  controller IP address (ipv4)
                    controller - is controller. Default True. If 'false' then server is 'router'
                    
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                
                Call example:
                    - Request:
                             {
                                "c":"4534564",
                                "m":"addcontroller",
                                "p" :{
                                    "token":"c010836281a24534e335fe22052378f7f2f5300d"
                                }
                            }                   

                    - Response:
                        - SUCCESS:
                            {"c": "4534564",
                             "r": {
                                    "address": "192.168.101.12",
                                    "id": "4fe0a8a76ee7224068000000",
                                    "name": "CONTROLLER-SERVER-COSTIA"
                                    },
                             "e": 0
                            }                                
                        - ERROR:
                            {"r": "Unable to add controller", "e": -1}
        """
        try:
            server = add_server(is_controller=controller, ip_address=ip_address)
        except Exception as exc:
            # TODO: log errors
            traceback.print_exc()
            raise ServerException("Unable to add controller: " + str(exc))
        ''' return dict with server id, name and ip address '''
        return dict(
                    id=str(server.id),
                    name=server.name,
                    address=str(server.address)
                    )
   
   
    @security_token_required
    def serverlist(self, **kwargs):
        """
            Get servers (controllers) list
           
                method call: serverlist(self, ip_address, controller, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token    - auth token
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            DATA_NOT_FOUND = -5
                
                Call example:
                    - Request:
                         {
                            "c":"4534564",
                            "m":"serverlist",
                            "p" :{
                                "token":"c010836281a24534e335fe22052378f7f2f5300d"
                            }
                        }                    

                    - Response:
                        - SUCCESS:
                            {
                                "c": "4534564",
                                "r": [{
                                    "name": "CONTROLLER-SERVER-COSTIA",
                                    "server_type": "controller",
                                    "created_at": 1340193417021,
                                    "is_controller": true,
                                    "address": "192.168.101.12", 
                                    "nodes": [{
                                        "last_ping": 1340194525548,
                                        "machine_name": "COSTIA-NODE1",
                                        "access_token": "92b422bddb295f0d4424a3703d030a2d23e2b001",
                                        "is_active": true,
                                        "register_at": 1340194525950,
                                        "address": "192.168.101.29"
                                    }],
                                    "id": "4fe190596ee7224b28000000"
                                }],
                                "e": 0
                            }
                                            
                        - ERROR:
                            {"r": "Unable to add controller", "e": -1}
        """
        try:
            ''' get all controllers and returns controller and nodes.
                raise exception DATA_NOT_FOUND if no server found 
            '''
            servers = controllers_list()
            if len(servers) > 0:
                srv_list = []
                for srv in servers:
                    srv_obj = dict(id=str(srv.id),
                                   name=srv.name,
                                   address=srv.address,
                                   is_controller=srv.is_controller,
                                   server_type=srv.server_type,
                                   created_at=date_to_int(srv.created_at)
                                   )
                    if len(srv.nodes) > 0:
                        srv_obj['nodes'] = MongoObject.to_json(srv.nodes)
                    srv_list.append(srv_obj)
                return srv_list
            raise DataNotFound("Server list empty")
        except Exception as exc:
            traceback.print_exc()
            raise ServerException("Unable to return server list - error: " + str(exc))

    
    @security_token_required
    def addrouter(self, ip_address=None, **kwargs):
        """
            Create new router
           
                method call: addrouter(self, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token    - auth token
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                
                Call example:
                    - Request:
                         {
                            "c":"4534564",
                            "m":"addrouter",
                            "p" :{
                                "token":"c010836281a24534e335fe22052378f7f2f5300d"
                            }
                        }                    

                    - Response:
                        - SUCCESS:
                            {"c": "4534564",
                             "r": {
                                    "address": "192.168.101.13",
                                    "id": "4fe0a8a76ee7224068000000",
                                    "name": "ROUTER-SERVER-COSTIA"
                                    },
                             "e": 0
                            }        
                                            
                        - ERROR:
                            {"r": "Unable to add controller", "e": -1}
        """
        try:
            server = add_server(is_controller=False, ip_address=ip_address)
        except Exception as exc:
            # TODO: log errors
            traceback.print_exc()
            raise ServerException("Unable to add router: " + str(exc))
        return dict(
                    id=str(server.id),
                    name=server.name,
                    address=str(server.address)
                    )
    
    
    @security_token_required
    def registernode(self, controllerid, address, name, verify_node=False, serialize=False, **kwargs):
        """
            Register new node

                method call: registernode(self,  controllerid, address, name, verify_node=False, serialize=False, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token        - auth token
                    controllerid - controller ID
                    address      - node IP address
                    name         - node name
                
                optional parameters:
                    verify_node  - Check node
                    serialize    - serialize object
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                
                Call example:
                    - Request:
                        {
                            "c":"4534564",
                            "m":"registernode",
                            "p" :{
                                "token":"c01066836281a24534e335fe22052378f7f2f5300d",
                                "controllerid":"4fe17ad76ee72244f0000001",
                                "address":"192.168.101.13",
                                "name":"COSTIA-NODE1"
                            }
                       }           

                    - Response:
                        - SUCCESS:
                            {"c": "4534564",
                             "r": {
                                    "address": "192.168.101.13",
                                    "id": "4fe0a8a76ee7224068000000",
                                    "name": "ROUTER-SERVER-COSTIA"
                                    },
                             "e": 0
                            }        
                                            
                        - ERROR:
                               {"m": "REST method exception: 'Host 192.168.190.29:8008 is down!'", "c": "4534564", "e": -9}

        """
        port = None
        if address is None or name is None:
            raise ServerParametersNotFound("Node name or address not specified!")
        ''' check host '''
        if DOUBLE_DOT in address:
            (host, port) = address.split(":")
        else:
            host = address
        if port is None:
            port = DEFAULT_WEB_PORT

        if verify_node:
            if not checkHost(host, int(port)):
                raise HostIsDown("Host " + str(host) + ":" + str(port) + " is down!")
        
        ''' get controller based on id '''
        srv_controller = check_controller(controllerid)
        ports = kwargs[PARAM_PORTS]
        ''' create new node '''
        srv_node = Node(
                        address=address,
                        machine_name=name,
                        ports=ports,
                        last_ping=datetime.datetime.now(), 
                        is_active=True
                        )
        if kwargs.has_key(PARAM_SYSTEM):
            try:
                srv_properties = json.loads(kwargs[PARAM_SYSTEM])
                srv_node.info = srv_properties
            except:
                traceback.print_exc()
                raise ServerException("Server properties are invalid!")

        ''' register server node '''
        try:
            ''' save node '''
            srv_node.save()
            ''' update controller node. save only the reference '''
            node = srv_controller.add_node(srv_node)
            if serialize:
                return MongoObject.to_json(node)
            return node
        except Exception as exc:
            traceback.print_exc()
            raise ServerException("Unable to register node - error: " + str(exc))


    @security_token_required
    def unregisternode(self, controllerid, nodeid, **kwargs):
        """
            Unregister node
                
                method call: unregisternode(self,  controllerid, nodeid, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token        - auth token
                    controllerid - controller ID
                    nodeid       - nodeid
                
                optional parameters:
                    verify_node  - Check node
                    serialize    - serialize object
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            DELETE_ERROR   = -7
                
                Call example:
                    - Request:
                     {
                        "c":"4534564",
                        "m":"unregisternode",
                        "p" :{
                            "token":"c01066836281a24534e335fe22052378f7f2f5300d",
                            "controllerid":"4fe190596ee7224b28000000",
                            "nodeid":"4fe194b06ee7224064000000"
                            }
                     }

                    - Response:
                        - SUCCESS:
                         {
                            "c": "4534564",
                            "r": [{
                                "last_ping": 1340207461024,
                                "machine_name": "L-MOB-COSTIA-NODE3",
                                "access_token": "32f0786f0b574b96843f11cd27b0372dec486f3f",
                                "is_active": true,
                                "register_at": 1340207461024,
                                "address": "192.168.190.29",
                                "id": "4fe1c7356ee7223f80000001"
                                }, {
                                    "last_ping": 1340210705375, 
                                    ...
                                }],
                             "e": 0
                        }                              
                                            
                        - ERROR:
                               {"m": "REST method exception: 'Unable to remove node with ID: 78237bbcjerj4'", "c": "4534564", "e": -9}
                              
        """
        ''' get controller based on id '''
        srv_controller = check_controller(controllerid)
        try:
            ''' remove node and return controller node list '''
            nodes = srv_controller.remove_node(nodeid)
            return Server.serialize_nodes(nodes)
        except Exception as exc:
            traceback.print_exc()
            raise DeleteDataException("Unable to remove node with ID: " + str(nodeid) )


    @security_token_required
    def listnodes(self, controllerid, **kwargs):
        """
            List all controller nodes

                method call: listnodes(self,  controllerid, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token        - auth token
                    controllerid - controller ID
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            DATA_NOT_FOUND = -5
                
                Call example:
                    - Request:
                           {
                            "c":"4534564",
                            "m":"listnodes",
                            "p" :{
                                "token":"c01066836281a24534e335fe22052378f7f2f5300d",
                                "controllerid":"4fe190596ee7224b28000000"
                                }
                           }          

                    - Response:
                        - SUCCESS:
                            {
                                "c": "4534564",
                                "r": [{
                                    "last_ping": 1340967817673,
                                    "machine_name": "127.0.0.1",
                                    "access_token": "603fccbc9a9ec13532d7f3259d184f5de35360da",
                                    "is_active": true,
                                    "id": "4fed61596ee722aeb0000000",
                                    "applications": [{
                                        "id": "4fed61596ee722aeb0000001"
                                        }, {
                                        "id": "4fed61596ee722aeb0000002"
                                    }],
                                    "register_at": 1340967817673, 
                                    "address": "127.0.0.1",
                                    "ports": {
                                        "udp": 110002,
                                        "http": 80,
                                        "tcp": 110003
                                    }
                                }],
                                "e": 0
                            }

                        - ERROR:
                               {"m": "REST method exception: 'No node(s) found for controller ID: 78237bbcjerj4'", "c": "4534564", "e": -9}
            
        """
        srv_controller = check_controller(controllerid)
        nodes = srv_controller.list_nodes()
        if len(nodes) > 0:
            return Server.serialize_nodes(nodes)
        raise DataNotFound("No node(s) found for controller ID: " + str(controllerid))
    
    
    @security_token_required
    def checknode(self, nodeid, **kwargs):
        """
            Get info about node

                method call: checknode(self,  nodeid, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token  - auth token
                    nodeid - node ID
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            DATA_NOT_FOUND = -5
                
                Call example:
                    - Request:
                           {
                            "c":"4534564",
                            "m":"checknode",
                            "p" :{
                                "token":"c01066836281a24534e335fe22052378f7f2f5300d",
                                "nodeid":"4fe194b06ee7224064000000"
                                }
                            }      

                    - Response:
                        - SUCCESS:
                            {
                                "c": "4534564",
                                "r": {
                                    "last_ping": 1340194525548,
                                    "machine_name": "L-MOB-COSTIA-NODE1",
                                    "access_token": "92b422bddb295f0d4424a3703d030a2d23e2b001",
                                    "is_active": true,
                                    "register_at": 1340194525950,
                                    "address": "192.168.190.29",
                                    "id": "4fe194b06ee7224064000000"
                                },
                                "e": 0
                            }

                        - ERROR:
                               {"m": "REST method exception: 'No node found'", "c": "4534564", "e": -9}
        """
        if nodeid is None:
            raise ServerParametersNotFound("Node id is not specified!")
        node = ServerNode(id=nodeid).get()
        if node is None:
            raise DataNotFound("No node found" )
        return ServerNode.serialize_node(node)
    
    
    @security_token_required
    def deletenode(self, nodeid, **kwargs):
        """
            Delete node from DB
            
                method call: checknode(self,  nodeid, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token  - auth token
                    nodeid - node ID
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            DELETE_ERROR   = -7
                
                Call example:
                    - Request:
                           {
                                "c":"4534564",
                                "m":"deletenode",
                                "p" :{
                                    "token":"c01066836281a24534e335fe22052378f7f2f5300d",
                                    "nodeid":"4fe1d3e16ee7225440000000"
                                }
                            }

                    - Response:
                        - SUCCESS:
                               {"c": "4534564", "r": "OK", "e": 0}

                        - ERROR:
                               {"m": "REST method exception: 'Unable to delete node'", "c": "4534564", "e": -7}
        """
        if nodeid is None:
            raise ServerParametersNotFound("Node id is not specified!")
        try:
            node = ServerNode(id=nodeid).delete()
            return SUCCESS
        except Exception as exc:
            traceback.print_exc()
            raise DeleteDataException("Unable to delete node!")

   
    @security_token_required
    def rtupdate(self, apps, ports, **kwargs):
        """
            Register RT server (node server) 
            
                method call: rtupdate(self,  apps, ports, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token - auth token
                    apps  - dict with application(s):
                             Example:
                                "apps":{
                                        "Dead Space Carbon": {
                                           "slots":2
                                        },
                                        "XandZero": {}
                                    }, 
                    ports - RTS available ports
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            SAVE_ERROR     = -3
                
                Call example:
                    - Request:
                            {
                                "c":"4534564",
                                "m":"rtupdate",
                                "p" :{
                                    "token":"603fccbc9a9ec13532d7f3259d184f5de35360da",
                                    "apps":{
                                        "Dead Space Carbon": {
                                           "slots":2
                                        },
                                        "XandZero": {}
                                    },
                                    "ports":{
                                        "udp":110002,
                                        "tcp":110003,
                                        "http":80
                                    }
                                }
                            }

                    - Response:
                        - SUCCESS:
                               {"c": "4534564", "r": "OK", "e": 0}

                        - ERROR:
                               {"m": "REST method exception: 'Unable to delete node'", "c": "4534564", "e": -7}
        """
        if apps is None:
            raise ServerParametersNotFound("Apps parameter not found")
        if ports is None:
            raise ServerParametersNotFound("Ports parameter not found")

        if not isinstance(apps, dict):
            raise ServerException("RT APPS object is not valid!")
        if not isinstance(ports, dict):
            raise ServerException("RT PORTS object is not valid!")
        
        if DEBUG_LEVEL:
            print " >>>> Applications: " + str(apps)
            print " >>>> Ports: " +str(ports) 
        
        ''' get web context and extract user IP address '''
        node_ip_address = get_remote_ip_address()
        ''' check node on default controller '''
        controllerid = get_default_controller_id()
        ''' check node '''
        node = ServerNode().get_by_addr(node_ip_address)
        if node is None:
            ''' register node if not found '''
            __token = kwargs["old_token"]
            node = self.registernode(
                                     controllerid,
                                     node_ip_address,
                                     node_ip_address,
                                     False,
                                     False,
                                     ports=ports,
                                     token=__token
                                     )
        node.applications = []
        ''' register applications on node '''
        if len(node.applications) == 0:
            try:
                ''' add application on node '''
                for key, value in apps.items():
                        app_obj = Application(
                                              name = key,
                                              info = value,
                                              last_ping = datetime.datetime.now(),
                                              is_active = True,
                                              load = 0
                                              )
                        node.applications.append(app_obj)
                node.save()
            except Exception as exc:
                traceback.print_exc()
                raise SaveDataException("Unable to add application : " + str(exc))
        return STATUS_SUCCESS

    
    @security_token_required
    def rtinfo(self, load, system, **kwargs):
        """
            Update RTS info   
            
                method call: rtinfo(self,  apps, ports, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token  - auth token
                    load   - RTS load (number of users for example)
                    system - system stats: availabe ram, processor, disk space etc 
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            SAVE_ERROR     = -3
                
                Call example:
                      - Request:
                             {
                                 "c": "6523",
                                "m": "rtinfo",
                                "p": {
                                    "load": {
                                        "Dead Space Carbon": 1,
                                        "XandZero": 3
                                    },
                                    "token": "603fccbc9a9ec13532d7f3259d184f5de35360da",
                                    "system": {
                                        "ram": 9.17578125, "cpu": 0.3
                                    }
                                } 
                            }                                  
                
                      - Response:
                        - SUCCESS:
                               {"c": "4534564", "r": "OK", "e": 0}

                        - ERROR:
                               {"m": "REST method exception: 'Unable to delete node'", "c": "4534564", "e": -7}
        """
        if not isinstance(load, dict):
            raise ServerException("Not dictionary")
        
        node_ip_address = get_remote_ip_address()
        ''' check node '''
        node = ServerNode().get_by_addr(node_ip_address)
        if node is None:
            raise ServerException("Node not found")
        node.system = system
        if len(node.applications) == 0:
            raise ServerException("Applications length is ZERO")
        try:
            ''' update applications '''
            for key,value in load.items():
                for app in node.applications:
                    if app.name == key:
                        app.load = value
                        app.last_ping = datetime.datetime.now()
                        break;
            
            ''' set last ping '''
            node.last_ping = datetime.datetime.now()
            node.save()
        except Exception as exc:
            traceback.print_exc()
            raise ServerException("Unable to update node : " + str(exc))
        return STATUS_SUCCESS 
    
    
    @security_token_required
    def unregisterapp(self, nodeid, name, **kwargs):
        """
            Unregister application   
            
                method call: unregisterapp(self,  nodeid, name, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token  - auth token
                    nodeid - node ID
                    name   - aplication name. Example: XandZero
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            DATA_NOT_FOUND = -5
                
                Call example:
                      - Request:
                             {
                                "c": "6523",
                                "m": "unregisterapp",
                                "p": {
                                    "token": "603fccbc9a9ec13532d7f3259d184f5de35360da",
                                    "nodeid":"4fe1d3e16ee7225440000000",
                                    "name" : "XandZero"
                                } 
                            }                                  
                
                      - Response:
                        - SUCCESS:
                               {"c": "4534564", "r": "OK", "e": 0}

                        - ERROR:
                               {"m": "REST method exception: 'Unable to delete node'", "c": "4534564", "e": -7}
        """
        if name is None:
            raise ServerParametersNotFound("Application name is invalid")
        if nodeid is None:
            raise ServerParametersNotFound("Server Node ID is invalid")

        srv_node = check_node(nodeid)
        try:
            applications = srv_node.unregister_application(name)
            _apps = []
            for app in applications:
                _apps.append(MongoObject.to_json(app))
            return _apps
        except Exception as exc:
            traceback.print_exc()
            raise ServerException("Unable to add application!")

    
    @security_token_required
    def getsession(self, game, uid, restriction={}, autoready=False, autosetteam=False, gametype=None, team=None, **kwargs):
        """
            Create (or join) game (application) session 
            
                method call: getsession(game, uid, restriction={}, autoready=False, autosetteam=False, gametype=None, team=None, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token  - auth token
                    uid    - user ID
                    game   - game name
                
                optional parameters:
                    restriction - game resctiction if any. Default empty dict
                    autoready   - start game automatic
                    autosetteam - auto set team with random users
                    gametype    - game type
                    team        - team name. Example: blue
                
                Returns:
                    SUCCESS: returns JSON object
                    ERROR:
                            REST_EXCEPTION = -1
                            DATA_NOT_FOUND = -5
                
                Call example:
                      - Request:
                                 {
                                    "c":"4534564",
                                    "m":"getsession",
                                    "p" :{
                                        "token":"603fccbc9a9ec13532d7f3259d184f5de35360da",
                                        "game":"Tetris",
                                        "uid":"7999o944"
                                    }
                                }
                                                
                      - Response:
                        - SUCCESS: JSON with session ID and RTS server:port and protocol (udp, web socket, tcp)
                                {
                                "c": "4534564",
                                 "r": {
                                     "udp": 110002,
                                     "session": "g9Pkv",
                                     "http": 80,
                                     "addr": "127.0.0.1",
                                     "tcp": 110003
                                    },
                                 "e": 0
                                }                                     

                        - ERROR:
                               {"m": "REST method exception: 'Unable to delete node'", "c": "4534564", "e": -7}
        """
        if game is None:
            raise ServerParametersNotFound("Application is invalid!")
        if uid is None:
            raise ServerParametersNotFound("UID is invalid")
        
        try:
            ''' create/join game session '''
            session =  GameSession(application=game, uid=uid)
            if gametype is not None:
                ''' set teams '''
                if autoready:
                    autosetteam = True
                session.auto_set_team(autosetteam)
                session.set_auto_ready(autoready)
                session.set_game_type(gametype)
            
            ''' create or get session '''
            user_session = session.get_session()
            if user_session is None:
                raise ServerException()
            
            if not user_session.rtserver.has_key(PARAM_ADDRESS):
                ''' search for node with less connections '''
                rtserver = session.get_rtserver()
                ''' save rt server in current session '''
                user_session.rtserver = rtserver
                user_session.save()
            else:
                rtserver = user_session.rtserver
            
            ''' return server info '''
            _sess = dict(session=user_session.name)
            ''' update session '''
            _sess.update(rtserver)
            return _sess
        except Exception as exc:
            traceback.print_exc()
            ''' TODO: get error message from list ( use locale!) - in development '''
            raise ServerException("Unable to create/join game session. Please, try again later!")
    
    
    @security_token_required
    def delete_session(self, id, **kwargs):
        """
            Delete game session  
            
                method call: delete_session(id, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token  - auth token
                    id     - session ID
                
                Returns:
                    SUCCESS: returns STATUS_SUCCESS = 0
                    ERROR:
                            REST_EXCEPTION = -1
                            DATA_NOT_FOUND = -5
                
                Call example:
                      - Request:
                                 {
                                    "c":"4534564",
                                    "m":"delete_session",
                                    "p" :{
                                        "token":"603fccbc9a9ec13532d7f3259d184f5de35360da",
                                        "id":"g9Pkv"
                                    }
                                }
                                                
                      - Response:
                        - SUCCESS: JSON with session ID and RTS server:port and protocol (udp, web socket, tcp)
                                {
                                "c": "4534564",
                                 "r": {
                                     "udp": 110002,
                                     "session": "g9Pkv",
                                     "http": 80,
                                     "addr": "127.0.0.1",
                                     "tcp": 110003
                                    },
                                 "e": 0
                                }                                     

                        - ERROR:
                               {"m": "REST method exception: 'Session not found'", "c": "4534564", "e": -7}
        """
        if id is None:
            raise ServerParametersNotFound("Session ID not specified or invalid")
        user_session = GameSession.check_session(id)
        if user_session is None:
            raise DataNotFound("Session not found")
        try:
            user_session.delete()
        except Exception as exc:
            traceback.print_exc()
            ''' TODO: get error message from list ( use locale!) - in development '''
            raise ServerException("Unable to delete game session.")
        return STATUS_SUCCESS
    
    
    @security_token_required
    def set_team(self, session, uid, team, **kwargs):
        """
            Set user team 
            
                method call: set_team(session, uid, team, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token   - auth token
                    uid     - user ID
                    session - session name
                    team    - team name. Example: Blue Team
                
                Returns:
                    SUCCESS: returns STATUS_SUCCESS = 0
                    ERROR:
                            REST_EXCEPTION      = -1
                            PARAMETER_NOT_FOUND = -4
                            DATA_NOT_FOUND      = -5
                            SAVE_ERROR          = -3
                
                Call example:
                      - Request:
                                {
                                    "c":"4534564",
                                    "m":"set_team",
                                    "p" :{
                                        "token":"0c8d4ef958eeb5e793f9b963686595781171b6e2",
                                        "session":"ShyU7",
                                        "uid":"yoyo",
                                        "team":"Blue Team"
                                    }
                                }       
                                                
                      - Response:
                        - SUCCESS: STATUS_SUCCESS = 0
                               {"m": "REST method exception: 'Session name not specified'", "c": "4534564", "e": -4}
        """
        if uid is None:
            raise ServerParametersNotFound("UID is invalid!")
        if session is None:
            raise ServerParametersNotFound("Session name not specified")
        if team is None:
            raise ServerParametersNotFound("Team name not specified")

        session = GameSession(uid=uid, session=session)
        game_session = session.find_session()
        if game_session is None:
            raise DataNotFound("Session not found")
        ''' read game (appliction) plugin '''
        try:
            game = PluginHandler.get_plugin(game_session.application_name)
            user_team_name = game.get_joinable_team(game_session.teams, uid, name=team)
            if user_team_name:
                _save = False
                for team in game_session.teams:
                    if team.name == user_team_name:
                        team.users.append(uid)
                        _save = True
                        break
                if _save:
                    game_session.save()
        except:
            traceback.print_exc()
            raise SaveDataException("Unable to set user in team")
        return STATUS_SUCCESS
    
    
    @security_token_required
    def set_ready(self, uid, session, **kwargs):
        """
             User is ready to play the game ?
             
                method call: set_ready(session, uid, name, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token   - auth token
                    uid     - user ID
                    session - session name
                    team    - team name. Example: Blue Team
                
                Returns:
                    SUCCESS: returns STATUS_SUCCESS = 0
                    ERROR:
                            REST_EXCEPTION      = -1
                            PARAMETER_NOT_FOUND = -4
                            DATA_NOT_FOUND      = -5
                            SAVE_ERROR          = -3
                
                Call example:
                      - Request:
                                {
                                    "c":"4534564",
                                    "m":"set_ready",
                                    "p" :{
                                        "token":"603fccbc9a9ec13532d7f3259d184f5de35360da",
                                        "session":"xJbh",
                                        "uid":"7999o944"
                                    }
                                }
                                                
                      - Response:
                        - SUCCESS: STATUS_SUCCESS = 0
                               {"m": "REST method exception: 'Unable to create RTS session'", "c": "4534564", "e": -1}
        
        """
        if uid is None:
            raise ServerParametersNotFound("UID is invalid!")
        if session is None:
            raise ServerParametersNotFound("Session name not specified")
        
        session = GameSession(uid=uid, session=session)
        game_session = session.find_session()
        if game_session is None:
            raise DataNotFound("Session not found")
        
        ''' session is expired ? '''
        if int(time.time()) > game_session.expired_at:
            raise ServerException("Session expired!")
        
        if len(game_session.users) < 1:
            raise ServerException("No users found in current session")
        ''' user is ready to play the game ?'''
        try:
            game_session = session.user_is_ready(game_session)
            game_session.save()
        except:
            traceback.print_exc()
            raise SaveDataException("Unable to save user data.")
        
        ''' create session on RT server and start the game '''
        game = PluginHandler.get_plugin(game_session.application_name)
        if game.can_start_game(game_session):
            try:
                game_session = session.create_rt_session(game_session)
            except Exception as exc:
                traceback.print_exc()
                raise ServerException("Unable to create RTS session")
            ''' save session data '''
            try:
                game_session.save()
            except:
                traceback.print_exc()
                raise SaveDataException("Unable to save session data.")
        return STATUS_SUCCESS


    @security_token_required
    def get_awaiting_session(self, uid, game, **kwargs):
        """
             Get user session list for selected game
             
                method call: get_awaiting_session(session, uid, game, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token   - auth token
                    uid     - user ID
                    game    - game name (plugin name)
                
                Returns:
                    SUCCESS: JSON
                    ERROR:
                            REST_EXCEPTION      = -1
                            PARAMETER_NOT_FOUND = -4
                            DATA_NOT_FOUND      = -5
                            SAVE_ERROR          = -3
                
                Call example:
                      - Request:
                                    {
                                        "c":"4534564",
                                        "m":"get_awaiting_session",
                                        "p" :{
                                            "token":"603fccbc9a9ec13532d7f3259d184f5de35360da",
                                            "game":"Tetris",
                                            "uid":"uid111"
                                        }
                                    }                                
                                                
                      - Response:
                        - SUCCESS:
                                    {
                                        "c": "4534564",
                                        "r": ["acPxt"],
                                        "e": 0
                                    } 
                        - ERROR:
                               {"m": "REST method exception: 'Unable to create RTS session'", "c": "4534564", "e": -1}
        """
        if uid is None:
            raise ServerParametersNotFound("UID is invalid!")
        if game is None:
            raise ServerParametersNotFound("Session name not specified")
        
        try:
            session = GameSession(uid=uid, application=game)
            sessions = session.get_awaiting_sessions()
            __sessions = []
            if len(sessions) > 0:
                for session in sessions:
                    __sessions.append(session.name)
            return __sessions
        except:
            traceback.print_exc()
            raise ServerException("Unable to read data.")

    
    @security_token_required
    def session_status(self, session, **kwargs):
        """
             Get session status
             
                method call: session_status(session, **kwargs)
                    -> where **kwargs : <optional parameters>
                
                mandatory parameters:
                    token   - auth token
                    session - session name
                
                Returns:
                    SUCCESS: JSON
                    ERROR:
                            REST_EXCEPTION      = -1
                            PARAMETER_NOT_FOUND = -4
                            READ_ERROR          = -6
                
                Call example:
                      - Request:
                               {
                                  "c":"4534564",
                                  "m":"session_status",
                                  "p" :{
                                        "token":"0c8d4ef958eeb5e793f9b963686595781171b6e2",
                                        "name":"acPxt"
                                    }
                                }
                      - Response:
                        - SUCCESS:
                                {
                                  "c": "4534564",
                                  "r": "INCOMPLETED",
                                  "e": 0
                                }
                        - ERROR:
                               {"m": "REST method exception: 'Unable to get session status'", "c": "4534564", "e": -6}
        
        """
        if session is None:
            raise ServerParametersNotFound("Session name is invalid!")
        try:
            user_session = GameSession.check_session(session)
            if user_session is None:
                raise ServerParametersNotFound("Session not found!")
            return user_session.status
        except:
            traceback.print_exc()
            raise ReadDataException("Unable to get session status")

