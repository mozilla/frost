import functools
import io
import json
import os

import pyjq


results_dir = os.environ["RESULTS_DIR"]
organization = os.environ["Organization"]
today = os.environ["TODAY"]
org_list = organization.split()

aux_files = {
    "repos_of_interest": "metadata_repos.json"
}


class GitHubException(Exception):
    pass


class GitHubFileNotFoundException(GitHubException):
    # error downloading file
    pass



def cur_org():
    return organization

def report_date():
    return today

def finalize_defaults(org=None, date=None):
    org = org if org else cur_org()
    date = date if date else report_date()
    return org, date

def get_data_for_org(org=None, date=None):
    org, date = finalize_defaults(org, date)
    srcname = f"{date}-{org}.db.obj.json"
    data = get_data_from_file(srcname)
    return data


@functools.lru_cache()
def get_data_from_file(file_name):
    """
    Fetches and return final data

    TODO: get caching working
    """

    # import pudb; pudb.set_trace()
    # we expect the file to already be in /results
    full_path = f"{results_dir}/{file_name}"
    try:
        result = open(full_path, encoding="UTF-8").read()
    except Exception as e:
        raise GitHubFileNotFoundException(str(e))

    return result


@functools.lru_cache()
def parse_data_to_json(json_data):
    result = []
    js = io.StringIO(json_data)
    while True:
        json_object = js.readline()
        if not json_object:
            break
        parsed = json.loads(json_object)
        result.append(parsed)
    return result

@functools.lru_cache()
def get_json_from_file(file_name):
    return parse_data_to_json(get_data_from_file(file_name))

@functools.lru_cache()
def get_aux_json(aux_name):
    return get_json_from_file(aux_files[aux_name])

@functools.lru_cache()
def get_org_json(org=None, date=None):
    org, date = finalize_defaults(org, date)
    return parse_data_to_json(get_data_for_org(org, date))


@functools.lru_cache()
def repos_of_interest_for_org(org=None):
    org, _ = finalize_defaults(org)
    of_interest = get_aux_json("repos_of_interest")
    jq_script = f"""
        .[] | # for each array element
        .repo |  # only look at repository URL
        select(startswith("https://github.com/{org}/")) # only in org
    """
    return pyjq.all(jq_script, of_interest)


@functools.lru_cache()
def org_default_branches(org=None, date=None):
    """
    Return [(org, repo, default_branch, date)]
    """
    org, date = finalize_defaults(org, date)
    org_json = get_org_json(org, date)
    urls = repos_of_interest_for_org(org)
    results = []
    for url in urls:
        repo = url.split('/')[-1]
        assert repo.endswith(".git")
        repo = repo[:-4]
        repo_api_url = f"/repos/{org}/{repo}"
        jq_for_repo = f"""
        . [] |  # for all elements
        select(.url == "{repo_api_url}")  # just this repo
        """
        record = pyjq.all(jq_for_repo, org_json)
        if len(record):
            branch = record[0]["body"]["default_branch"]
            assert branch
            results.append((org, repo, branch, date))
        else:
            # noexistant === protected, but we want to update our
            # metadata
            print(f"No default branch for {org}/{repo}")
    return results

