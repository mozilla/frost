

from collections import defaultdict
from datetime import datetime
import re
import warnings

import pytest


def parse_conf_file(conf_fd):
    """Marks tests as xfail based on test name and ID.

    Parses an open exemptions conf file and returns a two level dict with format:

    {<test_name>:
        {<test_id>: (<exemption line number>, <exemption expiration>, <exemption reason>)
        ...
        }
    ...
    }

    The config file consists of:

    comment lines that have the format:

    '#'<anything>\n

    and exemption lines with the format:

    <test name><whitespace><test id><whitespace><exemption expiration><whitespace><exemption reason>\n

    where:

    <anything> := is any non newline character
    <exemption line number> := line number from the exemption config file
    <exemption expiration> := date in YYYY-MM-DD format the exemption expires
    <exemption reason> := reason for the test exemption (e.g. S3 bucket contains public data)
    <test name> := unparametrized test name
    <test id> := id from the parametrize decorator, optionally prefixed with `*` to enable fuzzy matching
    <whitespace> := anything str.split i.e. one or more ' ', '\t', or '\n' chars

    Examples:

    >>> from io import StringIO
    >>> parse_conf_file(StringIO('# comment')) == {}
    True

    >>> parse_conf_file(StringIO('test_foo foo-id 2050-01-01 in prod never allow foo\\n'
    ... )) == {'test_foo': {'foo-id': (0, '2050-01-01', 'in prod never allow foo')}}
    True

    >>> parse_conf_file(StringIO('test_foo *foo-id 2050-01-01 in prod never allow foo\\n'
    ... )) == {'test_foo': {'*foo-id': (0, '2050-01-01', 'in prod never allow foo')}}
    True

    >>> parse_conf_file(StringIO(
    ... 'test_foo foo-id 2050-01-01 in prod never allow foo for foo-id\\n'
    ... 'test_foo bar-id 2050-01-01 in prod never allow foo for bar-id'
    ... )) == {
    ... 'test_foo': {
    ... 'foo-id': (0, '2050-01-01', 'in prod never allow foo for foo-id'),
    ... 'bar-id': (1, '2050-01-01', 'in prod never allow foo for bar-id')}}
    True


    Short lines are skipped with a warning:

    >>> parse_conf_file(StringIO('invalid line')) == {}
    True
    >>> # UserWarning: Line 0: Skipping line with fewer than 4 whitespace delimited parts.

    Invalid expirations dates are skipped with a warning:

    >>> parse_conf_file(StringIO('test_foo foo-id 2050-01-AA in prod never allow foo')) == {}
    True
    >>> # UserWarning: Line 0: Skipping line with invalid expiration day '2050-01-AA'
    >>> parse_conf_file(StringIO('test_foo foo-id 2000-01-01 in prod never allow foo')) == {}
    True
    >>> # UserWarning: Line 0: Skipping line with expiration day in the past '2000-01-01'

    Duplicate test name and IDs are ignored with a warning:

    >>> parse_conf_file(StringIO(
    ... 'test_foo foo-id 2050-01-01 in prod never allow foo for foo-id\\n'
    ... 'test_foo foo-id 2051-01-01 in prod never allow foo for bar-id'
    ... )) == {
    ... 'test_foo': {'foo-id': (0, '2050-01-01', 'in prod never allow foo for foo-id')}}
    True
    >>> # UserWarning: Line 1: Skipping line with duplicate test name and ID 'test_foo' 'foo-id'

    Does not check that test name and IDs exist (since names might not
    be collected and IDs can require an HTTP call).
    """
    # dict of test name to severity level
    rules = defaultdict(dict)

    if not conf_fd:
        return rules

    for line_number, line in enumerate(conf_fd):
        if line.startswith('#'):
            continue

        line_parts = line.split(maxsplit=3)
        if len(line_parts) < 4:
            warnings.warn('Line {}: Skipping line with fewer than 4 whitespace delimited parts.'.format(line_number))
            continue

        test_name, test_id, expiration, reason = line_parts[0], line_parts[1], line_parts[2], line_parts[3].strip('\n')
        try:
            expiration_date = datetime.strptime(expiration, '%Y-%m-%d')
        except ValueError:
            warnings.warn('Line {}: Skipping line with invalid expiration day {!r}'.format(line_number, expiration))
            continue
        if expiration_date < datetime.now():
            warnings.warn('Line {}: Skipping line with expiration day in the past {!r}'.format(line_number, expiration))
            continue

        if test_id in rules[test_name]:
            warnings.warn('Line {}: Skipping line with duplicate test name and ID {!r} {!r}'.format(
                line_number, test_name, test_id))
            continue

        rules[test_name][test_id] = (line_number, expiration, reason)

    return rules


def add_xfail_marker(item):
    """
    Adds xfail markers for test names and ids specified in the exemptions conf.
    """
    if not item.get_marker('parametrize'):
        warnings.warn('Skipping exemption checks for test without resource name {!r}'.format(item.name))
        return

    test_exemptions = item.config.exemptions.get(item.originalname, None)
    test_id = item._genid

    if test_exemptions:
        # Check for any substring matchers
        for exemption_test_id in test_exemptions:
            if exemption_test_id.startswith('*'):
                substring = exemption_test_id[1:]
                if re.search(substring, test_id):
                    line_number, expiration, reason = test_exemptions[test_id]
                    item.add_marker(pytest.mark.xfail(reason=reason, strict=True, expiration=expiration))
                    return

        if test_id in test_exemptions:
            line_number, expiration, reason = test_exemptions[test_id]
            item.add_marker(pytest.mark.xfail(reason=reason, strict=True, expiration=expiration))
