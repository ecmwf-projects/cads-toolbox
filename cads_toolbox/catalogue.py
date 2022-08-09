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

from typing import Any, Dict

import cdsapi


def collection(collection_id: str) -> Dict[str, Any]:
    return {"id": collection_id}


class Remote:
    def __init__(self, cdsapi_remote: cdsapi.Client):
        self.cdsapi_remote = cdsapi_remote


def retrieve(collection_id: str, request: Dict[str, Any]) -> Remote:
    client = cdsapi.Client()
    remote = client.retrieve(collection_id, request)
    return Remote(remote)
