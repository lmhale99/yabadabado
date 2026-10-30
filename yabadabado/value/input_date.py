from . import valuemanager
DateValue = valuemanager.get_class('date')
from . import InputValue

__all__ = ['InputDateValue']

class InputDateValue(InputValue, DateValue):
    pass
