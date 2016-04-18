from flask import jsonify, request, Blueprint, current_app
from kpm.kub import Kub
from werkzeug.exceptions import BadRequest


builder_app = Blueprint('builder', __name__,)


def _build(organization, package):
    name = "%s/%s" % (organization, package)
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


@builder_app.route("/api/v1/packages/<organization>/<package>/file/<path:filepath>")
def show(organization, package, filepath):
    name = "%s/%s" % (organization, package)
    k = Kub(name, endpoint=current_app.config['KPM_URI'])
    return jsonify(k.manifest)


@builder_app.route("/api/v1/packages/<organization>/<package>/tree")
def tree(organization, package):
    name = "%s/%s" % (organization, package)
    k = Kub(name, endpoint=current_app.config['KPM_URI'])
    return jsonify(k.manifest)


@builder_app.route("/api/v1/packages/<organization>/<package>/generate", methods=['POST', 'GET'])
def build(organization, package):
    k = _build(organization, package)
    return jsonify(k.build())


@builder_app.route("/api/v1/packages/<organization>/<package>/generate-tar", methods=['POST', 'GET'])
def build_tar(organization, package):
    k = _build(organization, package)
    resp = current_app.make_response(k.build_tar())
    resp.mimetype = 'application/tar'
    resp.headers['Content-Disposition'] = 'filename="%s_%s.tar.gz"' % (k.name.replace("/", "_"), k.version)
    return resp
