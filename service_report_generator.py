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
    "name": "pytest",
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


class ReportGenerator:
    def __init__(self, service_json, fout=None):
        self.fout = fout

        # {'test_name': [results], ...}
        self.test_results = defaultdict(list)

        # {'test_name_fail': 2, ...}
        self.test_status_counter = defaultdict(int)

        for result in service_json["results"]:
            if result["status"] in STATUSES_TO_LIST and result["severity"] != "INFO":
                self.test_results[result["test_name"]].append(result)
                self.test_status_counter[
                    result["test_name"] + "_" + result["status"]
                ] += 1

    def generate(self):
        self.print_header()
        self.print_table_of_contents()
        self.print_report()

    def _extract_resource_name(self, name):
        # "test_something[resource-name]" -> "resource-name"
        return name.split("[")[-1][0:-1]

    # test results include at least one with status of
    def _test_results_include_status(self, test_name, status):
        return bool(self.test_status_counter[test_name + "_" + status])

    def _get_resource_type(self, test_name):
        if "rds" in test_name:
            return "RDS"
        if "security_group" in test_name:
            return "Security Group"
        if "iam" in test_name:
            return "IAM"
        if "firewall" in test_name:
            return "GCP Firewall"
        if "bigquery" in test_name:
            return "BigQuery"
        return ""

    def _get_resource_id(self, resource_type, resource_name, result_metadata):
        if resource_type == "Security Group":
            return resource_name.split(" ")[0]
        if resource_type == "RDS":
            return result_metadata.get("DBInstanceIdentifier")
        return ""

    def _get_tag_value(self, tag_key, result_metadata):
        if result_metadata.get("TagList"):
            for tag in result_metadata["TagList"]:
                if tag["Key"] == tag_key:
                    return tag["Value"]
        if result_metadata.get("Tags"):
            for tag in result_metadata["Tags"]:
                if tag["Key"] == tag_key:
                    return tag["Value"]
        return ""

    def _get_region(self, result_metadata):
        if result_metadata.get("__pytest_meta"):
            return result_metadata["__pytest_meta"].get("region", "")
        return ""


class CsvReportGenerator(ReportGenerator):
    def print_header(self):
        print(
            "Test Name,Project,Resource Type,Resource Id,Resource Name,Region,App,Owner,Assignee",
            file=self.fout,
        )

    def print_table_of_contents(self):
        return

    def print_report(self):
        for test in self.test_results:
            self._print_test_result_csv(test)

    def _print_test_result_csv(self, test_name):
        for status in STATUSES_TO_LIST:
            if not self._test_results_include_status(test_name, status):
                continue

            for result in self.test_results[test_name]:
                if result["status"] != status:
                    continue

                rtype = self._get_resource_type(test_name)
                project = ""
                if result["metadata"].get("gcp_project_id", None) is not None:
                    resource_name = result["metadata"].get("name", "")
                    rid = result["metadata"].get("id", "")
                    project = result["metadata"]["gcp_project_id"]
                else:
                    resource_name = self._extract_resource_name(result["name"])
                    rid = self._get_resource_id(rtype, resource_name, result)

                display_resource_name = resource_name
                if rtype == "Security Group":
                    display_resource_name = " ".join(resource_name.split(" ")[1:])

                # Get App and Owner Tag
                app = self._get_tag_value("App", result["metadata"])
                owner = self._get_tag_value("Owner", result["metadata"])

                # Get Region
                region = self._get_region(result["metadata"])

                print(
                    "%s,%s,%s,%s,%s,%s,%s,%s,"
                    % (
                        test_name,
                        project,
                        rtype,
                        rid,
                        display_resource_name,
                        region,
                        app,
                        owner,
                    ),
                    file=self.fout,
                )

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
        "--co",
        "--csv-out",
        default="service-report.csv",
        dest="csv_out",
        help="Service csv output filename.",
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

    with open(args.csv_out, "w") as fout:
        CsvReportGenerator(service_json, fout=fout).generate()
