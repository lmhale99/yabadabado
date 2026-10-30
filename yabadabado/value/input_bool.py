from . import valuemanager
BoolValue = valuemanager.get_class('bool')
from . import InputValue

__all__ = ['InputBoolValue']

class InputBoolValue(InputValue, BoolValue):
    pass
