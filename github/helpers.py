import io
import itertools
import json
import os
import tempfile

import pyjq
import pytest






##@pytest.fixture(scope="session")
##def get_data_for_org(
##    org_filler,
##    date,
##    method_name=None,
##    call_args=None,
##    call_kwargs=None,
##    cache=None,
##    result_from_error=None,
##    debug_calls=False,
##    debug_cache=False,
##):
##    srcname = f"{date}-{org_filler}.db.obj.json"
##    print(f"date: {type(date)}, {date}")
##    assert date
##    data = get_data_from_file(srcname)
##    return data

#@pytest.fixture(scope="session")

##@pytest.fixture(scope="session")
##
##def get_aux_json(aux_name):
##    return parse_data_to_json(get_data_from_file(aux_files[aux_name]))
##
##@pytest.fixture(scope="module")
##def get_org_json(get_data_for_org):
##    return parse_data_to_json(get_data_for_org)
##
##@pytest.fixture(scope="module")
##def repos_of_interest_for_org(org_filler):
##    org = org_filler
##    of_interest = get_aux_json("repos_of_interest")
##    jq_script = f"""
##        .[] | # for each array element
##        .repo |  # only look at repository URL
##        select(startswith("https://github.com/{org}")) # only in org
##    """
##    return pyjq.all(jq_script, of_interest)
##
##@pytest.fixture(scope="module")
##        #params=list(repos_of_interest_for_org(org_filler)))
##def org_default_branches(org_filler, get_org_json, date):
##    """
##    Return [(org, repo, default_branch)]
##    """
##    org_json = get_org_json
##    urls = repos_of_interest_for_org(org_filler)
##    print(f"org_json: {len(get_org_json)}; urls: {len(urls)}")
##    results = []
##    for url in urls:
##        repo = url.split('/')[-1]
##        assert repo.endswith(".git")
##        repo = repo[:-4]
##        repo_api_url = f"/repos/{org_filler}/{repo}"
##        jq_for_repo = f"""
##        . [] |  # for all elements
##        select(.url == "{repo_api_url}")  # just this repo
##        """
##        record = pyjq.all(jq_for_repo, org_json)
##        if len(record):
##            branch = record[0]["body"]["default_branch"]
##            assert branch
##            results.append((org_filler, repo, branch, date))
##        else:
##            # noexistant === protected, but we want to update our
##            # metadata
##            print(f"couldn't find record for {repo}")
##    return results
##
##@pytest.fixture(scope="module",
##    params=org_default_branches(organization, get_org_json(get_data_for_org(organization, today)), today),
##    ids=[f"{x[1]}-{x[2]}" for x in org_default_branches(organization, get_org_json(get_data_for_org(organization, today)), today)],
##)
##def def_branch(request):
##    return request.param
##
##@pytest.fixture(scope="session", params=[today,])
##def date(request):
##    assert request.param, "TODAY not set in environment"
##    return request.param
