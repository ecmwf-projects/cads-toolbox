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

import dataclasses
from typing import Any, Dict, Optional

import cacholote
import cdsapi
import fsspec
import pandas as pd
import teal
import xarray as xr

from . import config


def _download(
    collection_id: str, request: Dict[str, Any], target: Optional[str] = None
):
    client = cdsapi.Client()
    path = client.retrieve(collection_id, request).download(target)
    return fsspec.open(path, "rb").open()


@dataclasses.dataclass
class Remote:
    collection_id: str
    request: Dict[str, Any]

    def download(self, target: Optional[str] = None) -> str:
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
        return teal.open(self.download())

    @property
    def to_xarray(self) -> xr.Dataset:
        return self.data.to_xarray

    @property
    def to_pandas(self) -> pd.DataFrame:
        return self.data.to_pandas


def retrieve(collection_id: str, request: Dict[str, Any]) -> Remote:
    return Remote(collection_id, request)
