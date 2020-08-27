#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Collect Information about branches sufficient to check for all branch
protection guideline compliance.

"""
# TODO add doctests

import csv
from functools import lru_cache
import logging
import os
from dataclasses import dataclass, field
import sys
from typing import Any, List

from sgqlc.operation import Operation  # noqa: I900
from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900

# from branch_check.github_schema import github_schema as schema  # noqa: I900
from ..github_schema import github_schema as schema  # noqa: I900

DEFAULT_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
EXTENSION_TO_STRIP = ".git"

# TODO use logger
logger = logging.getLogger(__name__)


# Collect and return information about branch protections
@dataclass
class BranchName:
    name: str
    prefix: str

    @classmethod
    def csv_header(cls) -> List[str]:
        return ["Branch Name", "Ref Prefix"]

    @classmethod
    def cvs_null(cls) -> List[str]:
        return [None, None]

    def csv_row(self) -> List[str]:
        return [self.name or None, self.prefix or None]


@dataclass
class BranchProtectionRule:
    is_admin_enforced: bool
    push_actor_count: int
    rule_conflict_count: int
    pattern: str
    matching_branches: List[BranchName] = field(default_factory=list)

    @classmethod
    def csv_header(cls) -> List[str]:
        return [
            "Inc Admin",
            "Restricted Pusher Count",
            "Conflicting Rule Count",
            "Pattern",
        ] + BranchName.csv_header()

    @classmethod
    def cvs_null(cls) -> List[str]:
        return [None, None, None, None] + BranchName.cvs_null()

    def csv_row(self) -> List[str]:
        my_info = [
            self.isAdminEnforced,
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


@dataclass
class RepoBranchProtections:
    default_branch_ref: str
    name_with_owner: str
    protection_rules: List[BranchProtectionRule] = field(default_factory=list)

    @classmethod
    def csv_header(cls) -> List[str]:
        return ["Login", "Repo"] + BranchProtectionRule.csv_header()

    def csv_row(self) -> List[str]:
        my_info = list(self.name_with_owner.split("/"))
        result = []
        for rule in self.protection_rules:
            for line in rule.csv_row():
                result.append(my_info + line)
        if len(result) == 0:
            result.append(my_info + BranchProtectionRule.cvs_null())
        return result


def _add_protection_fields(node) -> None:
    """ Build in fields we want to query

    In normal gQuery, this would be a fragment
    """
    node.__fields__(is_admin_enforced=True, id=True, pattern=True)
    node.branch_protection_rule_conflicts(first=0).__fields__(total_count=True,)
    node.push_allowances(first=0).__fields__(total_count=True,)


def create_operation(owner, name):
    """ Create the default Query operation

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
        name=True, prefix=True, id=True,
    )

    return op


def create_rule_query():
    """ Create a query object for additional branch protection entries

    Used to fetch subsequent pages. End Cursor is passed as a variable
    """
    op = Operation(schema.Query)

    node = op.branch_protection_rules.nodes(cursor="$LAST_CURSOR")
    _add_protection_fields(node)
    return op


# TODO Should be able to produce iterator for lowest level data


def get_nested_branch_data(endpoint, reponame):
    owner, name = reponame.split("/", 1)
    op = create_operation(owner, name)

    logger.info("Downloading base information from %s", endpoint)

    d = endpoint(op)
    errors = d.get("errors")
    if errors:
        endpoint.report_download_errors(errors)
        return RepoBranchProtections(reponame)

    repodata = (op + d).repository

    def _more_to_do(cur_result, fake_new_page=False):
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

    # TODO determine better way to test
    fake_next_page = False

    # TODO ensure errors are reported out to pytest when invoked from there
    while _more_to_do(repodata, fake_next_page):
        fake_next_page = False
        # Need to work from inside out.
        # and need to iterate over every rule -- KIS & hope for YAGNI
        more_refs = any(
            x.matching_refs.page_info.has_next_page
            for x in repodata.branch_protection_rules.nodes
        )
        if more_refs:
            # # setup for more matching branches
            # page_info = repodata.branch_protection_rules.nodes[0].matching_refs.page_info
            # logger.info(
            #     "Downloading extra matching nodes: branches=%s", page_info
            # )
            # op = create_rule_query()
            # gql_vars = {"$LAST_CURSOR": repodata}
            # pass
            logger.error("Pagination needed for matching refs - not yet implemented")
            break
        elif repodata.branch_protection_rules.page_info.has_next_page:
            # we can't advance here until all matching refs are gathered
            logger.error(
                "Pagination needed for branch protection rules - not yet implemented"
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
    """ extract relevant data from sgqlc structure

    """
    repo_data = RepoBranchProtections(
        name_with_owner=repodata.name_with_owner,
        default_branch_ref=repodata.default_branch_ref,
    )
    # Add in each rule for this repo
    rules = []
    for r in repodata.branch_protection_rules.nodes:
        rule = BranchProtectionRule(
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
    ap.add_argument(
        "repo", nargs="+", help='Repository full name, such as "login/repo".'
    )

    args = ap.parse_args()

    endpoint_loglevel = max(10, 40 - ((args.verbose - 3) * 10))
    logfmt = "%(levelname)s: %(message)s"
    if endpoint_loglevel < logging.ERROR:
        logfmt = "%(levelname)s:%(name)s: %(message)s"

    logging.basicConfig(format=logfmt, level=max(10, 40 - (args.verbose * 10)))
    HTTPEndpoint.logger.setLevel(endpoint_loglevel)

    if not args.token:
        raise SystemExit(
            "token must be provided. You may create an "
            "app or personal token at "
            "https://github.com/settings/tokens"
        )
    return args


# due to pytest parametrization, we'll call this many times for each
# repo consecutively, so a large cache is not needed.
@lru_cache(maxsize=2)
def get_repo_branch_protections(endpoint, repo: str) -> RepoBranchProtections:
    if repo.endswith(EXTENSION_TO_STRIP):
        repo = repo[: -len(EXTENSION_TO_STRIP)]
    data = get_nested_branch_data(endpoint, repo)
    return data


def get_gql_session(endpoint: str, token: str) -> Any:
    """
    Get a real session object
    """
    return HTTPEndpoint(endpoint, {"Authorization": "bearer " + token,})


def main():
    args = parse_args()
    if args.output:
        csv_out = csv.writer(open(args.output, "w"))
    else:
        csv_out = csv.writer(sys.stdout)
    endpoint = get_gql_session(args.graphql_endpoint, args.token,)
    csv_out.writerow(RepoBranchProtections.csv_header())
    for repo in args.repo:
        row_data = get_repo_branch_protections(endpoint, repo)
        csv_output(row_data, csv_writer=csv_out)


if __name__ == "__main__":
    main()
