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

`pytest --aws-profiles cloudservices-aws-stage --aws-regions us-east-1 -k test_my_test`

Skip it or other tests by file with --ignore e.g.

`pytest --ignore rules/rds --tb=no -s --aws-profiles cloudservices-aws-stage --aws-regions us-east-1 -m rds -k test_rds_db_instance_backup_enabled`


Run tests for certain AWS services:

Run test names matching a substring:

Run all the tests against all the profiles and regions:

Run tests against specific AWS profiles or regions:

Run tests using profile and creds from env vars:

Run all tests against a given resource:


## Development

### Adding a service

1. create a file in `rules/<service name>/test_my_test.py`

### Adding an endpoint

1. lookup the data you want on the [botocore docs](http://botocore.readthedocs.io/en/stable/reference/services/rds.html#RDS.Client.describe_db_snapshot_attributes)
1. add data fetching functions to the test for aws like using `botocore_client.get('rds', 'describe_db_instances', [], {}).values()`, which takes the args and kwargs to the botocore method call and profiles and regions from the command line, handles any pagination, caches the result, and returns an array of botocore responses (TODO: directions for testing it from the python shell)

### Adding a test

1. Apply it with `@pytest.mark.parametrize('rds_db_instance', rds_db_instances())`
1. Marking tests with expected failures using @pytest.mark.xfail can hide errors in the data fetching function
1. if other tests could use the function move it to `rules/<service name>/resources.py` and import it into the test


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
» head .cache/v/pytest_aws:cloudservices-aws-stage:us-east-1:rds:describe_db_instances::.json
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




There should be:

* one test per file
* separate data fetching functions in resources.py
* each test file should contain a single test function prefixed with `test_` using the standard AWS fixture names
* the test should be marked with any relevant AWS services it uses
* the test should be imported and added to the service `__init__.py`
