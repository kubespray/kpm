from kpm.formats.kub import Kub


DEFAULT_ENDPOINT = "http://localhost:5000"


def build(package,
          version_query=None,
          namespace="default",
          variables={},
          shards=None,
          endpoint=DEFAULT_ENDPOINT):
    """
    A build is the construction/expansion of a package.
    The result are the expanded/ready to use resources, including every dependencies.

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version_query (:obj:`str`): a version query, eg: ">=1.5,<2.0"
      namespace (:obj:`str`): kubernetes namespace to deploy the resource
      variables (:obj:`dict`): override default package variables to resolve templated resources
      shards (:obj:`json`, :obj:`int`): the shards (experimental)
      endpoint (:obj:`str`): the kpm-registry server

    Returns:
      :obj:`kpm.kub_jsonnet.Kub`: the Kub object.
      To generate the build runs one of the following commands:
        * :obj:`kpm.kub_jsonnet.Kub.build()`: create a `dict`
        * :obj:`kpm.kub_jsonnet.KubBase.build_tar()`: create a `tar.gz`

    Example:
      Flask route example::

         @builder_app.route("/api/v1/packages/<path:package>/generate", methods=['GET'])
         def build(package):
            k = kpm.api.impl.builder.build("ant31/postgresql",
                                           version=">=9.5.0",
                                           namespace="db",
                                           variables={'memory': "8Gi"}
                                           shards=None,
                                           endpoint="http://localhost:5000")
            build = k.build()
            return jsonify(build)

    See Also:
       * :obj:`kpm.api.builder.build`
       * :obj:`kpm.api.builder.build_tar`

    """
    variables['namespace'] = namespace
    k = Kub(package,
            endpoint=endpoint,
            variables=variables,
            namespace=namespace,
            version=version_query,
            shards=shards)
    return k


def show_file(package, filepath, version_query=None, endpoint=DEFAULT_ENDPOINT):
    """
    Returns the content of any file inside a package.
    Useful to navigate and inspect a package from a web-browser

    Args:
      package (:obj:`str`): package name in the format `namespace/name` or `domain.com/name`
      filepath (:obj:`str`): filepath relative to the package, eg: `templates/svc.yaml`
      version_query (:obj:`str`): a version query, eg: ">=1.5,<2.0"
      endpoint (:obj:`str`): the kpm-registry server

    Returns:
      :obj:`str`: the file content

    See Also:
       * :obj:`kpm.api.builder.show_file`

    """
    k = Kub(package, version=version_query, endpoint=endpoint)
    return k.package.file(filepath)


def tree(package, version_query=None, endpoint=DEFAULT_ENDPOINT):
    """
    List recursivly the files inside a package.

    Args:
      package (:obj:`str`): package name in the format `namespace/name` or `domain.com/name`
      version_query (:obj:`str`): a version query, eg: ">=1.5,<2.0"
      filepath (:obj:`str`): filepath relative to the package, eg: `templates/svc.yaml`
      endpoint (:obj:`str`): the kpm-registry server

    Returns:
      :obj:`list`: package file list::

    Example:
       >>> kpm.api.impl.builder.tree("ant31/rocketchat", "latest", "http://localhost:5000")
           [
            "README.md",
            "manifest.jsonnet",
            "manifest.yaml",
            "templates/rocketchat-rc.yml",
            "templates/rocketchat-svc.yml"
           ]


    See Also:
       * :obj:`kpm.api.builder.tree`

    """

    k = Kub(package, version=version_query, endpoint=endpoint)
    return k.package.tree()
