"""
make sure we can download a file on demand
"""
import itertools
import json
import os

import client
import pyjq
import pytest



def test_valid_org_file(get_data_for_org, get_org_json):
    # all the checks to see if we have sane input before proceeding
    assert len(get_data_for_org) > 200_000
    assert isinstance(get_data_for_org, str)
    # decoding is a pain, as we have one text line per JSON object, thus
    # we have to decode line by line
    assert isinstance(get_org_json, list)


def test_valid_aux_file():
    data = client.get_data_from_file(list(client.aux_files.values())[0])
    assert len(data) < 200_000
    assert isinstance(data, str)
    # decoding is a pain, as we have one text line per JSON object, thus
    # we have to decode line by line
    decoded = client.parse_data_to_json(data)
    assert isinstance(decoded, list)

def test_pyjq_working():
    decoded = client.parse_data_to_json(client.get_data_from_file(client.aux_files["repos_of_interest"]))
    data = pyjq.all(".[] | .repo", decoded)
    assert len(data) > 2
    assert isinstance(data[0], str)
