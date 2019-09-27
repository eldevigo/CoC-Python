import yaml
import os
import glob
import hashlib
from copy import deepcopy

from coc import Immutable
from coc.world import npc, monster, eventstream, town, dungeon, locale
from coc.exceptions import SchemaError


class World(Immutable):
    """ Contains a record of all world content. Worlds hold all object
    assets, and a template state object which a Player copies when a new
    game is started.
    Worlds are read-only after being initialized, and their contents are fully
    defined by a YAML world schema.
    """
    def __init__(self, schema_root):
        super().__init__()
        file_paths = glob.glob(os.path.join(schema_root, '*.yaml'))
        loaded_paths = list()
        subdirs = [d.name for d in os.scandir(schema_root) if d.is_dir()]
        for subdir in subdirs:
            file_paths.extend(glob.glob(
                    os.path.join(schema_root, subdir, '*.yaml')))
        schema_types = [
            'event_stream',
            'town',
            'dungeon',
            'npc',
            'monster',
            'world',
            'pc'
        ]
        schema_sets = {key: [] for key in schema_types}
        while file_paths:
            path = file_paths.pop()
            loaded_paths.append(path)
            with open(path, 'r') as file:
                loaded = list(yaml.safe_load_all(file.read()))
            for schema in loaded:
                try:
                    for path_ in schema['load_paths']:
                        additional_path = os.path.join(os.path.dirname(
                            path), path_)
                        if additional_path not in loaded_paths:
                            file_paths.extend(glob.glob(additional_path))
                            loaded_paths.append(additional_path)
                except KeyError:
                    pass
            try:
                for schema_type in schema_types:
                    schema_sets[schema_type].extend(filter(
                        lambda x: x['type'] == schema_type,
                        loaded
                    ))
            except KeyError:
                raise SchemaError("An object schema at path ``{0}`` is "
                                  "missing a 'type'` property")
        for schema_type in schema_types:
            for schema in schema_sets[schema_type]:
                self._load_schema(schema_type, schema)
        self.world_template = None
        self.id_ = hashlib.sha256(repr(self.get_state_template()).encode()
                                  ).hexdigest()
        self.initialized = True

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __getitem__(self, key):
        return self.__getattribute__(key)

    def get_state_template(self):
        if self.world_template:
            world = deepcopy(self.world_template)
        else:
            world = {
                    'npc': {obj.get_id(): obj.get_state_template()
                            for obj in npc.get_all()},
                    'monster': {obj.get_id(): obj.get_state_template()
                                for obj in monster.get_all()},
                    'locale': {obj.get_id(): obj.get_state_template()
                               for obj in locale.get_all_locales()},
                    }
            self.world_template = deepcopy(world)
        ret = {
                'pc': deepcopy(self.pc_template),
                'world': world,
                'game': dict()
                }
        return ret

    def get_id(self):
        return self.id_

    def _load_schema(self, path, schema):
        schema_handlers = {
                'town': town.Town,
                'dungeon': dungeon.Dungeon,
                'npc': npc.NPC,
                'monster': monster.Monster,
                'event_stream': eventstream.EventStream,
                'world': self._load_world_schema,
                'pc': self._load_pc_schema
                }
        try:
            schema_handlers[schema['type']](schema)
        except KeyError as e:
            if e.args[0] == 'type':
                raise SchemaError(
                        'unable to load schema from {0} with missing '
                        '``type`` parameter'.format(path), schema=schema)\
                    from e
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
    def _get_locale_by_id(id_):
        return locale.get_locale_by_id(id_)

    @staticmethod
    def _get_npc_by_id(id_):
        return npc.get_by_id(id_)

    @staticmethod
    def _get_monster_by_id(id_):
        return monster.get_by_id(id_)

    @staticmethod
    def _get_event_by_id(id_):
        return eventstream.get_eventstream_by_id(id_)

    @classmethod
    def get_locale_events(cls, id_, player):
        return locale.get_locale_by_id(id_).run(player)


def load(schema_path):
    return World(schema_path)
