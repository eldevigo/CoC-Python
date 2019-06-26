from coc.world.entity import Entity
from coc.exceptions import *

npc_registry = dict()

class NPC(Entity):
    """ Common base class for all interactable entities in the world (monsters,
    """
    def __init__(self, schema):
        super().__init__(schema)
        self.initialized = True

def get_all():
    return npc_registry.values()

def get_by_id(id):
    try:
        return npc_registry[id]
    except KeyError as e:
        raise ObjectNotFoundError("npc ``" + entity_id +
                "`` was not found in the npc registry") from e
