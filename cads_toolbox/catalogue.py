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
from typing import Any, Dict, Optional

import cdsapi


def collection(collection_id: str) -> Dict[str, Any]:
    return {"id": collection_id}


class Remote:
    def __init__(
        self, collection_id: str, request: Dict[str, Any], cache: bool = True
    ) -> None:
        self.client = cdsapi.Client()
        self.result = self.client.retrieve(collection_id, request)
        self.cache_path = None

    def download(self, target: Optional[str] = None, cache: bool = True) -> None:
        # FIXE: manage cache == False
        self.download_to_cache()
        # copy(self.cache_path, target)

    def download_to_cache(self) -> None:
        self.result.download(self.cache_path)

    def to_xarray(self, *args, **kwargs):
        return self.teal.to_xarray(*args, **kwargs)

    @functools.cached_property
    def teal(self):
        import teal

        return teal.open(self.cache_path)


def retrieve(collection_id: str, request: Dict[str, Any]) -> Remote:
    return Remote(collection_id, request)
