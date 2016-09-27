import json
from base64 import b64decode
from flask import jsonify, request, Blueprint, current_app
from kpm.api.app import getvalues
import kpm.api.impl.registry

from kpm.exception import (KpmException,
                           InvalidUsage,
                           InvalidVersion,
                           PackageAlreadyExists,
                           ChannelAlreadyExists,
                           PackageNotFound,
                           ChannelNotFound,
                           PackageVersionNotFound)

import etcd

registry_app = Blueprint('registry', __name__,)


@registry_app.errorhandler(etcd.EtcdKeyNotFound)
def render_etcdkeyerror(error):
    package = error.payload['cause']
    return render_error(PackageNotFound("Package not found: %s" % package, {"package": package}))


@registry_app.errorhandler(PackageAlreadyExists)
@registry_app.errorhandler(ChannelAlreadyExists)
@registry_app.errorhandler(InvalidVersion)
@registry_app.errorhandler(PackageNotFound)
@registry_app.errorhandler(PackageVersionNotFound)
@registry_app.errorhandler(KpmException)
@registry_app.errorhandler(InvalidUsage)
@registry_app.errorhandler(ChannelNotFound)
def render_error(error):
    response = jsonify({"error": error.to_dict()})
    response.status_code = error.status_code
    return response


@registry_app.route("/test_error")
def test_error():
    raise InvalidUsage("error message", {"path": request.path})


@registry_app.route("/api/v1/packages/<path:package>/pull", methods=['GET'], strict_slashes=False)
def pull(package):
    current_app.logger.info("pull %s", package)
    current_app.logger.info("headers %s", request.headers)
    values = getvalues()
    version = values.get("version", 'latest')
    r = kpm.api.impl.registry.pull(package, version)
    if 'format' in values and values['format'] == 'json':
        resp = jsonify({"package": r['package'], "kub": r['blob']})
    else:
        resp = current_app.make_response(b64decode(r['blob']))
        resp.headers['Content-Disposition'] = r['filename']
        resp.mimetype = 'application/x-gzip'
    return resp


@registry_app.route("/api/v1/packages/<path:package>", methods=['POST'], strict_slashes=False)
@registry_app.route("/api/v1/packages", methods=['POST'], strict_slashes=False)
def push(package=None):
    values = getvalues()
    blob = values['blob']
    package = values['package']
    version = values['version']
    force = False
    if 'force' in values:
        force = 'true' == values['force']

    r = kpm.api.impl.registry.push(package, version, blob, force)
    return jsonify(r)


@registry_app.route("/api/v1/packages", methods=['GET'], strict_slashes=False)
def list_packages():
    values = getvalues()
    organization = values.get('organization', None)
    r = kpm.api.impl.registry.list_packages(organization=organization)
    resp = current_app.make_response(json.dumps(r))
    resp.mimetype = 'application/json'
    return resp


@registry_app.route("/api/v1/packages/search", methods=['GET'], strict_slashes=False)
def search_package():
    values = getvalues()
    query = values.get("q")
    r = kpm.api.impl.registry.search(query)
    return jsonify(r)


@registry_app.route("/api/v1/packages/search_reindex", methods=['POST'], strict_slashes=False)
def search_reindex():
    r = kpm.api.impl.registry.search_reindex()
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>", methods=['GET'], strict_slashes=False)
def show_package(package):
    values = getvalues()
    version = values.get("version", 'latest')
    pullmode = False
    if 'pull' in values and (values['pull'] == 'true' or values['pull']):
        pullmode = True
    r = kpm.api.impl.registry.show_package(package, version, pullmode)
    return jsonify(r)


# CHANNELS
@registry_app.route("/api/v1/packages/<path:package>/channels", methods=['GET'], strict_slashes=False)
def list_channels(package):
    r = kpm.api.impl.registry.list_channels(package)
    resp = current_app.make_response(json.dumps(r))
    resp.mimetype = 'application/json'
    return resp


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>", methods=['GET'], strict_slashes=False)
def show_channel(package, name):
    r = kpm.api.impl.registry.show_channel(package, name)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>/<string:release>",
                    methods=['POST'], strict_slashes=False)
def add_channel_release(package, name, release):
    r = kpm.api.impl.registry.add_channel_release(package, name, release)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>/<string:release>",
                    methods=['DELETE'], strict_slashes=False)
def delete_channel_release(package, name, release):
    r = kpm.api.impl.registry.delete_channel_release(package, name, release)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>",
                    methods=['POST'], strict_slashes=False)
def create_channel(package, name):
    r = kpm.api.impl.registry.create_channel(package, name)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<path:package>/channels/<string:name>",
                    methods=['DELETE'], strict_slashes=False)
def delete_channel(package, name):
    r = kpm.api.impl.registry.delete_channel(package, name)
    return jsonify(r)


@registry_app.route("/api/v1/packages/<string:orga>/<string:pname>", methods=['DELETE'], strict_slashes=False)
def delete_package(orga, pname):
    package = "%s/%s" % (orga, pname)
    values = getvalues()
    version = values.get("version", "latest")
    r = kpm.api.impl.registry.delete_package(package, version)
    return jsonify(r)
