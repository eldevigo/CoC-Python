from coc import EventContext
from coc.exceptions import *


class Locale(EventContext):
    """ Common base class for all visitable locations in the world, incl. towns,
    dungeons, and wilderness areas.
    """
    def __init__(self, schema):
        super().__init__()


    def visit(self, player):
        return self.get_event_stream(player)

    def get_event_streams(self, player):
        raise NotImplementedError()

    def get_state_template(self):
        raise NotImplementedError()

# TODO: Let's come up with a more elegant solution for this. Maybe it makes
#   sense to have all locale subclasses register themselves in a shared locale
#   registry instead, and come up with a scheme to derive the locale type.
# Maye it makes more sense just to brute force search. Probably there won't be
#   that many locales to handle.
def get_by_id(id_):
    try:
        return town.get_by_id(id_)
    except ObjectNotFoundError:
        try:
            return dungeon.get_by_id(id_)
        except ObjectNotFoundError:
            pass
        raise ObjectNotFoundError("locale ``" + id_ +
                                  "`` was not found in the town or dungeon "
                                  "registry")
