from coc.world.locale import Locale
from coc.exceptions import *

town_registry = dict()


class Town(Locale):
    """ Represents a peaceful, visitable location with one or more selectable
    events as stores, NPCs, etc.
    """
    def __init__(self, schema):
        super().__init__(schema)
        self.state = {
                'flags': dict(),
                'counters': dict(),
                'numbers': dict(),
                'strings': dict(),
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
                except (TypeError, IndexError) as e:
                    raise SchemaError(
                            "malformed flag state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema) from e
        if 'counters' in schema['state']:
            for counter in schema['state']['counters']:
                try:
                    pair = counter.popitem()
                    self.state['counters'][pair[0]] = int(pair[1])
                except AttributeError:
                    self.state['counters'][counter] = 0
                except (TypeError, IndexError) as e:
                    raise SchemaError(
                            "malformed counter state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema) from e
        if 'numbers' in schema['state']:
            for number in schema['state']['numbers']:
                try:
                    pair = number.popitem()
                    self.state['numbers'][pair[0]] = bool(pair[1])
                except AttributeError:
                    self.state['numbers'][number] = 0.0
                except (TypeError, IndexError) as e:
                    raise SchemaError(
                            "malformed number state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema) from e
        if 'strings' in schema['state']:
            for string in schema['state']['strings']:
                try:
                    pair = string.popitem()
                    self.state['strings'][pair[0]] = str(pair[1])
                except AttributeError:
                    self.state['strings'][string] = ''
                except (TypeError, IndexError) as e:
                    raise SchemaError(
                            "malformed string state parameter ``{0}`` in town "
                            "object (id ``{1}``)".format(pair[0], self.id),
                            schema=schema) from e


def get_all():
    return town_registry.values()


def get_by_id(id_):
    try:
        return town_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("town ``" + entity_id +
                                  "`` was not found in the town registry"
                                  ) from e
