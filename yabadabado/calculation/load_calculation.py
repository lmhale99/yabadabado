from . import calculationmanager

def load_calculation(style, **kwargs):
    """
    Loads a Calculation subclass associated with a given calculation style

    Parameters
    ----------
    style : str
        The calculation style
    
    Returns
    -------
    subclass of iprPy.calculation.Calculation 
        A Calculation object for the style
    """
    return calculationmanager.init(style, **kwargs)