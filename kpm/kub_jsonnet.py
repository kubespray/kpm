import logging
import os.path
import yaml
import json
from collections import OrderedDict
import kpm.manifest_jsonnet as manifest
from kpm.utils import convert_utf8
from kpm.kub_base import KubBase


logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


class KubJsonnet(KubBase):
    def __init__(self, *args, **kwargs):
        shards = kwargs.get("shards", None)
        if shards.__class__ in [str, unicode]:
            shards = json.loads(shards)
            kwargs['shards'] = shards

        super(KubJsonnet, self).__init__(*args, **kwargs)

        self.tla_codes = {"variables": self._deploy_vars}
        if shards is not None:
            self.tla_codes["shards"] = shards

        self.manifest = manifest.ManifestJsonnet(self.package, {"params": json.dumps(self.tla_codes)})

    @property
    def kubClass(self):
        return KubJsonnet

    def _init_resources(self):
        index = 0
        for resource in self._resources:
            index += 1
            resource["order"] = index
            if 'protected' not in resource:
                resource["protected"] = False

    def prepare_resources(self, dest="/tmp", index=0):
        for resource in self.resources():
            index += 1
            path = os.path.join(dest, "%02d_%s_%s" % (index,
                                                      self.version,
                                                      resource['file']))
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
            for resource in kub.resources():
                kubresources['resources'].\
                    append(self._resource_build(kub, resource))

            result.append(kubresources)
        return {"deploy": result,
                "package": {"name": self.name,
                            "version": self.version}}
