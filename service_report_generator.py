"""
Transform results and metadata from a pytest report JSON output and writes Service JSON and Service Markdown reports.

Pytest Service JSON format:

{
  'name': 'pytest',
  'tool_url': 'https://github.com/mozilla-services/pytest-services',
  'version': 1,
  'meanings': {
    'pass': {
      'short': 'pass',    // text that _could_ be used in a badge
      'long': 'Test passed / no issues found.'
    },
    'warn': {
      'short': 'warn',
      'long': 'Non-critical test result like an unexpected test failure (xpass, xfail, skip). '
              'Examples: S3 bucket not tagged as public, error fetching resource from the AWS '
              'API, test skipped due to it not applying'
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
       'name':
       'status':
       'value':
       'reason':  # pytest test outcome reason if any (e.g. resource fetch failed)
       'markers':  # pytest markers on the test e.g. aws service, ruleset
       'metadata':  # additional metadata on the resource being tested
       'rationale': # (optional) rationale behind the test.
       'description': # (optional) description of the test
       'severity': # (optional) severity of the test
    },
    ...
  ]
}

"""

import json
import argparse
from collections import defaultdict

STATUSES_TO_LIST = ['fail', 'warn', 'err']

service_json_template = {
    'name': 'pytest',
    'tool_url': 'https://github.com/mozilla-services/pytest-services',
    'version': 1,
    'meanings': {
        'pass': {
            'short': 'Pass',
            'long': 'Test passed / no issues found.'
        },
        'warn': {
            'short': 'Warn',
            'long': 'Non-critical test result like an unexpected test failure '
            '(xpass, xfail, skip). Examples: S3 bucket not tagged as public, '
            'error fetching resource from the AWS API, test skipped due to it not applying'
        },
        'fail': {
            'short': 'FAIL',
            'long': 'Critical test failure that should never happen '
            'e.g. publicly accessible DB snapshot, user without MFA in prod.'
        },
        'err': {
            'short': 'Err',
            'long': 'Error fetching an resource from AWS.'
        }
    },
    'results': []
}


class MarkdownReportGenerator:

    def __init__(self, service_json, fout=None):
        self.fout = fout

        # {'test_name': [results], ...}
        self.test_results = defaultdict(list)

        # {'test_name_fail': 2, ...}
        self.test_status_counter = defaultdict(int)

        for result in service_json['results']:
            if result['status'] in STATUSES_TO_LIST:
                self.test_results[result['test_name']].append(result)
                self.test_status_counter[result['test_name']+"_"+result['status']] += 1

    def generate(self):
        self.print_header()
        self.print_table_of_contents()
        self.print_report()

    def print_header(self):
        print("# AWS pytest-services results\n", file=self.fout)
        print("#### Status Meanings: \n", file=self.fout)
        self._print_status_table()

    def print_table_of_contents(self):
        print("#### Table of Contents\n", file=self.fout)
        for test in self.test_results:
            print("- [%s](#%s)" % (test, test), file=self.fout)
            for status in STATUSES_TO_LIST:
                if self._test_results_include_status(test, status):
                    print("    - [%s (%s)](#%s)" % (
                        status,
                        self.test_status_counter[test+'_'+status],
                        test+'_'+status,
                    ), file=self.fout)
        print("---\n", file=self.fout)

    def print_report(self):
        for test in self.test_results:
            self._print_test_header(
                test,
                self.test_results[test][0]['description'],
                self.test_results[test][0]['rationale']
            )

            self._print_test_result_tables(test)

            print("\n---\n\n", file=self.fout)

    def _print_test_header(self, test_name, description, rationale):
        print("### %s\n\n" % test_name, file=self.fout)
        if description:
            print("**Description:** %s\n" % description, file=self.fout)
        if rationale:
            print("**Rationale:** %s\n" % rationale, file=self.fout)

    def _print_test_result_tables(self, test_name):
        for status in STATUSES_TO_LIST:
            if self._test_results_include_status(test_name, status):
                print("#### %s_%s\n\n" % (test_name, status), file=self.fout)
                print("Resource Name | Metadata", file=self.fout)
                print("------------ | -------------", file=self.fout)

                for result in self.test_results[test_name]:
                    if result["status"] == status:
                        print("%s | %s" % (
                            self._extract_resource_name(result['name']),
                            self._format_metadata(result['metadata'])
                        ), file=self.fout)

                print("\n\n", file=self.fout)

    def _print_status_table(self):
        print("Status Name | Meaning", file=self.fout)
        print("------------ | -------------", file=self.fout)
        print("fail | Critical test failure that should never happen e.g. publicly "
              "accessible DB snapshot, user without MFA in prod.", file=self.fout)
        print("warn | Non-critical test result like an unexpected test failure "
              "(xpass, xfail, skip). Examples: S3 bucket not tagged as public, "
              "error fetching resource from the AWS API, test skipped due to it not applying", file=self.fout)
        print("err | Error fetching an resource from AWS.", file=self.fout)
        print("\n\n", file=self.fout)

    def _extract_resource_name(self, name):
        # "test_something[resource-name]" -> "resource-name"
        return name.split("[")[-1][0:-1]

    def _format_metadata(self, metadata):
        """
        Formats the metadata dictionary to a string that is somewhat readable in a markdown table.

        >>> MarkdownReportGenerator({'results': []})._format_metadata({'foo': 'bar'})
        'foo: bar'
        >>> MarkdownReportGenerator({'results': []})._format_metadata({'VpcId': '1234', 'GroupName': 'ssh-only'})
        'GroupName: ssh-only - VpcId: 1234'
        """
        return ''.join(["{}: {} - ".format(k, v) for k, v in sorted(metadata.items())])[0:-3]

    # test results include at least one with status of
    def _test_results_include_status(self, test_name, status):
        return bool(self.test_status_counter[test_name+'_'+status])


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('--jo', '--json-out', default='service-report.json',
                        dest='json_out', help='Service json output filename.')

    parser.add_argument('--mo', '--markdown-out', default='service-report.md',
                        dest='markdown_out', help='Service markdown output filename.')

    parser.add_argument('pytest_json', metavar='<pytest-results.json>',
                        help='Pytest results output in JSON format.')

    return parser.parse_args()


def get_test_status(outcome):
    if outcome == 'errored':
        return 'err'
    elif outcome in ['xfailed', 'xpassed', 'skipped']:
        return 'warn'
    elif outcome == 'passed':
        return 'pass'
    elif outcome == 'failed':
        return 'fail'
    else:
        raise Exception('Unexpected test outcome %s' % outcome)


def get_result_for_test(test):
    meta = test['metadata'][0]
    return {
        'test_name': meta['unparametrized_name'],
        'name': meta['parametrized_name'],
        'status': get_test_status(meta['outcome']),
        'value': meta['outcome'],
        'reason': meta['reason'],
        'markers': meta['markers'],
        'metadata': meta['metadata'],
        'rationale': meta['rationale'],
        'description': meta['description'],
        'severity': meta['severity'],
    }


def pytest_json_to_service_json(pytest_json):
    service_json_template['results'] = []

    for test in pytest_json['report']['tests']:
        try:
            service_json_template['results'].append(get_result_for_test(test))
        except KeyError:
            pass
    return service_json_template


if __name__ == '__main__':
    args = parse_args()

    pytest_json = json.load(open(args.pytest_json, 'r'))

    service_json = pytest_json_to_service_json(pytest_json)

    with open(args.json_out, 'w') as fout:
        json.dump(service_json, fout, sort_keys=True, indent=4)

    with open(args.markdown_out, 'w') as fout:
        MarkdownReportGenerator(service_json, fout=fout).generate()
