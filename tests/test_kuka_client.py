import pytest
import mock
from clients.kuka_client import KukaClient
from clients.client import BaseClient

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