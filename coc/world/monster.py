from coc.world.entity import Entity
from coc.exceptions import *

monster_registry = dict()

class Monster(Entity):
    """ Common base class for all interactable entities in the world (monsters,
    """
    def __init__(self, schema):
        super().__init__(schema)
        try:
            self.state['victory_event_id'] = schema['state']['victory_event']
            self.state['defeat_event_id'] = schema['state']['defeat_event']
        except KeyError as e:
            raise SchemaError("monster schema missing required field ``{0}``"
                    .format(e.args[0]), schema=schema) from e
        self.initialized = True

def get_all():
    return monster_registry.values()

def get_by_id(id):
    try:
        return monster_registry[id]
    except KeyError as e:
        raise ObjectNotFoundError("monster ``" + entity_id +
                "`` was not found in the monster registry") from e
