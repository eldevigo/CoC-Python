from coc.world.entity import Entity
from coc.exceptions import *

class NPC(Entity):
    """ Common base class for all interactable entities in the world (monsters,
    """
    def __init__(self, schema):
        super().__init__(schema)
        self.initialized = True

