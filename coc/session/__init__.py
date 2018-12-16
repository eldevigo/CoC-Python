from coc import COCClass
from coc import world
from coc import player

class Session(COCClass):
    """ Represents an interactive play session, used by various interfaces to
    bind a Player and a World object to the interface so that they may be
    interacted with by a human.
    """
    def __init__(self, world_path, player_path):
        self.world = world.load(world_path)
        self.player_file = player_path
        try:
            self.player = player.load(player_path)
            if player.world_id != world.id:
                raise LoadError("Save file does not match the selected world!")
        except FileNotFoundError:
            player_name = os.path.split(os.path.splitext(path)[0])[-1]
            self.player = player.create(name=player_name, world=self.world)

    def save(self, save_path=None):
        try:
            self.player.dump(save_path)
        except Exception: # FIXME: this should only catch exceptions from trying to save a player file to None
            self.player.dump(self.player_file)

