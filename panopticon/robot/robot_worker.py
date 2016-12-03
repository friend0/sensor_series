import time
from threading import Thread, Timer
import msgpack
import zmq


class RobotVentilator:
    """

    The RobotVentilator class is used to coordinate the update cycles for many RobotWorkers.
    The ventilator works by broadcasting packets to the workers at the given interval.
    When the RobotWorkers receive the ventilator packet, they begin their refresh cycles.

    Planned functionality:
    - Implement scalable phase-sync for many robots.
        - Use many timers?
        - Use a single timer with an array for indicating how far apart pulses should be spaced
        - Store update intervals at the Robot level, to be read by the worker threads
    """

    def __init__(self, context, robots, interval=3, *args, **kwargs):
        self.context = context
        self._timer = None
        self.interval = interval
        self.args = args
        self.kwargs = kwargs
        self.is_running = False

        self.robots = robots
        # Set up a channel to generate work
        self.ventilator_pipe = self.context.socket(zmq.PUSH)
        self.ventilator_pipe.bind("tcp://127.0.0.1:5557")

        # Phase sync
        phases = kwargs.get('phases', None)
        # Let the system wind up
        time.sleep(1)
        self.start()
        self.client_workers = {}

    def __ventilate(self, *args, **kwargs):
        self.is_running = False
        self.start()
        self.ventilator_pipe.send(msgpack.packb('1'))

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self.__ventilate)
            self._timer.daemon = True
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False


class RobotWorker(Thread):
    """

    The RobotWorker thread is used to execute OPC subscription updates for the set of Robots contained by the 'robots'
    attribute.

    """

    def __init__(self, context, robots, **kwargs):
        """

        Given a zmq context from the parent process, and a list of Robots(), the RobotWorker thread
        will poll for cues from its assigned RobotVentilator. When the ventilator broadcasts, each worker under
        its employ will execute a subscription update sequence.

        :param context:
        :param robots:
        :param kwargs:

        """
        super(RobotWorker, self).__init__(daemon=True)
        self.robots = robots
        self.sampling_rate = kwargs.get('sampling_rate', .5)
        # todo: figure out a better default when we don't get id (UUID?)
        self.id = kwargs.get('id', None)
        # todo: test again after conversion to using the context arg.
        self.context = zmq.Context()
        # Initialize channels
        self.work_receiver = self.context.socket(zmq.PULL)
        self.results_sender = self.context.socket(zmq.PUSH)
        self.control_receiver = self.context.socket(zmq.SUB)
        self.poller = zmq.Poller()
        # Setup channels
        self.work_receiver.connect("tcp://127.0.0.1:5557")
        self.results_sender.connect("tcp://127.0.0.1:5558")
        self.control_receiver.connect("tcp://127.0.0.1:5559")
        time.sleep(1)

    def run(self):
        """

        The main function for this thread - polls all registered channels for work cues from the ventilator.
        When a new cue is received, each Robot manages by this thread will be instructed to update refresh (poll)
        its subsctiptions.

        Communication with the ventilator is routed through the 'work_receiver' PULL socket.
        After each Robot has returned a response from the update request, a multipart messages is minted.
        This messages contains:
            - The requested operation.
            - The Robot's hostname.
            - The Response() dict returned from the client.

        :return: None

        """

        self.control_receiver.setsockopt_string(zmq.SUBSCRIBE, "")
        self.poller.register(self.work_receiver, zmq.POLLIN)
        self.poller.register(self.control_receiver, zmq.POLLIN)

        # Loop and accept messages from both channels, acting accordingly
        while True:
            socks = dict(self.poller.poll())

            # If the message came from the ventilator
            if socks.get(self.work_receiver) == zmq.POLLIN:
                consume = msgpack.unpackb(self.work_receiver.recv())
                for host, robot in self.robots.items():
                    returner = robot.subscription_refresh()

                    # self.results_sender.send_multipart([msgpack.packb('update'), msgpack.packb(robot.hostname), msgpack.packb(returner)])
                    self.results_sender.send(msgpack.packb(returner, use_bin_type=True))

                    # todo: start debugging here. Let's see if we can funnel results to the sink.

                    # todo: act on the value returned from the client, update db if applicable

            # If the message came over the control channel, shut down the worker.
            if socks.get(self.control_receiver) == zmq.POLLIN:
                control_message = msgpack.unpackb(self.control_receiver.recv())
                if control_message == "POISON_PILL":
                    # todo: implement proper cleanup of client worker
                    break
