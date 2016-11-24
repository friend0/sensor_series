from __future__ import print_function
import pytest
import pymongo
from panopticon.mongo_documents import tseries

import time
import itertools
import random
from threading import Timer
import datetime
import pprint
import uuid
import threading


print("HAS_C", pymongo.has_c())

@pytest.fixture(scope="module")
def mongo_client():
    # return pymongo.MongoClient(host='10.0.2.2')
    return pymongo.MongoClient()

def test_setup(mongo_client):
    mongo_client.time_series_set.kuka_robots.drop()
    mongo_client.value_segments_db.kuka_robots.drop()

def test_create_test_db(mongo_client):
    mongo_client.test_robots.kuka_robots.drop()
    db = mongo_client['test_robots']

    db.kuka_robots.insert_one(
        {
            "_id": "BIW1-BPL010RB1",
            "hostname": "BIW1-BPL010RB1",
            "items": ['var', 'otherVar', 'yet_another_var'],
            "opc": True
        }
    )

    db.kuka_robots.insert_one(
        {
            "_id": "BIW1-BPO010RB1",
            "hostname": "BIW1-BPO010RB1",
            "items": ['var', 'otherVar', 'yet_another_var'],
            "opc": True
        }
    )
    databases = mongo_client.database_names()
    assert 'test_robots' in set(databases)


def test_create_time_series(mongo_client):

    time_series_set = mongo_client['time_series_set']
    value_segments = mongo_client['value_segments_db']
    db = mongo_client['test_robots']

    opc_robots = [robot for robot in mongo_client['test_robots']['kuka_robots'].find({'opc': True})]

    for robot in opc_robots:
        for item in robot['items']:

            db.kuka_robots.update_one(
                {'hostname': robot['hostname']},
                {'$set':
                     {"series_set.{}".format(item): tseries.Series(item).encode()}
                 },
                upsert=True
            )

            #value_segments.kuka_robots.update_one(
            #    {'_id': segment_id},
            #    {'$set':
            #         {"segment": value_segment}
            #     },
            #    upsert=True)


    databases = mongo_client.database_names()
    assert 'test_robots' in set(databases)


import threading
from queue import Queue

class Worker(threading.Thread):

    def __init__(self, tasks, mongo_client):
        threading.Thread.__init__(self)

        self.daemon = True
        self.tasks = tasks
        self.client = mongo_client
        self.db = mongo_client['test_robots']

    def update(self, robot, item, value, current_ptr, current_idx):


        self.db.kuka_robots.update_one(
            {'_id': robot},
            {'$set': {'series_set.{}.value_segments.{}.values.{}'.format(item, current_idx, current_ptr): value,
                      'series_set.{}.value_segments.{}.times.{}'.format(item, current_idx,
                                                                        current_ptr): datetime.datetime.now()}}
        )

        if current_ptr <= 0:
            value_segment = tseries.ValueSegment(
                segment_idx=current_idx + 1).encode()

            self.db.kuka_robots.update_one(
                {'_id': robot},
                {'$set': {'series_set.{}.last_time'.format(item): datetime.datetime.now(),
                          'series_set.{}.current_segment_idx'.format(item): current_idx + 1,
                          'series_set.{}.current_segment_ptr'.format(item): 180},
                 '$push': {'series_set.{}.value_segments'.format(item): value_segment}
                 }
            )

    def run(self):
        while True:
            robot, item, val, current_ptr, current_idx = self.tasks.get()
            try: self.update(robot, item, val, current_ptr, current_idx)
            except Exception as e: print(e)
            self.tasks.task_done()



class ThreadPool:
    """Pool of threads consuming tasks from a queue"""

    def __init__(self, num_threads, mongo_client):
        self.tasks = Queue(num_threads)
        self.db = mongo_client['test_robots']
        self.workers = []
        for _ in range(num_threads): self.workers.append(Worker(self.tasks, mongo_client))

    def add_task(self, robot, item, val):
        """Add a task to the queue"""

        robot_series = self.db.kuka_robots.find_one_and_update(
            {'_id': robot},
            {'$inc': {'series_set.{}.current_segment_ptr'.format(item): -1}},
            projection={'_id': False, 'series_set.{}.current_segment_idx'.format(item): True,
             'series_set.{}.current_segment_ptr'.format(item): True},
            return_document=pymongo.ReturnDocument.AFTER

        )

        current_ptr = robot_series['series_set'][item]['current_segment_ptr']
        current_idx = robot_series['series_set'][item]['current_segment_idx']


        self.tasks.put((robot, item, val, current_ptr, current_idx))

    def start(self):
        for worker in self.workers:
            worker.start()

    def wait_completion(self):
        """Wait for completion of all the tasks in the queue"""
        self.tasks.join()

def test_fire_non_periodic_updates(mongo_client):

    import threading
    time_series_set = mongo_client['time_series_set']
    value_db = mongo_client['value_segments_db']
    db = mongo_client['test_robots']

    time_series_set.kuka_robots.create_index([("_id", pymongo.DESCENDING)])
    value_db.kuka_robots.create_index("_id")

    #def write_to_db():
    """
    In the nominal case, writing requires two database updates.

    :return:
    """


    # Using the robots as keys, look up all Series objects
    robots = ['BIW1-BPO010RB1']
    items = ['var']
    #robot_item_cross = ['{}.{}'.format(robot[0], robot[1]) for robot in
    #                    list(itertools.product(robots_to_update, items_to_update))]

    #robot_item_cross = {robot_item:10 for robot_item in robot_item_cross}

    operations = []
    start_time = time.time()

    thread_pool = ThreadPool(30, mongo_client)
    thread_pool.start()

    for idx in range(10000):
        for robot in robots:
            for item in items:
                val = 10
                thread_pool.add_task(robot, item, val)

    thread_pool.wait_completion()

        #value_db.kuka_robots.bulk_write(operations, ordered=True)
    run_time = time.time()-start_time
    print(run_time)

        #timers = []
        #for x in range(1):
        #    random_interval = random.uniform(.15, .25)
        #    # time.sleep(random_interval)
        #    # write_to_db(mongo_client)
        #    timers.append(Timer(random_interval, write_to_db))
        #
        #for timer in timers:
        #    timer.start()
        #for timer in timers:
        #    timer.join()



