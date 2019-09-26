from abc import ABC

from coc.world.locale import Locale
from coc.exceptions import ObjectNotFoundError


class Dungeon(Locale, ABC):
    """ Represents a hostile visitable location with a room map, where each
    room contains one or more events, incl. puzzles, fights, and loot.
    """

    def __init__(self, schema):
        super().__init__(schema)
        self.state['flags'] = load_flags()
        self.state['counters'] = load_counters()
        self.state['numbers'] = load_numbers()
        self.state['strings'] = load_strings()
        self.state['events'] = load_events()
