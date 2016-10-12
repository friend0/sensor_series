# -*- coding: utf-8 -*-
from clients.client import BaseClient
from gritty_soap import Client

#todo: test if we need to use "true" or True in soap service calls
class KukaClient(BaseClient):

    def __init__(self, robot=None, wsdl=None, service='OpcXmlDA'):
        super(KukaClient, self).__init__()
        self.robot = robot
        self.wsdl, self.service = wsdl, service
        self.client = Client(wsdl="../OpcXMLDaServer.asmx", service_name=service)
        self.functions = self.client.service

    def get_status(self):
        result = self.functions.GetStatus()
        return result

    def browse(self, item_name=None, browse_filter=None, options=None):
        if not item_name:
            item_name = ''
        if not browse_filter:
            browse_filter = 'all'
        if not options:
            options = {'ItemName':item_name, 'BrowseFilter': browse_filter, 'LocaleID':'en-US', 'ClientRequestHandle': None,
                       'ReturnAllProperties':True, 'ReturnPropertyValues':True, 'ReturnErrorText':True}
        result = self.functions.Browse(**options)
        return result

    def read(self, item_name, element=None, options=None):
        if not options:
            options = {'ReturnItemTime':True, 'ReturnItemName':True}
        if not element:
            element = 'RobotVar'

        result = self.functions.Read(Options=options,
                            ItemList={'MaxAge':0, 'Items':{'ItemPath':'', 'ItemName':"{}.{}".format(element, item_name)}})
        return result

    def get_properties(self, item_name=None, item_path=None):
        if not item_name:
            item_name = 'RobotVar.TipDressCounter'
        if not item_path:
            item_path = ''

        result = self.functions.GetProperties(ReturnPropertyValues=True, ItemIDs=[{'ItemPath':item_path, 'ItemName':item_name}])
        return result

    def subscribe(self, item_name, server_handle, element=None, options=None):
        if not options:
            options = {'ReturnItemTime':True}
        if not element:
            element = 'RobotVar'
        self.functions.Subscribe(ReturnValuesOnReply=True, SubscriptionPingRate=5000, Options=options,
                            ItemList={'MaxAge': 0, 'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}})

    def polled_subscription(self, item_name, server_handle, element=None, options=None):
        if not options:
            options = {'ReturnItemTime':True}
        if not element:
            element = 'RobotVar'
        # hold time is given in this form...
        #todo: get hold time in this format. Figure out what hold time does, configure as needed.
        hold_time = '2016-10-11T10:31:02.311-07:00'
        self.functions.SubscribeHold(HoldTime=None, WaitTime=None, ReturnValuesOnReply=True, SubscriptionPingRate=5000,
                                     Options=options, ItemList={'MaxAge': 0, 'Items': {'ItemPath': '', 'ItemName': "{}.{}".format(element, item_name)}})

    def subscription_cancel(self, server_sub_handle, client_handle):
        options = {'ReturnItemTime':True}
        self.functions.SubscriptionCancel(Options=options, ServerSubHandle=server_sub_handle,
                                          ClientRequestHandle=client_handle)

BaseClient.register(KukaClient)

if __name__ == '__main__':
    kuka_client = KukaClient()
    ret_val = kuka_client.get_status()
    print(ret_val)
    ret_val = kuka_client.browse()
    print(ret_val)
    ret_val = kuka_client.get_properties()
    print(ret_val)
    ret_val = kuka_client.read('TipDressCounter')
    print(ret_val)