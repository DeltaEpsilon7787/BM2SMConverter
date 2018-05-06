import operator
from fractions import Fraction
from functools import partial


class Castable(object):
    cast_fail_message = "{it} cannot be converted to {class_name}"  # type: str

    @staticmethod
    def caster(it):
        return it

    @staticmethod
    def discretizer(it):
        return it

    @staticmethod
    def pre_check(_):
        return True

    @staticmethod
    def post_check(_):
        return True

    def __new__(cls, it, caller=None):
        fail_message = cls.cast_fail_message.format(it=it,
                                                    class_name=cls.__name__)
        if caller is not None:
            fail_message += '; source: {}'.format(caller.__name__)

        if not cls.pre_check(it):
            raise ValueError(fail_message)
        try:
            value = cls.caster(it)
        except ValueError:
            raise ValueError(fail_message)
        if not cls.post_check(value):
            raise ValueError(fail_message)
        value = cls.discretizer(value)

        return value


class CastableToInt(Castable, int):
    caster = int

    @staticmethod
    def pre_check(it):
        try:
            int(it)
        except ValueError:
            return False
        return True


class CastableToFraction(Castable, Fraction):
    @staticmethod
    def caster(it):
        return Fraction(it)

    @staticmethod
    def pre_check(it):
        try:
            Fraction(it)
        except ValueError:
            return False
        return True


class Negative(Castable):
    post_check = partial(operator.gt, 0)


class NonPositive(Castable):
    post_check = partial(operator.ge, 0)


class NonZero(Castable):
    post_check = partial(operator.ne, 0)


class Zero(Castable):
    post_check = partial(operator.eq, 0)


class NonNegative(Castable):
    post_check = partial(operator.le, 0)


class Positive(Castable):
    post_check = partial(operator.lt, 0)


class NegativeInt(CastableToInt, Negative):
    pass


class NegativeFraction(CastableToFraction, Negative):
    pass


class NonPositiveInt(CastableToInt, NonPositive):
    pass


class NonPositiveFraction(CastableToFraction, NonPositive):
    pass


class NonZeroInt(CastableToInt, NonZero):
    pass


class NonZeroFraction(CastableToFraction, NonZero):
    pass


class ZeroInt(CastableToInt, Zero):
    pass


class ZeroFraction(CastableToFraction, Zero):
    pass


class NonNegativeInt(CastableToInt, NonNegative):
    pass


class NonNegativeFraction(CastableToFraction, NonNegative):
    pass


class PositiveInt(CastableToInt, Positive):
    pass


class PositiveFraction(CastableToFraction, Positive):
    pass
