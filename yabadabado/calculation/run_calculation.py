from io import IOBase
from pathlib import Path
from typing import Optional, Union

from yabadaba.tools import is_uuid

from . import Calculation, load_calculation

def run_calculation(params: Union[str, dict, IOBase, None] = None,
                    calc_style: str | None = None,
                    calc_key: str | None = None,
                    raise_error: bool = False,
                    verbose: bool = True):
    """
    Runs a calculation from a parameter file and outputs results to
    results.json.

    Parameters
    ----------
    params : dict, str or file-like object, optional
        The parameters or parameter file to read in.  If not given, will
        run based on the current object attribute values.
    calc_style : str, optional
        Specifies the style of calculation to run.  Optional if params is a
        path to a file where the file's name is calc_<calc_style>.in.
    calc_key : str, optional
        Allows for a calculation UUID key to be passed in.  If not given, then
        will check if the parent directory's name is a UUID key and will use it
        if possible.  Otherwise, a new UUID key will be assigned to the
        calculation.
    raise_error : bool, optional
        The default behavior of run is to take any error messages from the
        calculation and set them to class attributes and save to
        results.json. This allows for calculations to successfully fail.
        Setting this to True will instead raise the errors, which can
        provide more details for debugging.
    verbose : bool, optional
        If True, a message relating to the calculation's status will be
        printed upon completion.  Default value is True.
    """
    if calc_style is None:
        # Extract calc_style from filename
        if isinstance(params, (str, Path)):
            calc_style = Path(params).stem.replace('calc_', '')
        else:
            raise ValueError('calc_style not given and cannot be determined from params')

    kwargs = {}
    if calc_key is None:
        
        # If params is a file, check if its parent directory name is a uuid key
        if isinstance(params, (str, Path)):
            calc_key = Path(params).absolute().parent.name
        
        # Otherwise, check the name of the working directory
        else:
            calc_key = Path('.').absolute().name
        
        if is_uuid(calc_key):
            kwargs['key'] = calc_key

    else:
        # Check that given calc_key is a valid uuid key
        if not is_uuid(calc_key):
            raise ValueError('calc_key must be a uuid key!')
        kwargs['key'] = calc_key

    # Load calculation style and read in paramfile
    calculation: Calculation = load_calculation(calc_style, params=params, **kwargs)
    
    # Run and create results_json
    calculation.run(results_json=True, raise_error=raise_error, verbose=verbose)
    