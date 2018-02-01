#!/usr/bin/env bash

# verbose Print shell input lines as they are read.
set -v
# fail on error
set -e

# Wrapper script for running the pytest service tests in Jenkins

# Docker should mount an ~/.aws/credentials file

make install

# allow pytest commands to fail so we can report results
set +e
make awsci AWS_PROFILE=$AWS_PROFILE
set -e

date=`date +%F`
venv/bin/python3 service_report_generator.py \
  --jo service-report-${AWS_PROFILE}-${date}.json \
  --jm service-report-${AWS_PROFILE}-${date}.md \
  results-${AWS_PROFILE}-${date}.json

# Check in the generated files
mkdir -p /$RESULTS_DIR/aws-pytest/${AWS_PROFILE}/
cp service-report-${AWS_PROFILE}-${date}.json /$RESULTS_DIR/aws-pytest/${AWS_PROFILE}/
cp service-report-${AWS_PROFILE}-${date}.md /$RESULTS_DIR/aws-pytest/${AWS_PROFILE}/

cd /$RESULTS_DIR/
git pull
git add aws-pytest/${AWS_PROFILE}/service-report-${AWS_PROFILE}-${date}.json
git add aws-pytest/${AWS_PROFILE}/service-report-${AWS_PROFILE}-${date}.md
git commit -m "Pytest Services Results ${AWS_PROFILE} ${date}"
git push origin master:master
