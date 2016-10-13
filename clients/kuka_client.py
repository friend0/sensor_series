# -*- coding: utf-8 -*-
import attr
from clients.client import BaseClient
from gritty_soap import Client


@attr.s
class KukaClient(BaseClient):
    """

    A Kuka Client class for making for communicating with an OPC server via XML DA.

    """

    robot = attr.ib(default=None)
    wsdl = attr.ib(default=None)
    service = attr.ib(default='OpcXmlDA')
    client = attr.ib(default=Client(wsdl="../OpcXMLDaServer.asmx", service_name=service))

    def status(self):
        result = self.functions.GetStatus()
        return result

    def browse(self, item_name='', browse_filter='all', options=None):
        if not options:
            options = {'ItemName':item_name, 'BrowseFilter': browse_filter, 'LocaleID':'en-US', 'ClientRequestHandle': None,
                       'ReturnAllProperties':True, 'ReturnPropertyValues':True, 'ReturnErrorText':True}

        return self.functions.Browse(**options)

    def read(self, item_name, element='RobotVar', options=None):
        if not options:
            options = {'ReturnItemTime':True, 'ReturnItemName':True}

        _read = self.client.services.Read
        return _read(Options=options,
                            ItemList={'MaxAge':0, 'Items':{'ItemPath':'', 'ItemName':"{}.{}".format(element, item_name)}})

    def get_properties(self, item_name=None, item_path=None):
        if not item_name:
            item_name = 'RobotVar.TipDressCounter'
        if not item_path:
            item_path = ''

        _get_properties = self.client.services.GetProperties
        return _get_properties(ReturnPropertyValues=True, ItemIDs=[{'ItemPath':item_path, 'ItemName':item_name}])

    def subscribe(self, item_name, server_handle, element='RobotVar', options=None):
        if not options:
            options = {'ReturnItemTime':True}

        _subscribe = self.client.services.Subscribe
        return _subscribe(ReturnValuesOnReply=True, SubscriptionPingRate=5000, Options=options,
                          ItemList={'MaxAge': 0, 'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}})

    def polled_subscription(self, item_name, server_handle, element=None, options=None):
        if not options:
            options = {'ReturnItemTime':True}
        if not element:
            element = 'RobotVar'
        # hold time is given in this form...
        #todo: get hold time in this format. Figure out what hold time does, configure as needed.
        hold_time = '2016-10-11T10:31:02.311-07:00'
        _polled_subscription = self.client.services.SubscriptionPolledRefresh
        return _polled_subscription(HoldTime=None, WaitTime=None, ReturnValuesOnReply=True, SubscriptionPingRate=5000,
                                     Options=options, ItemList={'MaxAge': 0, 'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}})

    def subscription_cancel(self, server_sub_handle, client_handle):
        options = {'ReturnItemTime':True}
        _subscription_cancel = self.client.services.SubscriptionCancel
        return _subscription_cancel(Options=options, ServerSubHandle=server_sub_handle,
                                          ClientRequestHandle=client_handle)

BaseClient.register(KukaClient)

# todo: transpose this sequence to a tests suite
if __name__ == '__main__':
    kuka_client = KukaClient()
    ret_val = kuka_client.status()
    print(ret_val)
    ret_val = kuka_client.browse()
    print(ret_val)
    ret_val = kuka_client.get_properties()
    print(ret_val)
    ret_val = kuka_client.read('TipDressCounter')
    print(ret_val)