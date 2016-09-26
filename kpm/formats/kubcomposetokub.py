from kpm.convert.kompose import Kompose
from kpm.formats.kub import Kub


class KubComposeToKub(Kub):
    def __init__(self, kubcompose):
        k8s_resources = Kompose(kubcompose).convert()
        self.namespace = kubcompose.namespace
        self._manifest = kubcompose.manifest
        self._manifest['resources'] = self.create_kub_resources(k8s_resources['items'])
        self._resources = None
        self._dependencies = None

    def create_kub_resources(self, resources):
        r = []
        for resource in resources:
            name = resource['metadata']['name']
            kind = resource['kind'].lower()
            r.append({
                "file": "%s-%s.yaml" % (name, kind),
                "name": name,
                "generated": True,
                "order": -1,
                "protected": False,
                "value": resource,
                "patch": [],
                "variables": {},
                "type": kind}
            )
        return r
