from typing import Any, Literal

from yabadaba.record import Record

# Import parent class
from . import valuemanager
RecordSubsetValue = valuemanager.get_class('recordsubset')

__all__ = ['CalculationSubsetValue']

class CalculationSubsetValue(RecordSubsetValue):
    
    def __init__(self,
                 name: str,
                 record: Record,
                 recordclass: str | type[Record],
                 defaultvalue: Any | None = None,
                 valuerequired: bool = False,
                 allowedvalues: tuple | None = None,
                 allowcustomvalue: bool = False,
                 metadatakey: str | Literal[False] | None = None,
                 metadataparent: str | None = None,
                 metadataprefix: str = '',
                 modelpath: str | Literal[False] | None = None,
                 description: str | None = None,
                 loadorder: int = 9999999,
                 **kwargs):
        """
        Initialize a Value that is a record object.  Allows for the reuse of
        common subsets across multiple records.

        Note: Many of the default Value parameter settings are limited or not
        used by this style. Read below!

        Parameters
        ----------
        name : str
            The name of the parameter.  This should correspond to the name of
            the associated class attribute.
        record : Record
            The Record object that the Value is used with, i.e. which record
            is it contained within.
        recordclass : str or class
            The type of record that this value represents.  Given either as a
            string record style or a Record class.
        defaultvalue : any or None, optional
            The default value to use for the property.  If given, then it must
            be an object of recordclass.  If None (default), a new empty object
            of recordclass will be created and set as the value.
        valuerequired: bool, optional
            This is meaningless for record subsets as an associated record
            object will always exist for the value.
        allowedvalues : tuple or None, optional
            Must be None (default) for record subsets as the data is complex.
        allowcustomvalue : bool, optional
            Determines how allowedvalues is interpreted. If False (default) then
            values are restricted to what is listed in allowedvalues.  If True,
            then the value is not restricted and allowedvalues becomes a list of
            recommended values.
        metadatakey: str, bool or None, optional
            Must be None or False for record subset values, where None is the
            default behavior and False indicates no metadata keys from the subset
            will be added to the parent record's metadata.
        metadataparent: str or None, optional
            If given, then this indicates that the metadatakey is actually an
            element of a dict in metadata with this name.  This allows for limited
            support for metadata having embedded dicts.
        metadataprefix: str or None, optional
            This specifies a prefix to add to the beginning of all of the subset's
            metadata keys when incorporated into the parent record's metadata.
            This makes it possible to avoid key name overlaps.  Default value is '',
            i.e. no prefix.
        modelpath: str or None, optional
            The period-delimited path after the record root element for
            where the parameter will be found in the built data model.  If set
            to None (default) then name will be used for modelpath.  Note that the
            final path name will override the subset's modelroot.
        description: str or None, optional
            A short description for the value.
        """

        super().__init__(name, record, recordclass, defaultvalue=defaultvalue,
                         valuerequired=valuerequired, allowedvalues=allowedvalues,
                         allowcustomvalue=allowcustomvalue,
                         metadatakey=metadatakey, metadataparent=metadataparent,
                         metadataprefix=metadataprefix,
                         modelpath=modelpath, description=description)

        # Save values to class attributes
        self.__loadorder = loadorder

    @property
    def style(self) -> str:
        """str: The value style"""
        return 'calculation_subset'

    def load_parameters(self, input_dict: dict):
        self.value.load_parameters(input_dict)

    @property
    def loadorder(self) -> int:
        """int: Specifies the load_parameter sorting order for the value"""
        return self.__loadorder

    @property
    def templatekeys(self) -> list:
        """list : The calculation-specific input keys."""
        return self.value.templatekeys

    @property
    def preparekeys(self) -> list:
        """list : The calculation-specific input keys."""
        return self.value.preparekeys

    @property
    def interpretkeys(self) -> list:
        """list : The calculation-specific input keys."""
        return self.value.interpretkeys

    def calc_inputs(self, kwargs: dict):
        """
        Adds values to the kwargs dict for the calculation function
        """
        kwargs.update(self.value.calc_inputs())