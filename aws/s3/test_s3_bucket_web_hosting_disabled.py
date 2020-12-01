import pytest

from aws.s3.helpers import get_s3_resource_id
from aws.s3.resources import s3_buckets, s3_buckets_website


@pytest.mark.s3
@pytest.mark.parametrize(
    ["s3_bucket", "s3_bucket_website"],
    zip(s3_buckets(), s3_buckets_website()),
    ids=get_s3_resource_id,
)
def test_s3_bucket_web_hosting_disabled(s3_bucket, s3_bucket_website):
    """
    Disable hosting static site in the S3 bucket.
    """
    assert not s3_bucket_website["IndexDocument"]
    assert not s3_bucket_website["ErrorDocument"]
    assert not s3_bucket_website["RedirectAllRequestsTo"]
