import io
import itertools
import json
import os
import tempfile

import pyjq
import pytest


class GitHubException(Exception):
    pass


class GitHubFileNotFoundException(GitHubException):
    # error downloading file
    pass

results_dir = os.environ["RESULTS_DIR"]
organization = os.environ["Organization"]
today = os.environ["TODAY"]
org_list = organization.split()

aux_files = {
    "repos_of_interest": "metadata_repos.json"
}






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
def get_data_from_file(
    file_name,
    method_name=None,
    call_args=None,
    call_kwargs=None,
    cache=None,
    result_from_error=None,
    debug_calls=False,
    debug_cache=False,
):
    """
    Fetches and return final data

    TODO: get caching working
    """
    if debug_calls:
        print(f"getting data from {file_name}")

    result = None
    if cache is not None:
        ckey = cache_key(file_name, method_name)
        result = cache.get(ckey, None)

        if debug_cache and result is not None:
            print("found cached value for", ckey)

    if result is None:
        # import pudb; pudb.set_trace()
        # we expect the file to already be in /results
        full_path = f"{results_dir}/{file_name}"
        try:
            with open(full_path, encoding="UTF-8") as f:
                result = f.read()
        except Exception as e:
            raise GitHubFileNotFoundException(str(e))

        if cache is not None:
            if debug_cache:
                print("setting cache value for", ckey)

            cache.set(ckey, result)

    return result

##@pytest.fixture(scope="session")
def parse_data_to_json(json_stream):
    result = []
    js = io.StringIO(json_stream)
    while True:
        json_object = js.readline()
        if not json_object:
            break
        parsed = json.loads(json_object)
        result.append(parsed)
    return result
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
