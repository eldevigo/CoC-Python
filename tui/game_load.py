import yaml

from coc.exceptions import *

from tui import interface as i


def select_player(save_path):
# Read existing save files to populate the menu
    try:
        with open(save_path + '/saves.yaml', 'r') as file:
            saves = yaml.load(file.read())
    except (yaml.YAMLError, KeyError) as e:
        raise LoadError("Unable to load your saves.\n"
                "saves.yaml is corrupted!") from e
    except FileNotFoundError as e:
# No save.yaml yet on the target path. Assume this is an uninitialized save path.
        saves = {'files': dict()}
        with open(save_path + 'saves.yaml', 'w+') as file:
            file.write(yaml.dump(saves))

    menu = list(saves['files'].keys())
    menu.insert(0, '< new game >')
    while True:
        save_name = i.menu_choice(menu, title="Select a save!")
        if save_name == '< new game >':
            name = i.get_line(prompt="Beginning a new game! What will we call you?")
            if not name:
                i.error("Empty names are not allowed!")
            elif name in saves['files']:
                i.error("A game with that name already exists!")
            else:
                i.prompt('')
                i.print("Welcome, {0}!".format(name))
                return save_path.rstrip('/') + '/' + name + '.csf'
        else:
            return save_path.rstrip('/') + '/' + saves['files'][save_name] + '.csf'
