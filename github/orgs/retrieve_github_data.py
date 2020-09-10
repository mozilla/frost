#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""
Collect Information about branches sufficient to check for all branch
protection guideline compliance.

"""

import csv
from functools import lru_cache
import logging
import os
from dataclasses import dataclass, field
import sys
from typing import Any, List, Optional

from sgqlc.operation import Operation  # noqa: I900
from sgqlc.endpoint.http import HTTPEndpoint  # noqa: I900

from github import github_schema as schema  # noqa: I900

DEFAULT_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

logger = logging.getLogger(__name__)


# Collect and return information about organization protections
@dataclass
class OrgInfo:
    name: str
    login: str
    requires_two_factor_authentication: bool

    @classmethod
    def csv_header(cls) -> List[str]:
        return ["Org Name", "Org Slug", "2FA Required"]

    @classmethod
    def cvs_null(cls) -> List[Optional[str]]:
        return [None, None, None]

    def csv_row(self) -> List[Optional[str]]:
        return [
            self.name or None,
            self.login or None,
            str(self.requires_two_factor_authentication) or None,
        ]


def create_operation(owner):
    """ Create the default Query operation

    We build the structure for:
      organization:
        name (may contain spaces)
        login (no spaces)
        requires 2fa
    """

    op = Operation(schema.Query)

    org = op.organization(login=owner)
    org.name()
    org.login()
    org.requires_two_factor_authentication()

    return op


def get_org_info(endpoint: Any, org: str) -> OrgInfo:
    op = create_operation(org)
    logger.info("Downloading base information from %s", endpoint)

    d = endpoint(op)
    errors = d.get("errors")
    if errors:
        endpoint.report_download_errors(errors)
        return OrgInfo(org)

    orgdata = (op + d).organization

    logger.info("Finished downloading organization: %s", org)
    logger.debug("%s", orgdata)
    return extract_org_data(orgdata)


def extract_org_data(orgdata) -> OrgInfo:
    """ extract relevant data from sgqlc structure

    """
    org_data = OrgInfo(
        name=orgdata.name,
        login=orgdata.login,
        requires_two_factor_authentication=orgdata.requires_two_factor_authentication,
    )
    return org_data


def csv_output(data, csv_writer) -> None:
    csv_writer.writerow(data.csv_row())


def parse_args(*args):
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
        "orgs", nargs="+", help='Organization slug name, such as "mozilla".'
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


def main(*args) -> int:
    args = parse_args(*args)
    if args.output:
        csv_out = csv.writer(open(args.output, "w"))
    else:
        csv_out = csv.writer(sys.stdout)
    # raise SystemExit("Not ready for CLI usage")
    endpoint = HTTPEndpoint(
        args.graphql_endpoint, {"Authorization": "bearer " + args.token,}
    )
    csv_out.writerow(OrgInfo.csv_header())
    for org in args.orgs:
        row_data = get_org_info(endpoint, org)
        csv_output(row_data, csv_writer=csv_out)


if __name__ == "__main__":
    main()
