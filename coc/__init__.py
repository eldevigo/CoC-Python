from coc.exceptions import ImmutablePropertyError
from abc import ABC


class COCClass(ABC):
    """ Common base class for all CoC module classes
    """


class Immutable(COCClass):
    """ Common base class for CoC subclasses that have properties which are
    immutable after being initialized (i.e. most of them)
    """
    def __init__(self):
        self.initialized = False
        self.mutable = []
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
    def __init__(self):
        super().__init__()
        self._events_loaded = False

    def load_events(self):
        if not self._events_loaded:
            self._events_loaded = True
            return self.event_path
        return False
