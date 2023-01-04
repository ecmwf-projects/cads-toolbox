"""
analysis is a wrapper for coucal which has its own unit tests.
Here we check that the modules and methods exist.
"""

from types import ModuleType

import cads_toolbox.analysis as cta

AGGREGATE_METHODS = [
    "daily_max",
    "daily_mean",
    "daily_min",
    "monthly_mean",
    "reduce",
    "resample",
    "rolling_reduce"
]

CLIMATE_METHODS = [
    "anomaly",
    "climatology_max",
    "climatology_mean",
    "climatology_median",
    "climatology_min",
    "climatology_percentiles",
    "climatology_quantiles",
    "climatology_std",
]

def test_aggregate() -> None:
    assert isinstance(cta.aggregate, ModuleType)

    for method in AGGREGATE_METHODS:
        assert method in dir(cta.aggregate)


def test_climate() -> None:
    assert isinstance(cta.climate, ModuleType)

    for method in CLIMATE_METHODS:
        assert method in dir(cta.climate)