from . import valuemanager
StrValue = valuemanager.get_class('str')
from . import InputValue

__all__ = ['InputStrValue']

class InputStrValue(InputValue, StrValue):
    pass
