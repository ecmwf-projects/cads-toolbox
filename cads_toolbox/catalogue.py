"""CADS Toolbox catalogue."""

# Copyright 2022, European Union.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pathlib
from typing import Any, Dict, Union

import cacholote
import cdsapi
import emohawk
import fsspec

from . import config


def _download(
    collection_id: str,
    request: Dict[str, Any],
    target: Union[str, pathlib.Path, None] = None,
) -> Union[
    fsspec.spec.AbstractBufferedFile, fsspec.implementations.local.LocalFileOpener
]:
    client = cdsapi.Client()
    path = client.retrieve(collection_id, request).download(target)
    with fsspec.open(path, "rb") as f:
        return f


class Remote:
    """
    CADS remote object class for handling data objects that are on the CADS/CDS cache volumes
    """

    def __init__(self, collection_id: str, request: Dict[str, Any]):
        """Initialise class"""
        self.collection_id = collection_id
        self.request = request

    def download(
        self, target: Union[str, pathlib.Path, None] = None
    ) -> Union[str, pathlib.Path]:
        """
        Download file with data.

        Parameters
        ----------
        target: str, optional
            Path to which to save data.

        Returns
        -------
        str: Path to which data are saved.
        """
        if config.USE_CACHE:
            with cacholote.config.set(io_delete_original=True):
                obj = cacholote.cacheable(_download)(self.collection_id, self.request)
            if target:
                obj.fs.get(obj.path, str(target))
        else:
            obj = _download(self.collection_id, self.request, target)
        return target or obj.path

    @property
    def data(self) -> emohawk.Data:
        """Object representing the requested data."""
        return emohawk.open(self.download())

    @property
    def to_xarray(self):
        """Convert remote object to xarray.Dataset, performs a hidden cachelotte download"""
        return self.data.to_xarray

    @property
    def to_pandas(self):
        """Convert remote object to pandas.DataFrame, performs a hidden cachelotte download"""
        return self.data.to_pandas


def retrieve(collection_id: str, request: Dict[str, Any]) -> Remote:
    """
    Retrieve CADS data.

    Parameters
    ----------
    collection_id: str
        ID of the dataset.
    request: dict
        Parameters of the request.

    Returns
    -------
    Remote: Object with various methods to access CADS data.
    """
    return Remote(collection_id, request)
