import sys
import socket
import threading
import time
import struct
import traceback
import json
import urllib2
import random
import subprocess
import os

CONTROLLER_URL    = "http://10.100.9.8:8080/"
CONTROLLER_SECRET = "c01066836281a24534e335fe22052378f7f2f5300d"
RTS_UPDATE_METHOD = "rtupdate"
RTS_INFO_METHOD   = "rtinfo"
REQUEST_TIMEOUT_SEC = 5

game_modules = {}

plugins_path = os.sep.join(sys.argv[0].split(os.sep)[:-1]+['plugins'])
if plugins_path not in sys.path:
    sys.path.append(plugins_path)
    
for module_file in os.listdir(plugins_path):
    if module_file[-3:] == '.py':
        module_name = module_file[:-3]
        print "Importing plugin '" +module_name+ "':",
        try:
            mod = __import__(module_name)
            game_modules[module_name] = mod
        except Exception as e:
            print "Failed"
            print "Import failed for plugin '" +module_name+ "' because of the following error:"
            traceback.print_exc(file=sys.stdout)

load = {}
for gid, game in game_modules.items():
    load[gid] = 0


listen_address = "0.0.0.0"
udp_port = 10101
tcp_port = 10101
http_port = 8080

have_controller = True

#Thread safe printing
print_lock = threading.Lock()
def sync_print(s):
    print_lock.acquire()
    print(s)
    print_lock.release()

def call_rest(method, params):
    try:
        res = urllib2.urlopen(CONTROLLER_URL, json.dumps({'m':method,'p':params,'c':str(random.randrange(10000))}), REQUEST_TIMEOUT_SEC)
        cnt = res.read()
        ret = json.loads(cnt)
        return ret
    except:
        traceback.print_exc()
        return None

if have_controller:
    #Sync games with controller
    sync_print("Sending boot update to controller... (timeout in 5s)")
    games = {}
    for gid, game in game_modules.items():
        games[gid] = game.init_controller()
    
    ports = dict(udp=udp_port,
                 tcp=tcp_port,
                 http=http_port
                 )
    update = dict(token=CONTROLLER_SECRET,
                  apps=games,
                  ports=ports
                  )
    sync_print(update)
    sync_result = call_rest(RTS_UPDATE_METHOD, update)
    
    if sync_result==None:
        sync_print("Couldn't send boot update to controller!")
        sys.exit(1)
    else:
        if sync_result['e'] != 0:
            sync_print("Controller raised error when sending boot update!")
            sync_print(sync_result['m'])
            sys.exit(2)

#Mark server as active
active = True

#Dictionary that stores active clients
clients = {}
#Dictionary that stores active sessions
sessions = {}

#Forward declaration of threads that contain blocking server sockets
udp = None
tcp = None
http = None

def stop():
    global active, udp, tcp, http
    if active:
        print "Initiating global shutdown"
        active = False
        try:
            if udp and udp.socket:
                try:
                    trigger_s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);
                    trigger_s.sendto("", udp.addr)
                except:
                    pass
            if tcp and tcp.socket:
                try:
                    trigger_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                    trigger_s.connect(tcp.addr)
                    trigger_s.close()
                except:
                    pass
            if http and http.socket:
                try:
                    trigger_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
                    trigger_s.connect(http.addr)
                    trigger_s.close()
                except:
                    pass
        except:
            traceback.print_exc()

class Factory:
    """
        Generic Factory for reusable objects
    """
    def __init__(self, kind, use_init=True):
        self.kind = kind
        self.use_init = use_init
        self.lock = threading.Lock()
        self.free = []
        self.cnt = 0
        
    def get(self, *args, **kwargs):
        self.lock.acquire()
        if len(self.free) > 0:
            ret = self.free.pop()
            #sync_print("REUSE: Factory("+str(self.kind)+"): Total/Free:"+str(self.cnt)+"/"+str(len(self.free)))
        else:
            self.cnt+=1
            #sync_print("NEW: Factory("+str(self.kind)+"): Total/Free:"+str(self.cnt)+"/"+str(len(self.free)))
            if self.use_init:
                ret = self.kind()
            else:
                ret = self.kind(*args, **kwargs)
                
        if self.use_init:
            ret.init(*args, **kwargs)
        self.lock.release()
        return ret
    
    def put(self, item):
        self.lock.acquire()
        try:
            self.free.insert(0, item)
        except:
            traceback.print_exc()
        self.lock.release()
        #sync_print("PUT: Factory("+str(self.kind)+"): Total/Free:"+str(self.cnt)+"/"+str(len(self.free)))

class Buffer:
    def __init__(self):
        self.data = bytearray(516)
        self.buffer = memoryview(self.data)
        self.content = self.buffer[4:]
        self.length = 0

bufferFactory = Factory(Buffer, use_init=False)

class HttpBuffer:
    def __init__(self):
        self.data = bytearray(65536)
        self.buffer = memoryview(self.data)
        self.length = 0

httpBufferFactory = Factory(HttpBuffer, use_init=False)

class Session:
    def __init__(self):
        pass
    
    def init(self, game, teams):
        self.game = game
        self.teams = teams
        self.lastrequest = time.time()

sessionFactory = Factory(Session)

sessions = {}

class Client:
    def __init__(self):
        pass
    
    def init(self, key, socket):
        self.active = True
        self.buffer = None
        self.key = key
        self.socket = socket            
        self.packet_cnt = 0
        self.server_packet_cnt = 1
        self.lastrequest = time.time()
        self.uid = None
        self.session = None
        
    def request(self):
        self.lastrequest = time.time()
        if self.session:
            self.session.lastrequest = self.lastrequest
        #sync_print("Having buffer of len="+str(self.buffer.length)+" content="+str(self.buffer.content[:self.buffer.length].tobytes()))
        cmd = self.buffer.content[0]
        if cmd=='p': #Probe
            self.send('p')
        elif cmd=='h': #Heart beat
            self.send('h')
        elif cmd=='e': #Event in session
            msg = self.buffer.content[1:self.buffer.length]
            #Delegate session event to game plugin
            self.session.game.on_event(self, msg)
        elif cmd=='j': #Join session
            sid = self.buffer.content[1:6].tobytes()
            #Is sid a session on this server?
            if sessions.has_key(sid):
                uid = self.buffer.content[6:11].tobytes()
                #Is uid supposed to join the session
                for tid, uids in sessions[sid].teams.items():
                    if uids.has_key(uid):
                        #Remember my uid in the client for further calls
                        self.uid = uid
                        #Remember my tid in the client for further calls
                        self.tid = tid
                        #Remember my session in the client for further calls
                        self.session = sessions[uid]
                        #Increment load based on protocol
                        if self.key[0]=='udp':
                            load[self.session.gid] += 1
                        elif self.key[0]=='tcp':
                            load[self.session.gid] += 5
                        elif self.key[0]=='http':
                            load[self.session.gid] += 10

                        if uids[uid]==None:
                            #Delegate session joining to the sessions's game plugin
                            sessions[sid].game.on_join(self)
                            #Mark user as joined
                            uids[uid] = self
                        self.send('jOK')
                        return
            self.send('jFAIL')
            
        elif cmd=='c': #Create session
            try:
                ngamename = ord(self.buffer.content[1])
                game = self.buffer.content[2:2 + ngamename].tobytes()
                pos = 2 + ngamename
                #Is game supported on this server?
                if game_modules.has_key(game):
                    sid = self.buffer.content[pos:pos + 5].tobytes()
                    nteams = self.buffer.content[pos + 5]
                    teams = {}
                    pos += 6
                    for i in xrange(ord(nteams)):
                        nteamname = ord(self.buffer.content[pos])
                        pos += 1
                        tid = self.buffer.content[pos:pos+nteamname].tobytes()
                        pos += nteamname
                        nuids = self.buffer.content[pos]
                        pos += 1
                        teams[tid] = {}
                        for j in xrange(ord(nuids)):
                            uid = self.buffer.content[pos: pos+5].tobytes()
                            teams[tid][uid]=None
                            pos += 5
                    session = sessionFactory.get(game_modules[game], teams)
                    session.gid = game
                    sessions[sid] = session
                    #Delegate session initialization to game plugin
                    game_modules[game].init_session(session)
                    
                    self.send('cOK')
                else:
                    self.send('cFAIL')
            except:
                traceback.print_exc()
                
    def send(self, data):
        if self.key[0]=='udp':
            packet = struct.pack("!I"+str(len(data))+"s", self.server_packet_cnt, data)
            self.server_packet_cnt += 1
            self.socket.sendto(packet, self.key[1])
        elif self.key[0]=='tcp':
            packet = struct.pack("!I"+str(len(data))+"s", len(data), data)
            self.socket.send(packet)
        elif self.key[0]=='http':
            packet = struct.pack("!I"+str(len(data))+"s", len(data), data)
            self.socket.send(packet)
            
    def die(self):
        self.active = False
        bufferFactory.put(self.buffer)
        self.buffer = None
        if self.session:
            if self.key[0]=='udp':
                load[self.session.gid] -= 1
            elif self.key[0]=='tcp':
                load[self.session.gid] -= 5
            elif self.key[0]=='http':
                load[self.session.gid] -= 10
            self.session.teams[self.tid][self.uid] = None
        if self.key[0]=='tcp':
            self.socket.close()

clientFactory = Factory(Client)

class UDPClientThread(threading.Thread):
    def __init__(self, client, socket):
        threading.Thread.__init__(self)
        self.buffer, self.addr = client
        self.socket = socket
        
    def run(self):
        (packet_cnt,) = struct.unpack("!I",self.buffer.buffer[:4].tobytes())
        client = None
        client_key = ('udp', self.addr)
        if clients.has_key(client_key):
            client = clients[client_key]
        else:
            client = clientFactory.get(client_key, self.socket)
            clients[client_key] = client
        if packet_cnt > client.packet_cnt:
            if client.buffer:
                bufferFactory.put(client.buffer)
            client.buffer = self.buffer
            client.buffer.length -= 4
            client.request()

class UDPListener(threading.Thread):
    def __init__(self, addr):
        threading.Thread.__init__(self)
        self.addr = addr
    def run(self):
        global active
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.bind(self.addr)
        except:
            sync_print("UDPListener::could not bind on "+str(self.addr))
            stop()
            return
        sync_print("UDPListener::started on "+str(self.addr))
        while(active):
            input_buffer = bufferFactory.get()
            (input_buffer.length, addr) = self.socket.recvfrom_into(input_buffer.buffer, nbytes=516)
            UDPClientThread((input_buffer, addr), self.socket).start()
        sync_print("UDPListener::closed")

class TCPClientThread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.socket, self.addr = client
        
    def run(self):
        client = None
        client_key = ('tcp', self.addr)
        if clients.has_key(client_key):
            client = clients[client_key]
        else:
            client = clientFactory.get(client_key, self.socket)
            clients[client_key] = client
        client.buffer = bufferFactory.get()

        while client.active:
            dataSize = 0
            while dataSize<4:
                try:
                    read = self.socket.recv_into(client.buffer.buffer[dataSize:4])
                    if read==0:
                        return
                    dataSize += read
                except:
                    traceback.print_exc()
                    return
            try:
                (sz,) = struct.unpack("!I", str(client.buffer.data[:4]))
            except:
                traceback.print_exc()
                return
            
            if sz>516:
                return
    
            dataSize = 0
            while dataSize<sz:
                try:
                    read = self.socket.recv_into(client.buffer.buffer[4+dataSize:])
                    if read==0:
                        return
                    dataSize += read
                except:
                    traceback.print_exc()
                    return
            client.buffer.length = dataSize
            client.request()

class TCPListener(threading.Thread):
    def __init__(self, addr):
        threading.Thread.__init__(self)
        self.addr = addr
        
    def run(self):
        global active
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind(self.addr)
        except:
            sync_print("TCPListener::could not bind on "+str(self.addr))
            stop()
            return
        self.socket.listen(128)
        sync_print("TCPListener::started on "+str(self.addr))
        while(active):
            TCPClientThread(self.socket.accept()).start()
        sync_print("TCPListener::closed")

class HTTPClientThread(threading.Thread):
    def __init__(self, client):
        threading.Thread.__init__(self)
        self.socket, self.addr = client
    def run(self):
        #Try to read the whole request in one go
        httpBuffer = httpBufferFactory.get()
        dataSize = 0
        while dataSize<65536:
            try:
                read = self.socket.recv_into(httpBuffer.buffer[dataSize:])
                if read==0:
                    break
                dataSize += read
            except:
                traceback.print_exc()
                return

        #Split request in lines and eventually content without allocations
        lines = []
        last_line = 0
        content_start = 0
        for i in xrange(dataSize):
            if httpBuffer.buffer[i]=='\n':
                lines.append((last_line, i-1))
                last_line = i+1
                if i+2<dataSize and httpBuffer.buffer[i+1]=='\r' and httpBuffer.buffer[i+2]=='\n':
                    content_start = i+3
                    break
        
        if dataSize-content_start>512:
            return
        
        first_line = httpBuffer.buffer[lines[0][0]:lines[0][1]]
        if len(first_line)<4:
            return
        
        #Headers should be ignored for now (until further development)
        #for sl,el in lines[1:]:
        #    sync_print("["+httpBuffer.buffer[sl:el].tobytes()+"]")

        #Parse first line
        request_parts = first_line.tobytes().split(' ')
        if len(request_parts)<3:
            return

        if request_parts[0]=='POST':
            #received message
            client = None
            client_key = ('http', request_parts[1][1:])
            if clients.has_key(client_key):
                client = clients[client_key]
            else:
                client = clientFactory.get(client_key, None)
                clients[client_key] = client
            client.buffer = bufferFactory.get()
            client.buffer.content[0:dataSize - content_start] = httpBuffer.buffer[content_start:dataSize]
            httpBufferFactory.put(httpBuffer)
            client.buffer.length = dataSize - content_start
            #Send response HTTP headers here
            self.socket.sendall("HTTP/1.0 200 OK\r\n\r\n")
            client.request()
        elif request_parts[0]=='GET':
            #expecting message from server
            client = None
            client_key = ('http', request_parts[1][1:])
            if clients.has_key(client_key):
                client = clients[client_key]
            else:
                client = clientFactory.get(client_key, self.socket)
                clients[client_key] = client
            #Send response HTTP headers here
            self.socket.sendall("HTTP/1.0 200 OK\r\n\r\n")
            client.socket = self.socket
        else:
            #Send response HTTP headers here
            self.socket.sendall("HTTP/1.0 404 Not found\r\n\r\n")
            return
            
class HTTPListener(threading.Thread):
    def __init__(self, addr):
        threading.Thread.__init__(self)
        self.addr = addr
        
    def run(self):
        global active
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.socket.bind(self.addr)
        except:
            sync_print("HTTPListener::could not bind on "+str(self.addr))
            stop()
            return
        self.socket.listen(128)
        sync_print("HTTPListener::started on "+str(self.addr))
        while(active):
            HTTPClientThread(self.socket.accept()).start()
        sync_print("HTTPListener::closed")
        
class Cleaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global active
        sync_print("Cleaner::started")
        while(active):
            ctime = time.time()
            for key,session in sessions.items():
                if ctime > session.lastrequest + 5:
                    session.game.stop_session(session)
                    sessionFactory.put(session)
                    #TODO: Let the controller know that the session has ended
                    del sessions[key]
            for key,client in clients.items():
                if ctime > client.lastrequest + 5:
                    if client.session:
                        client.session.game.on_leave(client)
                    client.die()
                    clientFactory.put(client)
                    del clients[key]
            sync_print("Clients: "+str(len(clients)) + " Sessions: "+str(len(sessions)))
            time.sleep(1)
        sync_print("Cleaner::closed")

def used_resources():
    """Return memory & cpu used by this process on POSIX."""
    if os.name=='posix':
        process = subprocess.Popen("ps -o rss -o pcpu -p %d | awk '{sum1+=$1; sum2+=$2} END {print sum1,sum2}'" % os.getpid(),
                                        shell=True,
                                        stdout=subprocess.PIPE,
                                        )
        stdout_list = process.communicate()[0].split('\n')
        parts = stdout_list[0].split(' ')
        return float(parts[0])/1024.0, float(parts[1])
    else:
        #Don't bother. Nobody runs this server on non-Posix machines for production
        return 0.0, 0.0

class ControllerPinger(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global active
        sync_print("ControllerPinger::started")
        while(active):
            ram, cpu = used_resources()
            sys_info = dict(ram=ram, cpu=cpu)
            info = dict(token=CONTROLLER_SECRET,
                        system=sys_info,
                        load=load
                        )
            sync_print(info)
            sync_result = call_rest(RTS_INFO_METHOD, info)
            if sync_result==None:
                sync_print("ControllerPinger::Couldn't send info to controller!")
            else:
                if sync_result['e']!=0:
                    sync_print("ControllerPinger::Controller returned error when sending info!")
                    sync_print(sync_result['m'])
            time.sleep(60)
        sync_print("ControllerPinger::closed")

udp = UDPListener((listen_address, udp_port))
udp.start()
time.sleep(0.1)
tcp = TCPListener((listen_address, tcp_port))
tcp.start()
time.sleep(0.1)
http = HTTPListener((listen_address, http_port))
http.start()
time.sleep(0.1)
Cleaner().start()
time.sleep(0.1)
if have_controller:
    ControllerPinger().start()
    time.sleep(0.1)

