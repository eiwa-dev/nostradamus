"""Dictionary driver with a yaml backend"""

import yaml

from .base import UriDriver
from .built_in import DictionaryDriver

import hashlib

__author__ = [  "Juan Carrano <jc@eiwa.ag>",
                "Federico M. Pomar <fp@eiwa.ag>"
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""


class YAMLDriver(UriDriver):
    URI_SCHEMES = ['file']

    def __init__(self, file_obj = None, filename = None):
        if file_obj is not None:
            self._file = file_obj
        else:
            try:
                self._file = open(filename, 'r+')
            except FileNotFoundError:
                self._file = open(filename, 'w+')

        self._prev_file_checksum = None
        self._reload()

    @classmethod
    def from_uri(cls, uri):
        return cls(filename = uri.path)

    def close(self):
        self._file.close()

    def _file_checksum(self):
        hash_md5 = hashlib.md5()
        self._file.seek(0)
        for chunk in iter(lambda: self._file.buffer.read(4096), b""):
            hash_md5.update(chunk)
        return hash_md5.hexdigest() 

    def _reload(self):
        file_checksum = self._file_checksum()
        if file_checksum != self._prev_file_checksum:
            self._file.seek(0)
            d = yaml.safe_load(self._file)
            self._dictd = DictionaryDriver(d)
            self._prev_file_checksum = file_checksum
            print('reloaded')

    def _dump(self):
        s = yaml.safe_dump(self._dictd.d)
        # truncate the file only after the dump succeeded
        self._file.seek(0)
        self._file.truncate(0)
        self._file.write(s)
        print('dumped')

    def getitem(self, k):
        self._reload()
        return self._dictd.getitem(k)

    def setitem(self, k, v):
        self._reload()
        self._dictd.setitem(k, v)
        self._dump()

    def update(self, items):
        self._reload()
        self._dictd.update(items)
        self._dump()

    def query_names(self, section, query=None):
        self._reload()
        return self._dictd.query_names(section, query)
