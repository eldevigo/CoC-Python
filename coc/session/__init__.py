import os
import sys

from coc import COCClass
from coc import world
from coc import player as playerlib
from coc.session.game_load import *

class Session(COCClass):
    """ Represents an interactive play session, used by various interfaces to
    bind a Player and a World object to the interface so that they may be
    interacted with by a human.
    """
    def __init__(self, world_path, save_path, interface):
        super().__init__()
        self.world = world.load(world_path)
        self.interface = interface
        self.player = None
        while not self.player:
            try:
                self.save_file = select_save(os.path.expanduser(save_path))
                self.player = self.load_player(self.save_file)
            except LoadError as e:
                interface.print(str(e), buffer='flush')
            except ExitMenuException:
                sys.exit(0)

    def load_player(self, save_file):
        try:
            player = playerlib.load(save_file)
# FIXME: world ID generation is broken. the same world generates multiple IDs.
# check the world ID scheme generating code, deepcopy may not be a stable operation.
            #if player.world_id != self.world.id:
            #    self.interface.prompt('')
            #    raise LoadError("Save file does not match the selected world!")
            return player
        except LoadError as e:
            raise LoadError(
                    "Encountered an error while loading ``{0}``: {1}".format(
                        save_file,
                        str(e)
                        )
                    )
        except FileNotFoundError:
            player = self.new_player()
            player.save(save_file)
            with open(os.path.join(os.path.dirname(self.save_file), 'saves.yaml'), 'r') as file:
                saves = yaml.load(file.read())
            assert player.name not in saves
            saves[player.name] = self.save_file
            with open(os.path.join(os.path.dirname(self.save_file), 'saves.yaml'), 'w') as file:
                file.write(yaml.dump(saves))
            return player


    def save_player(self, save_file=None):
        try:
            self.player.save(save_file)
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'endswith'":
# tried to check if a nonexistent path had the right file extension
                self.player.save(self.save_file)
            else:
                raise

    def new_player(self):
        state_template = self.world.get_state_template()['pc']
        player_name = os.path.split(self.save_file)[-1]
        if player_name.endswith('csf'):
            player_name = os.path.splitext(player_name)[0]
        initial_state = {
                'flags': dict(),
                'counters': dict(),
                'numbers': dict(),
                'strings': dict()
                }
        if 'defaults' in state_template:
            if 'flags' in state_template['defaults']:
                initial_state['flags'].update(
                        {
                            flag: False
                            for flag in
                            state_template['defaults']['flags']
                            }
                        )
            if 'counters' in state_template['defaults']:
                initial_state['counters'].update(
                        {
                            counter: 0
                            for counter in
                            state_template['defaults']['counters']
                            }
                        )
            if 'numbers' in state_template['defaults']:
                initial_state['numbers'].update(
                        {
                            number: 0.0
                            for number in
                            state_template['defaults']['numbers']
                            }
                        )
            if 'strings' in state_template['defaults']:
                initial_state['strings'].update(
                        {
                            string: ''
                            for string in
                            state_template['defaults']['strings']
                            }
                        )
        if 'statics' in state_template:
            if 'flags' in state_template['statics']:
                initial_state['flags'].update(
                        {
                            key:bool(state_template['statics']['flags'][key])
                            for key in
                            state_template['statics']['flags']
                            }
                        )
            if 'counters' in state_template['statics']:
                initial_state['counters'].update(
                        {
                            key:int(state_template['statics']['counters'][key])
                            for key in
                            state_template['statics']['counters']
                            }
                        )
            if 'numbers' in state_template['statics']:
                initial_state['numbers'].update(
                        {
                            key:float(state_template['statics']['numbers'][key])
                            for key in
                            state_template['statics']['numbers']
                            }
                        )
            if 'strings' in state_template['statics']:
                initial_state['strings'].update(
                        {
                            key:str(state_template['statics']['strings'][key])
                            for key in
                            state_template['statics']['strings']
                            }
                        )
        if 'choices' in state_template:
            if 'flags' in state_template['choices']:
                for key in state_template['choices']['flags']:
                    initial_state['flags'][key] = self.interface.boolean_choice(
                            state_template['choices']['flags'][key]['prompt']
                            )
            if 'counters' in state_template['choices']:
                for key in state_template['choices']['counters']:
                    initial_state['counters'][key] = self.interface.get_quantity(
                            text=state_template['choices']['counters'][key]['prompt'],
                            max=int(state_template['choices']['counters'][key]['max']),
                            min=0,
                            autoround=False
                            )
            if 'numbers' in state_template['choices']:
                for key in state_template['choices']['numbers']:
                    initial_state['numbers'][key] = self.interface.get_quantity(
                            text=state_template['choices']['numbers'][key]['prompt'],
                            max=state_template['choices']['numbers'][key]['max'],
                            min=state_template['choices']['numbers'][key]['min'],
                            autoround=False,
                            is_float=True
                            )
            if 'strings' in state_template['choices']:
                for key in state_template['choices']['strings']:
                    initial_state['strings'][key] = self.interface.menu_choice(
                            state_template['choices']['strings'][key]['choices'],
                            title=state_template['choices']['strings'][key]['prompt']
                            )

        new_player = playerlib.Player(player_name, self.world.id, initial_state, None)
        return new_player

