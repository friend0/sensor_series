from threading import Thread
import time
import msgpack
import attr
import zmq
from bson import json_util
import json
from threading import Timer
import math

class ClientVentilator(object):

    def __init__(self, robots, interval=.5, max_workers = 5, *args, **kwargs):
        self.context = zmq.Context()
        self._timer = None
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False

        self.robots = robots
        self.max_workers = max_workers
        # Set up a channel to generate work
        self.ventilator_pipe = self.context.socket(zmq.PUSH)
        self.ventilator_pipe.bind("tcp://127.0.0.1:5557")

        # Set up a channel to send control commands
        self.control_sender = self.context.socket(zmq.PUB)
        self.control_sender.bind("tcp://127.0.0.1:5559")

        # Phase sync
        phases = kwargs.get('phases', None)
        # Let the system wind up
        time.sleep(1)
        self.start(self.max_workers)
        self.client_workers = {}

    def __ventilate(self, *args, **kwargs):
        self.is_running = False
        self.start(self.max_workers)
        self.ventilator_pipe.send(msgpack.packb({'sync': []}))

    def start(self, max_workers):
        if not self.is_running:
            self._timer = Timer(self.interval, self.__ventilate)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

class ClientWorker(Thread):

    def __init__(self, context, robots, **kwargs):
        super(ClientWorker, self).__init__(daemon=True)
        self.context = context
        self.robots = robots
        self.sampling_rate = kwargs.get('sampling_rate', .5)
        # todo: figure out a better defualt when we don't get id (UUID?)
        self.id = kwargs.get('id', None)
        # Set up a channel to receive work from the ventilator
        self.work_receiver = self.context.socket(zmq.PULL)
        # Set up a channel to send result of work to the results reporter
        self.results_sender = self.context.socket(zmq.PUSH)
        # Set up a channel to receive control messages over
        self.control_receiver = self.context.socket(zmq.SUB)
        # Set up a poller to multiplex the work receiver and control receiver channels
        self.poller = zmq.Poller()

    #def _send_recv_msg(self, msg):
    #    self._socket.send_multipart(msg)
    #    return self._socket.recv_multipart()[0]

    #def get_doc(self, keys):
    #    msg = ['get', json.dumps(keys)]
    #    json_str = self._send_recv_msg(msg)
    #    return json.loads(json_str)

    #def add_doc(self, doc):
    #    msg = ['add', json.dumps(doc)]
    #    return self._send_recv_msg(msg)

    def run(self):

        self.work_receiver.connect("tcp://127.0.0.1:5557")
        self.results_sender.connect("tcp://127.0.0.1:5558")
        self.control_receiver.connect("tcp://127.0.0.1:5559")

        self.control_receiver.setsockopt_string(zmq.SUBSCRIBE, "")
        self.poller.register(self.work_receiver, zmq.POLLIN)
        self.poller.register(self.control_receiver, zmq.POLLIN)

        # Loop and accept messages from both channels, acting accordingly
        while True:
            socks = dict(self.poller.poll())
            # If the message came from work_receiver channel, square the number
            # and send the answer to the results reporter
            if socks.get(self.work_receiver) == zmq.POLLIN:
                for host, robot in self.robots.items():
                    print("ROBOT:", robot)
                    returner = robot.client.polled_subscription()
                    print(returner)
                    # todo: act on the value returned from the client, update db if applicable
            # If the message came over the control channel, shut down the worker.
            if socks.get(self.control_receiver) == zmq.POLLIN:
                control_message = self.control_receiver.recv()
                if control_message == "FINISHED":
                    # todo: implement proper cleanup of client worker
                    break


class ClientMongoConnection():
    """
    ZMQ server that adds/fetches documents (ie dictionaries) to a MongoDB.

    NOTE: mongod must be started before using this class
    """

    def __init__(self, table, table_name):
        """
        bind_addr: address to bind zmq socket on
        db_name: name of database to write to (created if doesn't exist)
        table_name: name of mongodb 'table' in the db to write to (created if doesn't exist)
        """

        # Initialize a zeromq context
        self.context = zmq.Context()

        # Set up a channel to receive results
        self.results_receiver = self.context.socket(zmq.PULL)
        self.results_receiver.bind("tcp://127.0.0.1:5558")

        # Set up a channel to send control commands
        self.control_sender = self.context.socket(zmq.PUB)
        self.control_sender.bind("tcp://127.0.0.1:5559")
        self._table = table

    def start(self):

        while True:
            msg = self.results_receiver.recv_multipart()
            print("Received msg: ", msg)
            #if  len(msg) != 3:
            #    error_msg = 'invalid message received: %s' % msg
            #    print(error_msg)
            #    reply = [msg[0], error_msg]
            #    socket.send_multipart(reply)
            #    continue
            id = msg[0]
            operation = msg[1]
            contents = json.loads(msg[2])
            # always send back the id with ROUTER
            reply = [id]
            if operation == 'add':
                self.add_document(contents)
                reply.append("success")
            elif operation == 'get':
                doc = self.get_document_by_keys(contents)
                json_doc = self._doc_to_json(doc)
                reply.append(json_doc)
            else:
                print('unknown request')
            #self.results_receiver.send_multipart(reply)

if __name__ == '__main__':
    import math
