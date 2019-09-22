from coc import Immutable
from coc.exceptions import *

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

        self.sequence = [
                load_sequence_item(item) for item in schema['sequence']]
        global event_registry
        if schema['id'] in event_registry:
            raise LoadError("attempted to load event ``{0}`` but that event id "
                            "already exists".format(schema['id']))
        event_registry[schema['id']] = self
        self.initialized = True

    def run(self, state):
        seq = self.sequence

        def _generator():
            for item in seq:
                if item.check_condition(state):
                    yield item
        return _generator


def get_all():
    return event_registry.values()


def get_by_id(id_):
    try:
        return event_registry[id_]
    except KeyError as e:
        raise ObjectNotFoundError("event ``" + entity_id +
                                  "`` was not found in the event registry"
                                  ) from e


class EventSequenceItem(Immutable):
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


class EventText(EventSequenceItem):
    """ An event sequence item containing a block of text. This is the core
    event sequence type for game content.
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.text = schema['text']
        self.initialized = True

    def do(self, interface, setfunc):
        interface.print(self.text)


class EventBranch(EventSequenceItem):
    """ An event item that jumps to another Event or EventStream. This is the
    core unit of event chaining and flow control.
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, interface, setfunc):
        raise NotImplementedError()

class EventPrompt(EventSequenceItem):
    """ An event that presents the user with a menu of choices and returns the
    selection, after optionally printing a prompt message.
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, interface, setfunc):
        raise NotImplementedError()


class EventModifyResource(EventSequenceItem):
    """ An event that modifies existing states, e.g. counters or strings.
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, interface, setfunc):
        raise NotImplementedError()


class EventAppendResource(EventSequenceItem):
    """ An event that adds a new resource to an existing set of states on an
    object, at the end of the list.
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, interface, setfunc):
        raise NotImplementedError()


class EventPrependResource(EventSequenceItem):
    """ An event that adds a new resource to an existing set of states on an
    object, at the beginning of the list.
>>>>>>> Stashed changes
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, interface, setfunc):
        raise NotImplementedError()

class EventRemoveResource(EventSequenceItem):
    """ An event that deletes a resource from the set of states on an existing
    object.
    """
    def __init__(self, schema, condition=None):
        super().__init__(schema, condition)
        self.initialized = True

    def do(self, interface, setfunc):
        raise NotImplementedError()

def implode(schema):
    # TODO: return an EventRemoveResource object that removes itself from the
    # current locale context's registered events
    raise NotImplementedError()


sequence_constructors = {
        'render_text': EventText,
        'branch': EventBranch,
        'modify_resource': EventModifyResource,
        'prompt': EventPrompt,
        'implode': implode,
        }
