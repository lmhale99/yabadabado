from . import valuemanager
LongStrValue = valuemanager.get_class('longstr')
from . import InputValue

__all__ = ['InputLongStrValue']

class InputLongStrValue(InputValue, LongStrValue):
    pass
