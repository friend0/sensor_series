#from gritty_soap import Client
from clients.client import BaseClient
#from clients.kuka_client import KukaClient
import socket
import struct

class MulticastSocket(socket.socket):

    def __init__(self, local_port, reuse=True):
        super(MulticastSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM)
        if reuse:
            self.setsockopt(socket.IPPROTO_IP, socket.SO_REUSEADDR, 1)
            if hasattr(socket, "SO_REUSEPORT"):
                self.setsockopt(socket.IPPROTO_IP, socket.SO_REUSEPORT, 1)
                #self.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        self.bind(('', local_port))

    def mcast_add(self, addr, iface):
        addrinfo = socket.getaddrinfo(addr, None)[0]
        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])
        mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
        #mreq = struct.pack('=', socket.inet_aton(addr), socket.inet_aton(iface))
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(addr) + socket.inet_aton(iface))

multi_socket = MulticastSocket(local_port=2222)
multi_socket.mcast_add('239.192.77.130', '172.16.22.1')
#multi_socket.mcast_add('239.192.77.130', '172.16.22.1')
#multi_socket.mcast_add('239.192.77.128', '127.0.0.1')
#multi_socket.mcast_add('239.192.77.130', '127.0.0.1')

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
    data, address = multi_socket.recvfrom(1024)
    from collections import namedtuple
    from pprint import pprint
    # item count, seq addr, length, conn_id, seq_num, conn_data_item, len,
    #item_count, seq_addr, length, conn_id, seq_num, conn_data_item, len = struct.unpack('<h46B', data)
    Packet = namedtuple('Packet', 'item_count seq_addr len conn_id seq_num conn_data_item data_length data')
    #Packet._make()
    #item_count, seq_addr, length, conn_id, seq_num, conn_data_item, len, data = struct.unpack('<2B 2B 2B 4B 4B 2B 2B 30B', data)
    packet = Packet._make(struct.unpack('<H H H L I H H 30p', data))
    #print(data, address)
    packet = dict(packet._asdict())
    packet['conn_data_item'] = format((packet['conn_data_item']), '#04x')
    packet['conn_id'] = hex(packet['conn_id'])
    #packet['data'] = format(packet['data'], 'b')
    import binascii

    packet['data'] = binascii.hexlify(bytearray(packet['data']))
    packet['data'] = bytearray(packet['data'])[14:]
    print(packet['data'][:2], packet['data'][3:22], packet['data'][23:-12], packet['data'][-12:])

    #pprint(packet)

