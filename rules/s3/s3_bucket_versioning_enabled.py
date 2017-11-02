
import pytest


@pytest.mark.s3
def test_s3_bucket_versioning_enabled(s3_bucket_from_list_buckets,
                                      s3_status_from_get_bucket_versioning):
    """
    Enable restoring every version of every object in the S3 bucket to easily recover data.

    http://docs.aws.amazon.com/AmazonS3/latest/dev/Versioning.html
    """
    assert s3_status_from_get_bucket_versioning == 'Enabled'
