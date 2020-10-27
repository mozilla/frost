"""
Transform results and metadata from a pytest report JSON output and writes Service JSON reports.

Pytest Service JSON format:

{
  'name': 'pytest',
  'tool_url': 'https://github.com/mozilla/frost',
  'version': 1,
  'created_at': '2000-01-01 15:50:00.123123',
  'meanings': {
    'pass': {
      'short': 'pass',    // text that _could_ be used in a badge
      'long': 'Test passed / no issues found.'
    },
    'warn': {
      'short': 'warn',
      'long': 'Expected test failures, either due to test-level xfail/xpass markers or exemptions.'
    },
    'fail': {
      'short': 'fail',
      'long': 'Critical test failure that should never happen e.g. publicly accessible DB snapshot,'
              ' user without MFA in prod.'
    },
    'err': {
      'short': 'err',
      'long': 'Error fetching an resource from AWS.'
    }
  },
  'results': [
    {
       'test_name':  # unparametrized pytest test name
       'resource_name': # best effort at resource name
       'name':
       'status':
       'value':
       'reason':  # pytest test outcome reason if any (e.g. resource fetch failed)
       'markers':  # pytest markers on the test e.g. aws service, ruleset
       'metadata':  # additional metadata on the resource being tested
       'rationale': # (optional) rationale behind the test. (null if not set)
       'description': # (optional) description of the test (null if not set)
       'severity': # (optional) severity of the test (null if not set)
       'regression': # (optional) regression comment (null if not set)
    },
    ...
  ]
}

"""

import json
import argparse
from collections import defaultdict

STATUSES_TO_LIST = ["fail", "warn", "err"]

service_json_template = {
    "name": "frost",
    "tool_url": "https://github.com/mozilla/frost",
    "version": 1,
    "created_at": "",
    "meanings": {
        "pass": {"short": "Pass", "long": "Test passed / no issues found."},
        "warn": {
            "short": "Warn",
            "long": "Expected test failures, either due to test-level "
            "xfail/xpass markers or exemptions.",
        },
        "fail": {
            "short": "FAIL",
            "long": "Critical test failure that should never happen "
            "e.g. publicly accessible DB snapshot, user without MFA in prod.",
        },
        "err": {"short": "Err", "long": "Error fetching an resource from AWS."},
    },
    "results": [],
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument(
        "--jo",
        "--json-out",
        default="service-report.json",
        dest="json_out",
        help="Service json output filename.",
    )

    parser.add_argument(
        "pytest_json",
        metavar="<pytest-results.json>",
        help="Pytest results output in JSON format.",
    )

    return parser.parse_args()


def get_test_status(outcome):
    if outcome == "errored":
        return "err"
    elif outcome in ["xfailed", "xpassed"]:
        return "warn"
    elif outcome in ["passed", "skipped"]:
        return "pass"
    elif outcome == "failed":
        return "fail"
    else:
        raise Exception("Unexpected test outcome %s" % outcome)


def get_resource_name(name):
    try:
        # test_elb_instances_attached[elb-name]
        rname = name.split("[")[1][:-1]
        return rname
    except:
        return name


def get_result_for_test(test):
    meta = test["metadata"][0]
    return {
        "test_name": meta["unparametrized_name"],
        "resource_name": get_resource_name(meta["parametrized_name"]),
        "name": meta["parametrized_name"],
        "status": get_test_status(meta["outcome"]),
        "value": meta["outcome"],
        "reason": meta["reason"],
        "markers": meta["markers"],
        "metadata": meta["metadata"],
        "rationale": meta["rationale"],
        "description": meta["description"],
        "severity": meta["severity"],
        "regression": meta["regression"],
    }


def pytest_json_to_service_json(pytest_json):
    service_json_template["created_at"] = pytest_json["report"]["created_at"]
    service_json_template["results"] = []

    for test in pytest_json["report"]["tests"]:
        try:
            service_json_template["results"].append(get_result_for_test(test))
        except KeyError:
            pass

    return service_json_template


if __name__ == "__main__":
    args = parse_args()

    pytest_json = json.load(open(args.pytest_json, "r"))

    service_json = pytest_json_to_service_json(pytest_json)

    with open(args.json_out, "w") as fout:
        json.dump(service_json, fout, sort_keys=True, indent=4)
