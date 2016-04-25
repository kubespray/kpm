import json
from flask import jsonify, request, Blueprint, current_app
from kpm.kub import Kub
from werkzeug.exceptions import BadRequest


builder_app = Blueprint('builder', __name__,)


def _build(package):
    name = package
    args = {}
    version = None
    try:
        body = request.get_json()
    except BadRequest:
        body = {}
    try:
        args = request.args
    except BadRequest:
        args = {}
    namespace = args.get('namespace', default='default')
    variables = {'namespace': namespace}
    if body is None:
        body = {}
    body.update(args.to_dict())
    if 'variables' in body:
        variables = body['variables']
    if 'namespace' in body:
        namespace = body['namespace']
        variables['namespace'] = namespace
    if 'version' in body:
        version = body['version']
    k = Kub(name, endpoint=current_app.config['KPM_URI'], variables=variables, namespace=namespace, version=version)
    return k


@builder_app.route("/api/v1/packages/<path:package>/file/<path:filepath>")
def show_file(package, filepath):
    k = Kub(package, endpoint=current_app.config['KPM_URI'])
    return k.package.file(filepath)


@builder_app.route("/api/v1/packages/<path:package>/tree")
def tree(package):
    k = Kub(package, endpoint=current_app.config['KPM_URI'])
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
