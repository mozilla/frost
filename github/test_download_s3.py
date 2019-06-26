"""
make sure we can download a file on demand
"""
import itertools
import os

import client
import pytest

organization = os.environ["Organization"]
today = os.environ["TODAY"]
org_list = organization.split()


@pytest.mark.parametrize(
    "org, date", itertools.zip_longest(org_list, [], fillvalue=today)
)
def test_real_file(org, date):
    data = client.get_data(org, date)
    assert len(data) > 200_000
    assert isinstance(data, str)
