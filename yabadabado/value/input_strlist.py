from . import valuemanager
StrListValue = valuemanager.get_class('strlist')
from . import InputValue

__all__ = ['InputStrListValue']

class InputStrListValue(InputValue, StrListValue):

    def load_parameters_value(self, val):
        """
        Function to modify values when reading them in from an input parameter
        file.
        """
        return val.split()