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
        mapping = cadsify_mapping(signature, kwarg_types)

        # add args to kwargs
        for arg, name in zip(args, signature.parameters):
            kwargs[name] = arg

        # transform kwargs if necessary
        for key, value in [(k,v) for k,v in kwargs.items() if k in mapping]:
            kwarg_types = ensure_iterable(mapping[key])
            for kwarg_type in kwarg_types:
                if kwarg_type is type(value):
                    break
            else:
                kwargs[key] = emohawk.transform(value, kwarg_types[0])

        return function(**kwargs)

    return wrapper


def cadsify_mapping(signature, kwarg_types):
    mapping = {}
    for key, parameter in signature.parameters.items():
        annotation = parameter.annotation
        if annotation not in EMPTY_TYPES:
            # 1. Use type setting from function
            if T.get_origin(annotation) in UNION_TYPES:
                kwarg_type = T.get_args(annotation)
            else:
                kwarg_type = annotation
        elif key in kwarg_types:
            # 2. Check for specifically assigned format
            kwarg_type = kwarg_types.get(key)
        else:
            # 3. Do nothing, cannot assign None, as None is a valid type
            continue
        mapping[key] = kwarg_type
    return mapping


def ensure_iterable(input_item):
    if not any([isinstance(input_item, _type) for _type in [tuple, list, dict, iter]]):
        return [input_item]
    return input_item