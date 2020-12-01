import pytest

from aws.s3.helpers import get_s3_resource_id
from aws.s3.resources import s3_buckets, s3_buckets_cors_rules


@pytest.mark.s3
@pytest.mark.parametrize(
    ["s3_bucket", "s3_bucket_cors_rules"],
    zip(s3_buckets(), s3_buckets_cors_rules()),
    ids=get_s3_resource_id,
)
def test_s3_bucket_cors_disabled(s3_bucket, s3_bucket_cors_rules):
    """
    Disable sharing S3 bucket contents cross origin with CORS headers.

    http://docs.aws.amazon.com/AmazonS3/latest/dev/cors.html
    """
    assert s3_bucket_cors_rules is None, "CORS enabled for {0[Name]}".format(s3_bucket)
