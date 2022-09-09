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

import functools
import os
from typing import Any, Dict, Optional

import cacholote
import cdsapi


def collection(collection_id: str) -> Dict[str, Any]:
    return {"id": collection_id}


@cacholote.cacheable
def download_to_cache(collection_id: str, request: Dict[str, Any]):
    c = cdsapi.Client()
    r = c.retrieve(collection_id, request)
    dirfs = cacholote.config.get_cache_files_dirfs()
    target = r.location.rsplit("/", 1)[-1]
    with dirfs.open(target, "wb") as f:
        r.download(f)
    return dirfs.open(target, "rb")


class Remote:
    def __init__(
        self, collection_id: str, request: Dict[str, Any], cache: bool = True
    ) -> None:
        self.collection_id = collection_id
        self.request = request
        self.cache = cache

    def download(
        self, target: Optional[str] = None, cache: Optional[bool] = None
    ) -> str:
        if cache is None:
            cache = self.cache

        if not cache:
            return self.retrieve.download(target)

        cached_file_path = download_to_cache(self.collection_id, self.request).path
        if target is None:
            return cached_file_path

        dirfs = cacholote.config.get_cache_files_dirfs()
        cached_basename = os.path.basename(cached_file_path)
        dirfs.get_file(cached_basename, target)
        return target

    def to_xarray(self, *args, **kwargs):
        return self.teal.to_xarray(*args, **kwargs)

    @property
    def teal(self):
        import teal

        return teal.open(self.download())

    @functools.cached_property
    def retrieve(self):
        return cdsapi.Client().retrieve(self.collection_id, self.request)


def retrieve(collection_id: str, request: Dict[str, Any], cache: bool = True) -> Remote:
    return Remote(collection_id, request, cache)
