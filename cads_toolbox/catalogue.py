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
import io
import shutil
import tempfile
from typing import Any, Dict, Optional

import cacholote
import cdsapi


def collection(collection_id: str) -> Dict[str, Any]:
    return {"id": collection_id}


@cacholote.cacheable
def download_to_cache(collection_id: str, request: Dict[str, Any]) -> io.BufferedReader:
    # TODO: add extension to file
    target = tempfile.NamedTemporaryFile().name
    cdsapi.Client().retrieve(collection_id, request, target)
    io_json = cacholote.extra_encoders.dictify_io_object(
        open(target, "rb"), delete_original=True
    )
    return open(io_json["file:local_path"], "rb")


class Remote:
    def __init__(
        self, collection_id: str, request: Dict[str, Any], cache: bool = True
    ) -> None:
        self.collection_id = collection_id
        self.request = request

    @property
    def cached_file_path(self) -> str:
        f = download_to_cache(self.collection_id, self.request)
        return f.name

    def download(self, target: Optional[str] = None, cache: bool = True) -> None:

        if cache:
            if target is None:
                # TODO: How to get the default target used by cdsapi?
                raise ValueError("not implemented yet")
            shutil.copyfile(self.cached_file_path, target)
        else:
            cdsapi.Client().retrieve(self.collection_id, self.request, target)

    def to_xarray(self, *args, **kwargs):
        return self.teal.to_xarray(*args, **kwargs)

    @functools.cached_property
    def teal(self):
        import teal

        return teal.open(self.cached_file_path)


def retrieve(collection_id: str, request: Dict[str, Any]) -> Remote:
    return Remote(collection_id, request)
