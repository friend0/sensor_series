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
    client = attr.ib(default=Client(wsdl="../OpcXMLDaServer.asmx", service_name='OpcXmlDA'))

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

    def get_properties(self, item_name=None, item_path=None):
        """

        Retrieve properties for a specific item.

        :param item_name:
        :param item_path:
        :return:
        """
        if not item_name:
            item_name = 'RobotVar.TipDressCounter'
        if not item_path:
            item_path = ''

        _get_properties = self.client.service.GetProperties
        return _get_properties(ReturnPropertyValues=True, ItemIDs=[{'ItemPath':item_path, 'ItemName':item_name}])

    def subscribe(self, item_name, server_handle, element='RobotVar', options=None):
        """

        Subscribe to updates on a particular item. Non-polling!

        :param item_name:
        :param server_handle:
        :param element:
        :param options:
        :return:
        """
        if not options:
            options = {'ReturnItemTime':True}

        _subscribe = self.client.services.Subscribe
        return _subscribe(ReturnValuesOnReply=True, SubscriptionPingRate=5000, Options=options,
                          ItemList={'MaxAge': 0, 'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}})

    def polled_subscription(self, item_name, server_handle, element=None, options=None):
        """

        Setup a polled subscription to updates on a particular item.

        :param item_name:
        :param server_handle:
        :param element:
        :param options:
        :return:

        """
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