# Frost

[![PyPI version](https://badge.fury.io/py/frost.svg)](https://badge.fury.io/py/frost)

Frost (for FiRefox Operations Security Testing) is a set of API
clients, [pytest](https://docs.pytest.org/en/latest/index.html) tests
to verify the configuration of third party services. For example:

* Are our AWS DB snapshots publicly accessible?
* Is there a dangling DNS entry in Route53?
* Will someone get paged when an alert goes off?

## Usage

### Requirements

* [Python 3.8](https://www.python.org/downloads/)

### Installing

```console
pip install frost
```

### Usage

```console
$ frost --help
Usage: frost [OPTIONS] COMMAND [ARGS]...

  FiRefox Operations Security Testing API clients and tests

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

  Commands:
    test  Run pytest tests passing all trailing args to pytest.

$ frost test --help
Usage: frost test [OPTIONS] [PYTEST_ARGS]...

  Run pytest tests passing all trailing args to pytest.

Options:
  --help  Show this message and exit.
```

### Running

To fetch RDS resources from the cache or AWS API and check that
backups are enabled for DB instances for [the configured aws
profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-config-files.html)
named `default` in the `us-west-2` region we can run:

```console
frost test -k test_rds_db_instance_backup_enabled --aws-profiles default --debug-calls
```

frost switches to its package directory and adds pytest options:

* `--debug-calls` for printing (with `-s`) API calls we make
* `--aws-profiles` for selecting one or more AWS profiles to fetch resources for or the AWS default profile / `AWS_PROFILE` environment variable
* `--offline` a flag to tell HTTP clients to not make requests and return empty params
* [`--config`](#custom-test-config) path to test custom config file

which can be combined with the standard pytest options for selecting frost tests and other local tests:

* [`-k`](https://docs.pytest.org/en/latest/example/markers.html#using-k-expr-to-select-tests-based-on-their-name) to select the test matching the substring `test_rds_db_instance_backup_enabled`
* [`-m`](https://docs.pytest.org/en/latest/example/markers.html#marking-test-functions-and-selecting-them-for-a-run) not used but the marker filter can be useful for selecting all tests for specific services (e.g. `-m rds`)
* [`-s`](https://docs.pytest.org/en/latest/capture.html) to disable capturing stdout so we can see the progress fetching AWS resources

and produces output like the following showing a DB instance with backups disabled:

```console
=========================================================== test session starts ===========================================================
platform darwin -- Python 3.6.2, pytest-3.3.2, py-1.5.2, pluggy-0.6.0
metadata: {'Python': '3.6.2', 'Platform': 'Darwin-15.6.0-x86_64-i386-64bit', 'Packages': {'pytest': '3.3.2', 'py': '1.5.2', 'pluggy': '0.6.
0'}, 'Plugins': {'metadata': '1.5.1', 'json': '0.4.0', 'html': '1.16.1'}}
rootdir: /Users/gguthe/frost, inifile:
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

#### IAM Policy for frost

The below policy will allow you to run all AWS tests in frost against all resources in your account.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PytestServicesReadOnly",
      "Action": [
        "autoscaling:DescribeLaunchConfigurations",
        "cloudtrail:DescribeTrails",
        "ec2:DescribeFlowLogs",
        "ec2:DescribeInstances",
        "ec2:DescribeSecurityGroups",
        "ec2:DescribeSnapshotAttribute",
        "ec2:DescribeSnapshots",
        "ec2:DescribeVolumes",
        "ec2:DescribeVpcs",
        "elasticache:DescribeCacheClusters",
        "elasticloadbalancing:DescribeLoadBalancers",
        "es:DescribeElasticsearchDomains",
        "es:ListDomainNames",
        "iam:GenerateCredentialReport",
        "iam:GetCredentialReport",
        "iam:GetLoginProfile",
        "iam:ListAccessKeys",
        "iam:ListAttachedGroupPolicies",
        "iam:ListAttachedRolePolicies",
        "iam:ListAttachedUserPolicies",
        "iam:ListGroupPolicies",
        "iam:ListGroupsForUser",
        "iam:ListMFADevices",
        "iam:ListRolePolicies",
        "iam:ListRoles",
        "iam:ListUserPolicies",
        "iam:ListUsers",
        "rds:DescribeDbInstances",
        "rds:DescribeDbSecurityGroups",
        "rds:DescribeDbSnapshotAttributes",
        "rds:DescribeDbSnapshots",
        "rds:ListTagsForResource",
        "redshift:DescribeClusterSecurityGroups",
        "redshift:DescribeClusters",
        "s3:GetBucketAcl",
        "s3:GetBucketCORS",
        "s3:GetBucketLogging",
        "s3:GetBucketPolicy",
        "s3:GetBucketVersioning",
        "s3:GetBucketWebsite",
        "s3:ListAllMyBuckets",
        "s3:ListBucket"
      ],
      "Effect": "Allow",
      "Resource": "*"
    }
  ]
}
```

#### Setting up GCP tests

##### Enabling required API's for your project

```
gcloud [--project <project name>] services enable bigquery-json.googleapis.com
gcloud [--project <project name>] services enable cloudresourcemanager.googleapis.com
gcloud [--project <project name>] services enable compute.googleapis.com
gcloud [--project <project name>] services enable sqladmin.googleapis.com
```

#### Setting up GSuite tests

Make sure to have an OAuth2 app created and have the `client_secret.json` file in `~/.credentials` and then run:
```
make setup_gsuite
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

## Custom Test Config

frost adds a `--config` cli option for passing in a custom config file specific to tests within frost.

The example config in repo (`config.yaml.example`):
```
exemptions:
  - test_name: test_ec2_instance_has_required_tags
    test_param_id: i-0123456789f014c162
    expiration_day: 2019-01-01
    reason: ec2 instance has no owner
  - test_name: test_ec2_security_group_opens_specific_ports_to_all
    test_param_id: '*HoneyPot'
    expiration_day: 2020-01-01
    reason: purposefully insecure security group
severities:
  - test_name: test_ec2_instance_has_required_tags
    severity: INFO
  - test_name: '*'
    severity: ERROR
regressions:
  - test_name: test_ec2_security_group_opens_all_ports_to_all
    test_param_id: '*mycustomgroup'
    comment: this was remediated by ops team
aws:
  admin_groups:
    - "Administrators"
  admin_policies:
    - "AWSAdminRequireMFA"
  user_is_inactive:
    no_activity_since:
      years: 1
      months: 0
    created_after:
      weeks: 1
  access_key_expires_after:
    years: 1
    months: 0
  required_tags:
    - Name
    - Type
    - App
    - Env
  required_amis:
    - ami-00000000000000000
    - ami-55555555555555555
  whitelisted_ports_global:
    - 25
  whitelisted_ports:
    - test_param_id: '*bastion'
      ports:
        - 22
        - 2222
gsuite:
  domain: 'example.com'
  user_is_inactive:
    no_activity_since:
      years: 1
      months: 0
pagerduty:
  users_with_remote_access_monitoring: 'pd_users.json'
  bastion_users: 'hierahash/*hierahash.json'
  alternate_usernames: 'alternate_usernames.json'
```

### Test Exemptions

frost custom config format adds support for
marking test and test resource IDs as expected failures.

The keys for each exemption rule is:
* test_name - Name of the test
* test_param_id - test ID (usually an AWS resource ID) (prefix with `*` to turn into a regex matcher)
* expiration_day - exception expiration day (as YYYY-MM-DD)
* reason - exception reason

The config looks like:
```
...
exemptions:
  - test_name: test_ec2_instance_has_required_tags
    test_param_id: i-0123456789f014c162
    expiration_day: 2019-01-01
    reason: ec2 instance has no owner
  - test_name: test_ec2_security_group_opens_specific_ports_to_all
    test_param_id: '*HoneyPot'
    expiration_day: 2020-01-01
    reason: purposefully insecure security group
...
```

#### Enabling regex for test ID

You can prefix the test ID with a `*` to enable regex matching for the test ID. The `*` prefix will be stripped
off, and the rest will be used as a regex.

For example:
 - `*foobar` becomes `foobar`
 - `*foo\w+` becomes `foo\w+`

For more information on Python's regex syntax see: [Regular Expression HOWTO](https://docs.python.org/3.4/howto/regex.html#regex-howto).

**Note:** All regex rules are applied first. As well, the ordering of both regex and non-regex rules is top to bottom and the first one wins.


When a json report is generated, the exemptions will show up in the
json metadata as serialized markers:

```json
python -m json.tool report.json | grep -C 20 xfail
...
                        "markers": {
                            "ec2": {
                                "name": "ec2",
                                "args": [],
                                "kwargs": {}
                            },
                            "parametrize": {
                                "name": "parametrize",
                                "args": [
                                    "...skipped..."
                                ],
                                "kwargs": [
                                    "...skipped..."
                                ]
                            },
                            "xfail": {
                                "name": "xfail",
                                "args": [],
                                "kwargs": {
                                    "reason": "ec2 instance has no owner",
                                    "strict": true,
                                    "expiration": "2019-01-01"
                                }
                            }
                        },
...
```


#### Test Severity

frost custom config format adds support for marking the severity of a certain test. A severity can be `INFO`, `WARN`, or `ERROR`.

These do not modify pytest results (pass, fail, xfail, skip, etc.).

The config looks like:

```
...
severities:
  - test_name: test_ec2_instance_has_required_tags
    severity: INFO
  - test_name: '*'
    severity: ERROR
...
```

And results in a severity and severity marker being included in the
json metadata:

```console
frost -s --aws-profiles stage --aws-require-tags Name Type App Stack -k test_ec2_instance_has_required_tags --config config.yaml.example --json=report.json
...
```

```json
python -m json.tool report.json
{
    "report": {
        "environment": {
            "Python": "3.6.2",
            "Platform": "Darwin-15.6.0-x86_64-i386-64bit"
        },
        "tests": [
            {
...
                "metadata": [
                    {
...
                    "markers": {
...
                            "severity": {
                                "name": "severity",
                                "args": [
                                    "INFO"
                                ],
                                "kwargs": {}
                            }
                        },
...
                        "severity": "INFO",
                        "unparametrized_name": "test_ec2_instance_has_required_tags"
                    }
...
```

### Test Regressions

frost custom config format adds support for marking specific tests on specific resources as regressions.
As with `severity` this does not modify the pytest results, but rather adds a marker that can be used when analyzing the results.

The config looks like:
```
...
regressions:
  - test_name: test_ec2_security_group_opens_all_ports_to_all
    test_param_id: '*mycustomgroup'
    comment: this was remediated by ops team
...
```

### AWS Config

frost has a suite of AWS tests. This section of the custom config includes configuration options specific
to these tests.

The config looks like:
```
...
aws:
  # Relative time delta for test_iam_user_is_inactive. no_activity_since will be used as the failure marker,
  # so in this example any user that hasn't had any activity for a year will be marked as a "failure". created_after
  # is used as a grace period, so in this case any user that was created within the last week will be automatically
  # pass this test.
  user_is_inactive:
    no_activity_since:
      years: 1
      months: 0
    created_after:
      weeks: 1
  # Required tags used within the test_ec2_instance_has_required_tags test
  required_tags:
    - Name
    - Type
    - App
    - Env
  # Whitelsited ports for the test_ec2_security_group_opens_specific_ports_to_all
  # test for all instances
  whitelisted_ports_global:
    - 25
  # Whitelsited ports for the test_ec2_security_group_opens_specific_ports_to_all
  # test for specific instances. In this example, we are whitelisting ports 22
  # and 2222 for all security groups that include the word 'bastion' in them.
  whitelisted_ports:
    - test_param_id: '*bastion'
      ports:
        - 22
        - 2222
...
```

### GSuite Config

frost has a suite of GSuite tests. This section of the
custom config includes configuration options specific to these tests.

**Make sure to [setup GSuite](#setting-up-gsuite-tests) before running GSuite tests**

The config looks like:
```
gsuite:
  # The specific GSuite domain to test.
  domain: 'example.com'
  # Relative time delta for test_admin_user_is_inactive. no_activity_since will be used as the failure marker,
  # so in this example any user that hasn't had any activity for a year will be marked as a "failure".
  user_is_inactive:
    no_activity_since:
      years: 1
      months: 0
```

### Pagerduty Config

frost does not query the pagerduty API, but can run tests against output from it.

The config looks like:
```
pagerduty:
  users_with_remote_access_monitoring: 'pd_users.json'
  bastion_users: 'hierahash/*hierahash.json'
  alternate_usernames: 'alternate_usernames.json'
```

Where `users_with_remote_access_monitoring` and `bastion_users` are
globs for multiple files relative to the current working directory and
`alternate_usernames` is the path to a single file.

The files have examples formats as follows:

* `users_with_remote_access_monitoring`:

```json
[
  {
    "avatar_url": "https://secure.gravatar.com/avatar/...",
    "billed": true,
    "color": "sea-green",
    "contact_methods": [],
    "description": null,
    "email": "example@example.com",
    "html_url": "https://example.pagerduty.com/users/AAA0999",
    "id": "AAA0999",
    "invitation_sent": false,
    "job_title": null,
    "name": "Example Examplerton",
    "notification_rules": [],
    "role": "user",
    "self_": "https://api.pagerduty.com/users/AAA0999",
    "summary": "C. Hobbes",
    "teams": [],
    "time_zone": "America/New_York",
    "type": "user"
  },
  ...
]
```

* `bastion_users`:

```json
{
  "chobbes": {
    "groups": [""],
    "root_ssh": true
  },
  "movedon": {
    "ensure": "absent"
  },
  ...
}
```

* `alternate_usernames`:

```json
{
  "chobbes": ["calvin", "spacemanspiff"]
}
```

### Test Accuracy

There are two important things to note about `frost` tests that may be different from your expectations.

First, the focus is on "actionable results". This plays out as an attempt to reduce false
positives by trying to filter out unused resources. An example of this can be seen by looking at
any of the security group tests, where we are skipping any security groups that are not attached to a resource.

Second, there are some tests that make naive assumptions instead of trying to capture the complexities
of the system. The current best example of this is all IAM tests that relate to "admin" users. How we
are determining what an user or role is an admin is based simply off substring matching on the policies
attached. This obviously has a high chance of false negatives.

## Development

### Goals

1. replace one-off scripts for each check
1. share checks with other organizations
1. consolidate bugs in one place (i.e. one thing to update)
1. in pytest use a known existing framework for writing checks
1. be vendor agnostic e.g. support checks across cloud providers or in hybrid environments or competing services
1. cache and share responses to reduce third party API usage (i.e. lots of tests check AWS security groups so fetch them once)
1. provide a way to run a single test or subset of tests
1. focus on actionable results (see [test accuracy](#test-accuracy) for more information)

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
* data checking and test helpers in a `helpers.py`
* prefix test files with `test_`
* doctests for non test files (e.g. `helpers.py`, `resources.py`, `client.py`)
  * tests that depend on external IO or the runtime environment (env vars, file system, HTTP) to use the prefix `meta_test_` (and probably `mock` or `pytest.monkeypatch`)
    * JSON fixtures for anonymized cached http call in `example_cache/v/`
* tests to have pytest markers for any services they depend on for data
* HTTP clients should be read only and use read only credentials
* running a test should not modify services

#### File Layout

```console
frost
...
├── example_cache
│   └── v
│       ├── cache
│       │   └── lastfailed
│       ├── pytest_aws:example-account:us-east-1:ec2:describe_instances::.json
│       ├── pytest_aws:example-account:us-east-1:ec2:describe_security_groups::.json
...
├── <third party service A>
│   ├── client.py
│   ├── meta_test_client.py
│   ├── <subservice A (optional)>
│   │   ├── __init__.py
│   │   ├── helpers.py
│   │   ├── resources.py
│   │   ├── ...
│   │   └── test_ec2_security_group_all_ports.py
│   ├── <subservice b (optional)>
│   │   ├── __init__.py
│   │   ├── resources.py
│   │   ├── ...
│   │   └─ test_s3_bucket_web_hosting_disabled.py
└── <third party service B>
    ├── __init__.py
    ├── helpers.py
    ├── resources.py
    └── test_user_has_escalation_policy.py
```

### Adding an example test

Let's write a test to check that http://httpbin.org/ip returns an AWS IP:

1. create a file `httpbin/test_httpbin_ip.py` with the contents:

```python
import itertools
import ipaddress
import pytest
import json
import urllib.request


def get_httpbin_ips():
    # IPs we always want to test
    ips = [
        '127.0.0.1',
        '13.58.0.0',
    ]

    req = urllib.request.Request('http://httpbin.org/ip')

    with urllib.request.urlopen(req) as response:
        body = response.read().decode('utf-8')
        ips.append(json.loads(body).get('origin', None))

    return ips


def get_aws_ips():
    req = urllib.request.Request('https://ip-ranges.amazonaws.com/ip-ranges.json')

    with urllib.request.urlopen(req) as response:
        body = response.read().decode('utf-8')
        return json.loads(body)['prefixes']


@pytest.mark.httpbin
@pytest.mark.aws_ip_ranges
@pytest.mark.parametrize(
    ['ip', 'aws_ip_ranges'],
    zip(get_httpbin_ips(), itertools.repeat(get_aws_ips())))
def test_httpbin_ip_in_aws(ip, aws_ip_ranges):
    for aws_ip_range in aws_ip_ranges:
        assert ipaddress.IPv4Address(ip) not in ipaddress.ip_network(aws_ip_range['ip_prefix']), \
          "{0} is in AWS range {1[ip_prefix]} region {1[region]} service {1[service]}".format(ip, aws_ip_range)
```

Notes:

* we add two data fetching functions that return lists that we can zip into tuples for [the pytest parametrize decorator](https://docs.pytest.org/en/latest/parametrize.html#pytest-mark-parametrize-parametrizing-test-functions)
* we add markers for the services we're fetching data from


1. Running `frost test` with the test file explicitly included we see that one of the IPs is an AWS IP:

```console
frost test ./httpbin/test_httpbin_ip.py
platform darwin -- Python 3.6.2, pytest-3.3.2, py-1.5.2, pluggy-0.6.0
metadata: {'Python': '3.6.2', 'Platform': 'Darwin-15.6.0-x86_64-i386-64bit', 'Packages': {'pytest': '3.3.2', 'py': '1.5.2', 'pluggy': '0.6.0'}, 'Plugins': {'metadata': '1.5.1', 'json': '0.4.0', 'html': '1.16.1'}}
rootdir: /Users/gguthe/frost, inifile:
plugins: metadata-1.5.1, json-0.4.0, html-1.16.1
collected 3 items

httpbin/test_httpbin_ip_in_aws.py .F.                                                                                               [100%]

================================================================ FAILURES =================================================================
____________________________________________ test_httpbin_ip_in_aws[13.58.0.0-aws_ip_ranges1] _____________________________________________

ip = '13.58.0.0'
aws_ip_ranges = [{'ip_prefix': '13.32.0.0/15', 'region': 'GLOBAL', 'service': 'AMAZON'}, {'ip_prefix': '13.35.0.0/16', 'region': 'GLOB...on': 'us-west-1', 'service': 'AMAZON'}, {'ip_prefix': '13.57.0.0/16', 'region': 'us-west-1', 'service': 'AMAZON'}, ...]

    @pytest.mark.httpbin
    @pytest.mark.aws_ip_ranges
    @pytest.mark.parametrize(
        ['ip', 'aws_ip_ranges'],
        zip(get_httpbin_ips(), itertools.repeat(get_aws_ips())),
        # ids=lambda ip: ip
        )
    def test_httpbin_ip_in_aws(ip, aws_ip_ranges):
        for aws_ip_range in aws_ip_ranges:
>           assert ipaddress.IPv4Address(ip) not in ipaddress.ip_network(aws_ip_range['ip_prefix']), \
              "{0} is in AWS range {1[ip_prefix]} region {1[region]} service {1[service]}".format(ip, aws_ip_range)
E           AssertionError: 13.58.0.0 is in AWS range 13.58.0.0/15 region us-east-2 service AMAZON
E           assert IPv4Address('13.58.0.0') not in IPv4Network('13.58.0.0/15')
E            +  where IPv4Address('13.58.0.0') = <class 'ipaddress.IPv4Address'>('13.58.0.0')
E            +    where <class 'ipaddress.IPv4Address'> = ipaddress.IPv4Address
E            +  and   IPv4Network('13.58.0.0/15') = <function ip_network at 0x107cf66a8>('13.58.0.0/15')
E            +    where <function ip_network at 0x107cf66a8> = ipaddress.ip_network

httpbin/test_httpbin_ip_in_aws.py:43: AssertionError
=================================================== 1 failed, 2 passed in 15.69 seconds ===================================================
```

Note: marking tests as expected failures with `@pytest.mark.xfail` can hide data fetching errors

To improve this we could:

1. Add parametrize ids so it's clearer which parametrize caused test failures
1. Add directions about why it's an issue and how to fix it or what the associated risks are

As we add more tests we can:

1. Move the JSON fetching functions to `<service name>/resources.py` files and import them into the test
1. Move the fetching logic to a shared library `<service name>/client.py` and save to the pytest cache
