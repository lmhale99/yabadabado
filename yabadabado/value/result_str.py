from . import valuemanager
StrValue = valuemanager.get_class('str')
from . import ResultValue

__all__ = ['ResultStrValue']

class ResultStrValue(ResultValue, StrValue):
    pass
