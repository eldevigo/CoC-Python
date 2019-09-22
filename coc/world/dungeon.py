from coc.world.locale import Locale
from coc.exceptions import *

dungeon_registry = dict()


class Dungeon(Locale):
    """ Represents a hostile visitable location with a room map, where each room
    contains one or more events, incl. puzzles, fights, and loot.
    """
    def __init__(self, schema):
        super().__init__(schema)


def get_all():
    return dungeon_registry.values()


def get_by_id(id_):
    try:
        return dungeon_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("dungeon ``" + id_ +
                "`` was not found in the dungeon registry") from e
