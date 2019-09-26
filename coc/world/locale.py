from coc import EventContext
from coc.exceptions import LoadError, NotPermittedError, ObjectNotFoundError

locale_registry = dict()


class Locale(EventContext):
    """ Common base class for all visitable locations in the world, incl.
    towns, dungeons, and wilderness areas.
    """


    def __init__(self, schema):
        super().__init__(schema)

    def visit(self, player):
        return self.get_event_streams(player)

    def get_event_streams(self, player):
        raise NotImplementedError()

    def get_state_template(self):
        raise NotImplementedError()

    def get_id(self):
        return self.id_


# TODO: Let's come up with a more elegant solution for this. Maybe it makes
#   sense to have all locale subclasses register themselves in a shared locale
#   registry instead, and come up with a scheme to derive the locale type.
# Maybe it makes more sense just to brute force search. Probably there won't be
#   that many locales to handle.
def get_by_id(id_):
    try:
        return locale_registry[id_]
    except KeyError:
        raise ObjectNotFoundError("locale ``" + id_ +
                                  "`` was not found in the locale registry")


def get_all_locales():
    return locale_registry.values()


def register_locale(id_, locale):
    if not isinstance(locale, Locale):
        raise NotPermittedError("Cannot register non-Locale object to locale"
                                " registry - object type is ``{}``".format(
                                    type(locale)
                                )
        )
    elif id_ in locale_registry:
        raise LoadError("attempted to load event ``{0}`` but that event id"
                        " already exists".format(id_))
    else:
        locale_registry[id_] = locale
