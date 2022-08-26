#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Collect Information about branches sufficient to check for all branch
protection guideline compliance."""
# TODO add doctests

import pathlib
import subprocess  # nosec
from datetime import date
from functools import lru_cache
import csv
from github import branches
import logging
import os
from dataclasses import dataclass, field
import json
import sys
from typing import Any, Generator, Optional, List

from sgqlc.operation import Operation  # noqa: I900
from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900

from github import github_schema as schema  # noqa: I900

DEFAULT_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
EXTENSION_TO_STRIP = ".git"

logger = logging.getLogger(__name__)


# Collect and return information about branch protections
# The relationships are (mermaid syntax):
#   erDiagram
#       Repo ||--|{ Branch : belongs-to
#       Repo ||--o{ BranchProtectionRule : may-have
#       Branch }o--o{ BranchProtectionRule: matches-pattern-of-bpr
#
# For processing, we flatten to BranchProtectionRule-Branch for every
# BPR that actually matches a current branch.
@dataclass
class BranchName:
    branch_name: str
    branch_prefix: str
    _type: str = "BranchName"
    _revision: int = 1

    @classmethod
    def csv_header(cls) -> List[str]:
        return ["Branch Name", "Ref Prefix"]

    @classmethod
    def cvs_null(cls) -> List[str]:
        return [None, None, None, None]

    def csv_row(self) -> List[str]:
        return [
            self.branch_name or None,
            self.branch_prefix or None,
        ]

    def flat_json(self) -> Generator:
        yield {**self.as_dict()}

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


@dataclass
class BranchProtectionRule:
    bpr_v4id: str
    bpr_v3id: str
    is_admin_enforced: bool
    push_actor_count: int
    rule_conflict_count: int
    pattern: str
    matching_branches: List[BranchName] = field(default_factory=list)
    _type: str = "BranchProtectionRule"
    _revision: int = 1

    @classmethod
    def csv_header(cls) -> List[str]:
        return [
            "bpr_v4id",
            "bpr_v3id",
            "Inc Admin",
            "Restricted Pusher Count",
            "Conflicting Rule Count",
            "Pattern",
        ] + BranchName.csv_header()

    @classmethod
    def cvs_null(cls) -> List[str]:
        return [None, None, None, None, None, None] + BranchName.cvs_null()

    def csv_row(self) -> List[str]:
        my_info = [
            self.bpr_v4id,
            self.bpr_v3id,
            self.is_admin_enforced,
            self.push_actor_count,
            self.rule_conflict_count,
            self.pattern,
        ]
        result = []
        for branch_names in self.matching_branches:
            result.append(my_info + branch_names.csv_row())
        if len(result) == 0:
            result.append(my_info + BranchName.cvs_null())
        return result

    def flat_json(self) -> Generator:
        exportable_dict = self.as_dict()
        del exportable_dict["matching_branches"]
        for branch in self.matching_branches:
            for match in branch.flat_json():
                copy = exportable_dict.copy()
                copy.update(match)
                assert len(copy) == len(exportable_dict) + len(match)
                yield copy

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}


# DEV_HACK figure out how to avoid global
_collection_date: str = "1970-01-01"


@dataclass
class RepoBranchProtections:
    name_with_owner: str
    default_branch_ref: str = ""
    owner_v4id: str = ""
    repo_v4id: str = ""
    repo_v3id: str = ""
    protection_rules: List[BranchProtectionRule] = field(default_factory=list)
    _type: str = "RepoBranchProtections"
    _revision: int = 1

    @classmethod
    def csv_header(cls) -> List[str]:
        return [
            "day",
            "Login",
            "Repo",
            "repo_v4id",
            "repo_v3id",
            "default branch",
            "owner_v4id",
        ] + BranchProtectionRule.csv_header()

    def csv_row(self) -> List[str]:
        global _collection_date
        my_info = [_collection_date]
        my_info.extend(self.name_with_owner.split("/"))
        my_info.extend(
            (self.repo_v4id, self.repo_v3id, self.default_branch_ref, self.owner_v4id)
        )
        result = []
        for rule in self.protection_rules:
            for line in rule.csv_row():
                result.append(my_info + line)
        if len(result) == 0:
            result.append(my_info + BranchProtectionRule.cvs_null())
        return result

    def flat_json(self) -> Generator:
        exportable_dict = self.as_dict()
        del exportable_dict["protection_rules"]
        for rule in self.protection_rules:
            for d in rule.flat_json():
                copy = {**exportable_dict, **d}
                assert len(copy) == len(exportable_dict) + len(d)
                yield copy

    def as_dict(self):
        global _collection_date
        d = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        d["day"] = _collection_date
        return d


@dataclass
class BranchOfInterest:
    """
    docstring
    """

    owner: str
    repo: str
    branch: str
    status: str

    @classmethod
    def metadata_to_log(_) -> List[str]:
        return ["owner", "repo", "branch", "status"]

    @staticmethod
    def idfn(val: Any) -> Optional[str]:
        """provide ID for pytest Parametrization."""
        if isinstance(val, (BranchOfInterest,)):
            return f"{val.owner}/{val.repo}:{val.branch}"
        return None


def _add_protection_fields(node) -> None:
    """Build in fields we want to query.

    In normal gQuery, this would be a fragment
    """
    node.__fields__(is_admin_enforced=True, id=True, pattern=True, database_id=True)
    node.branch_protection_rule_conflicts(first=0).__fields__(total_count=True,)
    node.push_allowances(first=0).__fields__(total_count=True,)


def create_operation(owner, name):
    """Create the default Query operation.

    We build the structure for:
      repository:
        0-n branch protections rules
          flags
          0-n conflicts with other rules (we only count)
          0-n actors who can push (we only count)
          0-n branches with this protection
    """

    op = Operation(schema.Query)

    repo = op.repository(owner=owner, name=name)
    repo.default_branch_ref.__fields__(name=True)
    repo.name_with_owner()
    repo.id()
    repo.database_id()
    repo.owner().id()
    repo.owner().login()

    # now specify which fields we care about
    # we only get one item at a time to
    # simplify getting all.
    # N.B. anything we can get multiple of, we need to gather the 'id'
    #       as well, in case pagination is needed
    branch_protection = repo.branch_protection_rules(first=10)
    branch_protection.total_count()
    branch_protection.page_info.__fields__(end_cursor=True, has_next_page=True)

    # we'll have to iterate on branch protection entries
    node = branch_protection.nodes()
    _add_protection_fields(node)

    # we'll have to iterate on matching branches for this branch
    # protection rule
    # Currently, we avoid iteration by tuning the value to never require
    # multiple pages. This technique is brittle, but may be sufficient.
    ref = node.matching_refs(first=50)
    ref.total_count()
    ref.page_info.__fields__(end_cursor=True, has_next_page=True)
    ref.nodes().__fields__(
        name=True, prefix=True,
    )

    return op


def create_rule_query():
    """Create a query object for additional branch protection entries.

    Used to fetch subsequent pages. End Cursor is passed as a variable
    """
    op = Operation(schema.Query)

    node = op.branch_protection_rules.nodes(cursor="$LAST_CURSOR")
    _add_protection_fields(node)
    return op


def get_nested_branch_data(endpoint, reponame):
    owner, name = reponame.split("/", 1)
    op = create_operation(owner, name)

    logger.info("Downloading base information from %s", endpoint)

    d = endpoint(op)
    errors = d.get("errors")
    if errors:
        endpoint.report_download_errors(errors)
        return RepoBranchProtections(name_with_owner=reponame)

    repodata = (op + d).repository

    def _more_to_do(cur_result, fake_new_page=False):
        """Determine if we need another query.

        There are two nested repeating elements in the query - if either
        is not yet exhausted, we have to do another query
        """
        # for hacky testing
        if fake_new_page:
            cur_result.branch_protection_rules.nodes[
                0
            ].matching_refs.page_info.has_next_page = True

        has_more_rules = cur_result.branch_protection_rules.page_info.has_next_page
        has_more_refs = any(
            x.matching_refs.page_info.has_next_page
            for x in cur_result.branch_protection_rules.nodes
        )
        return has_more_rules or has_more_refs

    # DEV_HACK for testing manually, set fake_next_page to True
    fake_next_page = False

    while _more_to_do(repodata, fake_next_page):
        fake_next_page = False
        # Need to work from inside out.
        # and need to iterate over every rule -- KIS & hope for YAGNI
        more_refs = any(
            x.matching_refs.page_info.has_next_page
            for x in repodata.branch_protection_rules.nodes
        )
        if more_refs:
            # pagination isn't implemented yet. Try upping the limits in the
            # query to avoid tripping this error.
            logger.error(
                f"Pagination needed for matching refs in {reponame}- not yet implemented"
            )
            break
        elif repodata.branch_protection_rules.page_info.has_next_page:
            # we can't advance here until all matching refs are gathered
            logger.error(
                f"Pagination needed for branch protection rules in {reponame}- not yet implemented"
            )
            break
        else:
            logger.error("ERROR: bad logic in pagination tests")

        logger.debug("Operation:\n%s", op)

        cont = endpoint(op)
        errors = cont.get("errors")
        if errors:
            return endpoint.report_download_errors(errors)

        (op + cont).repository

    logger.info("Finished downloading repository: %s", reponame)
    logger.debug("%s", repodata)
    return extract_branch_data(repodata)


def extract_branch_data(repodata) -> RepoBranchProtections:
    """extract relevant data from sgqlc structure."""
    repo_data = RepoBranchProtections(
        name_with_owner=repodata.name_with_owner,
        default_branch_ref=repodata.default_branch_ref.name,
        repo_v4id=repodata.id,
        repo_v3id=repodata.database_id,
        owner_v4id=repodata.owner.id,
    )
    # Add in each rule for this repo
    rules = []
    for r in repodata.branch_protection_rules.nodes:
        rule = BranchProtectionRule(
            r.id,
            r.database_id,
            r.is_admin_enforced,
            r.push_allowances.total_count,
            r.branch_protection_rule_conflicts.total_count,
            r.pattern,
        )
        # add branches that match this rule
        matches = []
        for m in r.matching_refs.nodes:
            match = BranchName(m.name, m.prefix)
            matches.append(match)
        rule.matching_branches = matches
        rules.append(rule)
    repo_data.protection_rules = rules
    return repo_data


def csv_output(data, csv_writer) -> None:
    for line in data.csv_row():
        csv_writer.writerow(line)


def parse_args():
    import argparse

    ap = argparse.ArgumentParser(description="GitHub Agile Dashboard")

    # Generic options to access the GraphQL API
    ap.add_argument(
        "--graphql-endpoint",
        help=("GitHub GraphQL endpoint. " "Default=%(default)s"),
        default=DEFAULT_GRAPHQL_ENDPOINT,
    )
    ap.add_argument(
        "--token", "-T", default=os.environ.get("GH_TOKEN"), help=("API token to use."),
    )
    ap.add_argument(
        "--output", help=("Filename to write to (default STDOUT)",),
    )
    ap.add_argument(
        "--verbose", "-v", help="Increase verbosity", action="count", default=0
    )
    # Default to no headers for common automation case of generating for
    # AWS Athena
    ap.add_argument(
        "--headers", help="Add column headers to csv output", action="store_true"
    )
    ap.add_argument(
        "--no-csv",
        help="Do not output to CSV (default True if called via cli).",
        action="store_true",
    )
    ap.add_argument("--no-json", help="Do not output JSON.", action="store_true")
    ap.add_argument("--prod", help="run against prod repo set", action="store_true")
    ap.add_argument(
        "--json",
        help="JSON output file name",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    ap.add_argument(
        "repo", nargs="*", help='Repository full name, such as "login/repo".'
    )

    args = ap.parse_args()

    endpoint_loglevel = max(10, 40 - ((args.verbose - 3) * 10))
    logfmt = "%(levelname)s: %(message)s"
    if endpoint_loglevel < logging.ERROR:
        logfmt = "%(levelname)s:%(name)s: %(message)s"

    logging.basicConfig(format=logfmt, level=max(10, 40 - (args.verbose * 10)))
    HTTPEndpoint.logger.setLevel(endpoint_loglevel)

    if not args.token:
        ap.error(
            "token must be provided. You may create an "
            "app or personal token at "
            "https://github.com/settings/tokens"
        )
    if not args.prod and (len(args.repo) == 0):
        ap.error("Must supply 'repo' or set '--prod'")
    return args


# due to pytest parametrization, we'll call this many times for each
# repo consecutively, so a large cache is not needed.
@lru_cache(maxsize=2)
def get_repo_branch_protections(endpoint, repo: str) -> RepoBranchProtections:
    if repo.endswith(EXTENSION_TO_STRIP):
        repo = repo[: -len(EXTENSION_TO_STRIP)]
    data = get_nested_branch_data(endpoint, repo)
    return data


# helper classes for graph errors
def _compact_fmt(d):
    s = []
    for k, v in d.items():
        if isinstance(v, dict):
            v = _compact_fmt(v)
        elif isinstance(v, (list, tuple)):
            lst = []
            for e in v:
                if isinstance(e, dict):
                    lst.append(_compact_fmt(e))
                else:
                    lst.append(repr(e))
            s.append("{}=[{}]".format(k, ", ".join(lst)))
            continue
        s.append(f"{k}={v!r}")
    return "(" + ", ".join(s) + ")"


def _report_download_errors(errors):
    """error handling for graphql comms."""
    logger.error("Document contain %d errors", len(errors))
    for i, e in enumerate(errors):
        msg = e.pop("message")
        extra = ""
        if e:
            extra = " %s" % _compact_fmt(e)
        logger.error("Error #%d: %s%s", i + 1, msg, extra)


def get_connection(base_url: str, token: str) -> Any:
    endpoint = HTTPEndpoint(base_url, {"Authorization": "bearer " + token,})
    endpoint.report_download_errors = _report_download_errors

    # determine which date we're collecting for
    global _collection_date
    assert _collection_date == "1970-01-01"
    _collection_date = date.today().isoformat()
    return endpoint


def _in_offline_mode() -> bool:
    is_offline = False
    try:
        # if we're running under pytest, we need to fetch the value from
        # the current configuration
        import conftest

        is_offline = conftest.get_client("github_client").is_offline()
        if not is_offline:
            # check for a valid GH_TOKEN here so we fail during test collection
            os.environ["GH_TOKEN"]
    except ImportError:
        pass

    return is_offline


def repos_to_check() -> List[BranchOfInterest]:
    # just shell out for now
    #   While there is no network operation done here, we don't want to go
    #   poking around the file system if we're in "--offline" mode
    #   (e.g. doctest mode)
    if _in_offline_mode():
        return []

    # real work
    # DEV_HACK: find better way to insert dev default
    path_to_metadata = os.environ.setdefault(
        "PATH_TO_METADATA", "~/repos/foxsec/master/services/metadata"
    )
    meta_dir = pathlib.Path(os.path.expanduser(path_to_metadata)).resolve()
    in_files = list(meta_dir.glob("*.json"))

    cmd = [
        "jq",
        "-rc",
        """.codeRepositories[]
                | select(.status != "deprecated")
                | .url as $url
                | .status as $status
                | .branchesToProtect[] // ""
                | [$url, ., $status ]
                | @csv
                """,
        *in_files,
    ]

    status = subprocess.run(cmd, capture_output=True)  # nosec
    owner_repo = []
    for line in [
        x.translate({ord('"'): None, ord("'"): None})
        for x in status.stdout.decode("utf-8").split("\n")
        if x
    ]:
        if "," in line:
            url, branch, status = line.split(",")
        else:
            url, branch = line, "", "unknown"
        owner, repo = url.split("/")[3:5]
        branch_info = BranchOfInterest(owner, repo, branch, status)
        owner_repo.append(branch_info)

    return owner_repo


def main() -> int:
    # hack to support doctests
    if "pytest" in sys.modules:
        return
    args = parse_args()
    endpoint = get_connection(args.graphql_endpoint, args.token)
    if args.prod:
        # DEVHACK should have way to preserve status from cli -- maybe filter
        # in this comprehension?
        args.repo = [f"{x.owner}/{x.repo}" for x in repos_to_check()]
    if not args.no_csv:
        if args.output:
            csv_out = csv.writer(open(args.output, "w"))
        else:
            csv_out = csv.writer(sys.stdout)
        csv_out.writerow(RepoBranchProtections.csv_header())
        for repo in args.repo:
            row_data = get_repo_branch_protections(endpoint, repo)
            csv_output(row_data, csv_writer=csv_out)

    with args.json as jf:
        if not args.no_json:
            for repo in args.repo:
                repo_data = get_repo_branch_protections(endpoint, repo)
                for bprs in repo_data.flat_json():
                    jf.write(f"{json.dumps(bprs)}\n")


if __name__ == "__main__":
    main()
