# Copyright (C) 2012 Costia Adrian
# Created on Feb 7, 2012
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

import imp
import platform
import traceback
import socket
from socket import error,  socket as sockets, AF_INET, SOCK_STREAM,SOCK_DGRAM, inet_ntoa,gethostname
from optparse import OptionParser
from subprocess import Popen, PIPE, STDOUT
import struct


fcntl_module_exists = False
fcntl_module = None
if 'Linux' in platform.system():
    module = "fcntl"
    fp, pathname, description = imp.find_module(module)
    try:
        fcntl_module = imp.load_module(module, fp, pathname, description)
        fcntl_module_exists = True
    finally:
        if fp:
            fp.close()
    
class Network:

    def __init__(self):
        self.hostname = None
        self.domain   = None

    def getHostName(self):
        proc   = Popen(['hostname','-A'],stdout=PIPE,stderr=PIPE)
        result = proc.wait()
        if result == 0:
            self.hostname = proc.stdout.read()
        return self.hostname

    def getDomain(self):
        proc   = Popen(['hostname','-d'],stdout=PIPE,stderr=PIPE)
        result = proc.wait()
        if result == 0:
            self.domain = proc.stdout.read()
        return self.domain

    def getHostByDomain(self):
        host = str(self.getHostName())
        if len(host) == 0:
            host = str(self.getHostName())+"."+str(self.getDomain())
        return host

    def getHost(self):
        self.hostname = gethostname()
        return self.hostname

    def getIpAddress(self,iface): # getIpAddress('eth0')
        if platform.system == "Linux" and fcntl_module_exists == True:
            s = socket(AF_INET, SOCK_DGRAM)
            ipAddr  =  inet_ntoa(fcntl_module.ioctl(s.fileno(),0x8915,struct.pack('256s', iface[:15]))[20:24])
        else:   # on windows
            try:
                ipAddr = [ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1]
            except Exception as exc:
                print str(exc)
        return ipAddr

    def getHwAddr(self,ifname=None):   # getHWAddr('eth0')
        if 'Linux' in platform.system() and fcntl_module_exists == True:
            if ifname == None:
                raise Exception('eth not specified!')
            s = socket(AF_INET, SOCK_DGRAM)
            info = fcntl_module.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15]))
            hwaddr = ''.join(['%02x:' % ord(char) for char in info[18:24]])[:-1]
        else:
            '''
                http://docs.python.org/library/uuid.html
                uuid.getnode() :
                    Get the hardware address as a 48-bit positive integer. The first time this runs,
                    it may launch a separate program, which could be quite slow. 
                    If all attempts to obtain the hardware address fail, we choose a random 48-bit number 
                    with its eighth bit set to 1 as recommended in RFC 4122.
                    "Hardware address" means the MAC address of a network interface,
                    and on a machine with multiple network interfaces the MAC address of 
                    any one of them may be returned. 
            '''
            import uuid
            mac_address = str(hex(uuid.getnode()))
            hwaddr = mac_address.replace("0x", "").replace("L", "").upper()
        return str(hwaddr)

def portIsOpen(port):
    ''' check if port is open '''
    s = sockets(AF_INET, SOCK_STREAM)
    try:
        try:
            s.connect(('localhost', port))
            return True
        except Exception as exc:
            traceback.print_exc()
    finally:
            s.close()
    return False


# test
if __name__ == "__main__":
    net = Network()
    mac = net.getHwAddr('eth0')
    print mac