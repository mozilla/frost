
import pytest


@pytest.mark.s3
def test_s3_bucket_logging_enabled(s3_bucket_from_list_buckets, s3_logging_enabled):
    """
    Enable access logs for S3 buckets.
    """
    assert s3_logging_enabled
