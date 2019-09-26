from coc import EventContext
from coc.exceptions import ObjectNotFoundError, SchemaError

entity_registry = dict()


class Entity(EventContext):
    """ Common base class for all interactable entities in the world (monsters,
    npcs, etc.)
    """
    def __init__(self, schema):
        super().__init__(schema)
        state_defaults = {
                'counters': 0,
                'flags': False
                }
        self.state = dict()
        try:
            self.state['encounter_event_id'] = \
                schema['state']['encounter_event']
        except KeyError:
            raise SchemaError("{0} schema missing required initial state "
                              "``encounter_event``".format(type(self)),
                              schema=schema)
        try:
            self.event_path = schema['load_events']
        except KeyError:
            self.event_path = None
        for key, default in state_defaults.items():
            try:
                self.state[key] = {
                        id_: default for id_ in schema['state'][key]
                }
            except KeyError:
                pass

    def get_id(self):
        return self.id_


def get_all():
    return entity_registry.values()


def get_by_id(id_):
    try:
        return entity_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("entity ``" + id_ +
                                  "`` was not found in the entity registry")\
            from e
