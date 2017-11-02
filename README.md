### AWS Unit Tests with pytest

Fetch AWS resources to use as fixtures for python test functions.

#### Install:

```
cd tools/aws-network-notebook
python3 -m venv venv
source venv/bin/activate
make install
```

### Usage / Examples:

Run tests for certain AWS services:

```
» # list markers pytest --markers
» pytest -m rds
```

Run test names matching a substring:

```
» pytest -k test_rds
...
```

Run all the tests against all the profiles and regions:

```
» pytest --json=report.json --html=report.html --self-contained-html
==================================================== test session starts =====================================================
platform darwin -- Python 3.6.2, pytest-3.2.3, py-1.4.34, pluggy-0.4.0
metadata: {'Python': '3.6.2', 'Platform': 'Darwin-15.6.0-x86_64-i386-64bit', 'Packages': {'pytest': '3.2.3', 'py': '1.4.34', 'pluggy': '0.4.0'}, 'Plugins': {'metadata': '1.5.0', 'json': '0.4.0', 'html': '1.16.0'}}
rootdir: /Users/gguthe/foxsec/tools, inifile:
plugins: metadata-1.5.0, json-0.4.0, html-1.16.0
collected 632 items

aws-network-notebook/services/test_tigerblood.py xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

------------------------------- generated json report: /Users/gguthe/foxsec/tools/report.json --------------------------------
-------------------------------- generated html file: /Users/gguthe/foxsec/tools/report.html ---------------------------------
========================================== 600 xfailed, 32 xpassed in 7.93 seconds ===========================================
```

Run tests against specific AWS profiles or regions:

TODO

```
» pytest --profiles=stage  --regions=us-east-1
```

Run tests using profile and creds from env vars:

TODO

Run all tests against a given resource:

TODO

```
» pytest -m rds --profiles=stage --regions=us-east-1 --rds-db-instance-id=test-db-id
```

### Caching

**By default tests cache and prefer cached AWS API JSON responses.**

#### Clearing the entire cache

```
» pytest --cache-clear
...
```

#### Show cached API responses:

```
» pytest --cache-show
...
```

#### Cache files

Cached files use the default filename `.cache/v/pytest_aws:<aws profile>:<aws region>:<aws service>:<service method>:<args>:<kwargs>.json` e.g.

```
» head .cache/v/pytest_aws:stage:us-east-1:rds:describe_db_instances::.json
{
    "DBInstances": [
        {
            "AllocatedStorage": 300,
            "AutoMinorVersionUpgrade": true,
            "AvailabilityZone": "us-east-1c",
```

#### Clearing cached files by age

TODO: these are files so some sort of find -mtime older than delete should work

#### Clearing cached files by service

TODO: glob in the cache dir example


## Development

### Writing Tests

* List Available AWS Resources provided as fixtures

```
» pytest --fixtures
...
xray_service
    xray.get_trace_graph(['TraceIds'])
xray_trace_summary
    xray.get_trace_summaries(['StartTime', 'EndTime'])

================================================ no tests ran in 1.05 seconds ================================================
```

* Add a function named `test_<thing to test>` in `test_aws_baseline.py` e.g.

```
# test_aws_baseline.py

@pytest.mark.ec2
def test_ec2_security_group_exists(ec2_security_group):
    assert ec2_security_group
```

* Run that test with `pytest -k <test_name>`e.g. `pytest -k test_ec2_security_group`

#### Adding a global test

If the test is generally applicable we can move the test function to its own file at a path like `rules/<aws service name>/<aws service name>_<thing being tested>.py` e.g. `rules/ec2/ec2_security_group_exists.py`.

There should be:

* one test per file
* each test file should contain a single test function prefixed with `test_` using the standard AWS fixture names
* the test should be marked with any relevant AWS services it uses
* the test should be imported and added to the service `__init__.py`

#### Adding tests for a service

TBD and requires better scoping (cloudformation, easier filtering)

Move the test to its own file in `services/test_<service name>.py`
Tests should probably be marked with the CloudOps service name and owner.

#### Adding exceptions to a test / scan profiles

TODO: clean up current skip, xfail config


### FAQ

TODO: fix this solution

* How do I fix throttling errors?

* In `~/aws/config` in the `[Boto]` section, add the line `num_retries = 10`.


## Use Cases

* Document security issues for a old AWS account we take ownership of (like Scout2)
* Run periodically and raise issues (like the baseline scan)
* Run a subset of tests against a service when it deploys and allow DevOps to write additional tests for their service (or infer config from resource tags)
* Run tests in an aws-config lambda for high priority alerting e.g. on lateral movement
* Ad hoc queries for incident response
