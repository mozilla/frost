import warnings

from apiclient.discovery import build as build_service
from apiclient.errors import HttpError

warnings.filterwarnings(
    "ignore", "Your application has authenticated using end user credentials"
)


def get_all_projects_in_folder(folder_id=None):
    if folder_id is None:
        return

    if not folder_id.startswith("folders/"):
        folder_id = "folders/" + folder_id

    crm = build_service("cloudresourcemanager", "v2")
    allFolders = get_all_folders_in_folder(crm, folder_id)
    crm.close()
    allFolders.append(folder_id)

    project_crm = build_service("cloudresourcemanager", "v1")
    allProjects = []
    for folder in allFolders:
        projects = (
            project_crm.projects().list(filter="parent.id:" + folder[8:]).execute()
        )
        if projects:
            allProjects.append(projects)
    project_crm.close()

    # flatten and return
    return sum([p["projects"] for p in allProjects], [])


def get_all_folders_in_folder(crm, folder_id=None):
    allFolders = []
    if folder_id is None:
        return allFolders
    folders = crm.folders().list(parent=folder_id).execute()
    if folders:
        for folder in folders["folders"]:
            allFolders.extend(get_all_folders_in_folder(crm, folder["name"]))
    else:
        allFolders = [folder_id]

    return allFolders


class GCPClient:
    def __init__(self, project_id, folder_id, debug_calls, offline):
        self.debug_calls = debug_calls
        self.offline = offline

        self.project_list = []
        if project_id is not None:
            self.project_list = [project_id]

        if folder_id is not None:
            self.project_list = [
                p["projectId"] for p in get_all_projects_in_folder(folder_id)
            ]

    def get_project_iam_policies(self):
        if self.offline:
            return []

        service = self._service("cloudresourcemanager")
        policies = []
        for project_id in self.project_list:
            try:
                resp = (
                    service.projects()
                    .getIamPolicy(resource=project_id, body={})
                    .execute()
                )
                policies += resp
            except HttpError as e:
                if "has not been used in project" in e._get_reason():
                    continue
                raise e
        return policies

    def get_project_container_config(self):
        if self.offline:
            return {}

        service = self._service("container")
        for project_id in self.project_list:
            try:
                # TODO : We may want to correlate the zone here with the corresponding clusters zone.
                request = (
                    service.projects()
                    .locations()
                    .getServerConfig(
                        name="projects/{}/locations/us-west1".format(project_id)
                    )
                )
                resp = request.execute()
            except HttpError as e:
                # This will be thrown if an API is disabled, so we will try the next project id
                if "has not been used in project" in e._get_reason():
                    continue
                raise e
            return resp

        return {}

    def get(
        self,
        project_id,
        product,
        subproduct,
        id_key,
        id_value,
        version="v1",
        call_kwargs=None,
    ):
        if self.offline:
            result = {}
        else:
            result = self._get(
                project_id, product, subproduct, id_key, id_value, version
            )
        return result

    def _get(
        self,
        project_id,
        product,
        subproduct,
        id_key,
        id_value,
        version="v1",
        call_kwargs=None,
    ):
        if call_kwargs is None:
            call_kwargs = {}
        call_kwargs["projectId"] = project_id
        call_kwargs[id_key] = id_value

        service = self._service(product, version)

        api_entity = getattr(service, subproduct.split(".")[0])()
        for entity in subproduct.split(".")[1:]:
            api_entity = getattr(api_entity, entity)()

        try:
            result = api_entity.get(**call_kwargs).execute()
        except HttpError as e:
            # This will be thrown if an API is disabled.
            if "has not been used in project" in e._get_reason():
                return {}
            raise e

        result["projectId"] = project_id

        return result

    def list(
        self, product, subproduct, version="v1", results_key="items", call_kwargs=None
    ):
        """Public list func. See _list func docstring for more info"""
        if self.offline:
            results = []
        else:
            if call_kwargs is not None:
                return list(
                    self._list(product, subproduct, version, results_key, call_kwargs)
                )

            results = []
            for project_id in self.project_list:
                call_kwargs = {"project": project_id}
                results += list(
                    self._list(product, subproduct, version, results_key, call_kwargs)
                )

        return results

    def _list(
        self, product, subproduct, version="v1", results_key="items", call_kwargs=None
    ):
        """
        Internal function for calling .list() on some service's resource. Supports debug printing
        and caching of the response.

        If a service supports "zones", then loop through each zone to collect all resources from
        that service. An example of this is collecting all compute instances (compute.instances().list()).
        """

        project_id = "-"
        if "project" in call_kwargs:
            project_id = call_kwargs["project"]

        service = self._service(product, version)

        api_entity = getattr(service, subproduct.split(".")[0])()
        for entity in subproduct.split(".")[1:]:
            api_entity = getattr(api_entity, entity)()

        if self.debug_calls:
            print(
                "calling {}.{} for project {}".format(product, subproduct, project_id)
            )

        if self._zone_aware(product, subproduct):
            results = []
            for zone in self._list_zones(project_id):
                results = sum(
                    [results],
                    self._list_all_items(
                        api_entity, {**call_kwargs, "zone": zone}, results_key
                    ),
                )
        else:
            results = self._list_all_items(api_entity, call_kwargs, results_key)

        # Append the project id to each resource for use in test metadata
        return [{"projectId": project_id, **result} for result in results]

    def _list_all_items(self, api_entity, call_kwargs, results_key):
        """Internal helper for dealing with pagination"""
        request = api_entity.list(**call_kwargs)
        items = []
        while request is not None:
            try:
                resp = request.execute()
            except HttpError as e:
                # This will be thrown if an API is disabled.
                if "has not been used in project" in e._get_reason():
                    return []
                raise e
            items = sum([items], resp.get(results_key, []))
            try:
                request = api_entity.list_next(request, resp)
            except AttributeError:
                request = None

        return items

    def _service(self, product, version="v1"):
        """Internal helper around google client lib's build service func"""
        return build_service(product, version)

    def _zone_aware(self, product, subproduct):
        """
        Internal helper for whether or not a product and subproduct take zones into account.

        Differing heavily from AWS, most GCP services do not take zones into account with API
        calls.
        """
        if product == "compute" and subproduct == "instances":
            return True
        return False

    def _list_zones(self, project_id):
        """Internal helper for listing all zones"""
        try:
            response = (
                self._service("compute")
                .zones()
                .list(project=project_id)
                .execute()["items"]
            )
        except HttpError as e:
            # This will be thrown if an API is disabled.
            if "has not been used in project" in e._get_reason():
                return []
            raise e
        return [result["name"] for result in response]
