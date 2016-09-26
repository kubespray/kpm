from flask import jsonify, Blueprint, current_app
import kpm.api.impl.builder
from kpm.api.app import getvalues

builder_app = Blueprint('builder', __name__,)


def _build(package):
    values = getvalues()
    version = values.get('version', None)
    namespace = values.get('namespace', None)
    variables = values.get('variables', {})
    shards = values.get('shards', None)
    variables['namespace'] = namespace
    k = kpm.api.impl.builder.build(package,
                                   version_query=version,
                                   namespace=namespace,
                                   variables=variables,
                                   shards=shards,
                                   endpoint=current_app.config['KPM_REGISTRY_HOST'])
    return k


@builder_app.route("/api/v1/packages/<path:package>/file/<path:filepath>")
def show_file(package, filepath):
    return kpm.api.impl.builder.show_file(package, filepath,
                                          endpoint=current_app.config['KPM_REGISTRY_HOST'])


@builder_app.route("/api/v1/packages/<path:package>/tree")
def tree(package):
    r = kpm.api.impl.builder.tree(package,
                                  endpoint=current_app.config['KPM_REGISTRY_HOST'])
    return jsonify(r)


@builder_app.route("/api/v1/packages/<path:package>/generate", methods=['POST', 'GET'])
def build(package):
    current_app.logger.info("generate %s", package)
    k = _build(package)
    return jsonify(k.build())


@builder_app.route("/api/v1/packages/<path:package>/generate-tar", methods=['POST', 'GET'])
def build_tar(package):
    k = _build(package)
    resp = current_app.make_response(k.build_tar())
    resp.mimetype = 'application/tar'
    resp.headers['Content-Disposition'] = 'filename="%s_%s.tar.gz"' % (k.name.replace("/", "_"), k.version)
    return resp
