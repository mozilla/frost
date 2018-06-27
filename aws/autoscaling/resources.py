from conftest import botocore_client


def autoscaling_launch_configurations():
    """
    http://botocore.readthedocs.io/en/latest/reference/services/autoscaling.html#AutoScaling.Client.describe_launch_configurations
    """
    return (
        botocore_client.get("autoscaling", "describe_launch_configurations", [], {})
        .extract_key("LaunchConfigurations")
        .flatten()
        .values()
    )
