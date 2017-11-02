
import pytest


@pytest.mark.s3
def test_s3_bucket_web_hosting_disabled(s3_bucket_from_list_buckets,
                                        s3_error_document,
                                        s3_index_document,
                                        s3_redirect_all_requests_to):
    """
    Disable hosting static site in the S3 bucket.

    """
    assert not (s3_index_document or s3_error_document or s3_redirect_all_requests_to)
