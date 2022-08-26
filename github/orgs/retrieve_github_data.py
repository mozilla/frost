#!/usr/bin/env python3
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Collect Information about branches sufficient to check for all branch
protection guideline compliance."""

import csv
import logging
import os
from dataclasses import dataclass
from datetime import date
import json
from pathlib import Path
import subprocess  # nosec
import sys
from typing import Any, List, Optional, Set

from sgqlc.operation import Operation
from sgqlc.endpoint.http import HTTPEndpoint

from github import github_schema as schema

DEFAULT_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"

logger = logging.getLogger(__name__)

# Todo figure out how to avoid global
_collection_date: str = "1970-01-01"

# Collect and return information about organization protections
@dataclass
class OrgInfo:
    org_name: str
    login: str
    requires_two_factor_authentication: bool
    org_v4id: str
    org_v3id: str
    _type: str = "OrgInfo"
    _revision: int = 1

    @classmethod
    def metadata_to_log(_) -> List[str]:
        return ["org_name", "login", "requires_two_factor_authentication", "org_v4id"]

    @staticmethod
    def idfn(val: Any) -> Optional[str]:
        """provide ID for pytest Parametrization."""
        if isinstance(val, (OrgInfo,)):
            return f"{val.login}"
        return None

    @classmethod
    def csv_header(cls) -> List[str]:
        return ["day", "Org Name", "Org Slug", "2FA Required", "org_v4id", "org_v3id"]

    @classmethod
    def cvs_null(cls) -> List[Optional[str]]:
        return [None, None, None, None, None]

    def csv_row(self) -> List[Optional[str]]:
        global _collection_date
        return [
            _collection_date,
            self.org_name or None,
            self.login or None,
            str(self.requires_two_factor_authentication) or None,
            self.org_v4id or None,
            self.org_v3id or None,
        ]

    def as_dict(self):
        global _collection_date
        d = {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
        d["day"] = _collection_date
        return d


def create_operation(owner):
    """Create the default Query operation.

    We build the structure for:
      organization:
        org_name (may contain spaces)
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
            org_name="",
            login=org,
            requires_two_factor_authentication=False,
            org_v4id=None,
            org_v3id=None,
        )

    orgdata = (op + d).organization

    logger.info("Finished downloading organization: %s", org)
    logger.debug("%s", orgdata)
    return extract_org_data(orgdata)


def extract_org_data(orgdata) -> OrgInfo:
    """extract relevant data from sgqlc structure."""
    org_data = OrgInfo(
        org_name=orgdata.name,
        login=orgdata.login,
        requires_two_factor_authentication=orgdata.requires_two_factor_authentication,
        org_v4id=orgdata.id,
        org_v3id=orgdata.database_id,
    )
    return org_data


def csv_output(data, csv_writer) -> None:
    csv_writer.writerow(data.csv_row())


def parse_args():
    import argparse

    ap = argparse.ArgumentParser(description="GitHub Organization Dashboard")

    # Generic options to access the GraphQL API
    ap.add_argument(
        "--graphql-endpoint",
        help=("GitHub GraphQL endpoint. " "Default=%(default)s"),
        default=DEFAULT_GRAPHQL_ENDPOINT,
    )
    ap.add_argument(
        "--token",
        "-T",
        default=os.environ.get("GH_TOKEN"),
        help=("API token to use."),
    )
    ap.add_argument(
        "--output",
        help=("Filename to write to (default STDOUT)",),
    )
    ap.add_argument(
        "--verbose", "-v", help="Increase verbosity", action="count", default=0
    )
    ap.add_argument(
        "--no-csv",
        help="Do not output to CSV (default False if called via cli).",
        action="store_true",
    )
    ap.add_argument("--no-json", help="Do not output JSON.", action="store_true")
    ap.add_argument(
        "--json",
        help="JSON output file name (default 'org.json')",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    meg = ap.add_mutually_exclusive_group()
    meg.add_argument("--prod", help="run against prod org set", action="store_true")
    meg.add_argument("--all", help="run against all orgs you own", action="store_true")

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
        ap.error(
            "token must be provided. You may create an "
            "app or personal token at "
            "https://github.com/settings/tokens"
        )
    if not (args.prod or args.all) and (len(args.orgs) == 0):
        ap.error("Must supply 'repo' or set either '--prod' or '--all'")
    return args


def validate_viewer(endpoint):
    # Debugging proper credentials can be challenging, so print out the
    # "viewer" ("authenticated user" in v3 parlance)

    from sgqlc.operation import Operation  # noqa: I900
    from github import github_schema as schema  # noqa: I900

    op = Operation(schema.Query)

    org = op.viewer()
    org.login()
    d = endpoint(op)
    errors = d.get("errors")
    if errors:
        raise ValueError("Invalid GitHub credentials")


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
            endpoint = get_connection(
                DEFAULT_GRAPHQL_ENDPOINT, os.environ.get("GH_TOKEN")
            )
            validate_viewer(endpoint)

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
    # DEV_HACK: find better way to insert dev default
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
    assert not status.stderr.decode("utf-8")
    # return as array of non-empty, unquoted, "lines"
    return {
        x.split("/")[3].translate({ord('"'): None, ord("'"): None})
        for x in status.stdout.decode("utf-8").split("\n")
        if x
    }


def _all_owned_orgs(endpoint: Any) -> List[str]:
    """Return a list of all orgs for which this user has owner permissions."""

    op = Operation(schema.Query)

    me = op.viewer()
    me.login()
    org = me.organizations(first=100).nodes()
    org.login()
    org.viewer_can_administer()
    d = endpoint(op)
    errors = d.get("errors")
    if errors:
        logger.error("using PAT {}".format(os.environ.get("GH_TOKEN", "<unset>")))
        endpoint.report_download_errors(errors)
        raise StopIteration
    else:
        for x in (op + d).viewer.organizations.nodes:
            if x.viewer_can_administer:
                yield x.login


def get_all_org_data(
    endpoint: Any = None, orgs: List[str] = None, all_permitted: bool = False
) -> List[OrgInfo]:
    """Generator of org data."""
    if not endpoint:
        # if we're creating the endpoint, then arguments must already be
        # in environment variables.
        endpoint = get_connection(DEFAULT_GRAPHQL_ENDPOINT, os.environ.get("GH_TOKEN"))
    if not orgs:
        if all_permitted:
            orgs = _all_owned_orgs(endpoint)
        else:
            # Just get the ones we are configured to monitor
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
    endpoint = HTTPEndpoint(
        base_url,
        {
            "Authorization": "bearer " + (token or ""),
        },
    )
    endpoint.report_download_errors = _report_download_errors

    # determine which date we're collecting for
    global _collection_date
    assert _collection_date == "1970-01-01"
    _collection_date = date.today().isoformat()
    return endpoint


def main() -> None:
    # hack to support doctests
    if "pytest" in sys.modules:
        return
    args = parse_args()
    if args.output:
        csv_out = csv.writer(open(args.output, "w"))
    else:
        csv_out = csv.writer(sys.stdout)
    endpoint = get_connection(args.graphql_endpoint, args.token)
    if not args.no_csv:
        csv_out.writerow(OrgInfo.csv_header())
        for row in get_all_org_data(endpoint, args.orgs, args.all):
            csv_output(row, csv_writer=csv_out)
    if not args.no_json:
        with args.json as jf:
            for row in get_all_org_data(endpoint, args.orgs, args.all):
                jf.write(f"{json.dumps(row.as_dict())}\n")

    ## csv_out.writerow(OrgInfo.csv_header())
    ## for org in args.orgs:
    ##     row_data = get_org_info(endpoint, org)
    ##     csv_output(row_data, csv_writer=csv_out)


if __name__ == "__main__":
    main()
