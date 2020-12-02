import pytest

from aws.s3.helpers import get_s3_resource_id
from aws.s3.resources import s3_buckets, s3_bucket_lifecycle_configuration


@pytest.mark.s3
@pytest.mark.parametrize(
    ["s3_bucket", "lifecycle_configuration"],
    zip(s3_buckets(), s3_bucket_lifecycle_configuration()),
    ids=get_s3_resource_id,
)
def test_s3_bucket_has_life_cycle_policy(s3_bucket, lifecycle_configuration):
    """
    Check a bucket has a life cycle policy.
    """
    assert (
        None not in lifecycle_configuration
    ), f"{s3_bucket['Name']} has no life cycle policy."
