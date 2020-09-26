#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Collect Information about branches sufficient to check for all branch
protection guideline compliance."""

import csv
from functools import lru_cache
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
import subprocess  # nosec
import sys
from typing import Any, List, Optional, Set

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
    id_: str
    database_id: str

    @staticmethod
    def idfn(val: Any) -> Optional[str]:
        """provide ID for pytest Parametrization."""
        if isinstance(val, (OrgInfo,)):
            return f"{val.id_}-{val.login}"
        return None

    @classmethod
    def csv_header(cls) -> List[str]:
        return ["Org Name", "Org Slug", "2FA Required", "v4id", "v3id"]

    @classmethod
    def cvs_null(cls) -> List[Optional[str]]:
        return [None, None, None, None, None]

    def csv_row(self) -> List[Optional[str]]:
        return [
            self.name or None,
            self.login or None,
            str(self.requires_two_factor_authentication) or None,
            self.id_ or None,
            self.database_id or None,
        ]


def create_operation(owner):
    """Create the default Query operation.

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
    org.id()
    org.database_id()

    return op


def get_org_info(endpoint: Any, org: str) -> OrgInfo:
    op = create_operation(org)
    logger.info("Downloading base information from %s", endpoint)

    d = endpoint(op)
    errors = d.get("errors")
    if errors:
        endpoint.report_download_errors(errors)
        return OrgInfo(
            name="",
            login=org,
            requires_two_factor_authentication=False,
            id_=None,
            database_id=None,
        )

    orgdata = (op + d).organization

    logger.info("Finished downloading organization: %s", org)
    logger.debug("%s", orgdata)
    return extract_org_data(orgdata)


def extract_org_data(orgdata) -> OrgInfo:
    """extract relevant data from sgqlc structure."""
    org_data = OrgInfo(
        name=orgdata.name,
        login=orgdata.login,
        requires_two_factor_authentication=orgdata.requires_two_factor_authentication,
        id_=orgdata.id,
        database_id=orgdata.database_id,
    )
    return org_data


def csv_output(data, csv_writer) -> None:
    csv_writer.writerow(data.csv_row())


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
        "orgs", nargs="*", help='Organization slug name, such as "mozilla".'
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


def _in_offline_mode() -> bool:
    is_offline = False
    try:
        # if we're running under pytest, we need to fetch the value from
        # the current configuration
        import conftest

        is_offline = conftest.get_client("github_client").is_offline()
    except ImportError:
        pass

    return is_offline


def _orgs_to_check() -> Set[str]:
    # just shell out for now
    #   While there is no network operation done here, we don't want to go
    #   poking around the file system if we're in "--offline" mode
    #   (aka doctest mode)
    if _in_offline_mode():
        return []
    path_to_metadata = os.environ.get(
        "PATH_TO_METADATA", "~/repos/foxsec/master/services/metadata"
    )
    meta_dir = Path(os.path.expanduser(path_to_metadata)).resolve()
    in_files = list(meta_dir.glob("*.json"))

    cmd = [
        "jq",
        "-rc",
        """.codeRepositories[]
                | select(.status == "active")
                | [.url]
                | @csv
                """,
        *in_files,
    ]

    # python 3.6 doesn't support capture_output
    status = subprocess.run(cmd, capture_output=True)  # nosec
    ## ##    # fmt: off
    ## ##    status = subprocess.run(  # nosec
    ## ##        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE  # nosec
    ## ##    )
    ## ##    # fmt:on
    assert not status.stderr.decode("utf-8")
    # return as array of non-empty, unquoted, "lines"
    return {
        x.split("/")[3].translate({ord('"'): None, ord("'"): None})
        for x in status.stdout.decode("utf-8").split("\n")
        if x
    }


def get_all_org_data(endpoint: Any = None, orgs: List[str] = None) -> List[OrgInfo]:
    """Generator of org data."""
    if not endpoint:
        # if we're creating the endpoint, then arguments must already be
        # in environment variables.
        endpoint = get_connection(DEFAULT_GRAPHQL_ENDPOINT, os.environ.get("GH_TOKEN"))
    if not orgs:
        orgs = _orgs_to_check()
    for org in orgs:
        data = get_org_info(endpoint, org)
        yield data


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


def get_connection(base_url: str, token: Optional[str]) -> Any:
    # corner case -- we come through here during CI when there is no
    # token and doctests are running, so token is None
    endpoint = HTTPEndpoint(base_url, {"Authorization": "bearer " + (token or ""),})
    endpoint.report_download_errors = _report_download_errors
    return endpoint


def main() -> int:
    # hack to support doctests
    if "pytest" in sys.modules:
        return
    args = parse_args()
    if args.output:
        csv_out = csv.writer(open(args.output, "w"))
    else:
        csv_out = csv.writer(sys.stdout)
    endpoint = get_connection(args.graphql_endpoint, args.token)
    if args.headers:
        csv_out.writerow(OrgInfo.csv_header())
    for row in get_all_org_data(endpoint, args.orgs):
        csv_output(row, csv_writer=csv_out)

    ## csv_out.writerow(OrgInfo.csv_header())
    ## for org in args.orgs:
    ##     row_data = get_org_info(endpoint, org)
    ##     csv_output(row_data, csv_writer=csv_out)


if __name__ == "__main__":
    main()
