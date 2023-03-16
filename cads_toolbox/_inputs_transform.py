"""
Module containing methods to transform the inputs of functions based on the function type setting,
common signitures or mapping defined at call time
"""
import inspect
import types
import typing as T
from functools import wraps

import emohawk

from cads_toolbox.catalogue import Remote


def _to_dataarray(dataset):
    if type(dataset).__name__ == "Dataset":
        return dataset.to_array()
    else:
        return dataset


TRANSFORM_METHODS = {
    "xarray.core.dataset.Dataset": lambda x: x.to_xarray(),
    "xarray.core.dataarray.DataArray": lambda x: _to_dataarray(x.to_xarray()),
    "numpy.ndarray": lambda x: x.to_numpy(),
    "pandas.core.frame.DataFrame": lambda x: x.to_pandas(),
}

EMPTY_TYPES = [inspect._empty]
DEFAULT_KWARG_TYPES = {
    "dataarray": "xarray.core.dataarray.DataArray",
    "dataset": "xarray.core.dataset.Dataset",
    "data": "numpy.ndarray",
}

try:
    UNION_TYPES = [T.Union, types.UnionType]
except AttributeError:
    # This sort of Union is not allowed in versions of python<3.9
    UNION_TYPES = [T.Union]


def stringify(obj_type):
    """Convert a full class name and import path to a string."""
    if not isinstance(obj_type, str):
        obj_type = f"{obj_type.__module__}.{obj_type.__name__}"
    return obj_type


def ensure_iterable(input_item):
    """Ensure that an item is iterable"""
    if not isinstance(input_item, (tuple, list, dict)):
        return [input_item]
    return input_item


def transform(source, target_type):
    if isinstance(source, Remote):
        source = source.data
    else:
        try:
            source = emohawk.load_from("file", source)
        except TypeError:
            # If we don't understand the input type, we should do nothing
            print("KHJKSDAFGH")
            return source
    target_string = stringify(target_type)
    if target_string in TRANSFORM_METHODS:
        method = TRANSFORM_METHODS[target_string]
    else:
        raise TypeError(f"No transformation method found for {target_string}")
    return method(source)


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


def is_decorated(func):
    return getattr(func, '_transform_applied', False)


def transform_module_inputs(module, decorator=transform_function_inputs):
    """
    Transform the inputs to all functions in a module.
    """
    for name in dir(module):
        func = getattr(module, name)
        if name.startswith("_") or is_decorated(func):
            continue
        if isinstance(func, types.FunctionType):
            func._transform_applied = True
            setattr(module, name, decorator(func))
    return module

transform_module_inputs._transform_applied = True