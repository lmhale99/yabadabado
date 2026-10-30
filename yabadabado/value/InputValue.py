from typing import Any, Literal

from yabadaba.value import Value

__all__ = ['InputValue']

class InputValue(Value):
    """Base input value class"""

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
                 templatedoc: str | None = None,
                 is_compare_term: bool = False,
                 compare_fterm_tol: float | None = None,
                 **kwargs):
        """
        Initialize an InputValue object for calculation inputs.

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
            The base name for any input file parameters associated with the
            value. If the value has a single input parameter, then this is the
            name of that parameter. Otherwise, this is the prefix to use for
            all associated input parameters.  If set to None (default) then
            name will be used for templatekey.
        templatedoc: str or None, optional
            If the value has a single input parameter, then this is its
            description include in the calculation's templatedoc documentation.
            If set to None (default) then the value's description will be used.
            For values with multiple input parameters this is ignored and
            the descriptions must be defined when the class overrides the
            templatedoc() attribute.
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
        **kwargs
            Any extra keyword arguments for the sibling Value classes.
        """
        # Call parent super
        super().__init__(name, record,
                         defaultvalue=defaultvalue,
                         valuerequired=valuerequired,
                         allowedvalues=allowedvalues,
                         allowcustomvalue=allowcustomvalue,
                         metadatakey=metadatakey,
                         metadataparent=metadataparent,
                         modelpath=modelpath,
                         description=description, **kwargs)
        
        # Set default calcname
        if calcname is None:
            calcname = self.name
        elif isinstance(calcname, bool):
            if calcname is True:
                raise TypeError('calcname can be None, False, or str')
        else:
            calcname = str(calcname)
        
        # Set default templatekey
        if templatekey is None:
            templatekey = self.name

        # Set default templatedoc
        if templatedoc is None:
            templatedoc = self.description
        
        # Check compare term/fterm settings
        if is_compare_term is True and compare_fterm_tol is not None:
            raise ValueError('value cannot be added to both compare_terms and compare_fterms')
        if compare_fterm_tol is not None:
            compare_fterm_tol = float(compare_fterm_tol)

        # Save values to class attributes
        self.__is_compare_term = bool(is_compare_term)
        self.__compare_fterm_tol = compare_fterm_tol
        self.__calcname =  calcname
        self.__templatekey = templatekey
        self.__templatedoc = templatedoc
        self.__loadorder = loadorder
    
    def load_parameters_value(self, val: Any) -> Any:
        """
        Function to modify values when reading them in from an input parameter
        file.
        """
        return val

    def load_parameters(self, input_dict: dict):
        """
        Reads in the templatekey value from the input parameter file and
        saves it to the class attribute value.
        """
        if len(self.templatekeys) == 1:
        
            if self.valuerequired is True and self.defaultvalue is None:
                val = input_dict[self.templatekeys[0]]
            else:
                val = input_dict.get(self.templatekeys[0], self.defaultvalue)
            
            self.value = self.load_parameters_value(val)

    @property
    def is_compare_term(self) -> bool:
        """bool: Indicates if the value should be in compare_terms"""
        return self.__is_compare_term
    
    @property
    def compare_fterm_tol(self) -> float | None:
        """float or None: tolerance to use for the value in compare_fterms"""
        return self.__compare_fterm_tol
    
    @property
    def calcname(self) -> str | bool:
        """str or bool: The calculation function parameter name to use"""
        return self.__calcname
    
    @property
    def templatekeys(self) -> list[str]:
        """
        list : The input parameter keys found in the text input parameter file
        associated with the value. Any keys listed here will be included in the
        generated template and templatedoc content. These keys must have simple
        string value representations.
        """
        # Single input parameter example
        return [self.__templatekey]

        # Multiple input parameter example:
        #return [
        #    f'{self.__templatekey}term1',
        #    f'{self.__templatekey}term2',
        #    ...
        #]

    @property
    def templatedoc(self) -> str:
        """str: The parameter description to use in templatedoc"""
        # Single input parameter example
        return f'- __{self.__templatekey}__: {self.__templatedoc}'

        # # Multiple input parameter example:
        #return '\n'.join([
        #    f'- __{self.__templatekey}term1__: Description of input term1',
        #    f'- __{self.__templatekey}term2__: Description of input term2',
        #    ...
        #])

    @property
    def preparekeys(self) -> list[str]:
        """
        list : All input parameter keys in the input_dict passed to
        load_parameters() that are associated with this value and used during
        prepare. This should be all templatekeys plus extra fields where
        pre-loaded content can be directly given. Typically, the extra terms are
        named "_content" and contain file contents so prepare can check input
        validity and uniqueness prior to copying the files to a calculation
        folder.
        """
        return list(self.templatekeys) + [
            #f'{self.__templatekey}_content' # Example
        ]

    @property
    def interpretkeys(self) -> list[str]:
        """
        list : All keys in load_parameter's input_dict that the value interacts
        with. This should be preparekeys plus any extra keys that are modified
        or created that can then be subsequently used by other values
        """
        return self.preparekeys + [
        ]
    
    @property
    def loadorder(self) -> int:
        """int: Specifies the load_parameter sorting order for the value"""
        return self.__loadorder
    
    def calc_inputs_value(self):
        """Function to modify values when passing them to the calculation function"""
        return self.value

    def calc_inputs(self, kwargs: dict):
        """
        Adds the value to the kwargs dict for the calculation function
        """
        if self.calcname is not False:
            kwargs[self.calcname] = self.calc_inputs_value()

