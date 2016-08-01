from flask import jsonify, request, Blueprint, current_app
import etcd
import kpm.deploy
from kpm.api.exception import (ApiException,
                               InvalidUsage,
                               InvalidVersion,
                               PackageAlreadyExists,
                               PackageNotFound,
                               PackageVersionNotFound)


deployment_app = Blueprint('deployment', __name__,)
etcd_client = etcd.Client(port=2379)

ETCD_PREFIX = "kpm/deployments/"


@deployment_app.errorhandler(PackageAlreadyExists)
@deployment_app.errorhandler(PackageNotFound)
@deployment_app.errorhandler(PackageVersionNotFound)
@deployment_app.errorhandler(ApiException)
@deployment_app.errorhandler(InvalidVersion)
@deployment_app.errorhandler(InvalidUsage)
def render_error(error):
    response = jsonify({"error": error.to_dict()})
    response.status_code = error.status_code
    return response


def _cmd(cmd, package):
    jsonbody = request.get_json(force=True, silent=True)
    values = request.values.to_dict()
    if jsonbody:
        values.update(jsonbody)
    params = {"version": values.get("version"),
              "namespace": values.get("namespace"),
              "dry": values.get("dry", False) == 'true',
              "variables": values.get("variables", None),
              "endpoint": current_app.config['KPM_REGISTRY_HOST'],
              "proxy": current_app.config['KUBE_APIMASTER'],
              "fmt": "json"}
    current_app.logger.info("%s %s: %s", cmd, package, params)
    return getattr(kpm.deploy, cmd)(package, **params)


@deployment_app.route("/api/v1/deployments/<path:package>", methods=['DELETE'], strict_slashes=False)
def remove(package):
    r = _cmd('delete', package)
    return jsonify({"result": r})


@deployment_app.route("/api/v1/deployments/<path:package>", methods=['POST'], strict_slashes=False)
def deploy(package):
    r = _cmd('deploy', package)
    return jsonify({"result": r})


@deployment_app.route("/api/v1/deployments/<path:package>", methods=['GET'], strict_slashes=False)
def show(package):
    pass


@deployment_app.route("/api/v1/deployments", methods=['GET'], strict_slashes=False)
def list():
    pass
