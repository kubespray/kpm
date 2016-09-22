import logging
import os.path
from collections import OrderedDict
from kpm.kubernetes import Kubernetes
from kpm.registry import Registry
from kpm.utils import colorize, mkdir_p
from kpm.display import print_deploy_result

logger = logging.getLogger(__name__)


def output_progress(kubsource, status, fmt="text"):
    if fmt == 'text':
        print " --> %s (%s): %s" % (kubsource.name, kubsource.kind, colorize(status))


def _process(package_name,
             version=None,
             dest="/tmp",
             namespace=None,
             force=False,
             dry=False,
             endpoint=None,
             action="create",
             fmt="text",
             proxy=None,
             variables=None,
             shards=None,
             packages=None):

    if packages is None:
        registry = Registry(endpoint=endpoint)
        packages = registry.generate(package_name,
                                     namespace=namespace,
                                     version=version,
                                     variables=variables,
                                     shards=shards)

    dest = os.path.join(dest, package_name)

    if version:
        dest = os.path.join(dest, version)
    mkdir_p(dest)
    table = []
    results = []
    if fmt == "text":
        print "%s %s " % (action, package_name)
    i = 0
    for package in packages["deploy"]:
        i += 1
        pname = package["package"]
        version = package["version"]
        namespace = package["namespace"]
        if fmt == "text":
            print "\n %02d - %s:" % (i, package["package"])
        for resource in package["resources"]:
            body = resource["body"]
            endpoint = resource["endpoint"]
            # Use API instead of kubectl
            with open(os.path.join(dest, "%s-%s" % (resource['name'], resource['file'].replace("/", "_"))), 'wb') as f:
                f.write(body)
            kubresource = Kubernetes(namespace=namespace, body=body, endpoint=endpoint, proxy=proxy)
            status = getattr(kubresource, action)(force=force, dry=dry)
            if fmt == "text":
                output_progress(kubresource, status)
            result_line = OrderedDict([("package", pname),
                                       ("version", version),
                                       ("kind", kubresource.kind),
                                       ("dry", dry),
                                       ("name", kubresource.name),
                                       ("namespace", kubresource.namespace),
                                       ("status", status)])

            if status != 'ok' and action == 'create':
                kubresource.wait(3)
            results.append(result_line)
            if fmt == "text":
                header = ["package", "version", "kind", "name",  "namespace", "status"]
                display_line = []
                for k in header:
                    display_line.append(result_line[k])
                table.append(display_line)
    if fmt == "text":
        print_deploy_result(table)
    return results


def deploy(*args, **kwargs):
    kwargs['action'] = 'create'
    return _process(*args, **kwargs)


def delete(*args, **kwargs):
    kwargs['action'] = 'delete'
    return _process(*args, **kwargs)
