import pytest

from aws.ec2.helpers import ec2_instance_test_id
from aws.ec2.resources import ec2_instances


@pytest.fixture
def required_tag_names(pytestconfig):
    return frozenset(pytestconfig.getoption('--aws-require-tags'))


@pytest.mark.ec2
@pytest.mark.parametrize(
    'ec2_instance',
    ec2_instances(),
    ids=ec2_instance_test_id)
def test_ec2_instance_has_required_tags(ec2_instance, required_tag_names):
    """
    Checks that all EC2 instances have the tags with the required names.

    Does not not check tag values.

    >>> test_ec2_instance_has_required_tags({'Tags': [{'Key': 'Name'}]}, frozenset(['Name']))

    >>> test_ec2_instance_has_required_tags({
    ... 'InstanceId': 'iid', 'Tags': [{'Key': 'Bar'}]}, frozenset(['Name']))
    Traceback (most recent call last):
    ...
    AssertionError: EC2 Instance iid missing required tags frozenset({'Name'})
    assert not frozenset({'Name'})
    """
    tags = ec2_instance.get('Tags', [])
    instance_tag_names = set(tag['Key'] for tag in tags if 'Key' in tag)

    # set difference to find required tags not on instance
    missing_tag_names = required_tag_names - instance_tag_names
    assert not missing_tag_names, \
      "EC2 Instance {0[InstanceId]} missing required tags {1!r}".format(ec2_instance, missing_tag_names)
