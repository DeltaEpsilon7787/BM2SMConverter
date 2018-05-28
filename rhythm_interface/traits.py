class TraitError(Exception):
    def __init__(self, trait_name=None, source_name=None):
        self.trait_name = trait_name
        self.source_name = source_name


class UndefinedTraitError(TraitError):
    pass


class ImmutableTraitError(TraitError):
    pass


class TraitMeta(type):
    """A metaclass used to implement traits.

    Search for attributes named in __traits__ and make them a trait.
    A trait is a one-time set property if initial value is None or not defined
        otherwise it's a constant.
    Once the value of a trait is set, it can be read, but not modified.
    For the sake of IDEs and such, it's recommended to define an empty attribute of the same name.
    It will be displaced in favor of the trait anyway.
    Attempting to read the trait before setting it will raise UndefinedTraitError
    Attempting to set the trait after setting it will raise ImmutableTraitError
    """

    __traits__ = []

    def __new__(mcs, name, bases, attributes):
        def constant_property(property_name):
            def read_value(self):
                return getattr(self, '_' + property_name)

            def set_value(self, value):
                raise ImmutableTraitError(trait_name=property_name,
                                          source_name=name)

            return property(read_value, set_value)

        def make_trait_property(property_name):
            has_been_set = False

            def read_value(self):
                nonlocal has_been_set
                if not has_been_set:
                    raise UndefinedTraitError(trait_name=property_name,
                                              source_name=name)
                return getattr(self, '_' + property_name)

            def set_value(self, value):
                nonlocal has_been_set
                if has_been_set:
                    raise ImmutableTraitError(trait_name=property_name,
                                              source_name=name)
                setattr(self, '_' + property_name, value)
                has_been_set = True

            return property(read_value, set_value)

        changed_attributes = attributes.copy()
        traits = attributes.get('__traits__', [])
        for attr_name in traits:
            try:
                if changed_attributes[attr_name] is not None:
                    changed_attributes[attr_name] = constant_property(attr_name)
                    changed_attributes['_' + attr_name] = changed_attributes[attr_name]
                else:
                    raise KeyError
            except KeyError:
                changed_attributes[attr_name] = make_trait_property(attr_name)
                changed_attributes['_' + attr_name] = None

        return super(TraitMeta, mcs).__new__(mcs, name, bases, changed_attributes)
