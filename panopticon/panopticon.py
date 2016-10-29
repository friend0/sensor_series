import gritty_soap
#import robot
from . import robot
from . import clients
import time
import uuid

# todo: see if the __all__ tag is working as expected/define what it should do.
__all__ = ['watch', 'listen', 'learn', 'Robot', 'Robots']

NUM_WORKERS = 5

def watch(robots, items, **kwargs):
    """

    Starts subscriptions to the given set of robots, for each of the given items.

    :param robots: Dictionary of robots (would this be better as just some iterable? Or an array?)
    :param items: A list of items for which we want to start a subscription.
    :return: robots, with updated server

    """
    loud = kwargs.get('lous', False)
    for host, robot_ in robots:
        print(host, robot_)
        for item in items:
            print(item)
            robot_.add_subscription(item, loud=loud)

def listen(robots):
    """

    Update subscriptions configured in `watch` function

    :param robots:
    :return:

    """
    # Initialize 'update workers'
    workers = {}
    #for work in range(NUM_WORKERS):
    #for work in range(len(robots)):
    #for robot_ in robots:

    unique_id = uuid.uuid4()

    client_worker = robot.ClientWorker(robots)
    workers[uuid] = client_worker
    workers[robots.group] = client_worker
    for id, worker in workers.items():
        worker.start()

    #bpl.client.status('TipDressCounter')
    # bpl.client.subscribe('TipDressCounter', None)

    # Start update workers

    #while True:
    #    time.sleep(10)
    #    print("Alive")

def learn():
    pass

