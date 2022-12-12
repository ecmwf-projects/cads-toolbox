import inspect
import types
import typing as T
from functools import wraps

import emohawk
import numpy as np
import xarray as xr

from cads_toolbox.catalogue import Remote

UNION_TYPES = [T.Union, types.UnionType]
EMPTY_TYPES = [inspect._empty]
DEFAULT_KWARG_TYPES = {
    "dataarray": xr.DataArray,
    "dataset": xr.Dataset,
    "data": np.ndarray,
}


def ensure_iterable(input_item):
    """Ensure that an item is iterable"""
    if not isinstance(input_item, (tuple, list, dict)):
        return [input_item]
    return input_item



def transform(thing, kwarg_type):
    """Wrapper of emohawk.transform such that it also handles cads-toolbox Remote objects"""
    if type(thing) == Remote:
        thing = thing.data
    return emohawk.transform(thing, kwarg_type)


def cadsify_function(function, **kwarg_types):
    """
    Cadsify a function (need a better name!). This function acts as a wrapper
    such that emohawk will handle the input arg/kwarg format.
    """
    def _wrapper(kwarg_types, *args, **kwargs):
        kwarg_types = {**DEFAULT_KWARG_TYPES, **kwarg_types}
        signature = inspect.signature(function)
        mapping = cadsify_mapping(signature, kwarg_types)

        for arg, name in zip(args, signature.parameters):
            kwargs[name] = arg
        # transform kwargs if necessary
        for key, value in [(k,v) for k,v in kwargs.items() if k in mapping]:
            kwarg_types = ensure_iterable(mapping[key])
            # Loop over all potential input formats and transform if necessary
            for kwarg_type in kwarg_types:
                if kwarg_type is type(value):
                    break
            else:
                try:
                    kwargs[key] = transform(value, kwarg_types[0])
                except:
                    # Transform was not possible, so leave item is it is and let the
                    # function handle the rest
                    pass

        result = function(**kwargs)

        return result

    @wraps(function)
    def wrapper(*args, **kwargs):
        return _wrapper(kwarg_types, *args, **kwargs)
    
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



def cadsify_module(module, decorator=cadsify_function):
    for name in dir(module):
        func = getattr(module, name)
        if isinstance(func, types.FunctionType):
            setattr(module, name, decorator(func))
    return module
