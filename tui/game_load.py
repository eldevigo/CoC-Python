import yaml

from coc.exceptions import *

from tui import interface as i

lorem = [
"I’ll never seen, Bob. They have to trace through hardhats and phone anywhere and all this is he? All right.",
"President Nixon: And they, they’ve been talking to get out they contacted--",
"President Nixon: That's what we have gotten a thing to hire Schorr.",
"President Nixon: Are they concluded that there’s no way things like this. Who is because I want somebody to record those?",
"Haldeman: On the big job. But then I asked, you want to--",
"President Nixon: That's the phone conversation on that, they were connected to see it. And he was bugging Humphrey, too.",
"All three hundred thousand [dollars]. It's two of the idea that the hell of the idea we're going to record, and the hell of [George] Shultz, has to whom?"
]


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
        save_name = i.menu_choice(menu, prompt="Select a save!")
        if save_name == '< new game >':
            name = i.get_line(prompt="Beginning a new game! What will we call you?")
            if not name:
                i.error("Empty names are not allowed!")
            elif name in saves['files']:
                i.error("A game with that name already exists!")
            else:
                for line in lorem:
                    i.print(line)
                i.print("Welcome, {0}!".format(name))
                return save_path.rstrip('/') + '/' + name + '.csf'
        else:
            return save_path.rstrip('/') + '/' + saves['files'][save_name] + '.csf'
