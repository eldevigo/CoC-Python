import yaml
import os
import copy

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

    def get_state(self, state_path):
        try:
            if state_path[0] not in self.state:
                raise Exception()
            if state_path[1] not in self.state[state_path[0]]:
                raise Exception()
            if state_path[2] not in self.state[state_path[0]][state_path[1]]:
                raise Exception()
            return copy.deepcopy(
                self.state[state_path[0]][state_path[1]][state_path[2]])
        except IndexError as e:
            raise

    def set_state(self, state_path, value):
        pass

    def save(self, save_file):
        """ Serialize all internal state and write to the given save path.
        """
        if not save_file.endswith('csf'):
            save_file = save_file + os.extsep + 'csf'
        with open(save_file, 'w+') as file:
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


def load(save_file):
    """ A factory function that loads a Player object from a file path.
    """
    with open(save_file, 'r') as file:
        player = yaml.load(file.read())
    return Player(**player)


# def create(name, world, interface):
#     """ A factory function that creates a new player object from parameters
#     and a world object.
#     """
#     race = interface.menu_choice(title='What race are you?',
#             options=['human',
#                 'orc',
#                 'elf'
#                 ]
#         )
#     return Player(name, world.id, **world.get_state_template())
