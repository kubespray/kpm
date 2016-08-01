import os.path
import logging
import utils
import re

__all__ = ['new_package']

logger = logging.getLogger(__name__)

DIRECTORIES = ['templates']


MANIFEST = """---
package:
  name: {name}
  author: <author>
  version: 1.0.0
  description: {app}
  license: MIT

# Defaults variables
# i.e:
# variables:
#   namespace: kube-system
#   replicas: 1
#   image: "gcr.io/google_containers/heapster:v0.18.2"
#   svc_type: "NodePort"
variables: {{}}

# List the resources
# resources :
#  - file: nginx-rc.yaml # Template file , relative to ./templates
#    name: nginx         # kubernetes resource name
#    type: rc            # kubernetes resource type (ds,rc,svc,secret....)
#    sharded: no         # Optional: use the shards to generate this resource
#    patch:              # Optional: array of 'json-patch'
#      - {{op: replace, path: /metadata/labels/app-name, value: 'nginx'}}
resources:
  # - file: {app}-rc.yaml
  #   name: {app}
  #   type: rc

  # - file: {app}-svc.yaml
  #   name: {app}
  #   type: svc

# Shard list (optional)
# shards:
#   - name: shard-name     # will be append to the resource name
#     variables: {{}}        # Optional: apply vars  only to this shard
shards: []

# List de dependencies
# Special name '$self' to deploy current package.
# Useful to sort the dependencies
# i.e:
# deploy:
#   - name: postgresql
#   - name $self
deploy:
  - name: $self
"""

README = """
{name}
===========

# Install

kpm deploy {name}

"""


def new_package(name, dest=".", with_comments=False):
    _, app = name.split("/")
    path = os.path.join(dest, name)
    utils.mkdir_p(path)
    readme = open(os.path.join(path, 'README.md'), 'w')
    readme.write(README.format(name=name))
    readme.close()
    manifest = open(os.path.join(path, 'manifest.yaml'), 'w')
    if with_comments:
        m = MANIFEST
    else:
        m = re.sub(r'(?m)^#.*\n?', '', MANIFEST)
    manifest.write(m.format(app=app, name=name))
    manifest.close()
    for directory in DIRECTORIES:
        utils.mkdir_p(os.path.join(path, directory))
