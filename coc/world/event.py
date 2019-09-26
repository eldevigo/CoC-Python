from abc import ABC, abstractmethod
from coc import Immutable
from coc.exceptions import LoadError, ObjectNotFoundError, SchemaError
from coc.world.locale import get_by_id as get_locale_by_id

event_registry = dict()


class Event(Immutable):
    """ Represents a narrative sequence, including conditional components and
    usually terminating at a conditional branch, a fight, or a decision menu.
    """
    def __init__(self, schema):
        def load_sequence_item(seq_schema):
            try:
                seq_type = seq_schema['type']
            except TypeError:
                seq_type = 'text'
                seq_schema = {'text': seq_schema}
            global sequence_constructors
            return sequence_constructors[seq_type](seq_schema, self)

        super().__init__()
        self.id_ = schema['id']
        try:
            self.sequence = [
                    load_sequence_item(item) for item in schema['sequence']
            ]
        except KeyError as e:
            raise SchemaError("encountered an unknown sequence type ``{0}`` "
                              "while attempting to load event ``{1}``"
                              .format(e.args[0], schema['id']))
        global event_registry
        if schema['id'] in event_registry:
            raise LoadError("attempted to load event ``{0}`` but that event id"
                            " already exists".format(schema['id']))
        self.initialized = True
        event_registry[self.id_] = self

    def get_id(self):
        return self.id_

    def run(self, state_func):
        for item in self.sequence:
            if item.check_condition(state_func):
                yield item

    def __repr__(self):
        return repr({
            'id': self.id_,
            'sequence': [
                dict(item) for item in self.sequence
            ]
        })


def get_all():
    return event_registry.values()


def get_by_id(id_):
    try:
        return event_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("event ``" + id_ +
                                  "`` was not found in the event registry"
                                  ) from e


def is_loaded(id_):
    return id_ in event_registry


class EventSequenceItem(Immutable, ABC):
    """ Parent class for all event sequence items - represents a single step in
    an event stream.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__()
        self.condition = condition

    def check_condition(self, getfunc):
        if self.condition is None:
            return True
        else:
            return self.condition.test(getfunc)

    @abstractmethod
    def do(self, player, world, interface):
        pass

    @abstractmethod
    def __dict__(self):
        pass


class EventText(EventSequenceItem):
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


class EventBranch(EventSequenceItem):
    """ An event item that jumps to another Event or EventStream. This is the
    core unit of event chaining and flow control.
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
        return get_by_id(self.event)

    def __dict__(self):
        return {
            'type': 'branch',
            'event': self.event
        }


class EventPrompt(EventSequenceItem):
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
                return get_by_id(item['branch'])
        raise RuntimeError("interface a selection that wasn't in the list "
                           "of options")

    def __dict__(self):
        return {
            'type': 'prompt',
            'choices': self.choices
        }


class EventModifyResource(EventSequenceItem):
    """ An event that modifies existing states, e.g. counters or strings.
    """
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventAppendResource(EventSequenceItem):
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


class EventPrependResource(EventSequenceItem):
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


class EventRemoveResource(EventSequenceItem):
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


class EventNpc(EventSequenceItem):
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
        return [get_by_id(event_id) for event_id in npc_events]

    def __dict__(self):
        return {
            'type': 'npc',
            'npc_id': self.npc_id
        }


class EventImplode(EventSequenceItem):
    """ An event sequence that de-registers the event from the current event
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


class EventRetire(EventSequenceItem):
    """ An event sequence that de-registers the event from the current event
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


class EventSetFlag(EventSequenceItem):
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
                    raise SchemaError("unable to load event sequence set_flag "
                                      "- a flag cannot be set on multiple "
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


class EventClearFlag(EventSequenceItem):
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
                    raise SchemaError("unable to load event sequence "
                                      "clear_flag - a flag cannot be cleared "
                                      "on multiple scopes at the same time "
                                      "[{0}]".format(', '.join(keys)))
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


class EventDoTrigger(EventSequenceItem):
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventBeginFight(EventSequenceItem):
    def __init__(self, schema, event, condition=None):
        super().__init__(schema, condition)

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventSetEncounterEvent(EventSequenceItem):
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


sequence_constructors = {
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
