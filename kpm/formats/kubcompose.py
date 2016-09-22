import os
import logging
import yaml
from kpm.kub_jsonnet import KubJsonnet
from kpm.utils import convert_utf8


logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


class KubCompose(KubJsonnet):
    def prepare_resources(self, dest="/tmp", index=0):
        path = os.path.join(dest, "docker-compose.yaml")
        f = open(path, 'w')
        f.write(yaml.safe_dump(convert_utf8(self.docker_compose())))
        f.close()
        return 1

    @property
    def kubClass(self):
        return KubCompose

    def docker_compose(self):
        return self.resources()[0]['value']

    def build(self):
        return self.docker_compose()
