
from apiclient.discovery import build as build_service


def get_gcp_developer_key():
    return ""


def cache_key(project_id, product, subproduct):
    return ':'.join([
        'pytest_gcp',
        str(project_id),
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

        # TODO: not oauth? or support for both?
        self.developer_key = get_gcp_developer_key()

    def get(self, product, subproduct):
        if self.offline:
            results = []
        else:
            results = sum(list(self._get(product, subproduct)), [])
        return results

    def _get(self, product, subproduct, call_kwargs=None):
        if call_kwargs is None:
            call_kwargs = {}

        for project_id in self.project_ids:
            # TODO - support zones
            ckey = cache_key(project_id, product, subproduct)
            cached_result = self.cache.get(ckey, None)
            if cached_result is not None:
                print('found cached value for', ckey)
                return cached_result

            service = self._service(product)
            api_entity = getattr(service, subproduct)()

            if self.debug_calls:
                print('calling', api_entity)

            # TODO - need to support looping through zones for instances
            #   - could potentially match on instances within _get_all_items?
            items = self._get_all_items(api_entity, {**call_kwargs, 'project': project_id})

            results = {
                'items': items,
                '__pytest_meta': dict(project_id=project_id)
            }

            if self.debug_cache:
                print('setting cache value for', ckey)

            self.cache.set(ckey, results)

            yield results

    def _get_all_items(self, api_entity):
        request = api_entity.list(project=self.projectId)
        items = []
        while request is not None:
            # TODO: exception handling on request.execute()
            resp = request.execute()
            items = sum([items], resp["items"])
            request = api_entity.list_next(request, resp)
        return items

    def _service(self, product, version="v1"):
        # TODO: developer keys or oauth? or support for both?
        return build_service(product, version, developerKey=self.developer_key)
