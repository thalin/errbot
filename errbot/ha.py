import logging
import threading
from abc import abstractmethod, ABCMeta
from uuid import uuid4

import etcd

log = logging.getLogger(__name__)

class HAInstance(metaclass=ABCMeta):
    """
    Contract for the controlled instance.

    The instance can be in 3 states:
    - loaded: only once, you have loaded/precached anything you could but you do not connect to dependent systems etc.
    - passive: be ready to switch to active at any moment. For example: connected to dependent systems but not acting.
    - active: answering requests etc. ready to be switched back to passive.

    Lifecycle:
    1. build HA, call start and wait to be called back on switch_to_loaded
    2.

    """
    def __init__(self):
        self._lock = None

    @abstractmethod
    def switch_to_loaded(self):
        pass

    @abstractmethod
    def switch_to_passivated(self):
        pass

    @abstractmethod
    def switch_to_actived(self):
        pass

    def load(self):
        self._lock = threading.Lock()
        with self._lock:
            self.switch_to_loaded()

    def passivate(self):
        with self._lock:
            self.switch_to_passivated()

    def activate(self):
        with self._lock:
            self.switch_to_activated()


class HA(object):
    """
    Implements the 1 master multiple-slave logic backed by etcd.
    """
    def __init__(self,
                 instance: HAInstance,
                 instance_uid: str=None,
                 etcd_address: str='http://localhost:2380',
                 ttl: int=2):
        self._client = etcd.Client(etcd_address)
        self._instance = instance
        self._uid = instance_uid if instance_uid else uuid4()
        self._thread = None
        self._ttl = ttl

    def start(self):
        """
        After this call, instance will be callbacked asynchronously on switch_to_loaded()
        """
        self._thread = threading.Thread(name='HA Thread', target=self._run)
        self._thread.start()

    def _run(self):
        self._instance.load()
        self._instance.passivate()
        while True:
            etcd_response = self._client.write('/errbot/master', self._uid, prevExist=False, ttl=self._ttl)
            if etcd_response.value == self._uid:
                self._instance.switch_to_actived()



        ### HA logic

