from . import valuemanager
IntArrayValue = valuemanager.get_class('intarray')
from . import InputValue

__all__ = ['InputIntArrayValue']

class InputIntArrayValue(InputValue, IntArrayValue):
    pass