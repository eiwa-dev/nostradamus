"""Document-database to object interface.
This is NOT an ODM.
"""

from abc import ABC, abstractmethod, ABCMeta
import collections
import uuid
import functools

__author__ = [  "Juan Carrano <jc@eiwa.ag>",
                "Federico M. Pomar <fp@eiwa.ag>"
             ]
__copyright__ = "Copyright 2016 EIWA S.A. All rights reserved."
__license__ = """Unauthorized copying of this file, via any medium is
                 strictly prohibited. Proprietary and confidential"""

class WithListMeta(ABCMeta):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        class _ElementList(self._ElementListBase):
            ELEMENT_CLASS = self
        self.List = _ElementList

class RefList(collections.UserList):
    LIST_KEY = 'contents'

    @property
    @abstractmethod
    def ELEMENT_CLASS(self):
        pass

    @classmethod
    def from_dict(cls, d, read_func = None, **kwargs):
        contents_d = d[cls.LIST_KEY]

        contents = [cls.ELEMENT_CLASS.from_ref(element_d, read_func)
                    for element_d in contents_d]

        return cls(contents, **kwargs)

    def as_dict(self, write_func):
        contents_d = [element.as_ref(write_func) for element in self]

        return {self.LIST_KEY: contents_d}

class List(collections.UserList):
    LIST_KEY = 'contents'

    @property
    @abstractmethod
    def ELEMENT_CLASS(self):
        pass

    @classmethod
    def from_dict(cls, d, read_func = None, **kwargs):
        contents_d = d[cls.LIST_KEY]

        contents = [cls.ELEMENT_CLASS.from_dict(element_d, read_func)
                    for element_d in contents_d]

        return cls(contents, **kwargs)

    def as_dict(self, write_func):
        contents_d = [element.as_dict(write_func=write_func) for element in self]

        return {self.LIST_KEY: contents_d}

class Serializable(metaclass=WithListMeta):
    """Base class for objects which can be read and written to and from
    a dict."""

    _ElementListBase = List

    @classmethod
    @abstractmethod
    def from_dict(cls, d, read_func = None, **kwargs):
        """Create a object from a dictionary.

        You probably don't want to use read_func directly, but rather pass it
        to from_ref.

        d: dictionary containing only base items.
        read_func: callable that takes (class, name) and returns the corresponding
                    object.
        """
        pass

    @abstractmethod
    def as_dict(self, write_func = None):
        """Create a dictionary from an object.
        :return:
        """
        pass

Serializable.register(RefList)
Serializable.register(List)

class Referenceable(Serializable):
    """Base class for objects which are not contained inside other objects, but
    instead can be referred to by name. Each name must be unique within each section.
    A blank name will cause the "name" property to be auto-assigned a (hopefully)
    unique name.

    Thanks to metaclass voodoo, all subclasses of Referenceable have a 'RefList' class
    attribute that contains a class dervived from RefList. This class can be used to
    build lists of references.

    Notes:
        from_dict must not take any kwargs, as deserialization of an independent object
            cannot depend on the context.
        from_dict must take the objects name as an argument following read_func.
    """
    _ElementListBase = RefList

    def __init__(self, name = None, **kwargs):
        self.name = name or self.generate_name()
        super().__init__(**kwargs)

    @property
    @abstractmethod
    def SECTION(self):
        pass

    @classmethod
    def from_ref(cls, d, read_func):
        """Lookup the object using read_func and the name specified in d."""
        return read_func((cls, d['target_name']))

    def as_ref(self, write_func):
        """Dump the object with write_func and return a dictionary representing the
        reference."""
        write_func(self)
        return {'_IS_REFERENCE': True,
                'target_name': self.name}

    @classmethod
    def generate_name(cls):
        return "{}-{}".format(cls.__name__, uuid.uuid1())


class ConsistencyError(Exception):
    """Raised whenever one tries to serialize two different objects with
    the same name."""
    pass

class ParseError(Exception):
    pass

class ObjectNotFound(Exception):
    #TODO: Use this.
    pass

class Database:
    def __init__(self, driver):
        self._driver = driver

    def _write(self, obj, write_cache, follow_refs=True):
        if (obj.SECTION, obj.name) not in write_cache:
            write_func = self._write if follow_refs else (lambda *args, **kwargs: None)
            d = obj.as_dict(functools.partial(write_func, write_cache = write_cache))
            write_cache[(obj.SECTION, obj.name)] = (obj, d)
        else:
            c_obj, c_d = write_cache[(obj.SECTION, obj.name)]
            if c_obj != obj:
                raise ConsistencyError("Tried to serialize different objects with the same name")

    def write(self, obj, write_cache = None, follow_refs=True):
        """Write an object and all directly or indirectly referenced objects.
        Consistency (one name corresponds to only one object) is checked before
        committing to the database.
        Note that consistency is not checked across multiple calls to write().
        In this respect, calling write() multiple times on the same Database instance
        is the same as calling write on different instances tied to the same backend.
        If you want to write multiple object in one operation, use write_many.
        If you do not want to write referenced objects, set follow_refs=False. Use with caution.
        """

        if write_cache is None:
            write_cache = {}

        self._write(obj, write_cache, follow_refs=follow_refs)
        self._driver.update((key, d) for key, (obj, d) in write_cache.items())

    def read(self, cls_name, read_cache = None):
        """Read an object from a section. Multiple read() calls will yield different
        objects for the same name. If you want to read many objects and get the same
        database object mapped to the same python object, use read_many().
        """
        cls, name = cls_name

        if read_cache is None:
            read_cache = {}

        if (cls, name) not in read_cache:
            d = self._driver.getitem((cls.SECTION, name))
            read_cache[(cls, name)] = cls.from_dict(d,
                                        functools.partial(self.read, read_cache = read_cache),
                                        name = name)

        return read_cache[(cls, name)]

    def read_many(self, cls_names):
        """
            :param section_names: Iterable yielding (section, name)
        """
        read_cache = {}
        return (self.read(cls_name, read_cache = read_cache)
                    for cls_name in cls_names)

    def write_many(self, objs):
        write_cache = {}

        for obj in objs:
            self._write(obj, write_cache = write_cache)

        self._driver.update((key, d) for key, (obj, d) in write_cache.items())

    def query_names(self, cls, query=None):
        return self._driver.query_names(cls.SECTION, query)
        
