
import pytest

@pytest.mark.s3
def test_s3_bucket_versioning_mfa_delete_enabled(s3_bucket_from_list_buckets,
                                                 s3_status_from_get_bucket_versioning,
                                                 s3_mfa_delete):
    """
    Enable MFA delete for versioned S3 buckets to prevent their accidental deletion.
    """
    if s3_status_from_get_bucket_versioning != 'Enabled':
        return pytest.skip()

    assert s3_mfa_delete != 'Disabled'
