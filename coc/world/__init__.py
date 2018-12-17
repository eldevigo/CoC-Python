import yaml
import os
import glob
import hashlib
import copy

from coc import *
from coc.world import entity,npc,monster,conditional,event,locale
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
            file_paths.extend(glob.glob(os.path.join(schema_root, subdir, '*.yaml')))
        schemas = []
        for path in file_paths:
            with open(path, 'r') as file:
                gen = yaml.load_all(file.read())
            for item in gen:
                schemas.append(item)
        for schema in schemas:
            self._load_schema(schema)

        self.id = hashlib.sha256(repr(self.get_state_template()).encode()).hexdigest()
        self.initialized = True

    def __setitem__(self, key, value):
        return self.__setattr__(key, value)

    def __getitem__(self, key):
        return self.__getattr__(key)

    def get_state_template(self):
        ret = {
                'entities': {e.id: copy.deepcopy(e.state) for e in entity.get_all()},
                'locales': {l.id: copy.deepcopy(l.state) for l in locale.get_all()},
                'self': copy.deepcopy(self.pc_template)
                }
        return ret

    def _load_schema(self, schema):
        schema_handlers = {
                'npc': npc.NPC,
                'monster': monster.Monster,
                'locale': locale.Locale,
                'pc': self._load_pc_template
                }
        try:
            schema_handlers[schema['type']](schema)
        except KeyError as e:
            if e[0] == 'type':
                raise SchemaError('unable to load schema with missing ``type``'
                        'parameter', schema=schema) from e
            else:
                raise SchemaError('unable to load schema. ``{0}`` is not a'
                        'supported object type.'.format(schema['type']),
                        schema=schema) from e

    def _load_pc_template(self, schema):
        try:
            self.pc_template = schema['state']
        except KeyError as e:
            raise SchemaError('pc state template missing required section '
                    '``state``', schema=schema) from e


    def entity_by_id(entity_id):
            return entity.get_by_id(entity_id)

def load(schema_path):
    return World(schema_path)
