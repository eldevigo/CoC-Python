from abc import ABC

from coc.world.locale import Locale
from coc.exceptions import ObjectNotFoundError


class Dungeon(Locale, ABC):
    """ Represents a hostile visitable location with a room map, where each
    room contains one or more events, incl. puzzles, fights, and loot.
    """

    def __init__(self, schema):
        super().__init__(schema)
