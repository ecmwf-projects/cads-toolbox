"""
Module containing methods to transform the inputs of functions based on the function type setting,
common signitures or mapping defined at call time
"""
import inspect
import types
import typing as T
from functools import wraps

import emohawk
import numpy as np
import xarray as xr

from cads_toolbox.catalogue import Remote

try:
    UNION_TYPES = [T.Union, types.UnionType]
except AttributeError:
    # This sort of Union is not allowed in versions of python<3.9
    UNION_TYPES = [
        T.Union,
    ]

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


def transform(obj, kwarg_type):
    """Wrapper of emohawk.transform such that it also handles cads-toolbox Remote objects"""
    if isinstance(obj, Remote):
        obj = obj.data
    return emohawk.transform(obj, kwarg_type)


def transform_function_inputs(function, **kwarg_types):
    """
    Transform the inputs to a function to match the requirements.
    This function acts as a wrapper such that emohawk will handle the input arg/kwarg format.
    """

    def _wrapper(kwarg_types, *args, **kwargs):
        kwarg_types = {**DEFAULT_KWARG_TYPES, **kwarg_types}
        signature = inspect.signature(function)
        mapping = signature_mapping(signature, kwarg_types)

        for arg, name in zip(args, signature.parameters):
            kwargs[name] = arg
        # transform kwargs if necessary
        for key, value in [(k, v) for k, v in kwargs.items() if k in mapping]:
            kwarg_types = ensure_iterable(mapping[key])
            # Transform value if necessary
            if type(value) not in kwarg_types:
                for kwarg_type in kwarg_types:
                    try:
                        kwargs[key] = transform(value, kwarg_type)
                    except ValueError:
                        # Transform was not possible, move to next kwarg type.
                        # If no trnasform is possible, format is unchanged and we rely on function to raise
                        # an Error.
                        continue
                    break

        result = function(**kwargs)

        return result

    @wraps(function)
    def wrapper(*args, **kwargs):
        return _wrapper(kwarg_types, *args, **kwargs)

    return wrapper


def signature_mapping(signature, kwarg_types):
    """
    Map args and kwargs to object types, using hierarchical selection method:
    1. Type setting
    2. Explicitly defined type
    3. Do nothing
    """
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


def transform_module_inputs(module, decorator=transform_function_inputs):
    """
    Transform the inputs to all functions in a module.
    """
    for name in dir(module):
        func = getattr(module, name)
        if isinstance(func, types.FunctionType):
            setattr(module, name, decorator(func))
    return module
