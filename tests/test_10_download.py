import os

import cacholote
import pytest

import cads_toolbox


@pytest.fixture
def request_args():
    return [
        "reanalysis-era5-single-levels",
        {
            "variable": "2m_temperature",
            "product_type": "reanalysis",
            "year": "2017",
            "month": "01",
            "day": "01",
            "time": "12:00",
        },
    ]


def test_cached_download(tmpdir, request_args):
    remote = cads_toolbox.catalogue.retrieve(*request_args)
    with cacholote.config.set(cache_store_directory=tmpdir):
        # Download to cache
        cache_file = remote.download()
        assert os.path.getsize(cache_file) == 2076600
        assert os.path.dirname(cache_file) == tmpdir

        # Use cached file
        expected_mtime = os.path.getmtime(cache_file)
        assert remote.download() == cache_file
        assert os.path.getmtime(cache_file) == expected_mtime

        # Copy from cache file
        target = str(tmpdir / "test.grib")
        assert remote.download(target=target) == target
        assert os.path.getsize(target) == 2076600
        assert os.path.getmtime(cache_file) == expected_mtime
