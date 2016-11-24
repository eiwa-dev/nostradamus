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

    def query_names(self, query_section_name, query=None):
        section = self.d.setdefault(query_section_name, {})
        return [name for name, obj in section.items()
                        if self._dict_match(obj, query)]

    @staticmethod
    def _dict_match(obj, query=None):
        query = {} if query is None else query
        for k, v in query.items():
            k_fields = k.split('.')
            o_value = obj
            for field in k_fields:
                try:
                    o_value = o_value[field]
                except KeyError:
                    return False
            if o_value != v:
                return False
        return True

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

    def query_names(self, cls, query=None):
        return set([name for driver in self.drivers
                             for name in driver.query_names(cls, query)])
