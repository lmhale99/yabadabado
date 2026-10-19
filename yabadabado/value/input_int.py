from . import valuemanager
IntValue = valuemanager.get_class('int')
from . import InputValue

__all__ = ['InputIntValue']

class InputIntValue(InputValue, IntValue):
    pass
