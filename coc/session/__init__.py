import os
import sys
import yaml

from coc import COCClass
from coc import world
from coc import player as playerlib
from coc.exceptions import ExitMenuException, LoadError, \
    IncorrectObjectTypeError
from coc.session import game_load, initialization
from coc.world.locale import Locale
from coc.world.event import Event


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
                self.save_file = game_load.select_save(
                    os.path.expanduser(save_path))
                self.player = self.load_player(self.save_file)
            except LoadError as e:
                interface.print(str(e), buffer='flush')
            except ExitMenuException:
                sys.exit(0)

    def load_player(self, save_file):
        try:
            player = playerlib.load(save_file)
# FIXME: world ID generation is broken. the same world generates multiple IDs.
#  check the world ID scheme generating code,
#  deepcopy may not be a stable operation.
            # if player.world_id != self.world.id:
            #     self.interface.prompt('')
            #     raise LoadError(
            #             "Save file does not match the selected world!")
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
            with open(os.path.join(os.path.dirname(self.save_file),
                                   'saves.yaml'), 'r') as file:
                saves = yaml.safe_load(file.read())
            assert player.name not in saves
            saves[player.name] = self.save_file
            with open(os.path.join(os.path.dirname(self.save_file),
                                   'saves.yaml'), 'w') as file:
                file.write(yaml.safe_dump(saves))
            return player

    def save_player(self, save_file=None):
        try:
            self.player.save(save_file)
        except AttributeError as e:
            if str(e) == "'NoneType' object has no attribute 'endswith'":
                # tried to check if a nonexistent path had
                # the right file extension
                self.player.save(self.save_file)
            else:
                raise

    def new_player(self):
        state_template = self.world.get_state_template()
        initial_state = dict()
        initial_state['pc'] = initialization.initialize_pc_state(
            state_template['pc'], self.interface)
        initial_state['game'] = initialization.initialize_game_state(
            state_template['game'], self.interface)
        initial_state['world'] = state_template['world']
        player_name = os.path.split(self.save_file)[-1]
        if player_name.endswith('csf'):
            player_name = os.path.splitext(player_name)[0]
        new_player = playerlib.Player(player_name, self.world.id,
                                      initial_state, None)
        return new_player

    def play(self):
        locales = [self.player.get_state('pc.strings.initial_locale')]
        # TODO: Wire up event playthrough, starting from coc.world.events.run()
        # It looks like conditionals aren't properly parsed and loaded from
        # event sequences at event schema read time
        # Also need a handler that is called when an event sequence terminates,
        # which calls the visit event on the current locale
        while True:
            current_locale = locales.pop()
            current_events = self.player.visit(current_locale)
            while current_events:
                current_event = current_events.pop()
                event_sequence = current_event.run(self.player.get_state)
                for item in event_sequence:
                    next_ = item.do(self.player, self.world,
                                        self.interface)
                    if isinstance(next_, Locale):
                        locales.append(next_)
                    elif isinstance(next_, Event):
                        current_events.append(next_)
                    elif next_ is not None:
                        raise IncorrectObjectTypeError(
                            "Sequence in event ``{0}`` returned an "
                            "unsupported next object type ``{1}``"
                            .format(current_event.id, type(next_)))
            if not locales:
                print("Ran out of locales on the stack, reattaching the last"
                      " one visited")
                locales.append(current_locale)
