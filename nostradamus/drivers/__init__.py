from abc import ABC, abstractmethod

class Driver(ABC):
    @abstractmethod
    def getitem(self, k):
        pass

    @abstractmethod
    def setitem(self, k, v):
        pass

    def update(self, items):
        for k, v in items:
            self.setitem(k, v)

class ChainDriver(Driver):
    def __init__(self, drivers):
        self.drivers = drivers

    def getitem(self, k):
        for driver in self.drivers:
            try:
                return driver.getitem(k)
            except KeyError:
                pass
        raise KeyError(k)

    def setitem(self, k, v):
        self.drivers[0].setitem(k, v)

    def update(self, items):
        self.drivers[0].update(items)
