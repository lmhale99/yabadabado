from . import valuemanager
StrListValue = valuemanager.get_class('strlist')
from . import ResultValue

__all__ = ['ResultStrListValue']

class ResultStrListValue(ResultValue, StrListValue):
    pass
