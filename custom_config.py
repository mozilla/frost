import re

import yaml

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

    def overlay_cli_opts(self, cli_opts):
        self.aws.overlay_cli_opts(cli_opts)
        return

    def add_markers(self, item):
        severity.add_severity_marker(item)
        exemptions.add_xfail_marker(item)
        regressions.add_regression_marker(item)


class AWSConfig:

    def __init__(self, config):
        self.required_tags = frozenset(config.get('required_tags', []))
        self.whitelisted_ports_global = set(config.get('whitelisted_ports_global', []))
        self.whitelisted_ports = config.get('whitelisted_ports', [])

    def overlay_cli_opts(self, cli_opts):
        if len(cli_opts['aws-require-tags']):
            self.required_tags = frozenset(cli_opts['aws-require-tags'])
        if len(cli_opts['aws-whitelisted-ports']):
            self.whitelisted_ports_global = set(cli_opts['aws-whitelisted-ports'])

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
