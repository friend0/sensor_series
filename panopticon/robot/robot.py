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

@attr.s
class Robots(collections.MutableMapping):
    """

    All instances of the class robot will share the same state, and robots are only initialized
    on first call to Robots().

    """

    robots = attr.ib(default=attr.Factory(dict))
    group = attr.ib(default=None)

    def load(self, robot_list):
        for robot in robot_list:
            self.robots[robot.hostname] = robot

    def __getitem__(self, key):
        return self.robots[key]

    def __setitem__(self, key, value):
        self.robots[key] = value
        if value.make:
            pass
        if value.line:
            pass
        #self.dbroot._p_changed = True

    def __delitem__(self, key):
        del self.robots[key]
        #self.dbroot._p_changed = True

    def __iter__(self):
        return iter(self.robots)

    def __len__(self):
        return len(self.robots.items())

    def __repr__(self):
        str = ''
        for key, val in self.items():
            str = str + key + '\n'
            for hostname, robot in val.items():
                str = str + hostname + '\t' + repr(robot) + '\n'
        return str
        #return json.dumps(self.robots['all'].values())

def client_init(instance, attribute, value):
    # todo: make this less hard coded, i.e. just use input args fo rthis validator to init client.
    print("HOSTNAME", instance.hostname, instance.ip)
    instance.client = kuka_client.KukaClient(hostname=instance.hostname, ip=instance.ip)

@attr.s
class Robot():

    hostname = attr.ib(default = None)
    ip = attr.ib(default='127.0.0.1', validator=valid_ip_address)
    line = attr.ib(default = None)
    cell = attr.ib(default = None)
    short_name = attr.ib(default = None)
    make = attr.ib(default=None)
    client = attr.ib(default=None, validator= client_init)
    items = attr.ib(default=attr.Factory(list))
    __server_sub_handles = attr.ib(default=attr.Factory(dict))

    def add_subscription(self, item, **kwargs):
        """

        :param item:
        :param kwargs:
        :return:

        """

        # todo: should have better management of subscriptions than this
        if item not in self.items:
            self.items.append(item)
        response, handle = self.client.subscribe(item, **kwargs)
        self.__server_sub_handles[item] = handle

    def subscription_refresh(self):

        # Get refresh results from the client, then add the hostname to the response dictionary
        returner = self.client.subscription_refresh()
        returner['hostname'] = self.hostname
        return returner

if __name__ == '__main__':
    bpl = Robot(hostname='BIW1-BPL010RB1', ip='172.16.22.101')
    bpg = Robot(hostname='BIW1-BPG010RB1', ip='172.16.22.101')
    bpr = Robot(hostname='BIW1-BPR010RB1', ip='172.16.22.101')

    robots = Robots(group='Group1')
    robots[bpl.hostname] = bpl
    robots[bpg.hostname] = bpg
    robots[bpr.hostname] = bpg
