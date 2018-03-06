import re
from datetime import datetime, timezone

import yaml
from dateutil.relativedelta import relativedelta

import exemptions
import severity
import regressions


class CustomConfig:

    def __init__(self, config_fd):
        parsed_config = {}
        if config_fd is not None:
            parsed_config = yaml.load(config_fd)
        self.aws = AWSConfig(parsed_config.get('aws', {}))
        self.exemptions = exemptions.load(parsed_config.get('exemptions'))
        self.severities = severity.load(parsed_config.get('severities'))
        self.regressions = regressions.load(parsed_config.get('regressions'))

    def add_markers(self, item):
        severity.add_severity_marker(item)
        exemptions.add_xfail_marker(item)
        regressions.add_regression_marker(item)


class AWSConfig:

    def __init__(self, config):
        self.required_tags = frozenset(config.get('required_tags', []))
        self.whitelisted_ports_global = set(config.get('whitelisted_ports_global', []))
        self.whitelisted_ports = config.get('whitelisted_ports', [])
        self.user_is_inactive = config.get('user_is_inactive', {})

    def get_whitelisted_ports(self, test_id):
        return self.get_whitelisted_ports_from_test_id(test_id) | self.whitelisted_ports_global

    def get_whitelisted_ports_from_test_id(self, test_id):
        for rule in self.whitelisted_ports:
            if rule['test_param_id'].startswith('*'):
                substring = rule['test_param_id'][1:]
                if re.search(substring, test_id):
                    return set(rule['ports'])

            if test_id == rule['test_param_id']:
                return set(rule['ports'])

        return set([])

    def considered_inactive(self):
        considered_inactive = self._parse_user_is_inactive_relative_time('considered_inactive')
        if considered_inactive is None:
            return datetime.now(timezone.utc)-relativedelta(years=+1)
        return considered_inactive

    def grace_period(self):
        grace_period = self._parse_user_is_inactive_relative_time('grace_period')
        if grace_period is None:
            return datetime.now(timezone.utc)-relativedelta(weeks=+1)
        return grace_period

    def _parse_user_is_inactive_relative_time(self, key):
        if self.user_is_inactive.get(key) is None:
            return None

        return datetime.now(timezone.utc)-relativedelta(
            years=+self.user_is_inactive[key].get('years', 0),
            months=+self.user_is_inactive[key].get('months', 0),
            weeks=+self.user_is_inactive[key].get('weeks', 0)
        )
