from functools import wraps

def cadsify_function(function):
    # Wrapper to ensure inputs to function are appropriate for the
    # function.
    # Tasks:
    #  ensure docstrings are imported
    #  data objects correct format
    #  args+kwargs correctly parsed.

    @wraps(function)
    def _function(*args, **kwargs):
        function(*args, **kwargs)

    return _function

