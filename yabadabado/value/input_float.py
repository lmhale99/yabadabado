from typing import Any, Literal

# Import parent record styles
from . import InputValue
from . import valuemanager
FloatValue = valuemanager.get_class('float')

import yabadaba
uc = yabadaba.unitconvert

__all__ = ['InputFloatValue']

class InputFloatValue(InputValue, FloatValue):

    def __init__(self,
                 name: str,
                 record,
                 defaultvalue: Any | None = None,
                 valuerequired: bool = True,
                 allowedvalues: tuple | None = None,
                 allowcustomvalue: bool = False,
                 metadatakey: str | Literal[False] | None = None,
                 metadataparent: str | None = None,
                 modelpath: str | Literal[False] | None = None,
                 description: str | None = None,
                 loadorder: int = 9999999,
                 calcname: str | bool | None = None,
                 templatekey: str | None = None,
                 templatedoc: str = '',
                 is_compare_term: bool = False,
                 compare_fterm_tol: float | None = None,
                 unit: str | None = None,
                 defaultunit: str | None = None):
        """
        Initialize an InputFloatValue object for calculation inputs.
        
        Parameters
        ----------
        name : str
            The name of the parameter.  This should correspond to the name of
            the associated class attribute.
        record : Record, optional
            The Record object that the Parameter is used with.
        defaultvalue : any or None, optional
            The default value to use for the property.  The default value of
            None indicates that there is no default value.
        valuerequired: bool, optional
            Indicates if a value must be given for the property.  If True, then
            checks will be performed that a value is assigned to the property.
            Should be True for input values.
        allowedvalues : tuple or None, optional
            A list/tuple of values that the parameter is restricted to have.
            Setting this to None (default) indicates any value is allowed.
        metadatakey: str, bool or None, optional
            The key name to use for the property when constructing the record
            metadata dict.  If set to None (default) then name will be used for
            metadatakey.  If set to False then the parameter will not be
            included in the metadata dict.
        metadataparent: str or None, optional
            If given, then this indicates that the metadatakey is actually an
            element of a dict in metadata with this name.  This allows for limited
            support for metadata having embedded dicts.
        modelpath: str or None, optional
            The period-delimited path after the record root element for
            where the parameter will be found in the built data model.  If set
            to None (default) then name will be used for modelpath.
        loadorder: int, optional
            Provides a sorting parameter for identifying when the value should
            be set by load_parameters(); the lower the loadorder the earlier
            the value will be set.  This allows for some values to be dependent
            on other values that have already been set. Default is 9999999
            indicating that no other values are expected to depend on it.
        calcname: str or None, optional
            The name of the input parameter for the calculation function
            that corresponds to this value.  If set to None
            (default) then name will be used for calcname.
        templatekey: str or None, optional
            The name of the input file/template key that corresponds to this
            value.  If set to None (default) then name will be used for
            templatekey.
        templatedoc: str, optional
            The description of the template parameter to include in the
            calculation's templatedoc documentation.  Default value is '',
            i.e. no information.
        is_compare_term: bool, optional
            Indicates if the corresponding metadata value is included in
            the compare_terms list for direct comparison of values for
            determining the uniqueness of the calculation.  Default value
            is False (not included in compare_terms).
        compare_fterm_tol: float or None, optional
            An absolute tolerance to associate with the metadata value for use
            in the compare_fterms dict of the calculation to determine
            uniqueness.  If None (default) then the value will not be included
            in compare_fterms.  If a float value is given then the term will
            be included in compare_fterms with the given tolerance.
        unit: str, optional
            The units to use when saving the value in a database.  A value of
            None (default) indicates that no unit conversions should be done.
        defaultunit: str, optional
            The default units for the value when set during load_parameters().
            If the parent record has a units calculation subset then this can
            contain placeholder terms matching the units styles that can be
            set. A value of None (default) indicates that no unit conversions
            should be done.

        """
        super().__init__(name, record, defaultvalue,
                         valuerequired = valuerequired,
                         allowedvalues = allowedvalues,
                         allowcustomvalue = allowcustomvalue,
                         metadatakey = metadatakey,
                         metadataparent = metadataparent,
                         modelpath = modelpath,
                         description = description,
                         loadorder = loadorder,
                         calcname = calcname,
                         templatekey = templatekey,
                         templatedoc = templatedoc,
                         is_compare_term = is_compare_term,
                         compare_fterm_tol = compare_fterm_tol,
                         unit = unit)

        self.__defaultunit = defaultunit


    @property
    def defaultunit(self) -> str | None:
        """str or None: The default units to use"""
        return self.__defaultunit

    def load_parameters_value(self, val: Any) -> Any:
        """
        Function to modify values when reading them in from an input parameter
        file.
        """
        try:
            # Try converting the full val to a float
            val = float(val)
        
        except ValueError as e:
            # If float conversion fails, then it should be 'val unit'
            val = uc.set_in_units(val)
        
        else:
            # Fill in defaultunit with specified units
            if self.defaultunit is not None and hasattr(self.record, 'units'):
                defaultunit = self.record.units.fillunit(self.defaultunit)
            else:
                defaultunit = self.defaultunit
            
            # Set float val in defaultunit
            val = uc.set_in_units(val, defaultunit)
        
        return val