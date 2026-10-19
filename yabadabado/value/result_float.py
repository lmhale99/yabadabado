from . import valuemanager
FloatValue = valuemanager.get_class('float')
from . import ResultValue

__all__ = ['ResultFloatValue']

class ResultFloatValue(ResultValue, FloatValue):
    pass
