import re
import yaml
import json
from base64 import b64decode
from flask import jsonify, request, Blueprint, current_app
import semantic_version
from kpm.api.app import getvalues
from kpm.packager import Package
import kpm.semver as semver
from kpm.semver import last_version, select_version
from kpm.api.exception import (ApiException,
                               InvalidUsage,
                               InvalidVersion,
                               PackageAlreadyExists,
                               PackageNotFound,
                               PackageVersionNotFound)

import etcd

registry_app = Blueprint('registry', __name__,)

etcd_client = etcd.Client(port=2379)

ETCD_PREFIX = "kpm/packages/"


def pathfor(package, version):
    return ETCD_PREFIX + "%s/%s" % (package, version)


def check_data(package, version, blob):
    try:
        semantic_version.Version(version)
    except ValueError as e:
        raise InvalidVersion(e.message, {"version": version})
    return None


def getversions(package):
    path = ETCD_PREFIX + package
    r = etcd_client.read(path, recursive=True)
    versions = []
    for p in r.children:
        version = p.key.split("/")[-1]
        versions.append(version)
    return versions


def getversion(package, version, stable=False):
    versions = getversions(package)
    if version is None or version == 'latest':
        return last_version(versions, stable)
    else:
        try:
            return select_version(versions, str(version), stable)
        except ValueError as e:
            raise InvalidVersion(e.message, {"version": version})


def push_etcd(package, version, data, force=False):
    path = pathfor(package, version)
    try:
        etcd_client.write(path, data, prevExist=force)
    except etcd.EtcdAlreadyExist as e:
        raise PackageAlreadyExists(e.message, {"package": path})


@registry_app.errorhandler(etcd.EtcdKeyNotFound)
def render_etcdkeyerror(error):
    package = error.payload['cause']
    return render_error(PackageNotFound("Package not found: %s" % package, {"package": package}))


@registry_app.errorhandler(PackageAlreadyExists)
@registry_app.errorhandler(InvalidVersion)
@registry_app.errorhandler(PackageNotFound)
@registry_app.errorhandler(PackageVersionNotFound)
@registry_app.errorhandler(ApiException)
@registry_app.errorhandler(InvalidUsage)
def render_error(error):
    response = jsonify({"error": error.to_dict()})
    response.status_code = error.status_code
    return response


@registry_app.route("/test_error")
def test_error():
    raise InvalidUsage("error message", {"path": request.path})


def get_package(package, values):
    # if version is None; Find latest version

    version_query = values.get("version", 'latest')
    version = getversion(package, version_query)
    if version is None:
        raise PackageVersionNotFound("No version match '%s' for package '%s'" % (version_query, package),
                                     {"package": package, "version_query": version_query})
    path = pathfor(package, str(version))
    package_data = etcd_client.read(path)
    return package_data


@registry_app.route("/api/v1/packages/<path:package>/pull", methods=['GET'], strict_slashes=False)
def pull(package):
    current_app.logger.info("pull %s", package)
    values = getvalues()
    package_data = get_package(package, values)
    if 'format' in values and values['format'] == 'json':
        resp = jsonify({"package": package, "kub": package_data.value})
    else:
        resp = current_app.make_response(b64decode(package_data.value))
        resp.headers['Content-Disposition'] = 'filename="%s_%s.tar.gz"' % (package.replace("/", "_"),
                                                                           package_data.key.split("/")[-1])
        resp.mimetype = 'application/x-gzip'
    return resp


@registry_app.route("/api/v1/packages/<path:package>", methods=['POST'], strict_slashes=False)
@registry_app.route("/api/v1/packages", methods=['POST'], strict_slashes=False)
def push(package=None):

    values = getvalues()
    blob = values['blob']
    package = values['package']
    print values
    version = values['version']
    force = False
    if 'force' in values:
        force = 'true' == values['force']
    check_data(package, version, blob)
    push_etcd(package, version, blob, force=force)
    return jsonify({"status": "ok"})


@registry_app.route("/api/v1/packages", methods=['GET'], strict_slashes=False)
def list_packages():
    values = getvalues()
    path = ETCD_PREFIX
    r = {}

    if 'organization' in values:
        path += "/%s" % values['organization']
    try:
        packages = etcd_client.read(path, recursive=True)
    except etcd.EtcdKeyNotFound:
        etcd_client.write(path, None, dir=True)

    for child in packages.children:
        m = re.match("^/%s(.+)/(.+)/(.+)$" % ETCD_PREFIX, child.key)
        if m is None:
            continue
        organization, name, version = (m.group(1), m.group(2), m.group(3))
        package = "%s/%s" % (organization, name)
        if package not in r:
            r[package] = {"name": package, 'available_versions': [], 'version': None}
        r[package]['available_versions'].append(version)

    for _, v in r.iteritems():
        v['available_versions'] = [str(x) for x in sorted(semver.versions(v['available_versions'], False),
                                                          reverse=True)]
        v['version'] = v['available_versions'][0]

    resp = current_app.make_response(json.dumps(r.values()))
    resp.mimetype = 'application/json'
    return resp


@registry_app.route("/api/v1/packages/<path:package>", methods=['GET'], strict_slashes=False)
def show_package(package):
    values = getvalues()
    package_data = get_package(package, values)
    p = Package(b64decode(package_data.value))
    manifest = yaml.load(p.manifest)
    stable = False
    if 'stable' in values and values['stable'] == 'true':
        stable = True

    response = {"manifest": manifest,
                "version": manifest['package']['version'],
                "name":  package,
                "available_versions": [str(x) for x in sorted(semver.versions(getversions(package), stable),
                                                              reverse=True)]}
    if 'pull' in values and values['pull'] == 'true':
        response['kub'] = package_data.value
    return jsonify(response)


@registry_app.route("/api/v1/packages/<path:package>", methods=['DELETE'], strict_slashes=False)
def delete_package(package):
    values = getvalues()
    package_data = get_package(package, values)
    etcd_client.delete(package_data.key)
    return jsonify({"status": "delete", "key": package_data.key})
