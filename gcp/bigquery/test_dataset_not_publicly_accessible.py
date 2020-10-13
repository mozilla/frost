import pytest

from helpers import get_param_id

from gcp.bigquery.resources import datasets


@pytest.mark.parametrize(
    "dataset", datasets(), ids=lambda d: get_param_id(d, "friendlyName"),
)
def test_dataset_not_publicly_accessible(dataset):
    """
    Test's whether a dataset is publicly accessible
    """
    for access in dataset["access"]:
        assert (
            access.get("specialGroup", "") != "allAuthenticatedUsers"
        ), "BigQuery Dataset {0[id]}'s IAM policy allows anyone to access it.".format(
            dataset
        )
