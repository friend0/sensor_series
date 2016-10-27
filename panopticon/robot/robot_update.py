import multiprocessing
from threading import Thread
import time
import zmq
import msgpack
import attr

class ClientVentilator():

    def __init__(self, robots):
        context = zmq.Context()

        ventilator_pipe = context.socket(zmq.PUSH)
        ventilator_pipe.bind("tcp://127.0.0.1:5555")

        time.sleep(1)

        for robot in robots:
            ventilator_pipe.send(msgpack.dumps(robot))

@attr.s
class ClientWorker(Thread):

    #def __init__(self, robots, sampling_rate, worker_id):
    context = attr.ib(zmq.Context())
    #self.queue = queue
    sampling_rate = attr.ib(default=.5)

    # Set up a channel to receive work from the ventilator
    work_receiver = attr.ib(context.socket(zmq.PULL))

    # Set up a channel to send result of work to the results reporter
    results_sender = attr.ib(context.socket(zmq.PUSH))

    # Set up a channel to receive control messages over
    control_receiver = attr.ib(context.socket(zmq.SUB))

    # Set up a poller to multiplex the work receiver and control receiver channels
    poller = attr.ib(zmq.Poller())


    def run(self):

        self.daemon = True
        self.work_receiver.connect("tcp://127.0.0.1:5557")
        self.results_sender.connect("tcp://127.0.0.1:5558")
        self.control_receiver.connect("tcp://127.0.0.1:5559")

        self.control_receiver.setsockopt(zmq.SUBSCRIBE, "")
        self.poller.register(self.work_receiver, zmq.POLLIN)
        self.poller.register(self.control_receiver, zmq.POLLIN)

        # Loop and accept messages from both channels, acting accordingly
        while True:
            socks = dict(self.poller.poll())

            # If the message came from work_receiver channel, square the number
            # and send the answer to the results reporter
            if socks.get(self.work_receiver) == zmq.POLLIN:
                work_message = self.work_receiver.recv_json()
                product = work_message['num'] * work_message['num']
                answer_message = { 'worker' : self.worker_id, 'result' : product }
                self.results_sender.send_json(answer_message)

            # If the message came over the control channel, shut down the worker.
            if socks.get(self.control_receiver) == zmq.POLLIN:
                control_message = self.control_receiver.recv()
                if control_message == "FINISHED":
                    print("Worker %i received FINSHED, quitting!" % self.worker_id)
                    break

    def run(self):

        #for robot in iter(self.queue.get, None):
        while True:
            for robot in self.robots:
                result = robot.client.polled_subscription()
                print(result)

class ClientMongoConnection():
    # Initialize a zeromq context
    context = zmq.Context()

    # Set up a channel to receive results
    results_receiver = context.socket(zmq.PULL)
    results_receiver.bind("tcp://127.0.0.1:5558")

    # Set up a channel to send control commands
    control_sender = context.socket(zmq.PUB)
    control_sender.bind("tcp://127.0.0.1:5559")

    for task_nbr in range(10000):
        result_message = results_receiver.recv_json()


    # Signal to all workers that we are finsihed
    control_sender.send("FINISHED")
    time.sleep(5)
