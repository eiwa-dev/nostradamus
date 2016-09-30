from . import Driver
from pymongo import MongoClient

class MongoDriver(Driver):
    @classmethod
    def from_uri(cls, uri, db_name):
        return cls(MongoClient(uri)[db_name])

    def __init__(self, db):
        self.db = db

    def getitem(self, k):
        section, name = k
        item = dict(self.db[section].find_one({'__ref_name__': name}))
        del item['__ref_name__']
        if item is None:
            raise KeyError(k)
        return item
    
    def setitem(self, k, v):
        section, name = k
        item = dict(v)
        item['__ref_name__'] = name
        self.db[section].replace_one({'__ref_name__': name}, item, upsert=True)
