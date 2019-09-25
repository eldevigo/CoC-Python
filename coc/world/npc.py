from coc.exceptions import ObjectNotFoundError, SchemaError
from coc.world.entity import Entity
from coc.world.event import is_loaded as is_event_loaded

npc_registry = dict()


class NPC(Entity):
    """ Represents non-combative dialogs with game characters. Transitioning to
    combat with a dialogueable character is implemented as an event transition
    to a fight with a Monster object that is only semantically associated.
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
                            "malformed flag state parameter ``{0}`` in npc"
                            " object (id ``{1}``)".format(pair[0], self.id_),
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
                            "malformed counter state parameter ``{0}`` in npc"
                            " object (id ``{1}``)".format(pair[0], self.id_),
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
                            "malformed number state parameter ``{0}`` in npc "
                            "object (id ``{1}``)".format(pair[0], self.id_),
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
                            "malformed string state parameter ``{0}`` in npc"
                            " object (id ``{1}``)".format(pair[0], self.id_),
                            schema=schema)
            except KeyError:
                pass
            return strings

        def load_events():
            events = list()
            try:
                event_id = schema['state']['encounter_event']
                if not is_event_loaded(event_id):
                    raise ObjectNotFoundError(
                        "tried to load npc object (id ``{0}``) with a "
                        "nonexistant event_id in its event registry - "
                        "requested id was ``{1}``"
                            .format(self.id_, event_id),
                        schema=schema)
                events.append(event_id)
            except KeyError as e:
                if e.args[0] == 'events':
                    # This is an error because eventless locales are not
                    # interactable and this error indicates that no events are
                    # attached to this npc.
                    raise SchemaError(
                        "tried to load npc object (id ``{0}``) with no"
                        " registered events".format(self.id_),
                        schema=schema)
                raise
            return events
        super().__init__(schema)
        try:
            self.id_ = schema['id']
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
        self.initialized = True
        npc_registry[self.id_] = self

    def get_state_template(self):
        pass


def get_all():
    return npc_registry.values()


def get_by_id(id_):
    try:
        return npc_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("npc ``" + id_ +
                                  "`` was not found in the npc registry")\
            from e
