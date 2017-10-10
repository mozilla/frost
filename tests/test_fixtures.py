# -*- coding: utf-8 -*-


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'aws:',
        '*--foo=DEST_FOO*Set the value for the fixture "bar".',
    ])


def test_hello_ini_setting(testdir):
    testdir.makeini("""
        [pytest]
        HELLO = world
    """)

    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def hello(request):
            return request.config.getini('HELLO')

        def test_hello_world(hello):
            assert hello == 'world'
    """)

    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_hello_world PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


rds_snapshot = {
    "DBSnapshots": [
        {
            "AllocatedStorage": 100,
            "AvailabilityZone": "us-east-1c",
            "DBInstanceIdentifier": "example-db",
            "DBSnapshotArn": "arn:aws:rds:us-east-1:123456789012:snapshot:example-db-final-snapshot",
            "DBSnapshotIdentifier": "arn:aws:rds:us-east-1:123456789012:snapshot:example-db-final-snapshot",
            "Encrypted": True,
            "Engine": "mysql",
            "EngineVersion": "5.6.23",
            "IAMDatabaseAuthenticationEnabled": False,
            "InstanceCreateTime": "2015-09-15T07:32:30.640000+00:00",
            "Iops": 1000,
            "LicenseModel": "general-public-license",
            "MasterUsername": "root",
            "OptionGroupName": "default:mysql-5-6",
            "PercentProgress": 100,
            "Port": 3306,
            "SnapshotCreateTime": "2015-09-16T03:30:08.456000+00:00",
            "SnapshotType": "public",
            "Status": "available",
            "StorageType": "io1",
            "VpcId": "vpc-fffffff"
        }
    ]
}


def test_rds_snapshots_fixture(testdir):
    # TODO: mock out aws profile

    testdir.makepyfile("""
        import pytest

        profiles = ['aws-stage']
        regions = ['us-east-1']

        def test_rds_snapshot_encrypted(rds_snapshot):
            assert bool(rds_snapshot['Encrypted'])
    """)

    config = testdir.parseconfigure()
    cache_key = 'pytest_aws:aws-stage:us-east-1:rds:describe_db_snapshots' \
        '::IncludeShared=True,IncludePublic=True'
    config.cache.set(cache_key, rds_snapshot)

    result = testdir.runpytest('-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_rds_snapshot_encrypted* PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


rds_snapshot_attrs = {
    "DBSnapshotAttributesResult": {
        "DBSnapshotAttributes": [
            {
                "AttributeName": "restore",
                "AttributeValues": []
            }
        ],
        "DBSnapshotIdentifier": "example-db-final-snapshot"
    },
    "ResponseMetadata": {
        "HTTPHeaders": {
            "content-length": "647",
            "content-type": "text/xml",
            "date": "Fri, 06 Oct 2017 21:05:17 GMT",
            "x-amzn-requestid": "0e8c2f55-aada-11e7-be46-57d722ce1111"
        },
        "HTTPStatusCode": 200,
        "RequestId": "0e8c2f55-aada-11e7-be46-57d722ce1111",
        "RetryAttempts": 0
    }
}


def test_rds_snapshot_attrs_fixture(testdir):
    testdir.makepyfile("""
        import pytest

        profiles = ['aws-stage']
        regions = ['us-east-1']


        def is_rds_snapshot_attr_public_access(rds_snapshot_attribute):
            return rds_snapshot_attribute['AttributeName'] == 'restore' \
              and 'any' in rds_snapshot_attribute['AttributeValues']


        def test_rds_snapshots_are_not_publicly_accessible(rds_snapshot_attributes):
            attrs = rds_snapshot_attributes['DBSnapshotAttributes']
            assert not any(is_rds_snapshot_attr_public_access(attr) for attr in attrs)
    """)

    config = testdir.parseconfigure()
    cache_key = 'pytest_aws:aws-stage:us-east-1:rds:describe_db_snapshots' \
        '::IncludeShared=True,IncludePublic=True'
    config.cache.set(cache_key, rds_snapshot)

    cache_key = 'pytest_aws:aws-stage:us-east-1:rds:describe_db_snapshot_attributes' \
        '::DBSnapshotIdentifier=example-db-final-snapshot'
    config.cache.set(cache_key, rds_snapshot_attrs)

    result = testdir.runpytest('-v')  # '--fixtures')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*::test_rds_snapshots_are_not_publicly_accessible* PASSED',
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0
