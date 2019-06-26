"""
make sure we can download a file on demand
"""
import itertools
import json
import os

import client
import pyjq
import pytest

organization = os.environ["Organization"]
today = os.environ["TODAY"]
org_list = organization.split()

aux_files = {
    "repos_of_interest": "metadata_repos.json"
}


@pytest.mark.parametrize(
    "org, date", itertools.zip_longest(org_list, [], fillvalue=today)
)
def test_valid_org_file(org, date):
    # all the checks to see if we have sane input before proceeding
    data = client.get_data_for_org(org, date)
    assert len(data) > 200_000
    assert isinstance(data, str)
    # decoding is a pain, as we have one text line per JSON object, thus
    # we have to decode line by line
    decoded = client.parse_data_to_json(data)
    assert isinstance(decoded, list)
    # thoughts:
    # should I put in a data structure, tinydb, or sqlite?
    # I'm leaning towards tinydb, or straight pyjq?


@pytest.mark.parametrize("aux_file", aux_files.values())
def test_valid_aux_file(aux_file):
    data = client.get_data_from_file(aux_file)
    assert len(data) < 200_000
    assert isinstance(data, str)
    # decoding is a pain, as we have one text line per JSON object, thus
    # we have to decode line by line
    decoded = client.parse_data_to_json(data)
    assert isinstance(decoded, list)

def test_pyjq_working():
    decoded = client.parse_data_to_json(client.get_data_from_file(aux_files["repos_of_interest"]))
    data = pyjq.all(".[] | .repo", decoded)
    assert len(data) > 2
    assert isinstance(data[0], str)
