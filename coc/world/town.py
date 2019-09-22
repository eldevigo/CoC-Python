import copy

from coc.world.locale import Locale
from coc.world.event import get_by_id as get_event_by_id
from coc.exceptions import *

town_registry = dict()


class Town(Locale):
    """ Represents a peaceful, visitable location with one or more selectable
    events as stores, NPCs, etc.
    """
    def __init__(self, schema):
        super().__init__(schema)
        town_registry[schema['id']] = self
        self.state = {
                'flags': dict(),
                'counters': dict(),
                'numbers': dict(),
                'strings': dict(),
                'events': list(),
                }
        try:
            self.id = schema['id']
        except KeyError:
            raise SchemaError("tried to load town object with no id field",
                              schema=schema)
        try:
            self.name = schema['name']
        except KeyError:
            raise SchemaError("tried to load town object with no id field",
                              schema=schema)
        if 'flags' in schema['state']:
            for flag in schema['state']['flags']:
                try:
                    pair = flag.popitem()
                    self.state['flags'][pair[0]] = bool(pair[1])
                except AttributeError:
                    self.state['flags'][flag] = False
                except (TypeError, IndexError):
                    raise SchemaError(
                            "malformed flag state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema)
        if 'counters' in schema['state']:
            for counter in schema['state']['counters']:
                try:
                    pair = counter.popitem()
                    self.state['counters'][pair[0]] = int(pair[1])
                except AttributeError:
                    self.state['counters'][counter] = 0
                except (TypeError, IndexError):
                    raise SchemaError(
                            "malformed counter state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema)
        if 'numbers' in schema['state']:
            for number in schema['state']['numbers']:
                try:
                    pair = number.popitem()
                    self.state['numbers'][pair[0]] = bool(pair[1])
                except AttributeError:
                    self.state['numbers'][number] = 0.0
                except (TypeError, IndexError):
                    raise SchemaError(
                            "malformed number state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema)
        if 'strings' in schema['state']:
            for string in schema['state']['strings']:
                try:
                    pair = string.popitem()
                    self.state['strings'][pair[0]] = str(pair[1])
                except AttributeError:
                    self.state['strings'][string] = ''
                except (TypeError, IndexError):
                    raise SchemaError(
                            "malformed string state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema)
        try:
            for event_id in schema['events']:
                self.state['events'].append(get_event_by_id(event_id))
        except KeyError as e:
            if e.args[0] == 'events':
                # This is an error because eventless locales are uninteractable.
                # Register an event on the town to add text, encounters, menu
                #   etc for the user to interact with.
                raise SchemaError(
                        "tried to load town object (id ``{0}``) with no "
                        "registered events".format(self.id),
                        schema=schema)
            raise
        except ObjectNotFoundError as e:
            raise SchemaError(
                    "tried to load town object (id ``{0}``) with a nonexistant "
                    "event_id in its event registry".format(self.id),
                    schema=schema) from e

    def get_state_template(self):
        return copy.deepcopy(self.state)

    def get_event_streams(self):
        # FIXME: this implies that runtime lists of events registered to a locale are stored in the Town object, which is in the World domain. This is undesirable! Figure out how to make this a problem for the Player object to solve, using the stored copy of this town's state (from get_state_template())
        pass



def get_all():
    return town_registry.values()


def get_by_id(id_):
    try:
        return town_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("town ``" + id_ +
                "`` was not found in the town registry") from e
