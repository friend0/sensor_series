import multiprocessing
from threading import Thread
import time

class RobotUpdateWorker(Thread):

    def __init__(self, robots, sampling_rate):
        super(RobotUpdateWorker, self).__init__()
        self.daemon = True
        #self.queue = queue
        self.sampling_rate = sampling_rate

    def run(self):

        #for robot in iter(self.queue.get, None):
        while True:
            for robot in self.robots:
                result = robot.client.polled_subscription()
                print(result)

