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

    Search for attributes ending with _trait and make them one-time set property.
    The name of the property is the same as the trait name, but without _trait.
    Once the value is set, it can be read, but not modified.
    Attempting to read the attribute before setting it will raise UndefinedTraitError
    Attempting to set the attribute after setting it will raise ImmutableTraitError
    """

    def __new__(mcs, name, bases, attributes):
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
        for attr_name, attr_value in attributes.items():
            if not attr_name.endswith('_trait'):
                continue
            changed_attributes[attr_name[:-6]] = make_trait_property(attr_name)
            changed_attributes['_' + attr_name] = attr_value
        return super(TraitMeta, mcs).__new__(mcs, name, bases, changed_attributes)
