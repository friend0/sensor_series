import multiprocessing
import zmq
import time

class WorkSender(multiprocessing.Process):

    def __init__(self):
        super(WorkSender, self).__init__()

    def run(self):
        self.context = zmq.Context.instance()
        self.sender = self.context.socket(zmq.PUSH)
        self.sender.bind("tcp://127.0.0.1:5558")
        time.sleep(1)
        for i in range(100):
            self.sender.send_json({'msg':'content'})

class WorkReceiver(multiprocessing.Process):
    def __init__(self):
        super(WorkReceiver, self).__init__()


    def run(self):
        self.context = zmq.Context.instance()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect("tcp://127.0.0.1:5558")
        time.sleep(1)
        for i in range(100):
            print(self.receiver.recv_json())


if __name__ == '__main__':
    processes = [WorkSender(), WorkReceiver()]
    time.sleep(1)
    for p in processes:
        print(p)
        p.start()
    for p in processes:
        p.join()