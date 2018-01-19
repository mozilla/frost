#!/usr/bin/env bash

# verbose Print shell input lines as they are read.
set -v
# fail on error
set -e

# Wrapper script for running the pytest service tests in Jenkins

# Docker should mount an ~/.aws/credentials file
# or provide cred env vars http://docs.aws.amazon.com/cli/latest/userguide/cli-environment.html

cd /foxsec/tools/pytest-services
make install

# allow pytest commands to fail so we can report results
set +e
make clean all
set -e

# Check in the generated files
date=`date +%F`
cp $date.* /foxsec-results/pytest-services
cd /foxsec-results/pytest-services

git pull

git add $date.*
git commit -m "Pytest Results $date"
git push origin master:master
