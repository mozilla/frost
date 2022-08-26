# Classes required by Frost
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
from typing import Optional


class GitHubClient:

    _debug_calls: bool = False
    _offline: bool = False

    @classmethod
    def debug_calls(cls) -> bool:
        return cls._debug_calls

    @classmethod
    def is_offline(cls) -> bool:
        return cls._offline

    @classmethod
    def update(cls, debug_calls: Optional[bool] = None, offline: Optional[bool] = None):
        # allow updates
        if debug_calls:
            cls._debug_calls = debug_calls
        if offline:
            cls._offline = offline

    def __init__(
        self, debug_calls: Optional[bool] = None, offline: Optional[bool] = None
    ):
        self.update(debug_calls, offline)
