import math
import uuid
import multiprocessing
import zmq
import mongoengine
import panopticon

# todo: see if the __all__ tag is working as expected/define what it should do.
__all__ = ['Robot', 'Robots', 'ClientWorker', 'ClientVentilator', 'Panopticon']

NUM_WORKERS = 5

class Panopticon():

    def __init__(self, context=None, db=None, robots=None):

        if context is None:
            self.context = zmq.Context()
        else:
            self.context = context

        self.workers = {}
        # Set up a channel to receive control messages over
        self.control_receiver = zmq.Context().socket(zmq.SUB)
        # Set up a poller to multiplex the work receiver and control receiver channels
        self.poller = zmq.Poller()

        # todo: remove when db load is implemented
        # get robots from db (use default list if not db - temp soln for testing
        self.robots = robots
        #if not db and robots:
        #    # make some default robots here
        #    self.robots = robots
        #else:
        #    # pull from db, create Robots instance
        #    pass


    def watch(self, items, **kwargs):
        #todo: robot should carry its own list of items, and those items should be stored in the database
        """

        Starts subscriptions to the given set of robots, for each of the given items.

        :param robots: Dictionary of robots (would this be better as just some iterable? Or an array?)
        :param items: A list of items for which we want to start a subscription.
        :return: robots, with updated server

        """

        loud = kwargs.get('loud', False)
        print(self.robots)
        for robot_ in self.robots:
            print(robot_)
            for item in items:
                print(item)
                robot_.add_subscription(item, loud=loud)

    def listen(self, max_workers=5):
        """

        Update subscriptions configured in `watch` function

        :param robots:
        :return:

        """

        unique_id = uuid.uuid4()

        # Assign robots to groups, then assign each group to a worker.

        actual_workers = min(len(self.robots), max_workers)
        work_group = [self.robots[x:x + math.ceil(len(self.robots) / actual_workers)] for x in
                      range(0, len(self.robots), math.ceil(len(self.robots) / actual_workers))]

        for group in work_group:
            print("GROUP: ", group)
            robot_group = panopticon.Robots()
            robot_group.load(group)
            client_worker = panopticon.ClientWorker(self.context, robots=robot_group)
            self.workers[id(client_worker)] = client_worker


    def learn(self):
        table = None
        table_name = None
        for worker in self.workers.values():
            worker.start()
        ventilator = panopticon.ClientVentilator(self.robots)
        # todo: write functions to interface with pymongo client
        #mongod = robot.ClientMongoConnection(table, table_name)


    def start(self):

        while True:
            # Loop and accept messages from both channels, acting accordingly
            while True:
                socks = dict(self.poller.poll())
                # If the message came from work_receiver channel, square the number
                # and send the answer to the results reporter

                if socks.get(self.control_receiver) == zmq.POLLIN:
                    control_message = self.control_receiver.recv()
                    if control_message == "FINISHED":
                        # todo: implement proper cleanup of client worker
                        break

# todo: write a sig-int for this to clean up the process nicely.
