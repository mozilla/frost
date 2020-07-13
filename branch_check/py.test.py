#!/usr/bin/env python3

"""
    Work around vs-code's debugger activation on normal system exit from pytest
"""

import os
import sys
import pytest

try:
    path_to_add = os.path.abspath(os.curdir)
    sys.path.insert(0, path_to_add)
    print(f"added {path_to_add}")
    pytest.main(sys.argv)
except SystemExit:
    pass
