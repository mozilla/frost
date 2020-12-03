#!/usr/bin/env bash
# driver script -- won't be in final checkin

set -eu

# set up env variable defaults
export GH_TOKEN=${GH_TOKEN:-$(pass show Mozilla/moz-hwine-PAT)}
set -x
export PATH_TO_METADATA=${PATH_TO_METADATA:-~/repos/foxsec/master/services/metadata}
export TODAY=${TODAY:-$(date --utc --iso=date)}
export PATH_TO_SCRIPTS=${PATH_TO_SCRIPTS:-$PWD/github}

PATH_TO_EXEMPTIONS=${PATH_TO_EXEMPTIONS:-$PWD/github/exemptions-github.yaml}

PROFILE="github"

pytest_json=pytest-results-$PROFILE-$TODAY.json
frost_json=results-$PROFILE-$TODAY.json


pytest --continue-on-collection-errors \
    --quiet --tb=no \
    $PROFILE \
    --json="$pytest_json" \
    --config "${PATH_TO_EXEMPTIONS}" || true

python service_report_generator.py --json-out "${frost_json}" "${pytest_json}"

# post processing works with the modified output from pytest
"$PATH_TO_SCRIPTS/manage_issues.py" "$frost_json"
"$PATH_TO_SCRIPTS/create_metrics.py" "$frost_json"



# # filter for errors we want to open an issue on
# jq '.report.tests[] | select(.call.outcome != "passed")
#     | { full_name: .name,
#         modified_status: .outcome,
#         reason:(.call.xfail_reason // "")
#     }' \
#     $pytest_json \
#     | create_issue
