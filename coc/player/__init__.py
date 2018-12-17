import yaml

from coc import *

class Player(Immutable):
    """ Contains all state for an in-progress game, including world state, NPC
    interaction state, PC status effects and possessions, etc.
    """
    def __init__(self, name, world_id, **kwargs):
        self.name = name
        self.world_id = world_id
        for item in kwargs:
            self[item] = kwargs[item]
        self.initialized = True

def load(path):
    """ A factory function that loads a Player object from a file path.
    """
    with open(path, 'r') as file:
        player = yaml.load(file.read())
    return Player(player)


def create(name, world, interface):
    """ A factory function that creates a new player object from parameters and
    a world object.
    """
    race = interface.menu_choice(title='What race are you?',
            options=['human',
                'orc',
                'elf'
                ]
        )
    return Player(name, world.id, **world.get_state_template())
