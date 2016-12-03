from panopticon.robot.robot_mongo import RobotMongo
from panopticon.mongo_documents import ValueSegment, Series
import pymongo
import pytest


@pytest.fixture(scope="module")
def robot_mongo():
    return RobotMongo(host='127.0.0.1')

def test_setup(robot_mongo):
    mongo_client = robot_mongo.client
    mongo_client.test_robots.kuka_robots.drop()
    mongo_client.time_series_set.kuka_robots.drop()
    mongo_client.value_segments_db.kuka_robots.drop()


def test_create_test_db(robot_mongo):
    mongo_client = robot_mongo.client

    test_robots = mongo_client['test_robots']
    test_robots.kuka_robots.insert_one(
        {
            "hostname": "BIW1-BPL010RB1",
            "items": ['var1', 'var2', 'var3', 'var4', 'var5', 'var6', 'var7','var8', 'var9', 'var10'],
            "opc": True,
        }
    )

    test_robots.kuka_robots.insert_one(
        {
            "hostname": "BIW1-BPO010RB1",
            "items": ['var1', 'var2', 'var3', 'var4', 'var5', 'var6', 'var7','var8', 'var9', 'var10'],
            "opc": True,
        }
    )
    databases = mongo_client.database_names()
    assert 'test_robots' in set(databases)

"""
"""

def test_create_time_series(robot_mongo):
    import uuid

    mongo_client = robot_mongo.client
    opc_robots = [robot for robot in mongo_client['test_robots']['kuka_robots'].find({'opc': True})]
    time_series_set = mongo_client['time_series_set']
    value_segments = mongo_client['value_segments_db']

    robot_mongo.instantiate_series()


def test_get_opc_robots(robot_mongo):
    # todo: compare length of returned list against a known value
    opc_robots = robot_mongo.get_opc_robots()
    assert opc_robots

def test_instantiate_time_series(robot_mongo):
    robot_mongo.instantiate_series()

def test_get_all_time_series(robot_mongo):
    all_time_series = robot_mongo.get_series('BIW1-BPO010RB1')
    assert all_time_series

def test_get_particular_time_series(robot_mongo):
    # todo: insert a test robot inro the database, with a known var name.
    particular_time_series = robot_mongo.get_series('BIW1-BPO010RB1', 'var1')
    print(particular_time_series)
    assert particular_time_series['robot_id'] == 'BIW1-BPO010RB1'



def test_update_time_series_non_cached(robot_mongo):
    import random
    import time
    # todo: simulate receiving random (first periodic) requests from the OPC client

    # todo: upon receipt of periodic work from OPC, update the server as soon as requests come in
    mongo_client = robot_mongo.client
    time_series_set = mongo_client['time_series_set']
    value_db = mongo_client['value_segments_db']

    time_series_set.kuka_robots.create_index([("_id", pymongo.DESCENDING)])
    value_db.kuka_robots.create_index("_id")
    r = [random.random() for i in range(1, 1000)]
    s = sum(r)
    r = [i / s for i in r]

    start_time = time.time()
    for time_period in r:
        time.sleep(time_period)
        robot_mongo.update_time_series(robot_hostname='BIW1-BPO010RB1', items_values={'var1':10})
    print('run_time: ', time.time()-start_time)

def test_update_time_series_cached(robot_mongo):
    """

    Simulated work requests frmo an OPC client are piped to a loop which services these requests as soon as they come in.
    That is, they call a direct update request to the MongoClient, instead of performing a batch update intermittently.

    :param robot_mongo: The RobotMongo class fixture under test.
    :return: None
    """
    import random
    import time
    # todo: simulate receiving random (first periodic) requests from the OPC client

    # todo: upon receipt of periodic work from OPC, update the server as soon as requests come in
    mongo_client = robot_mongo.client
    time_series_set = mongo_client['time_series_set']
    value_db = mongo_client['value_segments_db']

    time_series_set.kuka_robots.create_index([("_id", pymongo.DESCENDING)])
    value_db.kuka_robots.create_index("_id")
    r = [random.random() for i in range(1, 1000)]
    s = sum(r)
    r = [i / s for i in r]

    for time_period in r:
        time.sleep(time_period)
        robot_mongo.cached_update_time_series(robot_hostname='BIW1-BPO010RB1', items_values={'var1':10})
    start_time = time.time()
    robot_mongo.write_out_update_cache()
    print('run_time: ', time.time()-start_time)

def test_process_start(robot_mongo):
    import multiprocessing
    assert True

def test_zmq_poller(robot_mongo):
    assert True

"""
def test_get_last_value(robot_mongo):
    # todo: insert test robot into database, with known var name, last value.
    last_value = robot_mongo.get_last_value('BIW1-BPO010RB1', 'var1')
    assert last_value == 10
"""