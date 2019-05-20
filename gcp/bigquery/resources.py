from conftest import gcp_client


def datasets():
    datasets = gcp_client.list(
        "bigquery",
        "datasets",
        version="v2",
        results_key="datasets",
        call_kwargs={"projectId": gcp_client.get_project_id()},
    )
    return [get_dataset(d["datasetReference"]["datasetId"]) for d in datasets]


def get_dataset(dataset_id):
    return gcp_client.get("bigquery", "datasets", "datasetId", dataset_id, version="v2")
