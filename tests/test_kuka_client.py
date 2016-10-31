import sys
sys.path = [ "src" ] + sys.path

from panopticon import panopticon

panopticon.robot.Robot()

panopticon.watch()
panopticon.listen()
panopticon.learn()

"""
def test_client_api():
    assert isinstance(KukaClient(), BaseClient)

def test_client_read():
    client = KukaClient()
    result = client.read('TipDressCounter')
    #todo: come up with a better assertion
    assert type(result) == int

def test_client_status():
    client = KukaClient()
    result = client.status()
    # todo: come up with better assertion
    assert True

def test_client_properties():
    client = KukaClient()
    result = client.get_properties()
    # todo: come up with better assertion
    assert True
"""
