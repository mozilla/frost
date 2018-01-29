

"""
Pulls AWS metadata from the pytest report JSON output and writes service JSON.

Pytest service JSON format:

{
  'name': 'pytest',
  'tool_url': 'https://github.com/mozilla-services/foxsec/tree/master/tools/pytest-services',
  'version': 1,
  'meanings': {
    'pass' : {
      'short' : 'pass',    // text that _could_ be used in a badge
      'long' : 'Test passed / no issues found.'
    },
    'warn' : {
      'short' : 'warn',
      'long' : 'Non-critical test result like an unexpected test failure (xpass, xfail, skip). Examples: S3 bucket not tagged as public, error fetching resource from the AWS API, test skipped due to it not applying'
    },
    'fail' : {
      'short' : 'fail',
      'long' : 'Critical test failure that should never happen e.g. publicly accessible DB snapshot, user without MFA in prod.'
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
    },
    ...
  ]
}
"""


import argparse
import json


service_json_template = {
    'name': 'pytest',
    'tool_url': 'https://github.com/mozilla-services/foxsec/tree/master/tools/pytest-services',
    'version': 1,
    'meanings': {
        'pass' : {
            'short' : 'Pass',
            'long' : 'Test passed / no issues found.'
        },
        'warn' : {
            'short' : 'Warn',
            'long' : 'Non-critical test result like an unexpected test failure (xpass, xfail, skip). Examples: S3 bucket not tagged as public, error fetching resource from the AWS API, test skipped due to it not applying'
        },
        'fail' : {
            'short' : 'FAIL',
            'long' : 'Critical test failure that should never happen e.g. publicly accessible DB snapshot, user without MFA in prod.'
        },
        'err': {
            'short': 'Err',
            'long': 'Error fetching an resource from AWS.'
        }
    },
    'results': []
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-i', '--input', required=True,
                        help='pytest json report input filename.')

    parser.add_argument('-o', '--output', required=True,
                        help='service json output filename.')

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
    }


def pytest_json_to_service_json(pytest_json):
    service_json_template['results'] = [
        get_result_for_test(test)
        for test in pytest_json['report']['tests']
    ]
    return service_json_template


def main():
    args = parse_args()

    pytest_json = json.load(open(args.input, 'r'))

    service_json = pytest_json_to_service_json(pytest_json)

    with open(args.output, 'w') as fout:
        json.dump(service_json, fout, sort_keys=True, indent=4)


if __name__ == '__main__':
    main()
