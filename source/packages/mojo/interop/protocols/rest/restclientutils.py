
__author__ = "Myron Walker"
__copyright__ = "Copyright 2023, Myron W Walker"
__credits__ = []

import dataclasses
import urllib.parse

def normalize_query_arg_value(val) -> str:
    """
        Converts values to a normalized string that cen be used to fill a query string.
    """

    norm_val = None

    if type(val) == int:
        norm_val = val
    else:
        norm_val = urllib.parse.quote(val)

    return norm_val


def convert_to_foundation_datatype(val) -> dict:
    """
        Helper function for converting a value to a dictionary.
    """

    dval = None

    if dataclasses.is_dataclass(val):
        dval = dataclasses.asdict(val)
    elif hasattr(val, "as_dict"):
        dval = val.as_dict()
    elif isinstance(val, str) or isinstance(val, int) or isinstance(val, dict):
        dval = val
    elif isinstance(val, list) or isinstance(val, tuple):
        dval = [ convert_to_foundation_datatype(item) for item in val ]
    else:
        errmsg = f"Unable to convert value of type='{type(val)}' to a dictionary."
        raise ValueError(errmsg)
    
    return dval