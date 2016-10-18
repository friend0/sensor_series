# -*- coding: utf-8 -*-
import attr
from clients.client import BaseClient
from gritty_soap import Client


@attr.s
class KukaClient(BaseClient):
    """

    A Kuka Client class for communicating with an OPC server via XML DA.

    """

    robot = attr.ib(default=None)
    wsdl = attr.ib(default=None)
    client = attr.ib(default=Client(wsdl="/home/vagrant/dev/opc/OpcXMLDaServer.asmx", service_name='OpcXmlDA'))

    def status(self, **kwargs):
        """

        Retrieve the client's status and health parameters.

        Makes a direct call to the client service 'GetStatus'. You may pass in desired arguments by using kwargs.

        :return:

        """
        _status = self.client.service.GetStatus
        return _status()

    def browse(self, item_name='', browse_filter='all', options=None):
        """

        Browse the elements of the OPC server.

        By default, will return the elements at the OPC server's root. You may also use this function to browse
        Items in the returned elements list.

        :param item_name:
        :param browse_filter:
        :param options:
        :return:

        """
        if not options:
            options = {'ItemName':item_name, 'BrowseFilter': browse_filter, 'LocaleID':'en-US', 'ClientRequestHandle': None,
                       'ReturnAllProperties':True, 'ReturnPropertyValues':True, 'ReturnErrorText':True}

        _browse = self.client.service.Browse
        return _browse(**options)

    def read(self, item_name, element='RobotVar', options=None):
        """

        Read an item from the OPC server.

        By default, we read variables from the RobotVar element on the Kuka OPC server. You may access items from other
        other elements, i.e. 'KRCReg, ' by providing 'KRCReg' to the elements keyword argument of this function.

        :param item_name:
        :param element:
        :param options:
        :return:

        """
        if not options:
            options = {'ReturnItemTime':True, 'ReturnItemName':True}

        _read = self.client.service.Read
        return _read(Options=options,
                            ItemList={'MaxAge':0, 'Items':{'ItemPath':'', 'ItemName':"{}.{}".format(element, item_name)}})

    def get_properties(self, item_name=None, **kwargs):
        """

        Retrieve properties for a specific item.

        :param item_name:
        :param item_path:
        :return:

        """

        if not item_name:
            item_name = 'RobotVar.TipDressCounter'
        item_path = kwargs.get('item_path', '')

        _get_properties = self.client.service.GetProperties
        return _get_properties(ReturnPropertyValues=True, ItemIDs=[{'ItemPath':item_path, 'ItemName':item_name}])

    def subscribe(self, item_name, server_handle, **kwargs):
        """

        Subscribe to updates on a particular item. Non-polling!

        :param item_name:
        :param server_handle:
        :param element:
        :return:

        """

        options = kwargs.get('options', {'ReturnItemTime':True})
        rate = kwargs.get('rate', 5000)
        element = kwargs.get('element', 'RobotVar')
        # todo: determine proper format for MaxAge argument
        max_age = kwargs.get('max_age', 0)

        _subscribe = self.client.service.Subscribe
        return _subscribe(ReturnValuesOnReply=True, SubscriptionPingRate=rate, Options=options,
                          ItemList={'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}})

    def polled_subscription(self, item_name, server_handle, **kwargs):
        """

        Setup a polled subscription to updates on a particular item.

        :param item_name:
        :param server_handle:
        :param element:
        :param options:
        :return:

        """
        options = kwargs.get('options', {'ReturnItemTime':True})
        element = kwargs.get('element', 'RobotVar')
        rate = kwargs.get('rate', 5000)
        hold = kwargs.get('hold_time', None)
        wait = kwargs.get('wait', None)
        # todo: determine proper format for MaxAge argument
        max_age = kwargs.get('max_age', 0)

        # hold time is given in this form...
        #todo: get hold time in this format. Figure out what hold time does, configure as needed.
        hold_time = '2016-10-11T10:31:02.311-07:00'
        _polled_subscription = self.client.services.SubscriptionPolledRefresh
        return _polled_subscription(ReturnValuesOnReply=True, HoldTime=hold, WaitTime=wait, SubscriptionPingRate=rate,
                                     Options=options, ItemList={'MaxAge': max_age, 'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}})

    def subscription_cancel(self, server_sub_handle, client_handle):
        """

        Cancel an existing subscription.

        :param server_sub_handle:
        :param client_handle:
        :return:

        """
        options = {'ReturnItemTime':True}
        _subscription_cancel = self.client.services.SubscriptionCancel
        return _subscription_cancel(Options=options, ServerSubHandle=server_sub_handle,
                                          ClientRequestHandle=client_handle)

BaseClient.register(KukaClient)

import socket
import struct
#import sys

import twisted
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
#import zmq
import sys

port = "2222"

class MulticastClient(DatagramProtocol):

    def startProtocol(self):
        #for iface in ['172.16.1.1']:
        self.transport.joinGroup("239.192.77.128")
        #self.transport.write('Client: Ping', ("239.192.77.130", 2222))

    def datagramReceived(self, datagram, address):
        print("DGRAM {} received from {}".format(repr(datagram), repr(address)))


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

# todo: transpose this sequence to a tests suite
if __name__ == '__main__':
    #context = zmq.Context()
    #sock = context.socket(zmq.SUB)

    kuka_client = KukaClient()
    multi_socket = MulticastSocket(local_port=2222)
    multi_socket.mcast_add('239.192.77.128', '127.0.0.1')

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

    #sock.connect("pgm://eth0;10.0.2.15:{}".format(port))
    #sock.setsockopt_unicode(zmq.SUBSCRIBE, '')
    #for update in range(5):
    #    string = sock.recv()
    #    topic, messagedata = string.split()
    #    print(topic, messagedata)

    #multicast_group = '239.192.77.128'
    #mcast_port = 2222

    #sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    #sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #sock.bind(('', mcast_port))

    #mreq = struct.pack('=4sl', socket.inet_aton(multicast_group), socket.INADDR_ANY)
    #group = socket.inet_aton(multicast_group)
    #sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, address = multi_socket.recv(1024)
        print(multi_socket.recv(10240))
