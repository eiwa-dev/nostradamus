"""This drivers use only built in objects"""

from urllib.parse import unquote

from .base import Driver, UriDriver, new_driver

__author__ = [  "Juan Carrano <jc@eiwa.ag>",
                "Federico M. Pomar <fp@eiwa.ag>"
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""

class DictionaryDriver(Driver):
    def __init__(self, dictionary=None):
        dictionary = dictionary or {}
        self.d = dict(dictionary)

    def getitem(self, k):
        section_name, name = k
        section = self.d.setdefault(section_name, {})
        return section[name]

    def setitem(self, k, v):
        section_name, name = k
        section = self.d.setdefault(section_name, {})
        section[name] = v

class ChainDriver(UriDriver):
    URI_SCHEMES = ['chain']

    def __init__(self, drivers):
        self.drivers = drivers

    @classmethod
    def from_uri(cls, uri):
        sub_driver_uris = [unquote(s) for s in uri.path.split("/") if s]

        sub_drivers = [new_driver(u) for u in sub_driver_uris]

        return cls(sub_drivers)

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.drivers)

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

