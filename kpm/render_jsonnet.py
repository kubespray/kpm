import re
import os
import logging
import os.path
import yaml
import json
import _jsonnet
import jinja2
import kpm.jinja_filters as jinja_filters
from kpm.utils import convert_utf8

logger = logging.getLogger(__name__)


JSONNET_TEMPLATE = """
local kpm = import "kpm.libjsonnet";

function(
  namespace="default",
  variables={namespace: namespace},
  shards=null,
)

{
  package: {{manifest.package}},

  variables: kpm.variables(
    {{manifest.variables}}, variables),

{% if manifest.shards is defined and manifest.shards|length > 0 %}
 shards: kpm.shards(
   {{manifest.shards}}, shards),
{% endif %}

{% if manifest.resources is defined and manifest.resources|length > 0 %}
 resources: kpm.resources([{% for item in manifest.resources %}

    {{item|json}} + {template: (importstr "templates/{{item.file}}")}
   ,
{%- endfor %}], $.shards, $.variables),

{% endif %}
 deploy: kpm.deploy({{manifest.deploy}})

}
"""


def yaml_to_jsonnet(manifestyaml):
    jinja_env = jinja2.Environment()
    jinja_env.filters.update(jinja_filters.filters())
    template = jinja_env.from_string(JSONNET_TEMPLATE)
    v = {"manifest": convert_utf8(json.loads(json.dumps(yaml.load(manifestyaml))))}
    templatedjsonnet = template.render(v)
    jsonnet_str = re.sub(r'[\'"]{{(.*?)}}["\']', r"\1", templatedjsonnet)
    return jsonnet_str


class RenderJsonnet(object):
    def __init__(self, files=None):
        self.files = files

    #  Returns content if worked, None if file not found, or throws an exception
    def try_path(self, path, rel):
        if not rel:
            raise RuntimeError('Got invalid filename (empty string).')
        if self.files is not None and rel in self.files:
            if self.files[rel] is None:
                with open(rel) as f:
                    self.files[rel] = f.read()
            return rel, self.files[rel]

        if rel == "kpm.libjsonnet":
            with open(os.path.join(os.path.dirname(__file__), "jsonnet/%s" % rel)) as f:
                return rel, f.read()

        if rel[0] == '/':
            full_path = rel
        else:
            full_path = path + rel
        if full_path[-1] == '/':
            raise RuntimeError('Attempted to import a directory')
        if not os.path.isfile(full_path):
            return full_path, None
        with open(full_path) as f:
            return full_path, f.read()

    def import_callback(self, path, rel):
        full_path, content = self.try_path(path, rel)
        if content:
            return full_path, content
        raise RuntimeError('File not found')

    def render_jsonnet(self, manifeststr):
        try:
            json_str = _jsonnet.evaluate_snippet("snippet", manifeststr, import_callback=self.import_callback)
        except RuntimeError as e:
            print "\n".join(["%s %s" % (i, line) for i, line in enumerate(manifeststr.split("\n"))])
            raise e
        return json.loads(json_str)
