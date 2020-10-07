from conftest import gcp_client


def datasets():
    results = []
    for project_id in gcp_client.project_list:
        datasets = gcp_client.list(
            "bigquery",
            "datasets",
            version="v2",
            results_key="datasets",
            call_kwargs={"projectId": project_id},
        )
        results += [
            get_dataset(d["datasetReference"]["datasetId"], project_id)
            for d in datasets
        ]
    return sum(results, [])


def get_dataset(dataset_id, project_id):
    return gcp_client.get(
        project_id, "bigquery", "datasets", "datasetId", dataset_id, version="v2"
    )
