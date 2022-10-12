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

from typing import Any, Dict, Optional, Union

import cacholote
import cdsapi
import fsspec
import teal

from . import config


def _download(
    collection_id: str, request: Dict[str, Any], target: Optional[str] = None
) -> Union[
    fsspec.spec.AbstractBufferedFile, fsspec.implementations.local.LocalFileOpener
]:
    client = cdsapi.Client()
    path = client.retrieve(collection_id, request).download(target)
    return fsspec.open(path, "rb").open()


class Remote:
    def __init__(self, collection_id: str, request: Dict[str, Any]):
        self.collection_id = collection_id
        self.request = request

    def download(self, target: Optional[str] = None) -> str:
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
                obj.fs.get(obj.path, target)
        else:
            obj = _download(self.collection_id, self.request, target)
        return target or obj.path

    @property
    def data(self) -> teal.Data:
        """Object representing the requested data."""
        return teal.open(self.download())

    @property
    def to_xarray(self):
        return self.data.to_xarray

    @property
    def to_pandas(self):
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
