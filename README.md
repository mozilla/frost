# pytest-services

Clients and [pytest](https://docs.pytest.org/en/latest/index.html)
tests for checking that third party services the @foxsec team uses are
configured correctly.

We trust third party services to return their status correctly, but
want to answer questions whether they are configured properly such as:

* Are our AWS DB snapshots publicly accessible?
* Is there a dangling DNS entry in Route53?
* Will someone get paged when an alert goes off?

## Usage

### Requirements

* [GNU Make 3.81](https://www.gnu.org/software/make/)
* [Python 3.6.2](https://www.python.org/downloads/)

Note: other versions may work too these are the versions @g-k used for development

### Installing

From the project root run:

```console
make install
```

This will:

* create a Python [virtualenv](https://docs.python.org/3/library/venv.html) to isolate it from other Python packages
* install Python requirements in the virtualenv

### Running

Activate the venv in the project root:

```console
source venv/bin/activate
```

To fetch RDS resources from the cache or AWS API and check that
backups are enabled for DB instances for [the configured aws
profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html)
named `default` in the `us-west-2` region we can run:

```console
pytest --ignore pagerduty/ --ignore aws/s3 --ignore aws/ec2 -k test_rds_db_instance_backup_enabled -s --aws-profiles default --aws-regions us-west-2 --aws-debug-calls
```

The options include pytest options:

* [`--ignore`](https://docs.pytest.org/en/latest/example/pythoncollection.html#ignore-paths-during-test-collection) to skip fetching resources for non-RDS resources
* [`-k`](https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name) for selecting tests matching the substring `test_rds_db_instance_backup_enabled` for the one test we want to run
* [`-m`](https://docs.pytest.org/en/latest/example/markers.html#marking-test-functions-and-selecting-them-for-a-run) not used but the marker filter can be useful for selecting all tests for specific services (e.g. `-m rds`)
* [`-s`](https://docs.pytest.org/en/latest/capture.html) to disable capturing stdout so we can see the progress fetching AWS resources

and options pytest-services adds for the AWS client:

* `--aws-debug-calls` for printing (with `-s`) API calls we make
* `--aws-profiles` for selecting one or more AWS profiles to fetch resources for or the AWS default profile / `AWS_PROFILE` environment variable
* `--aws-regions` for selecting one or more AWS regions to fetch resources from or the default of all regions

and produces output like the following showing a DB instance with backups disabled:

```console
=========================================================== test session starts ===========================================================
platform darwin -- Python 3.6.2, pytest-3.3.2, py-1.5.2, pluggy-0.6.0
metadata: {'Python': '3.6.2', 'Platform': 'Darwin-15.6.0-x86_64-i386-64bit', 'Packages': {'pytest': '3.3.2', 'py': '1.5.2', 'pluggy': '0.6.
0'}, 'Plugins': {'metadata': '1.5.1', 'json': '0.4.0', 'html': '1.16.1'}}
rootdir: /Users/gguthe/mozilla-services/pytest-services, inifile:
plugins: metadata-1.5.1, json-0.4.0, html-1.16.1
collecting 0 items                                                                                                                        c
alling AWSAPICall(profile='default', region='us-west-2', service='rds', method='describe_db_instances', args=[], kwargs={})
collecting 4 items
...
aws/rds/test_rds_db_instance_backup_enabled.py ...F                                                                                 [100%]

================================================================ FAILURES =================================================================
_______________________________________ test_rds_db_instance_backup_enabled[test-db] ________________________________________

rds_db_instance = {'AllocatedStorage': 50, 'AutoMinorVersionUpgrade': True, 'AvailabilityZone': 'us-west-2c', 'BackupRetentionPeriod': 0, .
..}

    @pytest.mark.rds
    @pytest.mark.parametrize('rds_db_instance',
                             rds_db_instances(),
                             ids=lambda db_instance: db_instance['DBInstanceIdentifier'])
    def test_rds_db_instance_backup_enabled(rds_db_instance):
>       assert rds_db_instance['BackupRetentionPeriod'] > 0, \
            'Backups disabled for {}'.format(rds_db_instance['DBInstanceIdentifier'])
E       AssertionError: Backups disabled for test-db
E       assert 0 > 0

aws/rds/test_rds_db_instance_backup_enabled.py:12: AssertionError
=========================================================== 72 tests deselected ===========================================================
============================================ 1 failed, 3 passed, 72 deselected in 3.12 seconds ============================================
```

### Caching

The AWS client will use AWS API JSON responses when available and save them using AWS profile, region, service name, service method, [botocore](http://botocore.readthedocs.io/) args and kwargs in the cache key to filenames with the format `.cache/v/pytest_aws:<aws profile>:<aws region>:<aws service>:<service method>:<args>:<kwargs>.json` e.g.

```
head .cache/v/pytest_aws:cloudservices-aws-stage:us-west-2:rds:describe_db_instances::.json
{
    "DBInstances": [
        {
            "AllocatedStorage": 5,
            "AutoMinorVersionUpgrade": true,
            "AvailabilityZone": "us-west-2c",
            "BackupRetentionPeriod": 1,
            "CACertificateIdentifier": "rds-ca-2015",
            "CopyTagsToSnapshot": false,
            "DBInstanceArn": "arn:aws:rds:us-west-2:123456678901:db:test-db",
```

These files can be removed individually or all at once with [the pytest --cache-clear](https://docs.pytest.org/en/latest/cache.html#usage) option.

## Development

### Goals

1. replace one-off scripts for each check
1. share checks with other organizations
1. consolidate bugs in one place (i.e. one thing to update)
1. in pytest use a known existing framework for writing checks
1. be vendor agnostic e.g. support checks across cloud providers or in hybrid environments or competing services
1. cache and share responses to reduce third party API usage (i.e. lots of tests check AWS security groups so fetch them once)
1. provide a way to run a single test or subset of tests

### Non-Goals

1. Invent a new DSL for writing expectations (use pytest conventions)
1. Verify how third party services or their client libraries work
   (e.g. don't answer "Does GET / on the CRUD1 API return 400 when
   query param `q` is `$bad_value`?")

### Design

Currently this is a monolithic pytest package, but should eventually
[be extracted into a pytest plugin](#3) and with [separate dependent
pytest plugins for each service](#4).

API responses should fit on disk and in memory (i.e. don't use this
for log processing or checking binaries for malware), and be safe to
cache for minutes, hours, or days (i.e. probably don't use this for
monitoring a streaming API) (NB: [bug for specifying data
freshness](#5)).

Additionally we want:

* data fetching functions in a `resources.py`
* prefix test files with `test_`
* tests to have pytest markers for any services they depend on for data
* HTTP clients should be read only and use read only credentials
* running a test should not modify services

#### File Layout

```console
pytest-services
...
├── <third party service A>
│   ├── client.py
│   ├── <subservice A (optional)>
│   │   ├── resources.py
│   │   ├── ...
│   │   └── test_ec2_security_group_all_ports.py
│   └── <subservice B (optional)>
│       ├── __init__.py
│       ├── resources.py
│       ├── ...
│       └── test_s3_bucket_web_hosting_disabled.py
├── <third party service B>
    ├── resources.py
    └── test_user_has_escalation_policy.py
```

This is just a convention and any layout where tests can import
resources for parametrization should work.

