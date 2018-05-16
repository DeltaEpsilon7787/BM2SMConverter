from rhythm_interface.singletons import Key

class BasicObject(object):
    """Abstract class representing a game object."""
    key = ...  # type: Key
    position = ...  # type PositionalFraction
