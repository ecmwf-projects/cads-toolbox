import inspect
import types
import typing as T
from functools import wraps

import emohawk
import numpy as np
import xarray as xr

UNION_TYPES = [T.Union, types.UnionType]
EMPTY_TYPES = [inspect._empty]
DEFAULT_KWARG_TYPES = {
    "dataarray": xr.DataArray,
    "dataset": xr.DataSet,
    "data": np.ndarray,
}


def cadsify_module(module, decorator):
    for name in dir(module):
        func = getattr(module, name)
        if isinstance(func, types.FunctionType):
            setattr(module, name, decorator(func))


def cadsify_function(function, **kwarg_types):
    kwarg_types = {**DEFAULT_KWARG_TYPES, **kwarg_types}
    signature = inspect.signature(function)

    @wraps(function)
    def wrapper(*args, **kwargs):
        mapping = cadsify_mapping(signature, kwarg_types, *args, **kwargs)

        for arg, name in zip(args, signature.parameters):
            kwargs[name] = arg

        for key, value in kwargs.items():
            kwarg_type = mapping[key]
            if kwarg_type is not None:
                kwargs[key] = emohawk.transform(value, kwarg_type)

        return function(**kwargs)

    return wrapper


def cadsify_mapping(signature, kwarg_types, *args, **kwargs):
    mapping = {}
    for key, parameter in signature.parameters.items():
        annotation = parameter.annotation
        if annotation not in EMPTY_TYPES:
            if T.get_origin(annotation) in UNION_TYPES:
                kwarg_type = T.get_args(annotation)
            else:
                kwarg_type = annotation
        else:
            kwarg_type = kwarg_types.get(key)
        mapping[key] = kwarg_type
    return mapping
