from . import valuemanager
FloatArrayValue = valuemanager.get_class('floatarray')
from . import ResultValue

__all__ = ['ResultFloatArrayValue']

class ResultFloatArrayValue(ResultValue, FloatArrayValue):
    pass
