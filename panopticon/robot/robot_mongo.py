import multiprocessing
import time
import msgpack
import pymongo
import zmq


class RobotMongo(multiprocessing.Process):
    """

    RobotMongo runs a Mongo client alongside ZMQ sockets which are polled rapidly.
    Work received over the ZMQ channel prompt the RobotMongo process to take (or potentially deny) the requested action.
    Primarily, this interface is used to handle the retrieval, update, and potentially deletion of Robot documents in
    the db.

    .. note::
        The mongo container must be started before using this class.

    .. todo::
        Implement and test functions for simple document creation and retrieval.

    """

    def __init__(self, db, collection):
        """

        bind_addr: address to bind zmq socket on
        db_name: name of database to write to (created if doesn't exist)
        table_name: name of mongodb 'table' in the db to write to (created if doesn't exist)

        """
        super(RobotMongo, self).__init__()
        self.context = None
        self.poller = None
        self.context = None
        self._db = db
        self.collection = collection

        # todo: find a less brittle solution for pinging the host?
        # 10.0.2.2 is something that vBox sets up for access to host.
        # Do lazy connect to guard against problems induced by calls to 'fork'

        #self.client = pymongo.MongoClient(connect=False)
        self.client = pymongo.MongoClient(host='10.0.2.2', connect=False)

        existing_databases = set(self.client.database_names())
        self.robots = self.client.robots
        self.time_series = self.client.time_series
        self.databases = {'robots': self.robots, 'time_series':self.time_series}

        # todo: for debug purposes. Heres how to find out if a db exists already. Remove for production.
        for key, val in self.databases.items():
            print("Database '{}' exists? {}".format(key, key in existing_databases))

        # todo: if robots database does not exist, first populate it with base data

    def get_opc_robots(self):
        """

        Query the database for all OPC enabled robots, then return their host names, and network addresses.

        :return: A dictionary with a hostname/ip address pair.

        """
        # cursor = self.client.robots.kuka_robots.find({'studtech': {'$not':{'$eq':'N/A'}}})
        #cursor = self.client.robots.kuka_robots.find()
        cursor = self.client.robots.kuka_robots.find({'opc': True})
        # return a list of names
        for document in cursor:
            print(document)

    def get_time_series(self, robot_hostname):
        """

        Look up a value from the TimeSeries DB, which uses robot hostnames as the primary key.
        :param robot_hostname:
        :return:

        """

        pass

    def update_time_series(self, polled_subscription_response):
        """

        TimeSeries documents are tuned to store updates where the values are singular.
        For example, a TimeSeries would be appropriate for storing the value of an int over time, but not necessarily
        the value of an array over time.

        :param polled_subscription_response:
        :return:
        """

        # First, retrieve the time series document for the robot in question
        time_series = self.databases['time_series']

        robot_hostname = polled_subscription_response.get('hostname', None)
        if robot_hostname is None:
            print("Trying to process a response without a hostname key")
            return
        # From the TimeSeries, retrieve the active ValueSegment, or create a new one if the ValueSegment is full,
        # or does not exist.
        item_dicts = polled_subscription_response.get('items')
        import pprint
        if item_dicts:
            for key, val in item_dicts.items():
                print(key, '\n')
                pprint.pprint(val)

            # value_segment = time_series.find('series_trackers.item': item)

        #time_series.update({'_id': robot_hostname}, {'$set': {'':values}})

        pass

    def run(self):
        """

        The run function manages the RobotMongo instance's activity.
        Primarily, this involves servicing database requests via ZMQ sockets.

        :return:

        """

        # Initialize a zeromq context for this process. MUST occur in run function.
        self.context = zmq.Context()
        self.poller = zmq.Poller()


        # Set up a channel to receive results, register it with the poller device.
        self.results_receiver = self.context.socket(zmq.PULL)
        self.results_receiver.bind("tcp://127.0.0.1:5558")
        self.poller.register(self.results_receiver, zmq.POLLIN)
        time.sleep(1)

        print("Running Robomongo")
        while True:
            socks = dict(self.poller.poll())

            if socks.get(self.results_receiver) == zmq.POLLIN:
                msg = msgpack.unpackb(self.results_receiver.recv(), encoding='utf-8')
                msg = dict(msg)
                self.update_time_series(msg)
                # msg = self.results_receiver.recv_multipart()



if __name__ == '__main__':

    robomongo = RobotMongo('robots', 'kuka_robots')
    robomongo.get_opc_robots()
