import coucal

from cads_toolbox.cadsify import cadsify_function, cadsify_module


daily_mean = cadsify_function(
    coucal.aggregate.daily_mean,
)

daily_max = cadsify_function(
    coucal.aggregate.daily_max,
)

aggregate = cadsify_module(coucal, cadsify_function)