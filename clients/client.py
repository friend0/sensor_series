# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

class BaseClient(metaclass=ABCMeta):

    @abstractmethod
    def browse(self):
        pass
    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def subscribe(self, polled=False):
        pass
