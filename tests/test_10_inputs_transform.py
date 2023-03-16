import os

import numpy as np
import pandas as pd
import pytest
import xarray as xr

import cads_toolbox as ct
from cads_toolbox import _inputs_transform


XARRAY_DATASET_CLASS_STRING = "xarray.core.dataset.Dataset"


TEST_NC = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "tests", "data", "test.nc")


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
        },
    )

def dummy_ndarray_function_typeset(value: np.ndarray):
    assert isinstance(value, np.ndarray)


def dummy_ndarray_function_signature(data):
    assert isinstance(data, np.ndarray)


def dummy_dataset_function_typeset(value: xr.Dataset):
    assert isinstance(value, xr.Dataset)


def dummy_dataset_function_signature(dataset):
    assert isinstance(dataset, xr.Dataset)


def dummy_dataarray_function_signature(dataarray):
    assert isinstance(dataarray, xr.DataArray)


def dummy_dataarray_function_typeset(value: xr.DataArray):
    assert isinstance(value, xr.DataArray)


def dummy_dataframe_function(value: pd.DataFrame):
    assert isinstance(value, pd.DataFrame)


def test_ensure_iter():
    for thing in [list(), tuple(), dict()]:
        assert thing == _inputs_transform.ensure_iterable(thing)

    for thing in [
        "string",
        1,
        1.0,
        _inputs_transform,
        _inputs_transform.ensure_iterable,
    ]:
        assert [thing] == _inputs_transform.ensure_iterable(thing)


def test_stringify():
    assert _inputs_transform.stringify(xr.Dataset) == XARRAY_DATASET_CLASS_STRING


def test_transform(request_args):
    ct.config.USE_CACHE = False
    remote = ct.catalogue.retrieve(*request_args)
    transformed = _inputs_transform.transform(remote, xr.Dataset)
    assert type(transformed) == xr.Dataset

    local = remote.data
    transformed = _inputs_transform.transform(local, xr.Dataset)
    assert isinstance(transformed, xr.Dataset)


def test_transform_numpy_function_inputs():
    transformed_numpy_function_typeset = _inputs_transform.transform_function_inputs(
        dummy_ndarray_function_typeset
    )
    transformed_numpy_function_typeset(TEST_NC)

    transformed_numpy_function_signature = _inputs_transform.transform_function_inputs(
        dummy_ndarray_function_signature
    )
    transformed_numpy_function_signature(TEST_NC)


def test_transform_dataset_function_inputs():
    transformed_dataset_function_typeset = _inputs_transform.transform_function_inputs(
        dummy_dataset_function_typeset
    )
    transformed_dataset_function_typeset(TEST_NC)

    transformed_dataset_function_signature = (
        _inputs_transform.transform_function_inputs(dummy_dataset_function_signature)
    )
    transformed_dataset_function_signature(TEST_NC)


def test_transform_dataarray_function_inputs():
    transformed_dataarray_function_typeset = (
        _inputs_transform.transform_function_inputs(dummy_dataarray_function_typeset)
    )
    transformed_dataarray_function_typeset(TEST_NC)
    # transformed_dataarray_function_typeset(ds)  # NOT YET IMPLEMENTED IN emohawk

    transformed_dataarray_function_signature = (
        _inputs_transform.transform_function_inputs(dummy_dataarray_function_signature)
    )
    transformed_dataarray_function_signature(TEST_NC)
    # transformed_dataarray_function_signature(ds)  # NOT YET IMPLEMENTED IN emohawk


def test_transform_dataframe_function_inputs():
    transformed_dataframe_function = _inputs_transform.transform_function_inputs(
        dummy_dataframe_function
    )
    # transformed_dataframe_function(nd)  # NOT YET IMPLEMENT IN emohawk
    transformed_dataframe_function(TEST_NC)
