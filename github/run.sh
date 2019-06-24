#!/usr/bin/env bash

set -ex

PROFILE='github'
source /foxsec/tools/pytest-services/ci-functions.sh

cd /pytest-services/
. venv/bin/activate
pytest --continue-on-collection-errors \
    github/test_download_s3.py \
    --json=results-$PROFILE-$TODAY.json \
    --config /foxsec/tools/pytest-services/$PROFILE/config.yaml || true

generate_service_report $PROFILE $TODAY
create_bugs $PROFILE $TODAY
