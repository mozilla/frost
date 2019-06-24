"""
make sure we can download a file on demand
"""

import client

def test_real_file():
    data = client.get_data_file(organization="mozilla-bteam",
            date="2018-05-24")
    assert len(data) > 200_000
    assert isinstance(data, "")
