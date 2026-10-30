from . import valuemanager
LongStrValue = valuemanager.get_class('longstr')
from . import ResultValue

__all__ = ['ResultLongStrValue']

class ResultLongStrValue(ResultValue, LongStrValue):
    pass
