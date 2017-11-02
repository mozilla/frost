
import pytest


@pytest.mark.s3
def test_s3_bucket_cors_disabled(s3_bucket_from_list_buckets,
                                 s3_cors_rules):
    """
    Disable sharing S3 bucket contents cross origin with CORS headers.

    http://docs.aws.amazon.com/AmazonS3/latest/dev/cors.html
    """
    assert s3_cors_rules is None
