import re
from datetime import datetime, timezone

from ruamel.yaml import YAML
from dateutil.relativedelta import relativedelta

import exemptions
import severity


class CustomConfig:
    def __init__(self, config_fd):
        parsed_config = {}
        if config_fd is not None:
            yaml = YAML()
            parsed_config = yaml.load(config_fd)
        self.aws = AWSConfig(parsed_config.get("aws", {}))
        self.gcp = GCPConfig(parsed_config.get("gcp", {}))
        self.gsuite = GSuiteConfig(parsed_config.get("gsuite", {}))

        self.exemptions = exemptions.load(parsed_config.get("exemptions"))
        self.severities = severity.load(parsed_config.get("severities"))

    def add_markers(self, item):
        severity.add_severity_marker(item)
        exemptions.add_xfail_marker(item)


class CustomConfigMixin:
    def __init__(self, config):
        self.user_is_inactive = config.get("user_is_inactive", {})
        self.allowed_ports_global = set(config.get("allowed_ports_global", []))
        self.allowed_ports = config.get("allowed_ports", [])

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

    def get_allowed_ports(self, test_id):
        return self.get_allowed_ports_from_test_id(test_id) | self.allowed_ports_global

    def get_allowed_ports_from_test_id(self, test_id):
        for rule in self.allowed_ports:
            if rule["test_param_id"].startswith("*"):
                substring = rule["test_param_id"][1:]
                if re.search(substring, test_id):
                    return set(rule["ports"])

            if test_id == rule["test_param_id"]:
                return set(rule["ports"])

        return set([])


class AWSConfig(CustomConfigMixin):
    def __init__(self, config):
        self.required_tags = frozenset(config.get("required_tags", []))
        self.required_amis = frozenset(config.get("required_amis", []))
        self.access_key_expires_after = config.get("access_key_expires_after", None)
        self.admin_policies = frozenset(config.get("admin_policies", []))
        self.admin_groups = frozenset(config.get("admin_groups", []))
        self.owned_ami_account_ids = [
            str(x) for x in config.get("owned_ami_account_ids", [])
        ]
        self.max_ami_age_in_days = config.get("max_ami_age_in_days", 180)
        super().__init__(config)

    def get_access_key_expiration_date(self):
        if self.access_key_expires_after is None:
            return datetime.now(timezone.utc) - relativedelta(years=+1)

        return datetime.now(timezone.utc) - relativedelta(
            years=+self.access_key_expires_after.get("years", 0),
            months=+self.access_key_expires_after.get("months", 0),
            weeks=+self.access_key_expires_after.get("weeks", 0),
        )


class GCPConfig(CustomConfigMixin):
    def __init__(self, config):
        self.allowed_org_domains = config.get("allowed_org_domains", [])
        self.allowed_gke_versions = config.get("allowed_gke_versions", [])
        super().__init__(config)


class GSuiteConfig(CustomConfigMixin):
    def __init__(self, config):
        self.domain = config.get("domain", "")
        self.min_number_of_owners = int(config.get("min_number_of_owners", "2"))
        super().__init__(config)


class PagerdutyConfig(CustomConfigMixin):
    def __init__(self, config):
        self.users_with_remote_access_monitoring = config.get(
            "users_with_remote_access_monitoring", ""
        )
        self.bastion_users = config.get("bastion_users", "")
        self.alternate_usernames = config.get("alternate_usernames", "")
        super().__init__(config)
