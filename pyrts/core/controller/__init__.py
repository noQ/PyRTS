'''
Created on Jun 19, 2012

@author: Adrian Costia
'''

from pyrts.core.restexception import NotNode, ServerException, DataNotFound
from pyrts.datastore.models import *
from pyrts.core.util import attr2Class
from pyrts.core.params import PARAM_ID, PARAM_ROUTER, PARAM_CONTROLLER
from pyrts.core.net import *
from pyrts.core.serializers.base import *

class ServerNode(object):
    ''' Manipulate server node '''
    def __init__(self, id=None, **kwargs):
        self.is_master = False
        if id:
            setattr(self, PARAM_ID, id)
            self._node = Node.objects(id=self.id).first()
            if self._node is None:
                raise DataNotFound("No node found with ID: " + str(id))

    @staticmethod
    def serialize_node(node):
        return MongoObject.to_json(node)
    
    def _check_id(self):
        if not hasattr(self, PARAM_ID):
            raise Exception("Parameter ID is invalid!")

    def get_by_addr(self, addr):
        return Node.objects(address=addr).first()

    def save(self):
        self._node.save()
    
    def delete(self):
        self._check_id()
        ''' remove node from each controller '''
        controllers = controllers_list()
        for controller in controllers:
            controller_id = str(controller.id)
            Server(controller_id).remove_node(self.id)
        return self._node.delete()        
    
    def get(self):
        self._check_id()
        return self._node
    
    def update_applications(self, apps):
        for key, value in apps.items():
            for app in self.get_applications():
                if app.name == key:
                    app.load = value
                    break;

    def is_master(self, boolean):
        self.is_master = boolean
    
    def unregister_application(self, name):
        if self.get_applications().has_key(name):
            del self.get_applications()[name] 
            self._node.save()
        return self.get_applications()
    
    def get_applications(self):
        return self._node.applications
    

class ServerProperties(object):
    pass

def get_default_controller_id():
    controller = ControllerServer.objects().first()
    return str(controller.id)

class Server(object):
    SERVER_TYPE = {'CONTROLLER' : PARAM_CONTROLLER,
                   'ROUTER' : PARAM_ROUTER
                  }
    
    def __init__(self, id, is_controller=True, **kwargs):
        self.controller = ControllerServer.objects(id=id).first()
        if self.controller is None:
            raise ServerException("Server not found!")
        
        self.is_controller = True
        self.server_properties = ServerProperties()
        if kwargs:
            attr2Class(self.server_properties, kwargs)

    def add_node(self, node):
        if not self.is_controller:
            raise Exception("Not controller")
        if not isinstance(node, Node):
            raise NotNode
        ''' add new node '''
        self.controller.nodes.append(node)
        self.controller.save()
        return node
    
    def remove_node(self, nodeid):
        nodes = self.list_nodes()
        for node in nodes:
            if str(node.id) == nodeid:
                nodes.remove(node)
        self.controller.save()
        return nodes
    
    def check_node_by_addr(self, addr):
        return ServerNode().get_by_addr(addr)
    
    def list_nodes(self):
        return self.controller.nodes
    
    @staticmethod
    def serialize_nodes(nodes):
        _nodes = [] 
        for node in nodes:
            _nodes.append(MongoObject.to_json(node))
        return _nodes
    
    def _save_node(self):
        return ServerNode().save()
    
    def check_node(self, node_id):
        return ServerNode().get_node(node_id)

def add_server(hostname=None, ip_address=None, is_controller=True):
    '''
        Add new applications server
        - return server ID 
    '''
    net = Network()
    if hostname is None:
        '''
             generate from localhost 
        '''
        hostname = net.getHost()
    if ip_address is None:
        ip_address = net.getIpAddress('eth0')
        
    if isinstance(ip_address, list):
        if len(ip_address) > 0:
            ip_address = ip_address[0]
    if is_controller:
        server_type = Server.SERVER_TYPE.get(PARAM_CONTROLLER)
    else:
        server_type = Server.SERVER_TYPE.get(PARAM_ROUTER)
    ''' create server object '''
    server = ControllerServer(
                               name=hostname,
                               address = ip_address,
                               is_controller = is_controller,
                               server_type  = server_type
                               )
    server.save()
    return server 

def controllers_list():
    '''
        Get all controllers
    '''
    return ControllerServer.objects()    
        