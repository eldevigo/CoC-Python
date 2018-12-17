from coc import Immutable
from coc.exceptions import *

entity_registry = dict()

class Locale(Immutable):
    """ Common base class for all lisitable locations in the world, incl. towns,
    dungeons, and wilderness areas.
    """
    def __init__(self, schema):
        super().__init__()

def get_all():
    return entity_registry.values()
