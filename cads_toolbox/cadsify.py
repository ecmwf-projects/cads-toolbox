from functools import wraps
import types
import inspect
import typing as T
import numpy as np
import xarray as xr

import emohawk

UNION_TYPES = [T.Union, types.UnionType]
EMPTY_TYPES = [inspect._empty]


STANDARD_MAPPING = {
    'dataarray': xr.DataArray,
    'dataset': xr.DataSet,
    'data': np.ndarray,
}


def cadsify_module(module, decorator):
    for name in dir(module):
        func = getattr(module, name)
        if isinstance(func, types.FunctionType):
            setattr(module, name, decorator(func))


def cadsify_function(function, **_non_standard_mapping):
    def wrapper(*args, **kwargs):
        mapping = cadsify_mapping(function, _non_standard_mapping)
        new_kwargs = {}
        for arg, name in zip(args, inspect.signature(function).parameters):
            if name in mapping:
                new_kwargs[name] = emohawk.transform(arg, mapping[name])
            else:
                new_kwargs[name] = arg
        for name in kwargs:
            if name in mapping:
                new_kwargs[name] = emohawk.transform(kwargs[name], mapping[name])
            else:
                new_kwargs[name] = kwargs[name]

        return function(**new_kwargs)
    return wrapper



def cadsify_mapping(function, _non_standard_mapping):
    mapping = {}
    signature = inspect.signature(function)
    for thing in signature.parameters:
        annotation = signature.parameters[thing].annotation
        if thing in _non_standard_mapping:
            # 1. Check if cads-toolbox specifically assigns a required format
            required_format = _non_standard_mapping[thing]
        elif annotation not in EMPTY_TYPES:
            # 2. Use type setting
            if T.get_origin(annotation) in UNION_TYPES:
                required_format = T.get_args(annotation)
            else:
                required_format = annotation
        elif thing in STANDARD_MAPPING:
            # 3. Use standard signature mapping
            required_format = STANDARD_MAPPING[thing]
        else:
            # 4. Do nothing
            continue
        mapping[thing] = required_format
    
    return mapping



    
