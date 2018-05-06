from fractions import Fraction

from modules import CastableToInt, PositiveInt, transform_args, transform_return


@transform_args(CastableToInt, CastableToInt)
@transform_return(PositiveInt)
def lcm(a, b):
    numerator = abs(a * b)
    while b:
        a, b = b, a % b
    denominator = a
    return Fraction(numerator, denominator)
