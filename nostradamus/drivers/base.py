"""Base classes for all database drivers"""

from collections.abc import Iterable
from abc import ABCMeta, ABC, abstractmethod

from urllib.parse import urlparse

__author__ = [  "Juan Carrano <jc@eiwa.ag>",
                "Federico M. Pomar <fp@eiwa.ag>"
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""

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

class UriMeta(ABCMeta):
    """Metaclass for drivers that can be created from an uri. This
    metaclass takes care of registering the driver with
    register_driver_scheme so there is no need to apply the decorator.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.URI_SCHEMES, Iterable):
            for scheme in self.URI_SCHEMES:
                register_driver_scheme(scheme)(self)

class UriDriver(Driver, metaclass = UriMeta):
    """Base class for drivers that can be created from an uri"""

    @property
    @abstractmethod
    def URI_SCHEMES(self):
        """List of URI schemes supported by this driver."""
        pass

    @classmethod
    @abstractmethod
    def from_uri(cls, uri):
        """Create a instance from a uri. URI is not a string, but a
        urllib.parse.ParseResult object.
        """
        pass

REGISTERED_DRIVERS = {}

def register_driver_scheme(uri_scheme):
    """If you decorate your Driver-derived class with this function, it
    will be possible to create instances of that driver using new_driver

    Note that if your driver derives from UriDriver, then it is NOT
    necessary to use this decorator as the metaclass takes care.
    """

    def _f(cls):
        REGISTERED_DRIVERS[uri_scheme] = cls
        return cls

    return _f

def new_driver(uri_txt, default_scheme = ''):
    """Create a driver from a uri. default_scheme is used as the
    `scheme` parameter for urllib.parse.urlparse.

    To see the drivers that can be created with this function use the
    module-global variable `REGISTERED_DRIVERS`
    """
    uri = urlparse(uri_txt)

    cls = REGISTERED_DRIVERS[uri.scheme]

    return cls.from_uri(uri)
