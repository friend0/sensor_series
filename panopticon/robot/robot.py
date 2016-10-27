import collections
from ipaddress import AddressValueError, ip_address, IPv4Address, IPv6Address

import attr
import structlog

from panopticon.clients import kuka_client


def valid_ip_address(instance, attribute, value, logger=None):
    if logger is None:
        logger = structlog.get_logger('central_logger')
    potential_address = ip_address(value)
    try:
        if type(ip_address(potential_address)) is IPv4Address or IPv6Address:
            return potential_address
        else:
            return None
    except AddressValueError as e:
        logger.debug("{} is not a valid ip address.".format(potential_address))


class Robots(collections.MutableMapping):
    """

    All instances of the class robot will share the same state, and robots are only initialized
    on first call to Robots().

    """

    robots = attr.ib(default={'BIW1': {}, 'BIW2': {}, 'kuka': {}, 'fanuc': {}, 'all': {}})

    def __getitem__(self, key):
        return self.robots[key]

    def __setitem__(self, key, value):
        self.robots[key] = value
        self.dbroot._p_changed = True

    def __delitem__(self, key):
        del self.robots[key]
        self.dbroot._p_changed = True

    def __iter__(self):
        return iter(self.robots)

    def __len__(self):
        return len(self.robots)

    def __repr__(self):
        str = ''
        for key, val in self.items():
            str = str + key + '\n'
            for hostname, robot in val.items():
                str = str + hostname + '\t' + repr(robot) + '\n'
        return str
        #return json.dumps(self.robots['all'].values())

    def update(self):
        pass

    def run(self):
        pass

@attr.s
class Robot():

    ip = attr.ib(default='127.0.0.1', validator=valid_ip_address)
    line = attr.ib(default = None)
    hostname = attr.ib(default = None)
    cell = attr.ib(default = None)
    short_name = attr.ib(default = None)
    make = attr.ib(default=None)
    client = kuka_client.KukaClient()

