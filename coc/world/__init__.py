import yaml
import os
import glob
import hashlib
import copy

from coc import *
from coc.world import npc, monster, conditional, event, town, dungeon
from coc.exceptions import *


class World(Immutable):
    """ Contains a read-only (after load) record of all world content. Worlds
    hold all object assets, and a template state object which a Player copies
    when a new game is started.
    Worlds are read-only after being initialized, and their contents are fully
    defined by a YAML world schema.
    """
    def __init__(self, schema_root):
        super().__init__()
        file_paths = glob.glob(os.path.join(schema_root, '*.yaml'))
        subdirs = [d.name for d in os.scandir(schema_root) if d.is_dir()]
        for subdir in subdirs:
            file_paths.extend(glob.glob(
                    os.path.join(schema_root, subdir, '*.yaml')))
        schema_sets = dict()
        for path in file_paths:
            with open(path, 'r') as file:
                gen = yaml.load_all(file.read())
            schema_sets[path] = gen
        for set_ in schema_sets.items():
            for schema in set_[1]:
                self._load_schema(set_[0], schema)

        self.id = hashlib.sha256(repr(self.get_state_template()).encode()
                                 ).hexdigest()
        self.initialized = True

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def get_state_template(self):
        try:
            world = copy.deepcopy(self.world_template)
        except AttributeError:
            world = {
                    'npc': {obj.id: npc.state_template()
                            for obj in npc.get_all()},
                    'monster': {obj.id: obj.state_template()
                                for obj in monster.get_all()},
                    'town': {obj.id: obj.state_template()
                             for obj in town.get_all()},
                    'dungeon': {obj.id: obj.state_template()
                                for obj in dungeon.get_all()},
                    }
            self.world_template = copy.deepcopy(world)
        ret = {
                # 'entities': {
                #         e.id: copy.deepcopy(e.state) for e in entity.get_all()},
                # 'locales': {
                #         l.id: copy.deepcopy(l.state) for l in locale.get_all()},
                'pc': copy.deepcopy(self.pc_template),
                'world': world,
                'game': dict()
                }
        return ret

    def _load_schema(self, path, schema):
        schema_handlers = {
                'town': town.Town,
                'dungeon': dungeon.Dungeon,
                'npc': npc.NPC,
                'monster': monster.Monster,
                'event': event.Event,
                'world': self._load_world_schema,
                'pc': self._load_pc_schema
                }
        try:
            schema_handlers[schema['type']](schema)
        except KeyError as e:
            if e.args[0] == 'type':
                raise SchemaError(
                        'unable to load schema from {0} with missing'
                        '``type`` parameter'.format(path), schema=schema) from e
            else:
                raise SchemaError(
                        'unable to load schema from {0}. ``{1}`` is not a '
                        'supported object type.'.format(path, schema['type']),
                        schema=schema) from e

    def _load_pc_schema(self, schema):
        try:
            self.pc_template = schema
        except KeyError as e:
            raise SchemaError(
                    'pc state template missing required section ``state``',
                    schema=schema) from e

    def _load_world_schema(self, schema):
        for item in schema:
            self.__setattr__(item, schema[item])

    @staticmethod
    def _get_town_by_id(id_):
        return town.get_by_id(id_)

    @staticmethod
    def _get_dungeon_by_id(id_):
        return dungeon.get_by_id(id_)

    @staticmethod
    def _get_npc_by_id(id_):
        return npc.get_by_id(id_)

    @staticmethod
    def _get_monster_by_id(id_):
        return monster.get_by_id(id_)

    @staticmethod
    def _get_event_by_id(id_):
        return event.get_by_id(id_)


def load(schema_path):
    return World(schema_path)
