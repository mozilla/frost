
from apiclient.discovery import build as build_service


def cache_key(project_id, version, product, subproduct):
    return ':'.join([
        'pytest_gcp',
        project_id,
        version,
        product,
        subproduct
    ]) + '.json'


class GCPClient:

    def __init__(self,
                 project_ids,
                 cache,
                 debug_calls,
                 debug_cache,
                 offline):
        self.project_ids = project_ids
        self.cache = cache
        self.debug_calls = debug_calls
        self.debug_cache = debug_cache
        self.offline = offline

    def get(self, product, subproduct, version="v1", call_kwargs=None):
        if self.offline:
            results = []
        else:
            results = list(self._get(product, subproduct, version, call_kwargs))
        return results

    def _get(self, product, subproduct, version="v1", call_kwargs=None):
        if call_kwargs is None:
            call_kwargs = {}

        for project_id in self.project_ids:
            # TODO - support zones
            ckey = cache_key(project_id, version, product, subproduct)
            cached_result = self.cache.get(ckey, None)
            if cached_result is not None:
                print('found cached value for', ckey)
                return cached_result

            service = self._service(product, version)
            api_entity = getattr(service, subproduct)()

            if self.debug_calls:
                print('calling', api_entity)

            if self._zone_aware(product, subproduct):
                results = []
                for zone in self._get_zones(project_id):
                    results = sum(
                        [results],
                        self._get_all_items(api_entity, {**call_kwargs, 'project': project_id, 'zone': zone})
                    )
            else:
                results = self._get_all_items(api_entity, {**call_kwargs, 'project': project_id})

            if self.debug_cache:
                print('setting cache value for', ckey)

            self.cache.set(ckey, results)

            return results

    def _get_all_items(self, api_entity, call_kwargs):
        request = api_entity.list(**call_kwargs)
        items = []
        while request is not None:
            # TODO: exception handling on request.execute()
            resp = request.execute()
            items = sum([items], resp.get("items", []))
            request = api_entity.list_next(request, resp)
        return items

    def _service(self, product, version="v1"):
        return build_service(product, version)

    def _zone_aware(self, product, subproduct):
        if product == "compute" and subproduct == "instances":
            return True
        return False

    def _get_zones(self, project_id):
        # TODO: exception handling
        response = self._service('compute').zones().list(project=project_id).execute()['items']
        for result in response:
                yield result['name']
