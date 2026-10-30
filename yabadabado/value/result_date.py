from . import valuemanager
DateValue = valuemanager.get_class('date')
from . import ResultValue

__all__ = ['ResultDateValue']

class ResultDateValue(ResultValue, DateValue):
    pass
