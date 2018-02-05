#!/usr/bin/env bash

# Wrapper script for running the pytest service tests in Jenkins

set -ex

if [ -z "$1" ]; then
  echo "USAGE: ./pytest_wrapper.sh AWS_PROFILE [/path/to/severity.conf] [/path/to/exemptions.conf]"
  exit 1
fi

export _AWS_PROFILE=$1

pytestopts=""
if [ ! -z "$2" ]; then
  pytestopts="--severity-config ${2}"
fi
if [ ! -z "$3" ]; then
  pytestopts="--exemptions-config ${3}"
fi

make install
. venv/bin/activate

# allow pytest commands to fail so we can report results
make awsci AWS_PROFILE=$_AWS_PROFILE PYTEST_OPTS="${pytestopts}" || true

date=$(date +%F)
venv/bin/python3 service_report_generator.py \
  --jo service-report-${_AWS_PROFILE}-${date}.json \
  --mo service-report-${_AWS_PROFILE}-${date}.md \
  results-${_AWS_PROFILE}-${date}.json

# Check in the generated files
mkdir -p /$RESULTS_DIR/aws-pytest/${_AWS_PROFILE}/
cp service-report-${_AWS_PROFILE}-${date}.json /$RESULTS_DIR/aws-pytest/${_AWS_PROFILE}/
cp service-report-${_AWS_PROFILE}-${date}.md /$RESULTS_DIR/aws-pytest/${_AWS_PROFILE}/

cd /$RESULTS_DIR/
git pull
git add aws-pytest/${_AWS_PROFILE}/service-report-${_AWS_PROFILE}-${date}.json
git add aws-pytest/${_AWS_PROFILE}/service-report-${_AWS_PROFILE}-${date}.md
git commit -m "Pytest Services Results - ${_AWS_PROFILE} ${date}"
git push origin master:master
