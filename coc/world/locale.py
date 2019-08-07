from coc import EventContext
from coc.exceptions import *


class Locale(EventContext):
    """ Common base class for all visitable locations in the world, incl. towns,
    dungeons, and wilderness areas.
    """
    def __init__(self, schema):
        super().__init__()


# TODO: Let's come up with a more elegant solution for this. Maybe it makes
#   sense to have all locale subclasses register themselves in a shared locale
#   registry instead, and come up with a scheme to derive the locale type.
# Maye it makes more sense just to brute force search. Probably there won't be
#   that many locales to handle.
def get_by_id(id_):
    try:
        return get_town_by_id(id_)
    except ObjectNotFoundError:
        try:
            return get_dungeon_by_id(id_)
        except ObjectNotFoundError:
            pass
        raise ObjectNotFoundError("locale ``" + id_ +
                                  "`` was not found in the town or dungeon "
                                  "registry")
