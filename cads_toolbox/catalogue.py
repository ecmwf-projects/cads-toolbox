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
import logging
import time
from typing import Any, Dict, Optional

import cdsapi
import teal

logger = logging.getLogger(__name__)


def collection(collection_id: str) -> Dict[str, Any]:
    return {"id": collection_id}


class Remote:
    def __init__(
        self,
        collection_id: str,
        request: Dict[str, Any],
        cache: bool = True,
        wait_on_result=True,
    ) -> None:
        self.client = cdsapi.Client()
        self.result = self.client.retrieve(collection_id, request)
        self.cache_path = None
        if wait_on_result:
            self.wait_on_result()

    def wait_on_result(self) -> None:
        # TODO: make it work
        sleep = 1.0
        last_status = self.status
        while True:
            status = self.status
            if last_status != status:
                logger.info(f"status changed to {status}")
            if status == "successful":
                break
            elif status == "failed":
                raise RuntimeError()
            elif status in ("accepted", "running"):
                sleep *= 1.5
                if sleep > self.sleep_max:
                    sleep = self.sleep_max
            else:
                raise RuntimeError(f"Unknown API state {status!r}")
            logger.debug(f"waiting for {sleep} seconds")
            time.sleep(sleep)

    def download(self, target: Optional[str] = None, cache: bool = True) -> None:
        # FIXE: manage cache == False
        self.download_to_cache()
        # copy(self.cache_path, target)

    def download_to_cache(self) -> None:
        # FIXME: check if the file is in the cache
        self.wait_on_result()
        self.result.download(self.cache_path)

    def __getattr__(self, name: str) -> Any:
        # FIXME: do we want to keep it?
        if not name.startswith("_"):
            return getattr(self.data, name)

    @functools.cached_property
    def data(self):
        self.download()
        return teal.open(self.cache_path)


def retrieve(collection_id: str, request: Dict[str, Any]) -> Remote:
    return Remote(collection_id, request)
