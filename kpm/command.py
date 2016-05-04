#!/usr/bin/env python
import argparse
import getpass

import os
from kpm.auth import KpmAuth
import kpm.registry as registry
from kpm.registry import Registry
from kpm.packager import pack_kub, Package
import kpm.manifest
import kpm.deploy
from kpm.display import print_packages
from kpm.new import new_package
from kpm.console import KubernetesExec
from kpm.utils import parse_cmdline_variables


import base64


def new(options):
    new_package(options.package[0], options.directory, options.with_comments)


def show(options):
    r = Registry(options.registry_host)
    result = r.pull(options.package[0], version=options.version)
    p = Package(result)
    if options.tree:
        print "\n".join(p.tree())
    elif options.file:
        print p.file(options.file)
    else:
        print p.manifest


def install(options):
    variables = None
    if options.variables is not None:
        variables = parse_cmdline_variables(options.variables)
    kpm.deploy.deploy(options.package[0],
                      version=options.version,
                      dest=options.tmpdir,
                      namespace=options.namespace,
                      force=options.force,
                      dry=options.dry_run,
                      endpoint=options.registry_host,
                      proxy=options.api_proxy,
                      variables=variables)


def remove(options):
    kpm.deploy.delete(options.package[0],
                      version=options.version,
                      dest=options.tmpdir,
                      namespace=options.namespace,
                      dry=options.dry_run,
                      endpoint=options.registry_host,
                      proxy=options.api_proxy)


def pull(options):
    r = Registry(options.registry_host)
    result = r.pull(options.package[0], version=options.version)
    p = Package(result)
    path = os.path.join(options.directory, kpm.manifest.Manifest(p).package_name())
    p.extract(path)


def exec_cmd(options):
    c = KubernetesExec(options.name,
                       cmd=" ".join(options.cmd),
                       namespace=options.namespace,
                       container=options.container,
                       kind=options.kind)
    c.call()


def push(options):
    r = Registry(options.registry_host)
    # @TODO: Override organization
    manifest = kpm.manifest.Manifest(path=".")
    # @TODO: Pack in memory
    kubepath = os.path.join(".", manifest.package_name() + ".tar.gz")
    pack_kub(kubepath)
    f = open(kubepath, 'rb')
    r.push(manifest.package['name'], {"name": manifest.package['name'],
                                      "version": manifest.package['version'],
                                      "blob": base64.b64encode(f.read())}, options.force)
    f.close()
    os.remove(kubepath)
    print "package: %s (%s) pushed" % (manifest.package['name'],
                                       manifest.package['version'])


def list_packages(options):
    r = Registry(options.registry_host)
    response = r.list_packages(user=options.user, organization=options.organization)
    print_packages(response)


def login(options):
    r = Registry(options.registry_host)
    if options.user is not None:
        user = options.user
    else:
        user = raw_input("Username: ")
    if options.password is not None:
        p1 = options.password
    else:
        p1 = getpass.getpass()

    if options.signup:
        if options.password is not None:
            p2 = p1
        else:
            p2 = getpass.getpass('Password confirmation: ')
        if options.email is not None:
            email = options.email
        else:
            email = raw_input("Email: ")
        if p1 != p2:
            print "Error: password mismatch"
            exit(1)
        r.signup(user, p1, p2, email)
        print ' >>> Registration complete'
    else:
        r.login(user, p1)
        print ' >>> Login succeeded'


def logout(options):
    KpmAuth().delete_token()
    print ' >>> Logout complete'


def delete_package(options):
    r = Registry(options.registry_host)
    r.delete_package(options.package[0], version=options.version)
    print "Package %s deleted" % (options.package[0])


def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--namespace",
                        help="namespace to deploy the application")

    subparsers = parser.add_subparsers(help='command help')

    # PUSH
    push_parser = subparsers.add_parser('push', help='push a package to the registry')
    push_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                             help='registry API url')
    push_parser.add_argument("-o", "--organization", nargs="?", default=None,
                             help="push to another organization")
    push_parser.add_argument("-f", "--force", action='store_true', default=False,
                             help="force push")

    push_parser.set_defaults(func=push)

    # PULL
    pull_parser = subparsers.add_parser('pull', help='download a package and extract it')
    pull_parser.add_argument('package', nargs=1, help="package-name")
    pull_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                             help='registry API url')
    pull_parser.add_argument("--directory", nargs="?", default=".",
                             help="destionation directory")
    pull_parser.add_argument("-v", "--version", nargs="?", default=None,
                             help="package version")

    pull_parser.set_defaults(func=pull)

    # Show
    show_parser = subparsers.add_parser('show', help='print the package manifest')
    show_parser.add_argument('package', nargs=1, help="package-name")
    show_parser.add_argument('--tree', help="List files inside the package", action='store_true', default=False)
    show_parser.add_argument('-f', '--file', nargs="?", help="Display a file", default=None)
    show_parser.add_argument("-v", "--version", nargs="?", default=None,
                             help="package version")

    show_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                             help='registry API url')

    show_parser.set_defaults(func=show)

    # new
    new_parser = subparsers.add_parser('new', help='initiate a new package')
    new_parser.add_argument('package', nargs=1, help="package-name")
    new_parser.add_argument("--directory",  nargs="?", default=".",
                            help="destionation directory")
    new_parser.add_argument("--with-comments", action='store_true', default=False,
                            help="Add 'help' comments to manifest")

    new_parser.set_defaults(func=new)

    # Login
    login_parser = subparsers.add_parser('login', help='login')
    login_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                              help='registry API url')
    login_parser.add_argument("-s", "--signup", action='store_true', default=False,
                              help="Create a new account and login")
    login_parser.add_argument("-u", "--user", nargs="?", default=None,
                              help="username")
    login_parser.add_argument("-p", "--password", nargs="?", default=None,
                              help="password")
    login_parser.add_argument("-e", "--email", nargs="?", default=None,
                              help="email for signup")

    login_parser.set_defaults(func=login)

    # Logout
    logout_parser = subparsers.add_parser('logout', help='logout')
    logout_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                               help='registry API url')
    logout_parser.set_defaults(func=logout)

    # Install
    install_parser = subparsers.add_parser('deploy', help='deploy a package on kubernetes')
    install_parser.add_argument('package', nargs=1, help="package-name")
    install_parser.add_argument("--tmpdir", nargs="?", default="/tmp/",
                                help="directory used to extract resources")
    install_parser.add_argument("--dry-run", action='store_true', default=False,
                                help="do not create the resources on kubernetes")
    install_parser.add_argument("--namespace", nargs="?",
                                help="kubernetes namespace", default=None)
    install_parser.add_argument("--api-proxy", nargs="?",
                                help="kubectl proxy url", const="http://localhost:8001")
    install_parser.add_argument("-v", "--version", nargs="?",
                                help="package VERSION", default=None)
    install_parser.add_argument("-x", "--variables",
                                help="variables", default=None, action="append")

    install_parser.add_argument("--force", action='store_true', default=False,
                                help="force upgrade, delete and recreate resources")
    install_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                                help='registry API url')
    install_parser.set_defaults(func=install)

    # remove
    remove_parser = subparsers.add_parser('remove', help='remove a package from kubernetes')
    remove_parser.add_argument('package', nargs=1, help="package-name")
    remove_parser.add_argument("--tmpdir", nargs="?", default="/tmp/",
                               help="directory used to extract resources")
    remove_parser.add_argument("--dry-run", action='store_true', default=False,
                               help="Does not delete the resources on kubernetes")
    remove_parser.add_argument("--namespace", nargs="?",
                               help="kubernetes namespace", default=None)
    remove_parser.add_argument("--api-proxy", nargs="?",
                               help="kubectl proxy url", const="http://localhost:8001")

    remove_parser.add_argument("-v", "--version", nargs="?",
                               help="package VERSION to delete", default=None)

    remove_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                               help='registry API url')
    remove_parser.set_defaults(func=remove)

    # list
    list_parser = subparsers.add_parser('list', help='list packages')
    list_parser.add_argument("-u", "--user", nargs="?", default=None,
                             help="list packages owned by USER")
    list_parser.add_argument("-o", "--organization", nargs="?", default=None,
                             help="list ORGANIZATION packages")
    list_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                             help='registry API url')

    list_parser.set_defaults(func=list_packages)

    #  DELETE-PACKAGE
    delete_parser = subparsers.add_parser('delete-package', help='delete package from the registry')
    delete_parser.add_argument('package', nargs=1, help="package-name")
    delete_parser.add_argument("-H", "--registry-host", nargs="?", default=registry.DEFAULT_REGISTRY,
                               help='registry API url')
    delete_parser.add_argument("-v", "--version", nargs="?", default=None,
                               help="package version")

    delete_parser.set_defaults(func=delete_package)

    #  EXEC
    exec_parser = subparsers.add_parser('exec', help='exec a command in pod from the RC or RS name.\
    It executes the command on the first matching pod')
    exec_parser.add_argument('cmd', nargs='+', help="command to execute")
    exec_parser.add_argument("--namespace", nargs="?",
                             help="kubernetes namespace", default='default')

    exec_parser.add_argument('-k', '--kind', choices=['deployment', 'rs', 'rc'], nargs="?",
                             help="deployment, rc or rs", default='rc')
    exec_parser.add_argument('-n', '--name', help="resource name", default='rs')
    exec_parser.add_argument('-c', '--container', nargs='?', help="container name", default=None)

    exec_parser.set_defaults(func=exec_cmd)

    return parser
