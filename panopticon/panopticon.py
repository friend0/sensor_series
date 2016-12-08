import math
import uuid
import multiprocessing
import zmq
import panopticon
import pymongo

__all__ = ['Robot', 'Robots', 'ClientWorker', 'ClientVentilator', 'Panopticon']

NUM_WORKERS = 5

class Panopticon(multiprocessing.Process):
    """

    The Panopticon class handles the macroscopic tasks involved with starting, maintaining, and tearing down
    OPC client sessions. In particular, this function:

    * Instructs each robot in the given list of Robots() to subscribe to each item in the items arg.
      This is done using the 'watch' function.
    * Distributes the Robots amongst a set of RobotWorker threads, which are phase-synced using a RobotVentilator.
      When robots receive messages from the RobotVentilator, an update cycle is initiated, and all robots in all workers
      configured to listen to a given ventilator poll their subscriptions, and return the results. These results are
      then forwarded to the RobotMongo class to update the database. Done using the 'listen' function.
    * When the Panopticon process is started, all worker threads are started, along with a single RobotVentilator,
      therby initiating all require mechanisms for running the client. Apart from waiting for Interrupt signals,
      the Panopticon process will also provide TUI functionality for interfacing with live client connections,
      subscriptions, and etc.


    .. todo::
        Implement loading of robots from DB. Will require comm with RobotMongo, and calling of 'get_opc' function
        from that class.

    .. todo::
        Implement TUI for interfacing with live clients.

    """

    def __init__(self, robots=None, items=None, *args, **kwargs):
        super(Panopticon, self).__init__()
        self.context = zmq.Context()
        self.poller = zmq.Poller()
        # ZMQ channel initialization.
        self.control_receiver = self.context.socket(zmq.SUB)
        # todo: bring sanity to port numbering/management
        self.control_receiver.connect("tcp://127.0.0.1:5556")
        self.control_receiver.setsockopt_string(zmq.SUBSCRIBE, "")

        self.workers = {}
        self.items = None
        self.robots = []
        self.ventilator = None



    def watch(self, **kwargs):
        """

        Starts subscriptions to the given set of robots, for each of the given items.

        :param robots: Dictionary of robots (would this be better as just some iterable? Or an array?)
        :param items: A list of items for which we want to start a subscription.
        :return: robots, with updated server

        .. todo ::
            Robot should carry its own list of items, and those items should be stored in the database

        """

        client = pymongo.MongoClient('10.0.2.2')
        opc_robots = [robot for robot in client['test_robots']['kuka_robots'].find({'opc': True})]


        for robot_ in opc_robots:
            robot = panopticon.Robot(robot_['hostname'], robot_['ip'])
            self.robots.append(robot)
            print(robot_)
            for item in robot_['items']:
                robot.add_subscription(item, **kwargs)
        client.close()

    def listen(self, **kwargs):
        """

        Distribute Robots amongst RobotWorker threads.

        """
        max_workers = kwargs.get('max_workers', 5)

        # Assign robots to groups, then assign each group to a worker.
        actual_workers = min(len(self.robots), max_workers)
        work_group = [self.robots[x:x + math.ceil(len(self.robots) / actual_workers)] for x in
                      range(0, len(self.robots), math.ceil(len(self.robots) / actual_workers))]

        for group in work_group:
            robot_group = panopticon.Robots()
            robot_group.load(group)
            client_worker = panopticon.RobotWorker(self.context, robots=robot_group)
            self.workers[id(client_worker)] = client_worker

    def start(self):
        self.watch()
        self.listen()
        self.learn()

    def learn(self):
        """

        Start RobotWorker threads, and spawn a RobotVentilator.

        .. todo::
            Implement a TUI for interacting with live clients. Will probably need duplex communication with the
            RobotMongo client if both of them are to have influence over live subscriptions.

        """

        for key, worker in self.workers.items():
            print(key, worker)
            worker.start()
            print(key, worker)

        # RobotVentilator class broadcasts a heartbeat signal to all workers, indicating when to perform updates
        ventilator = panopticon.RobotVentilator(self.context, self.robots)

        while True:
            socks = dict(self.poller.poll())
            if socks.get(self.control_receiver) == zmq.POLLIN:
                control_message = self.control_receiver.recv()
                if control_message == "FINISHED":
                    # cleanup threads
                    break

        # todo: write a sig-int for this to clean up the process nicely.




