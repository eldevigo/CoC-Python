import os
from abc import ABC

class COCClass(ABC):
    """ Common base class for all CoC module classes
    """

class Immutable(COCClass):
    """ Common base class for CoC subclasses that have properties which are
    immutable after being initialized (i.e. most of them)
    """
    def __setitem__(self, key, value):
        if self.initialized and key not in self.mutable:
            raise ImmutablePropertyError(self.__class__.__name__, key)
        else:
            super().__setitem__(self, key, value)

from coc.session import Session
