import pytest
import xarray as xr

import cads_toolbox as ct
from cads_toolbox import inputs_transform


@pytest.fixture
def request_args():
    return (
        "reanalysis-era5-single-levels",
        {
            "variable": "2m_temperature",
            "product_type": "reanalysis",
            "year": "2017",
            "month": "01",
            "day": "01",
            "time": "12:00",
            "grid": "10/10",
        },
    )


def test_ensure_iter():
    for thing in [list(), tuple(), dict()]:
        assert thing == inputs_transform.ensure_iterable(thing)

    for thing in ["string", 1, 1.0, inputs_transform, inputs_transform.ensure_iterable]:
        assert [thing] == inputs_transform.ensure_iterable(thing)


def test_transform(request_args):

    ct.config.USE_CACHE = False
    remote = ct.catalogue.retrieve(*request_args)
    transformed = inputs_transform.transform(remote, xr.Dataset)
    assert type(transformed) == xr.Dataset

    local = remote.data
    transformed = inputs_transform.transform(local, xr.Dataset)
    assert type(transformed) == xr.Dataset
