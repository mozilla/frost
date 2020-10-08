from conftest import botocore_client


def s3_buckets():
    "http://botocore.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_buckets"
    return (
        botocore_client.get("s3", "list_buckets", [], {})
        .extract_key("Buckets")
        .flatten()
        .values()
    )


def s3_buckets_cors_rules():
    "http://botocore.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_bucket_cors"
    return [
        botocore_client.get(
            "s3",
            "get_bucket_cors",
            [],
            {"Bucket": bucket["Name"]},
            profiles=[bucket["__pytest_meta"]["profile"]],
            regions=[bucket["__pytest_meta"]["region"]],
            result_from_error=lambda error, call: {"CORSRules": None},
        )
        .extract_key("CORSRules")
        .values()[0]
        for bucket in s3_buckets()
    ]


def s3_buckets_logging():
    "http://botocore.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_bucket_logging"
    return [
        botocore_client.get(
            "s3",
            "get_bucket_logging",
            [],
            {"Bucket": bucket["Name"]},
            profiles=[bucket["__pytest_meta"]["profile"]],
            regions=[bucket["__pytest_meta"]["region"]],
        )
        .extract_key("LoggingEnabled", default=False)
        .values()[0]
        for bucket in s3_buckets()
    ]


def s3_buckets_acls():
    "http://botocore.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_bucket_acl"
    return [
        botocore_client.get(
            "s3",
            "get_bucket_acl",
            [],
            {"Bucket": bucket["Name"]},
            profiles=[bucket["__pytest_meta"]["profile"]],
            regions=[bucket["__pytest_meta"]["region"]],
        ).values()[0]
        for bucket in s3_buckets()
    ]


def s3_buckets_versioning():
    "http://botocore.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_bucket_versioning"
    return [
        botocore_client.get(
            "s3",
            "get_bucket_versioning",
            [],
            {"Bucket": bucket["Name"]},
            profiles=[bucket["__pytest_meta"]["profile"]],
            regions=[bucket["__pytest_meta"]["region"]],
        ).values()[0]
        for bucket in s3_buckets()
    ]


def s3_buckets_website():
    "http://botocore.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_bucket_website"
    empty_response = {
        "IndexDocument": None,
        "ErrorDocument": None,
        "RedirectAllRequestsTo": None,
    }
    return [
        website
        for bucket in s3_buckets()
        for website in botocore_client.get(
            "s3",
            "get_bucket_website",
            [],
            {"Bucket": bucket["Name"]},
            profiles=[bucket["__pytest_meta"]["profile"]],
            regions=[bucket["__pytest_meta"]["region"]],
            result_from_error=lambda e, call: empty_response,
        ).values()
    ]


def s3_buckets_policy():
    "http://botocore.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.get_bucket_policy"
    return [
        botocore_client.get(
            "s3",
            "get_bucket_policy",
            [],
            {"Bucket": bucket["Name"]},
            profiles=[bucket["__pytest_meta"]["profile"]],
            regions=[bucket["__pytest_meta"]["region"]],
            result_from_error=lambda e, call: {"Policy": ""},
        )
        .extract_key("Policy")
        .values()[0]
        for bucket in s3_buckets()
    ]


def s3_bucket_lifecycle_configuration():
    "https://botocore.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#S3.Client.get_bucket_lifecycle_configuration"
    return [
        botocore_client.get(
            "s3",
            "get_bucket_lifecycle_configuration",
            [],
            {"Bucket": bucket["Name"]},
            profiles=[bucket["__pytest_meta"]["profile"]],
            regions=[bucket["__pytest_meta"]["region"]],
            result_from_error=lambda e, call: [],
        )
        .extract_key("Rules")
        .values()
        for bucket in s3_buckets()
    ]
