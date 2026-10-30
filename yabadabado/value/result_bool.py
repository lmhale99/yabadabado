from . import valuemanager
BoolValue = valuemanager.get_class('bool')
from . import ResultValue

__all__ = ['ResultBoolValue']

class ResultBoolValue(ResultValue, BoolValue):
    pass
