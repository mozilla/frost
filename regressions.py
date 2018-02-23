
from collections import defaultdict
import re
import warnings

import pytest


def load(rules):
    """
    TODO
    """
    processed_rules = defaultdict(dict)

    if not rules:
        return processed_rules

    for rule in rules:
        test_name, test_id, comment = rule['test_name'], rule['test_param_id'], rule['comment']

        if test_id in processed_rules[test_name]:
            warnings.warn(
                'Regressions: test_name: {} | test_id: {} | Skipping line with duplicate test name and ID'
                .format(test_name, test_id)
            )
            continue

        processed_rules[test_name][test_id] = comment

    return processed_rules


# TODO: This is fairly similar to exemptions.add_xfail_marker
def add_regression_marker(item):
    """
    Adds regression markers as specified in the config file.
    """
    if not item.get_marker('parametrize'):
        warnings.warn('Skipping regression checks for test without resource name {!r}'.format(item.name))
        return

    test_regressions = item.config.custom_config.regressions.get(item.originalname, None)
    test_id = item._genid

    if test_regressions:
        for regression_test_id in test_regressions:
            if regression_test_id.startswith('*'):
                substring = regression_test_id[1:]
                if re.search(substring, test_id):
                    comment = test_regressions[regression_test_id]
                    item.add_marker(pytest.mark.regression(comment))
                    return

        if test_id in test_regressions:
            comment = test_regressions[test_id]
            item.add_marker(pytest.mark.regression(comment))
