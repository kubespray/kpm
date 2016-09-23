import tempfile
import os
import logging
import yaml
from kpm.formats.kub_base import KubBase
from kpm.formats.kubcomposetokub import KubComposeToKub
from kpm.utils import convert_utf8


logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


class KubCompose(KubBase):
    def prepare_resources(self, dest="/tmp", index=0):
        path = os.path.join(dest, "docker-compose.yaml")
        f = open(path, 'w')
        f.write(self.docker_compose(to_yaml=True))
        f.close()
        return 1

    @property
    def kubClass(self):
        return KubCompose

    def docker_compose(self, to_yaml=False):
        obj = self.resources()[0]['value']
        if to_yaml:
            return yaml.safe_dump(convert_utf8(obj))
        else:
            return obj

    def build(self):
        return self.docker_compose()

    def create_temp_compose_file(self):
        f = tempfile.NamedTemporaryFile()
        f.write(self.docker_compose(to_yaml=True))
        f.flush()
        return f

    def convert_to_kub(self):
        return KubComposeToKub(self)
