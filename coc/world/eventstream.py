from coc import Immutable
from coc.exceptions import LoadError, ObjectNotFoundError, SchemaError
from coc.world.event import Event

eventstream_registry = dict()


class EventStream(Immutable):
    """ Represents a narrative sequence, including conditional components and
    usually terminating at a conditional branch, a fight, or a decision menu.
    """
    def __init__(self, schema):
        super().__init__()
        self.id_ = schema['id']
        try:
            self.events = [
                    Event.construct(item, self) for item in schema['events']
            ]
        except KeyError as e:
            raise SchemaError("encountered an unknown event type ``{0}`` "
                              "while attempting to load event ``{1}``"
                              .format(e.args[0], schema['id']))
        global eventstream_registry
        if schema['id'] in eventstream_registry:
            raise LoadError("attempted to load event_stream ``{0}`` but that "
                            "event id already exists".format(schema['id']))
        self.initialized = True
        eventstream_registry[self.id_] = self

    def get_id(self):
        return self.id_

    def run(self, state_func):
        for item in self.events:
            if item.check_condition(state_func):
                yield item

    def __repr__(self):
        return repr({
            'id': self.id_,
            'events': [
                dict(item) for item in self.events
            ]
        })


def get_all_eventstreams():
    return eventstream_registry.values()


def get_eventstream_by_id(id_):
    try:
        return eventstream_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("event ``" + id_ +
                                  "`` was not found in the event registry"
                                  ) from e


def is_eventstream_loaded(id_):
    return id_ in eventstream_registry


