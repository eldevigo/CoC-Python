from coc import Immutable

entity_registry = dict()

class Conditional(Immutable):
    """ Common base class for all interactable entities in the world (monsters,
    """

def get_all():
    return entity_registry.values()
