import pytest

from aws.s3.helpers import get_s3_resource_id
from aws.s3.resources import s3_buckets, s3_buckets_versioning


@pytest.mark.s3
@pytest.mark.parametrize(
    ["s3_bucket", "s3_bucket_versioning"],
    zip(s3_buckets(), s3_buckets_versioning()),
    ids=get_s3_resource_id,
)
def test_s3_bucket_versioning_enabled(s3_bucket, s3_bucket_versioning):
    """
    Enable restoring every version of every object in the S3 bucket to easily recover data.

    http://docs.aws.amazon.com/AmazonS3/latest/dev/Versioning.html
    """
    assert s3_bucket_versioning.get("Status", None) == "Enabled"
