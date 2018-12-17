from coc import Immutable
from coc.exceptions import *

entity_registry = dict()

class Entity(Immutable):
    """ Common base class for all interactable entities in the world (monsters,
    npcs, etc.)
    """
    def __init__(self, schema):
        super().__init__()
        state_defaults = {
                'counters': 0,
                'flags': False
                }
        self.state = dict()
        try:
            self.id = schema['id']
            self.name = schema['name']
            self.state['encounter_event_id'] = schema['state']['encounter_event']
        except KeyError as e:
            raise SchemaError("entity schema missing required field ``{0}``"
                    .format(e.args[0]), schema=schema) from e
        try:
            self.event_path = schema['load_events']
        except KeyError:
            self.event_path = None
        for key,default in state_defaults.items():
            try:
                self.state[key] = {id: default for id in schema[key][counters]}
            except KeyError:
                pass

from coc.world import npc
from coc.world import monster

def construct(schemas):
    entity_class = {
            'npc': npc.NPC,
            'monster': monster.Monster
            }
    try:
        for item in schemas:
            entity = entity_class[schema['type']](schema)
            entity_registry[entity.id] = entity
            entity_registry[schema.type] = entity
    except AttributeError as e:
        if str(e) == 'string indices must be integers':
# schemas is of type schema, not of type list(schema)
            entity = entity_class[schema['type']](schemas)
            entity_registry[entity.id] = entity
            entity_registry[schemas.type] = entity

def get_all():
    return entity_registry.values()

def get_by_id(entity_id):
    try:
        return entity_registry[entity_id]
    except KeyError as e:
        raise EntityNotFoundError("entity " + entity_id +
                " was not found in the entity registry") from e
