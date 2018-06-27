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
        self.aws = AWSConfig(parsed_config.get("aws", {}))
        self.gsuite = GSuiteConfig(parsed_config.get("gsuite", {}))
        self.exemptions = exemptions.load(parsed_config.get("exemptions"))
        self.severities = severity.load(parsed_config.get("severities"))
        self.regressions = regressions.load(parsed_config.get("regressions"))

    def add_markers(self, item):
        severity.add_severity_marker(item)
        exemptions.add_xfail_marker(item)
        regressions.add_regression_marker(item)


class CustomConfigMixin:
    def __init__(self, config):
        self.user_is_inactive = config.get("user_is_inactive", {})

    def no_activity_since(self):
        no_activity_since = self._parse_user_is_inactive_relative_time(
            "no_activity_since"
        )
        if no_activity_since is None:
            return datetime.now(timezone.utc) - relativedelta(years=+1)
        return no_activity_since

    def created_after(self):
        created_after = self._parse_user_is_inactive_relative_time("created_after")
        if created_after is None:
            return datetime.now(timezone.utc) - relativedelta(weeks=+1)
        return created_after

    def _parse_user_is_inactive_relative_time(self, key):
        if self.user_is_inactive.get(key) is None:
            return None

        return datetime.now(timezone.utc) - relativedelta(
            years=+self.user_is_inactive[key].get("years", 0),
            months=+self.user_is_inactive[key].get("months", 0),
            weeks=+self.user_is_inactive[key].get("weeks", 0),
        )


class AWSConfig(CustomConfigMixin):
    def __init__(self, config):
        self.required_tags = frozenset(config.get("required_tags", []))
        self.whitelisted_ports_global = set(config.get("whitelisted_ports_global", []))
        self.whitelisted_ports = config.get("whitelisted_ports", [])
        self.access_key_expires_after = config.get("access_key_expires_after", None)
        super().__init__(config)

    def get_whitelisted_ports(self, test_id):
        return (
            self.get_whitelisted_ports_from_test_id(test_id)
            | self.whitelisted_ports_global
        )

    def get_whitelisted_ports_from_test_id(self, test_id):
        for rule in self.whitelisted_ports:
            if rule["test_param_id"].startswith("*"):
                substring = rule["test_param_id"][1:]
                if re.search(substring, test_id):
                    return set(rule["ports"])

            if test_id == rule["test_param_id"]:
                return set(rule["ports"])

        return set([])

    def get_access_key_expiration_date(self):
        if self.access_key_expires_after is None:
            return datetime.now(timezone.utc) - relativedelta(years=+1)

        return datetime.now(timezone.utc) - relativedelta(
            years=+self.access_key_expires_after.get("years", 0),
            months=+self.access_key_expires_after.get("months", 0),
            weeks=+self.access_key_expires_after.get("weeks", 0),
        )


class GSuiteConfig(CustomConfigMixin):
    def __init__(self, config):
        self.domain = config.get("domain", "")
        super().__init__(config)
