# -*- coding: utf-8 -*-

import requests
from clients.client import BaseClient

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
