from apiclient.discovery import build as build_service


def cache_key(project_id, version, product, subproduct, call="list", id_value="na"):
    return (
        ":".join(
            ["pytest_gcp", project_id, version, product, subproduct, call, id_value]
        )
        + ".json"
    )


class GCPClient:
    def __init__(self, project_id, cache, debug_calls, debug_cache, offline):
        self.project_id = project_id
        self.cache = cache
        self.debug_calls = debug_calls
        self.debug_cache = debug_cache
        self.offline = offline

    def get_project_id(self):
        if self.offline:
            return "test"
        return self.project_id

    def get_project_iam_policy(self):
        if self.offline:
            return {}

        service = self._service("cloudresourcemanager")
        request = service.projects().getIamPolicy(
            resource=self.get_project_id(), body={}
        )
        return request.execute()

    def get_project_container_config(self):
        if self.offline:
            return {}

        service = self._service("container")
        name = "projects/" + self.get_project_id() + "/locations/us-west1"
        request = service.projects().locations().getServerConfig(name=name)
        return request.execute()

    def get(
        self, product, subproduct, id_key, id_value, version="v1", call_kwargs=None
    ):
        if self.offline:
            result = {}
        else:
            result = self._get(product, subproduct, id_key, id_value, version)
        return result

    def _get(
        self, product, subproduct, id_key, id_value, version="v1", call_kwargs=None
    ):
        if call_kwargs is None:
            call_kwargs = {"projectId": self.project_id}
        call_kwargs[id_key] = id_value

        ckey = cache_key(self.project_id, version, product, subproduct, "get", id_value)
        cached_result = self.cache.get(ckey, None)
        if cached_result is not None:
            print("found cached value for", ckey)
            return cached_result

        service = self._service(product, version)

        api_entity = getattr(service, subproduct.split(".")[0])()
        for entity in subproduct.split(".")[1:]:
            api_entity = getattr(api_entity, entity)()

        result = api_entity.get(**call_kwargs).execute()

        if self.debug_cache:
            print("setting cache value for", ckey)

        self.cache.set(ckey, result)

        return result

    def list(
        self, product, subproduct, version="v1", results_key="items", call_kwargs=None
    ):
        """Public list func. See _list func docstring for more info"""
        if self.offline:
            results = []
        else:
            results = list(
                self._list(product, subproduct, version, results_key, call_kwargs)
            )
        return results

    def _list(
        self, product, subproduct, version="v1", results_key="items", call_kwargs=None
    ):
        """
        Internal function for calling .list() on some service's resource. Supports debug printing
        and caching of the response.

        If you want empty call kwargs, pass in `{}`.
        """
        if call_kwargs is None:
            call_kwargs = {"project": self.project_id}

        ckey = cache_key(self.project_id, version, product, subproduct)
        cached_result = self.cache.get(ckey, None)
        if cached_result is not None:
            print("found cached value for", ckey)
            return cached_result

        results = self._get_list_results(
            product, subproduct, version, results_key, call_kwargs
        )

        if self.debug_cache:
            print("setting cache value for", ckey)

        self.cache.set(ckey, results)

        return results

    def _get_list_results(self, product, subproduct, version, results_key, call_kwargs):
        """
        Internal helper for actually constructing the .list() function call and calling it.

        If a service supports "zones", then loop through each zone to collect all resources from
        that service. An example of this is collecting all compute instances (compute.instances().list()).
        """
        service = self._service(product, version)

        api_entity = getattr(service, subproduct.split(".")[0])()
        for entity in subproduct.split(".")[1:]:
            api_entity = getattr(api_entity, entity)()

        if self.debug_calls:
            print("calling", api_entity)

        if self._zone_aware(product, subproduct):
            results = []
            for zone in self._list_zones():
                results = sum(
                    [results],
                    self._list_all_items(
                        api_entity, {**call_kwargs, "zone": zone}, results_key
                    ),
                )
        else:
            results = self._list_all_items(api_entity, call_kwargs, results_key)

        return results

    def _list_all_items(self, api_entity, call_kwargs, results_key):
        """Internal helper for dealing with pagination"""
        request = api_entity.list(**call_kwargs)
        items = []
        while request is not None:
            # TODO: exception handling on request.execute()
            resp = request.execute()
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
        calls and such.
        """
        if product == "compute" and subproduct == "instances":
            return True
        return False

    def _list_zones(self):
        """Internal helper for listing all zones"""
        # TODO: exception handling
        response = (
            self._service("compute")
            .zones()
            .list(project=self.project_id)
            .execute()["items"]
        )
        for result in response:
            yield result["name"]
