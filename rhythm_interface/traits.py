class TraitMeta(type):
    def __new__(mcs, name, bases, attributes):
        current_init = set(attributes['__init_kwarg_required__'])
        for base in bases:
            try:
                if base.__additional_init_kwarg_required__:
                    current_init |= base.__additional_init_kwarg_required__
            except AttributeError:
                continue
        attributes['__init_kwarg_required__'] = current_init
        return super(TraitMeta, mcs).__new__(mcs, name, bases, attributes)


class RhythmObject(object, metaclass=TraitMeta):
    __init_kwarg_allowed__ = {}
    __additional_init_kwarg_allowed__ = {}

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            if k not in self.__init_kwarg_allowed__:
                raise ValueError('Incorrect init of {} with {}'.format(self.__class__.__name__,
                                                                       kwargs))
            setattr(self, k, v)

    def convert_to(self, other_type):
        """Attempt to convert this object to another object

        Arguments:
            other_type (RhythmObject):
                Which type to try to convert to?

        Returns:
            other_type:
                Converted object

        Raises:
            TypeError:
                If this object cannot be converted to `other_type`
            """
        raise TypeError


class RhythmTime(RhythmObject):
    __init_kwarg_allowed__ = {'abstract_time'}


class AbsoluteTime(RhythmTime):
    __init_kwarg_allowed__ = {'abstract_absolute_time'}


class RelativeTime(RhythmTime):
    __init_kwarg_allowed__ = {'abstract_relative_time'}


class Keyed(RhythmObject):
    __init_kwarg_allowed__ = {'abstract_key'}


class Fundamental(RhythmObject):
    __init_kwarg_allowed__ = {'abstract_fundamental_value'}


class Declarative(RhythmObject):
    __init_kwarg_allowed__ = {'abstract_value'}


class Structural(RhythmTime):
    __additional_init_kwarg_allowed__ = {'abstract_time', 'abstract_value'}
