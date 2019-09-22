import yaml
import os
import copy

from coc import *
from coc.exceptions import *


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
        path_tokens = state_path.split('.')
        scope = state
        resolved = list()
        for token in path_tokens:
            try:
                scope = scope[token]
                resolved.append(token)
            except KeyError:
                raise StateNotFoundError(
                        msg="unable to resolve state path ``{0}``"
                          .format('.'.join(resolved)),
                        found=resolved[0:-1],
                        requested=state_path,
                        error=resolved[-1])
        if type(scope) == dict:
            raise StateNotFoundError(
                    msg="incomplete state path ``{0}`` - result is not a "
                      "single state element"
                      .format('.'.join(resolved)))
        # TODO: figure out how to return a copy of this state so it is not
        # modifiable
        return scope

    def set_state(self, state_path, value):
        # TODO: factor out the state resolution algorithm in get_state() above
        # into a private helper method that returns a shallow-copied reference
        # to the target state, and then modify it
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
        return yaml.safe_dump(save)


def load(save_file):
    """ A factory function that loads a Player object from a file path.
    """
    with open(save_file, 'r') as file:
        player = yaml.safe_load(file.read())
    return Player(**player)
