# coding: utf-8
# Standard Python libraries
from io import IOBase
from pathlib import Path
from typing import Optional, Union, Generator, Any
from importlib import resources
from copy import deepcopy

from DataModelDict import DataModelDict as DM

import uuid

import yabadaba
from yabadaba.record import Record

from ..value.InputValue import InputValue
from ..value.ResultValue import ResultValue
from ..value.calculation_subset import CalculationSubsetValue
from ..input import parse

class CalculationSubset(Record):
    """Base class for managing calculations"""

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 database = None,
                 noname: bool = True,
                 extensible: Optional[bool] = None,
                 **kwargs):
        """
        Initializes a CalculationSubset object for a given style.

        Parameters
        ----------
        model : str, file-like object or DataModelDict, optional
            Record content in data model format to read in.  Cannot be given
            with params.
        name : str, optional
            The name to use for saving the record.  By default, this should be
            the calculation's key.
        database : yabadaba.Database, optional
            A default Database to associate with the Record, typically the
            Database that the Record was obtained from.  Can allow for Record
            methods to perform Database operations without needing to specify
            which Database to use.
        params : str, file-like object or dict, optional
            Calculation input parameters or input parameter file.  Cannot be
            given with model.
        **kwargs : any
            Any other core Calculation record attributes to set according to 
            :class:`atomman.library.record.Record`.  Cannot be
            given with model.
        """
        # Throw error for default class
        if self.__module__ == __name__:
            raise TypeError("Don't use CalculationSubset itself, only use derived classes")

        # Call Record's init
        super().__init__(model=model, name=name, database=database,
                         noname=noname, extensible=extensible, **kwargs)

    @property
    def modelroot(self) -> str:
        """str: The model root for the calculation subset"""
        return 'units'

    @property
    def style(self) -> str:
        """str: The record style for the calculation subset"""
        return 'units'

############################### Value handling ##############################

    def iter_input_objects(self) -> Generator[InputValue, Any, Any]:
        """Iterates over the class's input value objects"""
        for value_object in self.value_objects:
            if isinstance(value_object, InputValue):
                yield value_object

    def iter_result_objects(self) -> Generator[ResultValue, Any, Any]:
            """Iterates over the class's result value objects"""
            for value_object in self.value_objects:
                if isinstance(value_object, ResultValue):
                    yield value_object 

    def iter_calcsubset_objects(self) -> Generator[CalculationSubsetValue, Any, Any]:
            """Iterates over the class's calculation subset value objects"""
            for value_object in self.value_objects:
                if isinstance(value_object, CalculationSubsetValue):
                    yield value_object

##################### Parameter file interactions ###########################

    def load_parameters(self,
                        params: Union[str, Path, IOBase, dict]):
        """
        Reads in and sets calculation parameters.

        Parameters
        ----------
        params : dict, str or file-like object
            The parameters or parameter file to read in.
        key : str, optional
            A new key value to assign to the object.  If not given, will use
            calc_key field in params if it exists, or leave the key value
            unchanged.
        """
        # Parse params to input_dict if needed
        if isinstance(params, dict):
            input_dict = params
        else:
            input_dict = parse(params, allsingular=True)

        # Build list of input values sorted by loadorder
        input_objects = sorted([x for x in self.iter_input_objects()] +
                               [x for x in self.iter_calcsubset_objects()],
                               key = lambda x: x.loadorder)

        # Read parameters for each input value
        for input_object in input_objects:
            input_object.load_parameters(input_dict)

    @property
    def template_header(self) -> str:
        return '# Input/Output Units'

    @property
    def template(self) -> str:
        """str: The template to use for generating calc.in files."""

        # Build subset content
        lines = []
        i = -1
        for i, input_object in enumerate(self.iter_input_objects()):
            
            if i == 0:
                # Add header before first value
                lines.append(self.template_header)
            
            # Build template line
            name = input_object.name
            spacelen = 32 - len(name)
            if spacelen < 1:
                spacelen = 1
            space = ' ' * spacelen
            lines.append(f'{name}{space}<{name}>')
        
        if i >= 0:
            # Add extra newline if parameters were added
            lines.append('')

        # Build subset content
        for input_object in self.iter_calcsubset_objects():
            lines.append(input_object.value.template)

        # Join and return lines
        return '\n'.join(lines)

    @property
    def templatedoc(self) -> str:
        """str: The documentation for the template lines for this calculation."""

        # Build subset content
        lines = []
        i = -1
        for i, input_object in enumerate(self.iter_input_objects()):
            
            if i == 0:
                # Add header before first value
                lines.append('#' + self.template_header)
            
            # Build template line
            name = input_object.name
            doc = input_object.description
            lines.append(f'- __{name}__: {doc}')
        
        if i >= 0:
            # Add extra newline if parameters were added
            lines.append('')

        # Build subset content
        for input_object in self.iter_calcsubset_objects():
            lines.append(input_object.value.templatedoc)

        # Join and return lines
        return '\n'.join(lines)

    @property
    def singularkeys(self) -> list:
        """list: Calculation keys that can have single values during prepare."""
        return  []

    @property
    def multikeys(self) -> list:
        """list: Calculation key sets that can have multiple values during prepare."""
        return []

########################### Data model interactions ###########################

    @property
    def compare_terms(self) -> list:
        """list: The terms to compare metadata values absolutely."""
        terms = []
        for input_object in self.iter_input_objects():
            if input_object.is_compare_term:
                terms.append(input_object.name)
        return terms

    @property
    def compare_fterms(self):
        """dict: The terms to compare metadata values using a tolerance."""
        fterms = {}
        for input_object in self.iter_input_objects():
            if input_object.compare_fterm_tol is not None:
                fterms[input_object.name] = input_object.compare_fterm_tol
        return fterms

    def calc_inputs(self) -> dict:
        """Builds calculation inputs from the class's attributes"""
        inputs = {}
        for input_object in self.iter_input_objects():
            input_object.calc_inputs(inputs)

        return inputs

    def process_results(self, results_dict: dict) -> None:
        """
        Processes calculation results and saves them to the object's results
        attributes.

        Parameters
        ----------
        results_dict: dict
            The dictionary returned by the calc() method.
        """
        for result_object in self.iter_result_objects():
            result_object.process_results(results_dict)
