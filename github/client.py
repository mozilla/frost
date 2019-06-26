import json
import os
import tempfile

# RESULTS_DIR is present for local testing, but is not passed into
# container. Inside the container, it's hardcoded.
results_dir = os.environ.get("RESULTS_DIR", "/results")


class GitHubException(Exception):
    pass


class GitHubFileNotFoundException(GitHubException):
    # error downloading file
    pass


def get_data(
    organization,
    date,
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
        print("calling", method_name, "on", organization)

    result = None
    if cache is not None:
        ckey = cache_key(organization, method_name)
        result = cache.get(ckey, None)

        if debug_cache and result is not None:
            print("found cached value for", ckey)

    if result is None:
        # import pudb; pudb.set_trace()
        # we expect the file to already be in /results
        srcname = f"{results_dir}/{date}-{organization}.db.obj.json"
        try:
            with open(srcname, encoding="UTF-8") as f:
                result = f.read()
        except Exception as e:
            raise GitHubFileNotFoundException(str(e))

        if cache is not None:
            if debug_cache:
                print("setting cache value for", ckey)

            cache.set(ckey, result)

    return result
