# -*- coding: utf-8 -*-

from clients.client import BaseClient
# from

class FanucClient(BaseClient):

    def __init__(self, robot=None):
        super(FanucClient, self).__init__()
        self.robot = robot

    def status(self):
        pass

    def browse(self, item_name=None):
        pass

    def read(self, item_name):
        pass

    def subscribe(self, item_name, server_handle):
        pass
