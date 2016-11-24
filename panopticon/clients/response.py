import collections
from datetime import datetime

class ResponseTypes():
    """

    The ResponseType class is used to indicate to the Response class which reponse type it should expect.
    THis class is primarily provided as an aid to programmers, such that they don't have to memorize all the keys
    for the different response types, but can just use dot notation on an instance of ResponseTypes to determine the
    appropriate response type from the provided attributes.

    """

    BROWSE = 'browse'
    READ = 'read'
    WRITE = 'write'
    SUBSCRIPTION = 'subscribe'
    CANCEL_SUBSCRIPTION = 'subscription_cancel'
    POLLED_SUBSCRIPTION = 'subscription_polled_refresh'

class Response(collections.MutableMapping):
    """

    The Response class is used to unpack SOAP responses, Currently, response type must be specified - this is just a key
    indicating to the Response class which decoder function it should use on the SOAP envelope. Future iterations will
    implement auto-type detection for SOAP packets, obviating the need for ResponseTypes.

    """

    def __init__(self, type, *args, **kwargs):
        # todo: see if we can automate reponse type detection
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys
        decode_function_mapping = {'subscription_polled_refresh': self.subscription_results_parser,
                                   'subscription_cancel': self.subscription_cancel_parser,
                                   'subscribe':self.subscription_results_parser,
                                   'browse':self.browse_parser,
                                   'read':self.read_parser,
                                   'write': self.write_parser,
                                   'status':self.status_parser}
        self.type = decode_function_mapping.get(type, None)
        self.open_envelope = decode_function_mapping[type]

    def __call__(self, response, *args, **kwargs):
        return self.open_envelope(response, *args, **kwargs)

    def browse_parser(self):
        raise NotImplementedError

    def read_parser(self):
        raise NotImplementedError

    def write_parser(self):
        raise NotImplementedError

    def status_parser(self):
        raise NotImplementedError

    def subscription_results_parser(self, response, **kwargs):
        """

        The subscription parser is used to convert SOAP responses into python types, then load them into the
        Response dictionary attribute at 'store'.

        :param response:
        :param kwargs:
        :return:
        """

        polled = kwargs.get('polled_refresh', None)
        result =  response.SubscriptionPolledRefreshResult if polled else response.SubscribeResult
        invalid_handles = response.InvalidServerSubHandles if polled else None

        errors = response.Errors
        items = response.RItemList

        self.store['status'], self.store['errors'], self.store['items'] = {}, {}, {}
        self.store['status']['recv_time'] = self.json_serial(result.RcvTime)
        self.store['status']['reply_time'] = self.json_serial(result.ReplyTime)
        self.store['status']['client_request_handle'] = result.ClientRequestHandle
        self.store['status']['locale_id'] = result.RevisedLocaleID
        self.store['status']['server_state'] = result.ServerState

        self.store['errors']['invalid_handles'] = invalid_handles
        self.store['errors']['errors'] = errors

        for item in items:
            #todo: does the line below ever cause issues?
            # todo: update: I believe we will not detect buffered values returned if we always pull just the first value
            # todo: need to test what our responses look like when we use buffering
            print(item)
            for item in item.Items:
                print(item)
                item_name = item.ItemName
                item_value = item.Value
                item_value_type = type(item_value)
                print("TYPE", item_value_type)
                self.store['items'].update({item_name: {'diagnostic': item.DiagnosticInfo}})
                self.store['items'].update({item_name: {'quality': item.Quality}})
                if 'array' in str(item_value_type).lower():
                    for key, val in item_value.__values__.items():
                        print("Items {} is an array. It has value {}".format(item_name, {key:val}))
                        self.store['items'].update({item_name: {'type': key, 'value': val}})
                else:

                    print("Item {} is NOT in an array. It has value {}.".format(item_name, item_value))

        return self.store

    def subscription_cancel_parser(self):
        raise NotImplementedError

    def json_serial(self, obj):
        """

        JSON serializer for objects not serializable by default json code.

        """

        if isinstance(obj, datetime):
            serial = obj.isoformat()
            return serial
        raise TypeError("Type not serializable")

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key
