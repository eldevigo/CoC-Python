from abc import ABC
from copy import deepcopy

from coc.exceptions import ImmutablePropertyError, SchemaError


class COCClass(ABC):
    """ Common base class for all CoC module classes
    """


class Immutable(COCClass):
    """ Common base class for CoC subclasses that have properties which are
    immutable after being initialized (i.e. most of them)
    """
    def __init__(self):
        self.initialized = False
        self.mutable = list()
        super().__setattr__('initialized', False)
        self.immutable = list()

    def __setattr__(self, key, value):
        try:
            if self.initialized and key not in self.mutable:
                raise ImmutablePropertyError(self.__class__.__name__, key)
            else:
                super().__setattr__(key, value)
        except AttributeError:
            super().__setattr__(key, value)


class EventContext(Immutable):
    """ Common base class for world objects that have events associated with
    them. Used mainly to handle event loading.
    """
    def __init__(self, schema):
        super().__init__()
        self.state = {}
        try:
            self.id_ = schema['id']
        except KeyError:
            raise SchemaError("{0} schema missing required field ``id``"
                              .format(type(self)), schema=schema)
        try:
            self.name = schema['name']
        except KeyError:
            raise SchemaError("{0} schema missing required field ``name``"
                              .format(type(self)), schema=schema)

    def get_state_template(self):
        return deepcopy(self.state)
