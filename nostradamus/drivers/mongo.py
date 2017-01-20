"""MongoDB backend"""

import posixpath

from pymongo import MongoClient

from .base import UriDriver

__author__ = [  "Juan Carrano <jc@eiwa.ag>",
                "Federico M. Pomar <fp@eiwa.ag>"
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""

class MongoDriver(UriDriver):
    URI_SCHEMES = ["mongodb"]

    @classmethod
    def from_uri(cls, uri):
        if not posixpath.basename(uri.path):
            raise ValueError("The connection uri must specify the database name")

        dbname = uri.path[1:]

        return cls(MongoClient(uri.geturl())[dbname])

    def __init__(self, db):
        self.db = db

    def __repr__(self):
        return "{}({!r})".format(type(self).__name__, self.db)

    def getitem(self, k):
        section, name = k
        fetch = self.db[section].find_one({'__ref_name__': name})
        if fetch is None:
            raise KeyError(k)
        item = dict(fetch)
        del item['__ref_name__']
        del item['_id']
        return item

    def setitem(self, k, v):
        section, name = k
        item = dict(v)
        item['__ref_name__'] = name
        self.db[section].replace_one({'__ref_name__': name}, item, upsert=True)

    def query_names(self, section, query=None):
        cursor = self.db[section].find(filter=query, projection=['__ref_name__'])
        return (obj['__ref_name__'] for obj in cursor)

    def query_elements(self, section, projection, query=None):
        cursor = self.db[section].find(filter=query, projection=projection)
        return cursor

