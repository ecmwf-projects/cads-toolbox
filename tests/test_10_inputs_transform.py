import pytest
import xarray as xr
import numpy as np
import pandas as pd

import cads_toolbox as ct
from cads_toolbox import inputs_transform


def dummy_ndarray_function(
    value: np.ndarray
):
    assert type(value)==np.ndarray

def dummy_dataset_function(
    value: xr.Dataset
):
    assert type(value)==xr.Dataset

def dummy_dataarray_function(
    value: xr.DataArray
):
    assert type(value)==xr.DataArray

def dummy_dataframe_function(
    value: pd.DataFrame
):
    assert type(value)==pd.DataFrame


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


def test_transform_function_inputs():
    da = xr.DataArray(
        np.arange(10)*2., name='test', dims=['x'], coords={'x':np.arange(10)}
    )
    ds = da.to_dataset()
    nd = da.values
    transformed_numpy_function = inputs_transform._transform_function_inputs(
        dummy_ndarray_function
    )
    transformed_numpy_function(nd)
    transformed_numpy_function(da)
    transformed_numpy_function(ds)

    transformed_dataset_function = inputs_transform._transform_function_inputs(
        dummy_dataset_function
    )
    transformed_dataset_function(da)
    transformed_dataset_function(ds)


    transformed_dataarray_function = inputs_transform._transform_function_inputs(
        dummy_dataarray_function
    )
    transformed_dataarray_function(da)
    # transformed_dataarray_function(ds)  # NOT YET IMPLEMENTED IN emohawk

    transformed_dataframe_function = inputs_transform._transform_function_inputs(
        dummy_dataframe_function
    )
    # transformed_dataframe_function(nd)  # NOT YET IMPLEMENT IN emohawk
    transformed_dataframe_function(da)
    transformed_dataframe_function(ds)

