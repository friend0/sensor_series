from panopticon.clients import *
import pytest
import xml

@pytest.fixture(scope="module")
def kuka_client():
    return KukaClient(ip='172.16.22.101')

def test_format_wsdl(kuka_client):
    client = kuka_client.client
    assert kuka_client.ip in client.service._binding_options['address']

def test_messages(kuka_client):
    required_services = {'Browse', 'GetStatus', 'SubscriptionCancel', 'Subscribe', 'Read', 'Write', 'GetProperties',
                         'SubscriptionPolledRefresh'}
    required_services_responses = {'BrowseResponse', 'GetStatusResponse', 'SubscriptionCancelResponse',
                                   'SubscribeResponse', 'ReadResponse', 'WriteResponse', 'GetPropertiesResponse',
                                   'SubscriptionPolledRefreshResponse'}
    for key, val in kuka_client.client.wsdl.__dict__['messages'].items():
        assert val.__dict__['parts']['parameters'].element.name in required_services.union(required_services_responses)

