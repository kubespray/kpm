import copy
import logging
import os.path
import jinja2
import yaml
import jsonpatch
import json
from collections import OrderedDict
import kpm.manifest as manifest
from kpm.template_filters import jinja_filters
from kpm.kub_base import KubBase
from kpm.kubernetes import get_endpoint
from kpm.utils import convert_utf8, recursive_update


# __all__ = ['Kub']

logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


jinja_env = jinja2.Environment()
jinja_env.filters.update(jinja_filters())


class Kub(KubBase):
    def __init__(self, *args, **kwargs):
        super(Kub, self).__init__(*args, **kwargs)
        self.manifest = manifest.Manifest(self.package)

    @property
    def kubClass(self):
        return Kub

    def _create_namespaces(self, resources):
        # @TODO create namespaces for all manifests
        if self.namespace:
            ns = self.create_namespace(self.namespace)
            resources[ns['file']] = ns
        return resources

    def _append_patch(self, resources={}):
        index = 0

        for resource in self.manifest.resources:
            index += 1
            resources[resource['file']] = resource
            resource["order"] = index
            if 'protected' not in resource:
                resource["protected"] = False
            if 'patch' not in resource:
                resource['patch'] = []

        if self._deploy_resources is not None:
            for resource in self._deploy_resources:
                if 'patch' in resource and len(resource['patch']) > 0:
                    resources[resource['file']]["patch"] += resource['patch']

        return resources

    def _generate_shards(self, resources):
        if not len(self.shards):
            return resources
        sharded = {}
        to_remove = []
        index = 0
        for _, resource in resources.iteritems():
            index += 1
            resource['order'] = index
            if 'sharded' in resource and resource['sharded'] is True:
                for shard in self.shards:
                    shard_vars = shard.get('variables', {})
                    shard_vars.update({"name": shard['name']})

                    r = {"file": "%s-%s.yaml" % (os.path.splitext(resource['file'])[0].replace("/", "_"),
                                                 shard['name']),
                         "order": index,
                         "protected": False,
                         "template": resource['file'],
                         "variables": shard_vars,
                         "patch": resource['patch'] + shard.get('patch', []),
                         "name": "%s-%s" % (resource['name'], shard['name']),
                         "type": resource['type']}
                    sharded[r['file']] = r
                    index += 1
                to_remove.append(resource['file'])
        map(resources.pop, to_remove)
        resources.update(sharded)
        return resources

    def _default_patch(self, resources):
        for _, resource in resources.iteritems():
            patch = [
                {"op": "replace",
                 "path": "/metadata/name",
                 "value": resource['name']},
            ]
            if 'patch' not in resource:
                resource['patch'] = []
            resource['patch'] += patch
        return resources

    def _resolve_jinja(self, resources, from_value=False):
        for _, resource in resources.iteritems():
            if 'template' in resource:
                tpl_file = resource['template']
            else:
                tpl_file = resource['file']
            if from_value or resource.get('generated', False) is True:
                val = yaml.safe_dump(convert_utf8(resource['value']), width=float("inf"))
            else:
                val = self.package.files[os.path.join('templates', tpl_file)]
            template = jinja_env.from_string(val)
            variables = copy.deepcopy(self.variables)
            if 'variables' in resource:
                variables = recursive_update(variables, resource['variables'])
            if len(self.shards):
                variables['kpmshards'] = self.shards
            t = template.render(variables)
            resource['value'] = yaml.safe_load(t)
        return resources

    def _apply_patches(self, resources):
        for _, resource in resources.iteritems():
            if self.namespace:
                if 'namespace' in resource['value']['metadata']:
                    op = 'replace'
                else:
                    op = 'add'
                resource['patch'].append({"op": op, "path": "/metadata/namespace", "value": self.namespace})

            if len(resource['patch']):
                patch = jsonpatch.JsonPatch(resource['patch'])
                result = patch.apply(resource['value'])
                resource['value'] = result
        return resources

    def resources(self):
        if self._resources is None:
            self._resources = OrderedDict()
            resources = self._resources
            resources = self._create_namespaces(resources)
            resources = self._append_patch(resources)
            resources = self._generate_shards(resources)
            resources = self._default_patch(resources)
            resources = self._resolve_jinja(resources)
            resources = self._apply_patches(resources)
            resources = self._resolve_jinja(resources, True)
        return self._resources

    def prepare_resources(self, dest="/tmp", index=0):
        for _, resource in self.resources().iteritems():
            index += 1
            path = os.path.join(dest, "%02d_%s_%s" % (index,
                                                      self.version,
                                                      resource['file'].replace("/", "_")))
            f = open(path, 'w')
            f.write(yaml.safe_dump(convert_utf8(resource['value'])))
            resource['filepath'] = f.name
            f.close()
        return index

    def build(self):
        result = []
        for kub in self.dependencies:
            kubresources = OrderedDict([("package",  kub.name),
                                        ("version", kub.version),
                                        ("namespace", kub.namespace),
                                        ("resources", [])])
            for _, resource in kub.resources().iteritems():
                resource = self._annotate_resource(kub, resource)

                kubresources['resources'].\
                    append(OrderedDict({"file": resource['file'],
                                        "hash": resource['value']['metadata']['annotations'].get('kpm.hash', None),
                                        "protected": resource['protected'],
                                        "name": resource['name'],
                                        "kind": resource['value']['kind'].lower(),
                                        "endpoint": get_endpoint(
                                            resource['value']['kind'].lower()).
                                        format(namespace=self.namespace),
                                        "body": json.dumps(resource['value'])}))

            result.append(kubresources)
        return {"deploy": result,
                "package": {"name": self.name,
                            "version": self.version}}
