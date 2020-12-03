#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# Data structures to assist with reporting mis-configured items

from dataclasses import dataclass
from typing import Any, ClassVar, List, Optional


@dataclass
class Criteria:
    standard_number: str  # as defined in messages file. alpha-numeric
    slug: str  # id to match. alpha-numeric
    description: str  # whatever you want
    # hack to not issue duplicate metaddata_to_log
    _metadata_to_log: ClassVar[List] = ["standard_number"]

    @classmethod
    def metadata_to_log(cls) -> List[str]:
        list_to_return = cls._metadata_to_log
        cls._metadata_to_log = []
        return list_to_return

    @staticmethod
    def idfn(val: Any) -> Optional[str]:
        """provide ID for pytest Parametrization."""
        if isinstance(val, (Criteria,)):
            return f"{val.standard_number}-{val.slug}"
        return None

    def __str__(self: Any) -> str:
        return f"{self.standard_number} {self.description}"
