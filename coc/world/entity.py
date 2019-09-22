from coc import EventContext
from coc.exceptions import *

entity_registry = dict()


class Entity(EventContext):
    """ Common base class for all interactable entities in the world (monsters,
    npcs, etc.)
    """
    def __init__(self, schema):
        super().__init__()
        state_defaults = {
                'counters': 0,
                'flags': False
                }
        self.state = dict()
        try:
            self.id = schema['id']
            self.name = schema['name']
            self.state['encounter_event_id'] = \
                schema['state']['encounter_event']
        except KeyError as e:
            raise SchemaError("entity schema missing required field ``{0}``"
                              .format(e.args[0]), schema=schema) from e
        try:
            self.event_path = schema['load_events']
        except KeyError:
            self.event_path = None
        for key, default in state_defaults.items():
            try:
                self.state[key] = {
                        id_: default for id_ in schema[key][counters]}
            except KeyError:
                pass


def get_all():
    return entity_registry.values()


def get_by_id(id_):
    try:
        return entity_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("entity ``" + id_ + "`` was not found in the "
                                                      "entity registry") from e
