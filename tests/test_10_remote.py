import os
import pathlib
from typing import Any, Dict, Tuple

import pytest

import cads_toolbox


@pytest.fixture
def request_args() -> Tuple[str, Dict[str, Any]]:
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


def test_uncached_download(
    tmp_path: pathlib.Path, request_args: Tuple[str, Dict[str, Any]]
):
    cads_toolbox.config.USE_CACHE = False

    remote = cads_toolbox.catalogue.retrieve(*request_args)
    target = str(tmp_path / "test.grib")

    # Download
    assert remote.download(target) == target
    assert os.path.getsize(target) == 2076600

    # Re-download
    previous_mtime = os.path.getmtime(target)
    assert remote.download(target) == target
    assert os.path.getmtime(target) != previous_mtime
    assert os.path.getsize(target) == 2076600


def test_cached_download(
    tmp_path: pathlib.Path, request_args: Tuple[str, Dict[str, Any]]
):
    cads_toolbox.config.USE_CACHE = True

    remote = cads_toolbox.catalogue.retrieve(*request_args)
    # Download to cache
    cache_file = remote.download()
    assert os.path.getsize(cache_file) == 2076600
    assert os.path.dirname(cache_file) == str(tmp_path / "cache_files")

    # Use cached file
    previous_mtime = os.path.getmtime(cache_file)
    assert remote.download() == cache_file
    assert os.path.getmtime(cache_file) == previous_mtime

    # Copy from cache file
    target = str(tmp_path / "test.grib")
    assert remote.download(target=target) == target
    assert os.path.getsize(target) == 2076600
    assert os.path.getmtime(cache_file) == previous_mtime


def test_to_xarray(tmp_path: pathlib.Path, request_args: Tuple[str, Dict[str, Any]]):
    xr = pytest.importorskip("xarray")

    cads_toolbox.config.USE_CACHE = True
    remote = cads_toolbox.catalogue.retrieve(*request_args)
    assert isinstance(remote.to_xarray(), xr.Dataset)


def test_to_pandas(tmp_path: pathlib.Path, request_args: Tuple[str, Dict[str, Any]]):
    pd = pytest.importorskip("pandas")

    cads_toolbox.config.USE_CACHE = True
    remote = cads_toolbox.catalogue.retrieve(*request_args)
    assert isinstance(remote.to_pandas(), pd.DataFrame)
