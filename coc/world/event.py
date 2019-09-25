from abc import ABC, abstractmethod
from coc import Immutable
from coc.exceptions import LoadError, ObjectNotFoundError, SchemaError

event_registry = dict()


class Event(Immutable):
    """ Represents a narrative sequence, including conditional components and
    usually terminating at a conditional branch, a fight, or a decision menu.
    """
    def __init__(self, schema):
        super().__init__()

        def load_sequence_item(seq_schema):
            try:
                seq_type = seq_schema['type']
            except TypeError:
                seq_type = 'text'
                seq_schema = {'text': seq_schema}
            global sequence_constructors
            return sequence_constructors[seq_type](seq_schema)

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
        self.id_ = schema['id']
        event_registry[self.id_] = self
        self.initialized = True

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
    def __init__(self, schema, condition=None):
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
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.text = schema['text']
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
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.event = schema['event']
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
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        try:
            self.choices = schema['choices']
        except KeyError:
            raise SchemaError("Unable to load event sequence prompt - the "
                              "prompt is missing a choices section")
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
    def __init__(self, schema, condition=None):
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
    def __init__(self, schema, condition=None):
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
    def __init__(self, schema, condition=None):
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
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, player, world, interface):
        raise NotImplementedError()

    def __dict__(self):
        raise NotImplementedError()


class EventNpc(EventSequenceItem):
    """ An event that represents an encounter with an NPC.
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.npc_id = schema['npc_id']
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
    """ An event that represents an encounter with an NPC.
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, player, world, interface):
        # TODO: return an EventRemoveResource object that removes itself
        # from the current locale context's registered events
        raise NotImplementedError()

    def __dict__(self):
        return {
            'type': 'implode'
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

    def __init__(self, schema, condition=None):
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
        self.flag_id = schema['flag_id']
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


class EventUnsetFlag(EventSequenceItem):
    """ An event that enables a state flag
    """
    supported_scopes = [
        'npc',
        'monster',
        'dungeon',
        'town'
    ]

    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        path_prefix = None
        for key in schema:
            if key in self.supported_scopes:
                if path_prefix:
                    keys = schema.keys()
                    del keys['flag_id']
                    del keys['type']
                    raise SchemaError("unable to load event sequence "
                                      "unset_flag - a flag cannot be unset on "
                                      "multiple scopes at the same time [{0}]"
                                      .format(', '.join(keys)))
                path_prefix = 'world.{0}.{1}'.format(key, schema[key])
                self.scope = {key: schema[key]}
        if not path_prefix:
            path_prefix = 'pc'
        self.flag_id = schema['flag_id']
        self.flag_state_path = '.'.join([path_prefix, 'flags', self.flag_id])
        self.initialized = True

    def do(self, player, world, interface):
        player.set_state(state_path=self.flag_state_path, value=False)

    def __dict__(self):
        ret = {
            'type': 'unset_flag',
            'flag_id': self.flag_id,
        }
        try:
            ret.update(self.scope)
        except AttributeError:
            pass
        return ret




sequence_constructors = {
        'text': EventText,
        'branch': EventBranch,
        'modify_resource': EventModifyResource,
        'prompt': EventPrompt,
        'npc': EventNpc,
        'implode': EventImplode,
        'set_flag': EventSetFlag,
        'unset_flag': EventUnsetFlag,
        }
