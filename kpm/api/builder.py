import json
from flask import jsonify, Blueprint, current_app
from kpm.kub import Kub
from kpm.api.app import getvalues

builder_app = Blueprint('builder', __name__,)


def _build(package):
    name = package
    values = getvalues()
    version = values.get('version', None)
    namespace = values.get('namespace', 'default')
    variables = values.get('variables', {})
    variables['namespace'] = namespace
    k = Kub(name, endpoint=current_app.config['KPM_REGISTRY_HOST'],
            variables=variables, namespace=namespace, version=version)

    return k


@builder_app.route("/api/v1/packages/<path:package>/file/<path:filepath>")
def show_file(package, filepath):
    k = Kub(package, endpoint=current_app.config['KPM_REGISTRY_HOST'])
    return k.package.file(filepath)


@builder_app.route("/api/v1/packages/<path:package>/tree")
def tree(package):
    k = Kub(package, endpoint=current_app.config['KPM_REGISTRY_HOST'])
    return json.dumps(k.package.tree())


@builder_app.route("/api/v1/packages/<path:package>/generate", methods=['POST', 'GET'])
def build(package):
    k = _build(package)
    return jsonify(k.build())


@builder_app.route("/api/v1/packages/<path:package>/generate-tar", methods=['POST', 'GET'])
def build_tar(package):
    k = _build(package)
    resp = current_app.make_response(k.build_tar())
    resp.mimetype = 'application/tar'
    resp.headers['Content-Disposition'] = 'filename="%s_%s.tar.gz"' % (k.name.replace("/", "_"), k.version)
    return resp
