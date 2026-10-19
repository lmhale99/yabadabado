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

class Calculation(Record):
    """Base class for managing calculations"""

############################# Core properties #################################

    def __init__(self,
                 model: Union[str, IOBase, DM, None] = None,
                 name: Optional[str] = None,
                 params: Union[str, Path, IOBase, dict, None] = None,
                 database = None,
                 noname: bool = False,
                 extensible: Optional[bool] = None,
                 **kwargs):
        """
        Initializes a Calculation object for a given style.

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
            raise TypeError("Don't use Calculation itself, only use derived classes")

        # Check for params
        if params is not None and model is not None:
            raise ValueError('model and params cannot both be given')

        self._init_calc()

        # Call Record's init
        super().__init__(model=model, name=name, database=database,
                         noname=noname, extensible=extensible, **kwargs)

        # Load parameters if given
        if params is not None:
            self.load_parameters(params, key=kwargs.get('key', None))

    @property
    def defaultname(self) -> Optional[str]:
        """str: The name to default to: key"""
        return self.key

    def _init_calc(self):
        """Sets the calculation's primary function, which should return a dict"""
        # Default to empty function that returns a dict
        self.calc = lambda: {}

    @property
    def maindoc(self) -> str:
        """str: the overview documentation for the calculation"""
        try:
            if hasattr(resources, 'files'):
                return resources.files(self.parent_module).joinpath('README.md').read_text(encoding='UTF-8')
            else:
                return resources.read_text(self.parent_module, 'README.md', encoding='UTF-8')
        except:
            return ""

    @property
    def theorydoc(self) -> str:
        """str: the methods and theory documentation for the calculation"""
        try:
            if hasattr(resources, 'files'):
                return resources.files(self.parent_module).joinpath('theory.md').read_text(encoding='UTF-8')
            else:
                return resources.read_text(self.parent_module, 'theory.md', encoding='UTF-8')
        except:
            return ""

    @property
    def filenames(self) -> list:
        """list: the names of each file used by the calculation."""        
        return []

    @property
    def files(self) -> dict:
        """dict: the names and contents of all required files."""
        files = {}
        for filename in self.filenames:
            files[filename] = resources.read_text(self.parent_module, filename)
        
        return files

    @property
    def parent_module(self) -> str:
        """str: The parent module where other related files should be located"""
        return '.'.join(self.__module__.split('.')[:-1])

    @property
    def calc_style(self) -> str:
        """str: The calculation style"""
        # Default to parent module's name
        return self.__module__.split('.')[-2]

    @property
    def style(self) -> str:
        """str: The record style for the calculation"""
        # Default to calc_style with calculation prefix
        return f'calculation_{self.calc_style}'

############################### Value handling ##############################

    def _init_values(self):
        """
        Method that defines the value objects for the Record.  This should
        call the super of this method, then use self._add_value to create new Value objects.
        Note that the order values are defined matters
        when build_model is called!!!
        """
        self._add_value('input_str', 'key',
                        defaultvalue = str(uuid.uuid4()),
                        calcname = False,
                        description = 'A unique uuid4 key for the calculation run')
        
        self._add_value('str', 'url',
                        modelpath = 'URL',
                        description = 'A URL where the calculation record can be found')

        self._add_value('str', 'yabadaba_version',
                        defaultvalue = yabadaba.__version__,
                        description = 'The version of yabadaba used')

        self._add_value('input_str', 'branch',
                        modelpath = 'calculation.branch',
                        defaultvalue = 'main',
                        calcname = False,
                        description = "The workflow branch associated with the calculation run")

        self._add_value('str', 'status',
                        modelpath = 'status',
                        defaultvalue = 'not calculated',
                        allowedvalues = ('not calculated', 'error', 'finished'),
                        description = 'The current status of the calculation run')

        self._add_value('longstr', 'error',
                        description = 'The error message raised by the calculation run if it failed')

        # Get the names of the base terms
        self.__base_names = self.valuenames

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
                        params: Union[str, Path, IOBase, dict],
                        key: Optional[str] = None):
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

        # Manually set key if given directly
        if key is not None:
            input_dict['key'] = key

        # Build list of input values sorted by loadorder
        input_objects = sorted([x for x in self.iter_input_objects()] +
                               [x for x in self.iter_calcsubset_objects()],
                               key = lambda x: x.loadorder)

        # Read parameters for each input value
        for input_object in input_objects:
            input_object.load_parameters(input_dict)

        # Update name if key was updated
        if 'key' in input_dict:
            self.name = self.key

    @property
    def templatekeys(self) -> dict:
        """dict : The calculation-specific input keys and their descriptions."""
        templatedict = {}
        for input_object in self.iter_input_objects():
            templatedict[input_object.templatekey] = input_object.templatedoc

        return templatedict

    @property
    def template(self) -> str:
        """str: The template to use for generating calc.in files."""
        # Start template
        lines = [f'# Input script for iprPy calculation {self.calc_style}', '']

        # Build common content
        lines += ['# Calculation Metadata']
        for input_object in self.iter_input_objects():
            name = input_object.name
            
            # Skip calc-specific values until below
            if name not in self.__base_names:
                continue

            # Build template line
            spacelen = 32 - len(name)
            if spacelen < 1:
                spacelen = 1
            space = ' ' * spacelen
            lines.append(f'{name}{space}<{name}>')
        lines.append('')

        # Build subset content
        for input_object in self.iter_calcsubset_objects():
            lines.append(input_object.value.template)

        # Build calculation-specific run parameters
        first = True
        for input_object in self.iter_input_objects():
            name = input_object.name
        
            # Skip common values as they were done above
            if name in self.__base_names:
                continue

            # Add header before first calc-specific value
            if first:
                lines += ['# Run Parameters']
                first = False

            # Build template line
            spacelen = 32 - len(name)
            if spacelen < 1:
                spacelen = 1
            space = ' ' * spacelen
            lines.append(f'{name}{space}<{name}>')

        # Join and return lines
        return '\n'.join(lines)      

    @property
    def templatedoc(self) -> str:
        """str: The documentation for the template lines for this calculation."""

        lines = [f'# Calculation {self.calc_style} Input Terms', '']

        # Build common content
        lines += ['## Calculation Metadata']
        for input_object in self.iter_input_objects():
            name = input_object.name
            
            # Skip calc-specific values until below
            if name not in self.__base_names:
                continue

            # Build template line
            doc = input_object.description
            lines.append(f'- __{name}__: {doc}')
        lines.append('')

        # Build subset content
        for input_object in self.iter_calcsubset_objects():
            lines.append(input_object.value.templatedoc)

        # Build calculation-specific run parameters
        first = True
        for input_object in self.iter_input_objects():
            name = input_object.name
        
            # Skip common values as they were done above
            if name in self.__base_names:
                continue

            # Add header before first calc-specific value
            if first:
                lines += ['## Run Parameters']
                first = False

            # Build template line
            doc = input_object.description
            lines.append(f'- __{name}__: {doc}')

        # Join and return lines
        return '\n'.join(lines)

    @property
    def singularkeys(self) -> list:
        """list: Calculation keys that can have single values during prepare."""
        return  ['branch']

    @property
    def multikeys(self) -> list:
        """list: Calculation key sets that can have multiple values during prepare."""
        return []

    @property
    def allkeys(self) -> list:
        """
        list: All keys used by the calculation.
        """
        # Build list of all keys
        allkeys = deepcopy(self.singularkeys)
        for keyset in self.multikeys:
            allkeys.extend(keyset)

        return allkeys

########################### Data model interactions ###########################

    @property
    def xsd_filename(self):
        """tuple: The module path and file name of the record's xsd schema"""
        return (self.parent_module, f'{self.style}.xsd')

    @property
    def xsl_filename(self):
        """tuple: The module path and file name of the record's xsl transform"""
        return (self.parent_module, f'{self.style}.xsl')

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


########################### Calculation interactions ##########################

    def clean(self,
              files=False,
              path: Union[str, Path] = '.'):
        """
        Resets the calculation state for running again.
        
        Parameters
        ----------
        files : bool, optional
            Setting this to True will also delete any files that were generated
            during the calculation's run.
        path : str or Path, optional
            The path to the calculation's run directory containing the files.
            Default value is '.': current working directory.  Only used if
            files=True.
        """
        self.__status = 'not calculated'
        self.__error = None

        if files:
            self.clean_files(path)

    @property
    def calc_output_files(self) -> list:
        """list : Glob path strings for files generated by this calculation"""
        return []

    def clean_files(self, path: Union[str, Path] = '.'):
        """
        Deletes any files generated by the calc function.
        
        Parameters
        ----------
        path : str or Path, optional
            The path to the calculation's run directory containing the files.
            Default value is '.': current working directory.
        """
        for file_glob in self.calc_output_files:
            for file in Path(path).glob(file_glob):
                file.unlink()

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

    def run(self,
            params: Union[str, dict, IOBase, None] = None,
            newkey: bool = False,
            results_json: bool = False,
            raise_error: bool = False,
            verbose: bool = False):
        """
        Runs the calculation using the current object attribute values or
        supplied parameters. Status after running will be either "finished"
        or "error".

        Parameters
        ----------
        params : dict, str or file-like object, optional
            The parameters or parameter file to read in.  If not given, will
            run based on the current object attribute values.
        newkey : bool, optional
            If True, then the calculation's key and name will be replaced with
            a new UUID4.  This allows for iterations on previous runs to be
            uniquely labeled.  Default value is False.
        results_json : bool, optional
            If True, then a "results.json" file will be generated following
            the run.
        raise_error : bool, optional
            The default behavior of run is to take any error messages from the
            calculation and set them to class attributes and save to
            results.json. This allows for calculations to successfully fail.
            Setting this to True will instead raise the errors, which can
            provide more details for debugging.
        verbose : bool, optional
            If True, a message relating to the calculation's status will be
            printed upon completion.  Default value is False.
        """
        # Clean record back to not calculated state
        self.clean()

        # Change the calculation's key if requested
        if newkey:
            self.key = self.name = str(uuid.uuid4())

        # Load params if given
        if params is not None:
            self.load_parameters(params)

        # Build calculation inputs
        input_dict = self.calc_inputs()

        try:
            # Pass inputs to calc function
            results_dict = self.calc(**input_dict)

        except Exception as e:
            if raise_error:
                raise e
            # Catch any error messages
            self.status = 'error'
            self.error = str(e)
            results_dict = None

        else:
            self.status = 'finished'
            self.process_results(results_dict)

        if verbose:
            if self.status == 'finished':
                print('Calculation finished successfully')
            else:
                print('Error:', self.error)

        # Save results to json
        if results_json is True:
            model = self.build_model()
            savesuccess = False
            savetries = 0
            while savetries < 5:
                try:
                    with open('results.json', 'w', encoding='UTF-8') as f:
                        model.json(fp=f, indent=4, ensure_ascii=False)
                except OSError:
                    savetries += 1
                else:
                    savesuccess = True
                    break

            if savesuccess is False:
                with open('results.json', 'w', encoding='UTF-8') as f:
                    model.json(fp=f, indent=4, ensure_ascii=False)
            
