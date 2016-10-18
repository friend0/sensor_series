from gritty_soap import Client
from clients.client import BaseClient
from clients.kuka_client import KukaClient
import socket

class MulticastSocket(socket.socket):

    def __init__(self, local_port, reuse=True):
        super(MulticastSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        if reuse:
            self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.bind(('', local_port))
    def mcast_add(self, addr, iface):
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
                        socket.inet_aton(addr) + socket.inet_aton(iface))

# context = zmq.Context()
# sock = context.socket(zmq.SUB)

kuka_client = KukaClient()

ret_val = kuka_client.status()
print(ret_val)
ret_val = kuka_client.browse()
print(ret_val)
ret_val = kuka_client.get_properties()
print(ret_val)
ret_val = kuka_client.read('TipDressCounter')
print(ret_val)
ret_val = kuka_client.subscribe('TipDressCounter', None)
print(ret_val)

multi_socket = MulticastSocket(local_port=2222)
multi_socket.mcast_add('239.192.77.128', '172.16.22.1')
multi_socket.mcast_add('239.192.77.130', '172.16.22.1')
multi_socket.mcast_add('239.192.77.128', '127.0.0.1')
multi_socket.mcast_add('239.192.77.130', '127.0.0.1')

# sock.connect("pgm://eth0;10.0.2.15:{}".format(port))
# sock.setsockopt_unicode(zmq.SUBSCRIBE, '')
# for update in range(5):
#    string = sock.recv()
#    topic, messagedata = string.split()
#    print(topic, messagedata)

# multicast_group = '239.192.77.128'
# mcast_port = 2222

# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
# sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# sock.bind(('', mcast_port))

# mreq = struct.pack('=4sl', socket.inet_aton(multicast_group), socket.INADDR_ANY)
# group = socket.inet_aton(multicast_group)
# sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while True:
    data, address = multi_socket.recv(1024)
    print(multi_socket.recv(10240))

