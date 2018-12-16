import yaml
import os
import glob
import hashlib

from coc import *
from coc.exceptions import *

class World(Immutable):
    """ Contains a read-only (after load) record of all world content. Worlds
    hold all object assets, and a template state object which a Player copies
    when a new game is started.
    Worlds are read-only after being initialized, and their contents are fully
    defined by a YAML world schema.
    """
    def __init__(self, schema_root):
        self.schemas = dict()
        subdirs = [d.name for d in os.scandir(schema_root) if d.is_dir()]
        for subdir in subdirs:
            self.schemas[subdir] = [yaml.load(obj) for obj in glob.glob(subdir + '/*.yaml')]

        self.id = hashlib.sha256(repr(self.state_object()).encode()).hexdigest()
        self.initialized = True


    def state_object(self):
        return dict(self.state)

def load(path):
    return World(path)
