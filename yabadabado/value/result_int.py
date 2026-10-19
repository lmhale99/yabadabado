from . import valuemanager
IntValue = valuemanager.get_class('int')
from . import ResultValue

__all__ = ['ResultIntValue']

class ResultIntValue(ResultValue, IntValue):
    pass
