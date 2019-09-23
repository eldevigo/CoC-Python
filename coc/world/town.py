import copy

from coc.world.locale import Locale, register_locale
from coc.world.event import get_by_id as get_event_by_id
from coc.exceptions import ObjectNotFoundError, SchemaError


class Town(Locale):
    """ Represents a peaceful, visitable location with one or more selectable
    events as stores, NPCs, etc.
    """

    def __init__(self, schema):
        def load_flags():
            flags = dict()
            try:
                for flag in schema['state']['flags']:
                    try:
                        pair = flag.popitem()
                        flags[pair[0]] = bool(pair[1])
                    except AttributeError:
                        # this is expected to occur because this flag has no
                        # associated value (i.e. it's implicitly false)
                        flags[flag] = False
                    except (TypeError, IndexError):
                        raise SchemaError(
                            "malformed flag state parameter ``{0}`` in town"
                            " object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema)
            except KeyError:
                pass
            return flags

        def load_counters():
            counters = dict()
            try:
                for counter in schema['state']['counters']:
                    try:
                        pair = counter.popitem()
                        counters[pair[0]] = int(pair[1])
                    except AttributeError:
                        counters[counter] = 0
                    except (TypeError, IndexError):
                        raise SchemaError(
                            "malformed counter state parameter ``{0}`` in town"
                            " object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema)
            except KeyError:
                pass
            return counters

        def load_numbers():
            numbers = dict()
            try:
                for number in schema['state']['numbers']:
                    try:
                        pair = number.popitem()
                        numbers[pair[0]] = bool(pair[1])
                    except AttributeError:
                        numbers[number] = 0.0
                    except (TypeError, IndexError):
                        raise SchemaError(
                            "malformed number state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema)
            except KeyError:
                pass
            return numbers

        def load_strings():
            strings = dict()
            try:
                for string in schema['state']['strings']:
                    try:
                        pair = string.popitem()
                        strings[pair[0]] = str(pair[1])
                    except AttributeError:
                        strings[string] = ''
                    except (TypeError, IndexError):
                        raise SchemaError(
                            "malformed string state parameter ``{0}`` in town"
                            " object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema)
            except KeyError:
                pass
            return strings

        def load_events():
            events = list()
            try:
                for event_id in schema['state']['events']:
                    try:
                        events.append(get_event_by_id(event_id))
                    except ObjectNotFoundError as e:
                        raise ObjectNotFoundError(
                            "tried to load town object (id ``{0}``) with a "
                            "nonexistant event_id in its event registry - "
                            "requested id was ``{1}``"
                            .format(self.id, event_id),
                            schema=schema) from e
            except KeyError as e:
                if e.args[0] == 'events':
                    # This is an error because eventless locales are not
                    # interactable and this error indicates that no events are
                    # attached to this town.
                    raise SchemaError(
                        "tried to load town object (id ``{0}``) with no"
                        " registered events".format(self.id),
                        schema=schema)
                raise
            return events

        super().__init__(schema)
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
        self.state = {
            'flags': load_flags(),
            'counters': load_counters(),
            'numbers': load_numbers(),
            'strings': load_strings(),
            'events': load_events()
        }
        register_locale(self.id, self)

    def get_state_template(self):
        return copy.deepcopy(self.state)

    def get_event_streams(self, player):
        # FIXME: this implies that runtime lists of events registered to a
        # locale are stored in the Town object, which is in the World
        # domain. This is undesirable! Figure out how to make this a
        # problem for the Player object to solve, using the stored copy of
        # this town's state (from get_state_template())
        pass

