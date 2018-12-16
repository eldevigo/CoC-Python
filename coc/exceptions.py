class COCException(Exception):
    """ Parent class for all coc-secific exception types
    """
    def __init__(self, msg=None):
        super().__init__(msg)

class LoadError(COCException):
    """ Exception type for all logical issues with loading game state and assets
    """
    def __init__(self, msg=None):
        super().__init__(msg)

class ExitMenuException(COCException):
    """ Exception type for backing out of a menu
    """
    def __init__(self, msg=None):
        super().__init__(msg)

class NotPermittedError(COCException):
    """ Exception raised when inter-class permissions prevent an action
    """
    def __init__(self, msg=None):
        super().__init__(msg)

class ImmutablePropertyError(NotPermittedError):
    """ Exception raised when trying to set immutable attributes on an
    initialized Immutable object
    """
    def __init__(self, attr, classname):
        super().__init__("``{0}.{1}`` is immutable after initialization")
