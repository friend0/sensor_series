import multiprocessing
import datetime
import time
import msgpack
import pymongo
import zmq
import uuid
from panopticon.documents import *

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

    def __init__(self, db=None, collection=None, host=None):
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
        self.operations = []

        """
        todo: update the last value cache on each query. On updates, we can check against this cache - if an entry
        exists, we will only trigger an update if the data has changed. This saves us db write throughput.
        """
        self.last_value_cache = {}
        # todo: find a less brittle solution for pinging the host?

        # 10.0.2.2 is something that vBox sets up for access to host.
        # Do lazy connect to guard against problems induced by calls to 'fork'

        if host is None:
            self.client = pymongo.MongoClient(host='10.0.2.2', connect=False)
        else:
            self.client = pymongo.MongoClient(host=host, connect=False)

        existing_databases = set(self.client.database_names())
        # todo: refactor robots to robots_db
        self.robots = self.client.robots_db
        # todo: refactor time_series to time_series_db
        self.time_series = self.client.time_series_db
        self.values = self.client.value_segment_db


        self.databases = {'robots': self.robots, 'time_series':self.time_series}
        # todo: for debug purposes. Heres how to find out if a db exists already. Remove for production.
        for key, val in self.databases.items():
            print("Database '{}' exists? {}".format(key, key in existing_databases))

        # todo: if robots database does not exist, first populate it with base data

    def get_opc_robots(self):
        """

        Query the database for all OPC enabled robots, then return a list of all robot documents.

        :return: A dictionary with a hostname/ip address pair.

        """
        # cursor = self.client.robots.kuka_robots.find({'studtech': {'$not':{'$eq':'N/A'}}})
        #cursor = self.client.robots.kuka_robots.find()
        return [robot for robot in self.client['test_robots']['kuka_robots'].find({'opc': True})]

    def instantiate_series(self):
        """

        :return:
        """

        time_series_set = self.client['time_series_set']
        value_segments = self.client['value_segments_db']

        opc_robots = self.get_opc_robots()
        for robot in opc_robots:
            for item in robot['items']:
                segment_id = uuid.uuid1(clock_seq=1)

                value_segment = ValueSegment(
                    series_id='{}.{}'.format(robot.get('hostname'), item.ljust(64, ' '))).encode()
                update_result = time_series_set.kuka_robots.update_one(
                    {'_id': '{}.{}'.format(robot['hostname'], item), 'robot_id': robot['hostname']},
                    {'$setOnInsert':
                         {"series": Series(current_segment_id=segment_id, first_segment_id=segment_id).encode(),
                          'robot': robot['hostname'],
                          'type': 'time_series'
                          }
                     },
                    upsert=True)
                # If the series has just been created, give it an initial value segment as well.
                if update_result.upserted_id:
                    value_segments.kuka_robots.update_one(
                        {'_id': segment_id},
                        {'$set':
                             {"segment": value_segment}
                         },
                        upsert=True)

    def get_series(self, robot_hostname, item=None):

        time_series_set = self.client['time_series_set']

        if item is None:
            find_function = time_series_set.kuka_robtos.find
            query = {'robot_id': robot_hostname}
        else :
            find_function = time_series_set.kuka_robots.find_one
            query = {'_id': '{}.{}'.format(robot_hostname, item)}

        robot_series = find_function(
            query,
            projection={'_id': 0}
        )
        if isinstance(robot_series, pymongo.cursor.Cursor):
            robot_series = robot_series[:]

        return robot_series

    def get_time_series(self, robot_hostname, item=None, time_range=None):
        """

        Look up a value from the TimeSeries DB, which uses robot hostnames as the primary key.
        :param robot_hostname:
        :return:

        """

        value_db = self.client['value_segments_db']
        series = self.get_series(robot_hostname, item)

        # querey value segments db
        if not time_range:
            values_segments = value_db.kuka_robots.find({'segment.series_id': '{}.{}'.format(robot_hostname, item)})
        return values_segments

    def get_last_value(self, robot_hostname, item):
        time_series_set = self.client['time_series_set']

        robot_series = time_series_set.kuka_robots.find_one(
            {'_id': '{}.{}'.format(robot_hostname, item)},
            projection={'_id': 0, "series.last_value": 1}
        )
        return robot_series['series']['last_value']

    # todo: implement a cached version of this function which takes advantage of BulkUpdate speed increase
    def update_time_series(self, polled_subscription_response=None, **kwargs):
        """

        TimeSeries documents are tuned to store updates where the values are singular.
        For example, a TimeSeries would be appropriate for storing the value of an int over time, but not necessarily
        the value of an array over time.

        :param polled_subscription_response:
        :return:
        """
        time_series_set = self.client['time_series_set']
        value_db = self.client['value_segments_db']

        if not polled_subscription_response:
            robot_hostname = kwargs.get('robot_hostname')
            items_values = kwargs.get('items_values')

            if not (robot_hostname and items_values) or not isinstance(items_values, dict):
                raise ValueError("Update of time series requires a polled_subscription_response, "
                                 "or robot hostname, and a dictionary of item/value pairs")
        else:
            # Unwrap necessary data from polled subscription response
            robot_hostname = polled_subscription_response['hostname']
            items_values = {key:val['value'] for key, val in polled_subscription_response['items'].items()}

        for item, value in items_values.items():
            robot_series = time_series_set.kuka_robots.find_one_and_update(
                {'_id': '{}.{}'.format(robot_hostname, item)},
                {'$set': {'series.last_value': value},
                 '$currentDate': {'series.last_time': True},
                 '$inc': {'series.current_segment_ptr': -1}},
                projection={'_id': 0, "series.current_segment_ptr": 1, "series.current_segment_id": 1}
            )
            current_segment_ptr = robot_series['series']['current_segment_ptr']
            current_segment_id = robot_series['series']['current_segment_id']

            value_db.kuka_robots.update_one(
                {'_id': current_segment_id},
                {'$set': {'segment.times.{}'.format(current_segment_ptr): datetime.datetime.now(),
                          'segment.values.{}'.format(current_segment_ptr): value}}
            )
            if current_segment_ptr <= 0:
                self.create_new_segment(robot_hostname, value, item)


        #value_db.kuka_robots.bulk_write(operations, ordered=True)

    def create_new_segment(self, robot_hostname, value, item):
        time_series_set = self.client['time_series_set']
        value_db = self.client['value_segments_db']
        segment_id = uuid.uuid1(clock_seq=1)
        value_segment = ValueSegment(
            series_id='{}.{}'.format(robot_hostname, item),
            segment_id=segment_id).encode()
        time_series_set.kuka_robots.update_one(
            {'_id': '{}.{}'.format(robot_hostname, item)},
            {'$set': {'series.current_segment_id': segment_id, 'series.last_time': datetime.datetime.now(),
                      'series.current_segment_ptr': 180}}
        )
        value_db.kuka_robots.update_one(
            {'_id': segment_id},
            {'$set': {"segment": value_segment}},
            upsert=True)

    def cached_update_time_series(self, polled_subscription_response=None, **kwargs):
        """

        TimeSeries documents are tuned to store updates where the values are singular.
        For example, a TimeSeries would be appropriate for storing the value of an int over time, but not necessarily
        the value of an array over time.

        :param polled_subscription_response:
        :return:
        """
        time_series_set = self.client['time_series_set']
        value_db = self.client['value_segments_db']

        if not polled_subscription_response:
            robot_hostname = kwargs.get('robot_hostname')
            items_values = kwargs.get('items_values')

            if not (robot_hostname and items_values) or not isinstance(items_values, dict):
                raise ValueError("Update of time series requires a polled_subscription_response, "
                                 "or robot hostname, and a dictionary of item/value pairs")
        else:
            # Unwrap necessary data from polled subscription response
            robot_hostname = polled_subscription_response['hostname']
            items_values = {key:val['value'] for key, val in polled_subscription_response['items'].items()}

        for item, value in items_values.items():
            robot_series = time_series_set.kuka_robots.find_one_and_update(
                {'_id': '{}.{}'.format(robot_hostname, item)},
                {'$set': {'series.last_value': value},
                 '$currentDate': {'series.last_time': True},
                 '$inc': {'series.current_segment_ptr': -1}},
                projection={'_id': 0, "series.current_segment_ptr": 1, "series.current_segment_id": 1}
            )
            current_segment_ptr = robot_series['series']['current_segment_ptr']
            current_segment_id = robot_series['series']['current_segment_id']

            self.operations.append(pymongo.UpdateOne(
                {'_id': current_segment_id},
                {'$set': {'segment.times.{}'.format(current_segment_ptr): datetime.datetime.now(),
                          'segment.values.{}'.format(current_segment_ptr): value}}
            ))
            if current_segment_ptr <= 0:
                self.create_new_segment(robot_hostname, value, item)

    def write_out_update_cache(self):
        value_db = self.client['value_segments_db']
        value_db.kuka_robots.bulk_write(self.operations, ordered=True)

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
                multipart = self.results_receiver.recv_multipart()
                instruction = multipart[0]

                msg = dict(msg)
                # todo: implement version with send/receive multipart to support calls to db client api.


                self.update_time_series(msg)
                # msg = self.results_receiver.recv_multipart()



if __name__ == '__main__':

    robomongo = RobotMongo('robots', 'kuka_robots')
    robomongo.get_opc_robots()
