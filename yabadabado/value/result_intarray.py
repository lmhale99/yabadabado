from . import valuemanager
IntArrayValue = valuemanager.get_class('intarray')
from . import ResultValue

__all__ = ['ResultIntArrayValue']

class ResultIntArrayValue(ResultValue, IntArrayValue):
    pass
