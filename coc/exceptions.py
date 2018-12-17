class COCException(Exception):
    """ Parent class for all coc-secific exception types
    """
    def __init__(self, msg=None, **kwargs):
        super().__init__(msg)

class LoadError(COCException):
    """ Exception type for all logical issues with loading game state and assets
    """
    def __init__(self, msg=None):
        super().__init__(msg)

class InterfaceException(COCException):
    """
    """
    def __init__(self, msg=None):
        super().__init__(msg)

class ExitMenuException(InterfaceException):
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

class SchemaError(COCException):
    """ Generic error for syntactic or structural issues with the world schema
    """
    def __init__(self, msg=None, **kwargs):
        super().__init__(msg)

class EntityNotFoundError(SchemaError):
    """ Raised when a request to the entity registry fails to find something
    """
    def __init__(self, msg=None, **kwargs):
        super().__init__(msg)
