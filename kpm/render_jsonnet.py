import os
import logging
import os.path
import yaml
import json
import _jsonnet


logger = logging.getLogger(__name__)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


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

 shards: kpm.shards(
   {{manifest.shards}}, shards),

{% if manifest.resources|length > 0 %}
 resources: kpm.resources([{% for item in manifest.resources %}

    {{item|json}} + {template: (importstr "templates/{{item.file}}")}
   ,
{%- endfor %}], $.shards, $.variables),

{% endif %}
 deploy: kpm.deploy({{manifest.deploy}})

}
"""


class RenderJsonnet(object):
    def __init__(self, files=None):
        self.files = files

    #  Returns content if worked, None if file not found, or throws an exception
    def try_path(self, path, rel):
        if not rel:
            raise RuntimeError('Got invalid filename (empty string).')
        print self.files
        print "try_path"
        if rel in self.files:
            print "true"
            if self.files[rel] is None:
                print "none"
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

    def render_jsonnet(self, manifeststr=None):
        if manifeststr is None:
            manifeststr = self.files['manifest.jsonnet']
        json_str = _jsonnet.evaluate_snippet("snippet", manifeststr, import_callback=self.import_callback)
        return json.loads(json_str)
