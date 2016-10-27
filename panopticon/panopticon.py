import gritty_soap
from . import robot
from . import clients
import time

# todo: see if the __all__ tag is working as expected/define what it should do.
__all__ = ['watch', 'listen', 'learn', 'Robot', 'Robots']

def watch():
    pass

def listen():
    # Application will initialize robots (eventually, should pull robots from DB)
    bpl = robot.Robot()
    # Initialize 'update workers'
    updater = clients.ClientWorker(bpl)
    bpl.client.status('TipDressCounter')
    bpl.client.subscribe('TipDressCounter', None)
    # Start update workers
    updater.start()

    while True:
        time.sleep(10)
        print("Alive")

def learn():
    pass

