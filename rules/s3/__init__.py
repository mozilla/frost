

from .s3_bucket_logging_enabled import test_s3_bucket_logging_enabled
from .s3_bucket_versioning_mfa_delete_enabled import test_s3_bucket_versioning_mfa_delete_enabled
from .s3_bucket_versioning_enabled import test_s3_bucket_versioning_enabled
from .s3_bucket_web_hosting_disabled import test_s3_bucket_web_hosting_disabled
from .s3_bucket_no_world_acl import test_s3_bucket_no_world_acl
from .s3_bucket_does_not_grant_all_principals_all_actions import test_s3_bucket_does_not_grant_all_principals_all_actions
from .s3_bucket_cors_disabled import test_s3_bucket_cors_disabled

__all__ = [
    'test_s3_bucket_logging_enabled',
    # 'test_s3_bucket_versioning_mfa_delete_enabled',
    # 'test_s3_bucket_versioning_enabled',
    # 'test_s3_bucket_cors_disabled',
    # 'test_s3_bucket_web_hosting_disabled',
    # 'test_s3_bucket_no_world_acl',
    # TODO: break into principal * check, action * check, and missing condition checks?
    # 'test_s3_bucket_does_not_grant_all_principals_all_actions',

    # TODO: Lifecycle checks?
]
