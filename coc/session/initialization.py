def initialize_pc_state(state_template, interface):
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
                    key: bool(state_template['statics']['flags'][key])
                    for key in
                    state_template['statics']['flags']
                }
            )
        if 'counters' in state_template['statics']:
            initial_state['counters'].update(
                {
                    key: int(state_template['statics']['counters'][key])
                    for key in
                    state_template['statics']['counters']
                }
            )
        if 'numbers' in state_template['statics']:
            initial_state['numbers'].update(
                {
                    key: float(state_template['statics']['numbers'][key])
                    for key in
                    state_template['statics']['numbers']
                }
            )
        if 'strings' in state_template['statics']:
            initial_state['strings'].update(
                {
                    key: str(state_template['statics']['strings'][key])
                    for key in
                    state_template['statics']['strings']
                }
            )
    if 'choices' in state_template:
        if 'flags' in state_template['choices']:
            for key in state_template['choices']['flags']:
                initial_state['flags'][key] = interface.boolean_choice(
                    state_template['choices']['flags'][key]['prompt']
                )
        if 'counters' in state_template['choices']:
            for key in state_template['choices']['counters']:
                initial_state['counters'][key] = interface.get_quantity(
                    text=state_template['choices']['counters'][key]['prompt'],
                    max_=int(
                        state_template['choices']['counters'][key]['max']
                    ),
                    min_=0,
                    autoround=False
                )
        if 'numbers' in state_template['choices']:
            for key in state_template['choices']['numbers']:
                initial_state['numbers'][key] = interface.get_quantity(
                    text=state_template['choices']['numbers'][key]['prompt'],
                    max_=state_template['choices']['numbers'][key]['max'],
                    min_=state_template['choices']['numbers'][key]['min'],
                    autoround=False,
                    is_float=True
                )
        if 'strings' in state_template['choices']:
            for key in state_template['choices']['strings']:
                initial_state['strings'][key] = interface.menu_choice(
                    state_template['choices']['strings'][key]['choices'],
                    title=state_template
                    ['choices']['strings'][key]['prompt']
                )
    return initial_state


def initialize_game_state(state_template, interface):
    return {}


def initialize_locale_state(state_template, interface):
    return {}
