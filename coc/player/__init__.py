import yaml
import os

from coc import *

class Player(Immutable):
    """ Contains all state for an in-progress game, including world state, NPC
    interaction state, PC status effects and possessions, etc.
    """
    def __init__(self, name, world_id, state, meta):
        super().__init__()
        self.meta = meta
        self.name = name
        self.world_id = world_id
        self.state = state
        self.initialized = True

    def save(self, path):
        """ Serialize all internal state and write to the given save path.
        """
        if not path.endswith('csf'):
            path = path + os.extsep + 'csf'
        with open(path, 'w+') as file:
            file.write(self._serialize())

    def _serialize(self):
        """ returns a string that represents the internal state of self,
        suitable for rebuilding this player state with player.load()
        """
        save = dict()
        save['name'] = self.name
        save['world_id'] = self.world_id
        save['state'] = self.state
        save['meta'] = self.meta
        return yaml.dump(save)


def load(path):
    """ A factory function that loads a Player object from a file path.
    """
    with open(path, 'r') as file:
        player = yaml.load(file.read())
    return Player(**player)


# def create(name, world, interface):
#     """ A factory function that creates a new player object from parameters and
#     a world object.
#     """
#     race = interface.menu_choice(title='What race are you?',
#             options=['human',
#                 'orc',
#                 'elf'
#                 ]
#         )
#     return Player(name, world.id, **world.get_state_template())
