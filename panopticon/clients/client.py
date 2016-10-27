# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class BaseClient(metaclass=ABCMeta):

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def browse(self, item_name=None):
        pass

    @abstractmethod
    def read(self, item_name):
        pass

    @abstractmethod
    def subscribe(self, item_name, server_handle):
        pass
