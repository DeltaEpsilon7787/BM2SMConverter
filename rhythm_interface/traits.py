class TraitError(Exception):
    pass


class TraitMeta(type):
    """A metaclass used to implement traits.

    Search for attributes ending with _trait and make them one-time set property.
    Once the value is set, it can be read, but not modified.
    Attempting to read the attribute before setting it will raise TraitError
    Attempting to set the attribute after setting it will raise TraitError
    """

    def __new__(mcs, name, bases, attributes):
        def make_trait_property(property_name):
            has_been_set = False

            def read_value(self):
                nonlocal has_been_set
                if not has_been_set:
                    raise TraitError('Trait {} must be defined for {}'.format(property_name, name))
                return getattr(self, '_' + property_name)

            def set_value(self, value):
                nonlocal has_been_set
                if has_been_set:
                    raise TraitError('Trait {} has already been defined for {}'.format(property_name, name))
                setattr(self, '_' + property_name, value)
                has_been_set = True

            return property(read_value, set_value)

        changed_attributes = attributes.copy()
        for attr_name, attr_value in attributes.items():
            if not attr_name.endswith('_trait'):
                continue
            changed_attributes[attr_name] = make_trait_property(attr_name)
            changed_attributes['_' + attr_name] = attr_value
        return super(TraitMeta, mcs).__new__(mcs, name, bases, changed_attributes)


class RhythmObject(object, metaclass=TraitMeta):
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
    abstract_time_trait = None


class AbsoluteTime(RhythmTime):
    abstract_absolute_time_trait = None


class RelativeTime(RhythmTime):
    abstract_relative_time_trait = None


class Keyed(RhythmObject):
    abstract_key_trait = None


class Fundamental(RhythmObject):
    abstract_fundamental_value_trait = None


class Declarative(RhythmObject):
    abstract_value_trait = None


class Structural(RhythmTime):
    abstract_time_trait = None
    abstract_value_trait = None
