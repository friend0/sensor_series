# -*- coding: utf-8 -*-
import attr
from gritty_soap.client import Client
from panopticon.clients.client import BaseClient


def hostname(robot):

    return True

@attr.s
class KukaClient(BaseClient):
    """

    A Kuka Client class for communicating with an OPC server via XML DA.

    """

    wsdl = attr.ib(default=None)
    client = attr.ib(default=Client(wsdl="/home/vagrant/dev/opc/OpcXMLDaServer.asmx", service_name='OpcXmlDA'))
    subscriptions = attr.ib(default=attr.Factory(dict))

    def subscribe_all(self):
        """

        Using a master list of standard variable names, begin subscriptions to all of them.

        :return:
        """
        raise NotImplementedError

    def unsubscribe_all(self):
        """

        Using a master list of standard variable names, end subscriptions to all of them.
        :return:
        """
        raise NotImplementedError

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
        response = _subscribe(ReturnValuesOnReply=True, SubscriptionPingRate=rate, Options=options,
                   ItemList={'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}})

        # todo: check for errors here
        handle = response.get('ServerSubHandle', None)
        if not handle:
            # raise an exception
            pass
        else:
            self.subscriptions[item_name] = handle
        return response

    def polled_subscription(self, **kwargs):
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

        some_dict = {}
        subs = self.subscriptions.values()
        handle_string = ''
        for sub in subs:
            handle_string += sub
        #'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}}

        # hold time is given in this form...
        #todo: get hold time in this format. Figure out what hold time does, configure as needed.
        hold_time = '2016-10-11T10:31:02.311-07:00'
        _polled_subscription = self.client.services.SubscriptionPolledRefresh
        results = _polled_subscription(ReturnAllItems=True, HoldTime=hold, WaitTime=wait, ItemList=item_list)
        return results

    def subscription_cancel(self, server_sub_handle, client_handle):
        """

        Cancel an existing subscription.

        :param server_sub_handle:
        :param client_handle:
        :return:

        """
        options = {'ReturnItemTime':True}
        _subscription_cancel = self.client.services.SubscriptionCancel
        response = _subscription_cancel(Options=options, ServerSubHandle=server_sub_handle, ClientRequestHandle=client_handle)

        if response:
            pop = self.subscriptions.pop(server_sub_handle, None)
            if not pop:
                # raise an exception, the subscription did not exist
                pass
        else:
            # raise an exception
            pass

        return response

BaseClient.register(KukaClient)

# todo: transpose this sequence to a tests suite
if __name__ == '__main__':
    #context = zmq.Context()
    #sock = context.socket(zmq.SUB)

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
