"""
make sure we can download a file on demand
"""

import client

def test_real_file():
    data = client.get_data()
    assert len(data) > 200_000
    assert isinstance(data, "")
