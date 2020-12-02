from helpers import get_param_id


def get_s3_bucket_name(bucket):
    return get_param_id(bucket, "Name")


def get_s3_resource_id(resource):
    if isinstance(resource, dict) and "Name" in resource:
        return get_s3_bucket_name(resource)
    if isinstance(resource, dict) and "ID" in resource:
        return get_param_id(resource, "ID")
    if isinstance(resource, dict) and "Owner" in resource:  # ACL
        return get_param_id(resource["Owner"], "DisplayName")
    if isinstance(resource, dict) and "Status" in resource:  # Versioning
        return get_param_id(resource, "Status")
    if isinstance(resource, dict) and "AllowedHeaders" in resource:  # CORS
        return "cors-rules"

    if isinstance(resource, dict) and "ResponseMetadata" in resource:
        return "empty"

    if isinstance(resource, dict) and not resource:
        return "empty"

    if isinstance(resource, list):
        if len(resource) == 0:
            return "empty"
        else:
            return get_s3_resource_id(resource[0])

    if resource is None:
        return "none"

    return None
