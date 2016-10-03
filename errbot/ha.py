from abc import abstractmethod, ABCMeta

import etcd


class HAInstance(metaclass=ABCMeta):
    """
    Contract for the controlled instance.
    """

    @abstractmethod
    def master(self):
        pass

    @abstractmethod
    def slave(self):
        pass


class HA(object):
    """
    Implements the 1 master multiple-slave logic backed by etcd.
    """
    def __init__(self, etcd_address: str, callback: HAInstance):
        self.client = etcd.Client(etcd_address)
        self.callback = callback