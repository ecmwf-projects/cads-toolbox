import pathlib
import zipfile
from typing import Any, Dict, Tuple

import pytest

import cads_toolbox


@pytest.fixture
def era5_request_args() -> Tuple[str, Dict[str, Any]]:
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


@pytest.fixture
def zipped_request_args() -> Tuple[str, Dict[str, Any]]:
    return (
        "insitu-gridded-observations-global-and-regional",
        {
            "format": "zip",
            "origin": "gistemp",
            "region": "global",
            "variable": "temperature_anomaly",
            "time_aggregation": "monthly",
            "horizontal_aggregation": "horizontal_average",
            "year": "1880",
            "version": "v4.0",
            "statistic": "mean",
        },
    )


def test_uncached_download(
    tmp_path: pathlib.Path, era5_request_args: Tuple[str, Dict[str, Any]]
):
    cads_toolbox.config.USE_CACHE = False

    remote = cads_toolbox.catalogue.retrieve(*era5_request_args)
    target = tmp_path / "test.grib"

    # Download
    assert remote.download(target) == target
    assert target.stat().st_size == 2076600

    # Re-download
    previous_mtime = target.stat().st_mtime
    assert remote.download(target) == target
    assert target.stat().st_mtime != previous_mtime
    assert target.stat().st_size == 2076600


def test_cached_download(
    tmp_path: pathlib.Path, era5_request_args: Tuple[str, Dict[str, Any]]
):
    cads_toolbox.config.USE_CACHE = True

    remote = cads_toolbox.catalogue.retrieve(*era5_request_args)
    # Download to cache
    cache_file = pathlib.Path(remote.download())
    assert cache_file.stat().st_size == 2076600
    assert cache_file.parent == tmp_path / "cache_files"

    # Use cached file
    previous_mtime = cache_file.stat().st_mtime
    assert remote.download() == str(cache_file)
    assert cache_file.stat().st_mtime == previous_mtime

    # Copy from cache file
    target = tmp_path / "test.grib"
    assert remote.download(target) == target
    assert target.stat().st_size == 2076600
    assert cache_file.stat().st_mtime == previous_mtime


def test_to_xarray(
    tmp_path: pathlib.Path, era5_request_args: Tuple[str, Dict[str, Any]]
):
    pytest.importorskip("cfgrib")
    xr = pytest.importorskip("xarray")

    cads_toolbox.config.USE_CACHE = True
    remote = cads_toolbox.catalogue.retrieve(*era5_request_args)
    assert isinstance(remote.to_xarray(), xr.Dataset)


def test_to_pandas(
    tmp_path: pathlib.Path, era5_request_args: Tuple[str, Dict[str, Any]]
):
    pytest.importorskip("cfgrib")
    pd = pytest.importorskip("pandas")

    cads_toolbox.config.USE_CACHE = True
    remote = cads_toolbox.catalogue.retrieve(*era5_request_args)
    assert isinstance(remote.to_pandas(), pd.DataFrame)


def test_zipped_request_args(zipped_request_args: Tuple[str, Dict[str, Any]]):
    cads_toolbox.config.USE_CACHE = True
    remote = cads_toolbox.catalogue.retrieve(*zipped_request_args)
    target = remote.download()
    assert zipfile.is_zipfile(target) is False
