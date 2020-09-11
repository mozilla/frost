#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/

import sys
import os
from pathlib import Path


# Pretend we're running from the root of frost
# TODO: refactor to avoid this
sys.path.append(str(Path(__file__).resolve().parents[1]))

# from . import *
from orgs import retrieve_github_data


retrieve_github_data.main(*sys.argv[1:])
