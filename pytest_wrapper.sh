#!/usr/bin/env bash

# Wrapper script for running the pytest service tests in Jenkins

set -ex

if [ -z "$1" ]; then
  echo "USAGE: ./pytest_wrapper.sh AWS_PROFILE"
  exit 1
fi

export AWS_PROFILE=$1

make install
. venv/bin/activate

# allow pytest commands to fail so we can report results
make awsci AWS_PROFILE=$AWS_PROFILE || true

date=$(date +%F)
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
git commit -m "Pytest Services Results - ${AWS_PROFILE} ${date}"
git push origin master:master
