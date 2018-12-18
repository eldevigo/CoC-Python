from coc import Immutable

entity_registry = dict()

class Event(Immutable):
    """ Common base class for all interactable entities in the world (monsters,
    """
    def __init__(self, schema):
        super().__init__()

def get_all():
    return entity_registry.values()
