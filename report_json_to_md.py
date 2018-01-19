

"""
Using AWS metadata from the pytest report JSON output and writes a report
in markdown format.

The report contains:

* one table per unique group by tuple (e.g. cloudservices-aws-stage, us-east-1, rds if grouping by account/profile, region, and service)

* each table consists of rows with columns for each testname, test result, AWS fixtures (e.g. Test S3 Bucket Public, fail, <S3 bucket name>)
"""

import argparse
import functools
import itertools
import json


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('-i', '--input', required=True,
                        help='pytest json report input filename.')

    parser.add_argument('-o', '--output', required=True,
                        help='service json output filename.')

    # TODO: sort results by one or more of (ruleset, rule, app, stack, resource type, region, service, account/owner, or test name)
    parser.add_argument('-s', '--sort-keys', default='',
                        help='CSV list of keys to sort test results. Keys applied left to right. Default: ')

    # TODO: groups results by one or more of (ruleset, rule, app, stack, resource type, region, service, account/owner, or test name)
    parser.add_argument('-g', '--group-keys', default='',
                        help='CSV list of keys to group test results by. Keys applied left to right. Default: ')

    args = parser.parse_args()

    args.sort_keys = args.sort_keys.split(',')
    args.group_keys = args.group_keys.split(',')

    if args.group_keys:
        assert args.sort_keys[:len(args.group_keys)] == args.group_keys, 'First sort keys do not match group keys.'

    return args


@functools.lru_cache()
def get_key_fn(key_index, key):
    "Returns a function that returns sort keys to sort by."

    if key in ['profile', 'account']:
        return lambda test: 'not implemented'
    elif key == 'region':
        return lambda test: test['metadata'][0]['unparametrized_name']
    elif key == 'testname':
        return lambda test: test['metadata'][0]['unparametrized_name']
    elif key == 'outcome':
        return lambda test: test['metadata'][0]['outcome']
    else:
        raise NotImplementedError('key function for %s not defined.' % key)


def table_header(table_name, column_names, alignment=None):
    if alignment:
        raise NotImplementedError()

    return '\n'.join([
        '\n#### {}'.format(table_name),
        ' | '.join([''] + column_names + ['']),
        ' | '.join([''] + [':---'] * len(column_names) + ['']),
        '',
    ])


def table_row(values):
    return ' | '.join([''] + [str(v) for v in values] + ['']) + '\n'


def pytest_json_to_md(pytest_json, sort_keys, group_keys, fout):
    tests = pytest_json['report']['tests']

    for i, sort_key in enumerate(sort_keys):
        tests.sort(key=get_key_fn(i, sort_key))

    group_name = lambda test: ' - '.join([
        get_key_fn(0, group_key)(test) for group_key in group_keys
    ])

    # write a table for each group
    for name, tests in itertools.groupby(tests, key=group_name):
        tests = list(tests)

        fixtures = tests[0]['metadata'][0]['fixtures']

        fout.write(table_header(
            table_name=name,
            column_names=['Outcome'] + list(fixtures.keys())))

        for test in tests:
            meta = test['metadata'][0]

            # TODO: make sure these match the column order
            values = [meta['outcome']] + list(fixtures.keys())

            fout.write(table_row(values))


def main():
    args = parse_args()

    pytest_json = json.load(open(args.input, 'r'))

    with open(args.output, 'w') as fout:
        pytest_json_to_md(pytest_json,
                          args.sort_keys,
                          args.group_keys,
                          fout)


if __name__ == '__main__':
    main()
