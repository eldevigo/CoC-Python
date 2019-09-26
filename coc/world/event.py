from abc import ABC, abstractmethod

from coc import Immutable, SchemaError
from coc.world.locale import get_locale_by_id


class Event(Immutable, ABC):
    """ Parent class for all event sequence items - represents a single step in
    an event stream.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__()
        self.condition = condition

    @abstractmethod
    def do(self, player, world, interface):
        pass

    @abstractmethod
    def __dict__(self):
        pass

    def check_condition(self, getfunc):
        if self.condition is None:
            return True
        else:
            return self.condition.test(getfunc)

    @staticmethod
    def construct(event_schema, eventstream):
        try:
            seq_type = event_schema['type']
        except TypeError:
            seq_type = 'text'
            event_schema = {'text': event_schema}
        global _event_constructors
        return _event_constructors[seq_type](event_schema, eventstream)


class EventBeginFight(Event):
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventText(Event):
    """ An event sequence item containing a block of text. This is the core
    event sequence type for game content.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        try:
            self.text = schema['text']
        except KeyError:
            raise SchemaError("{0} schema missing required field "
                              "``text``".format(type(self)))
        self.initialized = True

    def do(self, player, world, interface):
        interface.print(self.text)

    def __dict__(self):
        return {
            'type': 'text',
            'text': self.text
        }


class EventBranch(Event):
    """ An event item that jumps to another EventStream. This is the core
    unit of event chaining and flow control.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        try:
            self.event = schema['event_id']
        except KeyError:
            raise SchemaError("{0} schema missing required field "
                              "``event_id``".format(type(self)))
        self.initialized = True

    def do(self, player, world, interface):
        return {
            'type': 'eventstream',
            'id': self.event
        }

    def __dict__(self):
        return {
            'type': 'branch',
            'event': self.event
        }


class EventPrompt(Event):
    """ An event that presents the user with a menu of choices and returns the
    selection, after optionally printing a prompt message.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        try:
            self.choices = schema['choices']
        except KeyError:
            raise SchemaError("{0} schema missing required field "
                              "``choices``".format(type(self)))
        self.initialized = True

    def do(self, player, world, interface):
        choice = interface.menu_choice(
            [choice['label'] for choice in self.choices]
        )
        for item in self.choices:
            if item['label'] == choice:
                return {
                    'type': 'eventstream',
                    'id': item['branch']
                }
        raise RuntimeError("interface a selection that wasn't in the list "
                           "of options")

    def __dict__(self):
        return {
            'type': 'prompt',
            'choices': self.choices
        }


class EventModifyResource(Event):
    """ An event that modifies existing states, e.g. counters or strings.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventAppendResource(Event):
    """ An event that adds a new resource to an existing set of states on an
    object, at the end of the list.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventPrependResource(Event):
    """ An event that adds a new resource to an existing set of states on an
    object, at the beginning of the list.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventRemoveResource(Event):
    """ An event that deletes a resource from the set of states on an existing
    object.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventNpc(Event):
    """ An event that represents an encounter with an NPC.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        try:
            self.npc_id = schema['npc_id']
        except KeyError:
            raise SchemaError("{0} schema missing required field "
                              "``npc_id``".format(type(self)))
        self.initialized = True

    def do(self, player, world, interface):
        npc_events = player.get_state(
            'world.npc.{0}.events'.format(self.npc_id)
        )
        return [
            {
                'type': 'eventstream',
                'id': event_id
            }
            for event_id
            in npc_events
        ]

    def __dict__(self):
        return {
            'type': 'npc',
            'npc_id': self.npc_id
        }


class EventImplode(Event):
    """ An event that de-registers the event from the current event
    context, thus preventing it from happening in the same way in the future.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        self.event = event.get_id()
        self.initialized = True

    def do(self, player, world, interface):
        context = player.current_locale
        context_type = type(get_locale_by_id(context)).__name__.lower()
        if context_type in ['town', 'dungeon']:
            context_type = 'locale'
        state_path = 'world.{0}.{1}.events'.format(context_type,
                                                   context)
        registered = player.get_state(state_path)
        player.set_state(state_path, [event for event in registered if event
        != self.event])

    def __dict__(self):
        return {
            'type': 'implode'
        }


class EventRetire(Event):
    """ An event that de-registers the event from the current event
    context, thus preventing it from happening in the same way in the future.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        self.event = event.get_id()
        self.initialized = True

    def do(self, player, world, interface):
        raise NotImplementedError()
        # TODO: figure out a reasonably efficient means to scan all
        #  EventContexts and remove this context from all of them.
        for context_type in ['locale', 'npc', 'monster']:
            pass
        state_path = 'world.{0}.{1}.events'.format(context_type,
                                                   context)
        registered = player.get_state(state_path)
        player.set_state(state_path, [event for event in registered if event
                                      != self.event])

    def __dict__(self):
        return {
            'type': 'retire'
        }


class EventSetFlag(Event):
    """ An event that enables a state flag
    """
    supported_scopes = [
        'npc',
        'monster',
        'dungeon',
        'town'
    ]

    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        path_prefix = None
        for key in schema:
            if key in self.supported_scopes:
                if path_prefix:
                    keys = schema.keys()
                    del keys['flag_id']
                    del keys['type']
                    raise SchemaError("unable to load event set_flag - a flag "
                                      "cannot be set on multiple scopes at "
                                      "the same time [{0}]"
                                      .format(', '.join(keys)))
                path_prefix = 'world.{0}.{1}'.format(key, schema[key])
                self.scope = {key: schema[key]}
        if not path_prefix:
            path_prefix = 'pc'
        try:
            self.flag_id = schema['flag_id']
        except KeyError:
            raise SchemaError("{0} schema missing required field "
                              "``flag_id``".format(type(self)))
        self.flag_state_path = '.'.join([path_prefix, 'flags', self.flag_id])
        self.initialized = True

    def do(self, player, world, interface):
        player.set_state(state_path=self.flag_state_path, value=True)

    def __dict__(self):
        ret = {
            'type': 'set_flag',
            'flag_id': self.flag_id,
        }
        try:
            ret.update(self.scope)
        except AttributeError:
            pass
        return ret


class EventClearFlag(Event):
    """ An event that enables a state flag
    """
    supported_scopes = [
        'npc',
        'monster',
        'dungeon',
        'town'
    ]

    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        path_prefix = None
        for key in schema:
            if key in self.supported_scopes:
                if path_prefix:
                    keys = schema.keys()
                    del keys['flag_id']
                    del keys['type']
                    raise SchemaError("unable to load event clear_flag - a "
                                      "flag cannot be cleared on multiple "
                                      "scopes at the same time [{0}]"
                                      .format(', '.join(keys)))
                path_prefix = 'world.{0}.{1}'.format(key, schema[key])
                self.scope = {key: schema[key]}
        if not path_prefix:
            path_prefix = 'pc'
        try:
            self.flag_id = schema['flag_id']
        except KeyError:
            raise SchemaError("{0} schema missing required field "
                              "``flag_id``".format(type(self)))
        self.flag_state_path = '.'.join([path_prefix, 'flags', self.flag_id])
        self.initialized = True

    def do(self, player, world, interface):
        player.set_state(state_path=self.flag_state_path, value=False)

    def __dict__(self):
        ret = {
            'type': 'clear_flag',
            'flag_id': self.flag_id,
        }
        try:
            ret.update(self.scope)
        except AttributeError:
            pass
        return ret


class EventDoTrigger(Event):
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventSetEncounterEvent(Event):
    def __init__(self, schema, event, condition=None):
        try:
            self.npc = schema['npc']
        except KeyError:
            raise SchemaError("{0} schema missing required field "
                              "``npc``".format(type(self)))
        try:
            self.event_id = schema['event_id']
        except KeyError:
            raise SchemaError("{0} schema missing required field "
                              "``event_id``".format(type(self)))
        super().__init__(schema, condition)

    def do(self, player, world, interface):
        player.set_state('world.npc.{0}.encounter_event'.format(self.npc),
                         self.event_id)

    def __dict__(self):
        return {
            'type': 'set_encounter_event',
            'npc': self.npc,
            'event_id': self.event_id,
        }


_event_constructors = {
    'text': EventText,
    'branch': EventBranch,
    'modify_resource': EventModifyResource,
    'prompt': EventPrompt,
    'npc': EventNpc,
    'implode': EventImplode,
    'set_flag': EventSetFlag,
    'clear_flag': EventClearFlag,
    'trigger': EventDoTrigger,
    'begin_fight': EventBeginFight,
    'set_encounter_event': EventSetEncounterEvent,
}
