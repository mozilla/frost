import pytest

from aws.s3.helpers import get_s3_resource_id
from aws.s3.resources import s3_buckets, s3_buckets_logging


@pytest.mark.s3
@pytest.mark.parametrize(
    ["s3_bucket", "s3_bucket_logging_enabled"],
    zip(s3_buckets(), s3_buckets_logging()),
    ids=get_s3_resource_id,
)
def test_s3_bucket_logging_enabled(s3_bucket, s3_bucket_logging_enabled):
    """
    Enable access logs for S3 buckets.
    """
    assert s3_bucket_logging_enabled, "Logging not enabled for {0[Name]}".format(
        s3_bucket
    )
