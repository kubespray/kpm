from flask import jsonify, Blueprint, current_app
import kpm.api.impl.builder
from kpm.api.app import getvalues
from cnr.api.app import repo_name


builder_app = Blueprint('builder', __name__,)


def _build(package, version, media_type='kpm'):
    values = getvalues()
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


@builder_app.route("/api/v1/packages/<string:namespace>/<string:package_name>/file/<path:filepath>")
def show_file(namespace, package_name, filepath):
    reponame = repo_name(namespace, package_name)

    return kpm.api.impl.builder.show_file(reponame, filepath,
                                          endpoint=current_app.config['KPM_REGISTRY_HOST'])


@builder_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/<string:release>/<string:media_type>/tree")
def tree(namespace, package_name, release, media_type):
    reponame = repo_name(namespace, package_name)
    r = kpm.api.impl.builder.tree(reponame,
                                  endpoint=current_app.config['KPM_REGISTRY_HOST'])
    return jsonify(r)


@builder_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/<string:release>/<string:media_type>/generate",
    methods=['POST', 'GET'])
def build(namespace, package_name, release, media_type):
    reponame = repo_name(namespace, package_name)
    current_app.logger.info("generate %s", namespace, package_name)
    k = _build(reponame, release, media_type)
    return jsonify(k.build())


@builder_app.route(
    "/api/v1/packages/<string:namespace>/<string:package_name>/<string:release>/<string:media_type>/generate-tar",
    methods=['POST', 'GET'])
def build_tar(namespace, package_name, release, media_type):
    reponame = repo_name(namespace, package_name)
    k = _build(reponame, release, media_type)
    resp = current_app.make_response(k.build_tar())
    resp.mimetype = 'application/tar'
    resp.headers['Content-Disposition'] = 'filename="%s_%s.tar.gz"' % (k.name.replace("/", "_"), k.version)
    return resp
