import logging
import kpm.semver as semver
from kpm.models.etcd.package import Package
from kpm.models.etcd.channel import Channel


logger = logging.getLogger(__name__)


def _get_package(package, version_query='latest', package_class=Package):
    """
      Fetch the package data from the datastore
      and instantiate a :obj:`kpm.models.package_base.PackageModelBase`

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version_query (:obj:`str`): a version query, eg: ">=1.5,<2.0"
      package_class (:obj:`kpm.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`kpm.kub_jsonnet.KubJsonnet`: :obj:`kpm.models.package_base.PackageModelBase`

    See Also:
       * :obj:`kpm.api.models.package_base.PackageModelBase`
       * :obj:`kpm.api.models.etcd.package.Package`

    Raises:
      :obj:`kpm.exception.PackageNotFound`: package not found
      :obj:`kpm.exception.InvalidVersion`: version-query malformated
      :obj:`kpm.exception.PackageVersionNotFound`: version-query didn't match any release

    """
    # if version is None; Find latest version
    p = package_class.get(package, version_query)
    return p


def pull(package, version='latest', package_class=Package):
    """
    Retrives the package blob from the datastore

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version_query (:obj:`str`): a version query, eg: ">=1.5,<2.0"
      package_class (:obj:`kpm.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: package data
        * package: package name
        * version: version that matched the version query
        * filename: suggested filename to create the tarball
        * blob: a `tar.gz` encoded in base64.

    Example:
      >>> kpm.api.impl.registry.pull("coreos/etcd", version=">=3")
        {
         'blob': 'H4sICHDFvlcC/3RpdF9yb2NrZXRjaGF0XzEuMTAuMGt1Yi50YXIA7ZdRb5swEM',
         'filename': u'coreos_etcd_3.0.1.tar.gz',
         'package': 'coreos_etcd',
         'version': u'3.0.1'
        }

    Raises:
      :obj:`kpm.exception.PackageNotFound`: package not found
      :obj:`kpm.exception.InvalidVersion`: version-query malformated
      :obj:`kpm.exception.PackageVersionNotFound`: version-query didn't match any release

    See Also:
       * :obj:`kpm.api.registry.pull`

    """

    packagemodel = _get_package(package, version, package_class=package_class)
    resp = {"package": package,
            "blob": packagemodel.blob,
            "version": packagemodel.version,
            "filename": "%s_%s.tar.gz" % (packagemodel.package.replace("/", "_"), packagemodel.version)}
    return resp


def push(package, version, blob, force=False, package_class=Package):
    """
    Push a new package release in the the datastore

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version (:obj:`str`): the 'exact' package version (this is not a version_query)
      blob (:obj:`str`): the package directory in `tar.gz` and encoded in base64
      force (:obj:`boolean`): if the package exists already, overwrite it
      package_class (:obj:`kpm.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: push status

    Example:
      >>> kpm.api.impl.registry.push("coreos/etcd", "3.0.1",
            "H4sICHDFvlcC/3RpdF9yb2NrZXRjaGF0XzEuMTAuMGt1Yi50YXIA7ZdRb5swEM")
        {
         'status': u'ok'
        }

    Raises:
      PackageAlreadyExists: if package already exists and `force` is False

    See Also:
       * :obj:`kpm.api.registry.push`

    """
    p = package_class(package, version, blob)
    p.save(force=force)
    return {"status": "ok"}


def search_reindex(package_class=Package):
    Package.reindex()
    return {"status": "ok"}


def search(query, package_class=Package):
    """
    Search packages

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      package_class (:obj:`kpm.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`list`: list of package names

    Example:
      >>> kpm.api.impl.registry.search("etcd")
        [
         'coreos/etcd',
         'ant31/etcd',
         'my-etcd/stable'
        ]

    See Also:
       * :obj:`kpm.api.registry.search`

    """
    p = package_class.search(query)
    return p


def list_packages(organization=None, package_class=Package):
    """
    List all packages, filters can be applied
    Must have at least a release to be visible

    Todos:
       - sort_by: name, created_at, downloads, number of stars
       - filter_by: users

    Args:
      organization (:obj:`str`): returns packages from the `organization` only
      package_class (:obj:`kpm.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`list of dict`: list packages
        * name: package name
        * available_versions (list of str):  All releases
        * created_at (datetime, optional): package creation date
        * downloads (int, optional): number of downloads
        * version: release name

    Example:
      >>> kpm.api.impl.registry.list_packages()
      [
       {
        'available_versions': ['0.1.0'],
        'name': u'quentinm/rados-gateway',
        'version': '0.1.0',
        'created_at": "2016-04-22T11:58:34.103Z",
        'downloads': 41
       },
       {
        'available_versions': ['0.1.0'],
        'name': u'quentinm/nova',
        'version': '0.1.0'
       },
      ]

    See Also:
       * :obj:`kpm.api.registry.list_packages`
    """
    resp = package_class.all(organization)
    return resp


def show_package(package,
                 version="latest",
                 pullmode=False,
                 channel_class=Channel,
                 package_class=Package):
    """
    Returns package details

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      version (:obj:`str`): the 'exact' package version (this is not a version_query)
      pullmode (:obj:`boolean`): include the package blob in the response
      channel_class (:obj:`kpm.models.channel_base:ChannelBase`): the implemented Channel class to use
      package_class (:obj:`kpm.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: package data
        * version (str)
        * name (str)
        * created_at (str)
        * digest (str)
        * channels (list)
        * available_versions (list)
        * dependencies (list)
        * variables (dict)
        * manifest (str)

    Example:
      >>> kpm.api.impl.registry.show_package("ns/mypackage")
      {
      "version": "3.2.0-rc",
      "name": "ns/mypackage",
      "created_at": "2016-08-25T10:16:16.366758",
      "digest": "93de60f59238f9aebce5b9f8bc708e02a0d740364fcd4b185c6da7fc1cdfe1ba",
      "channels": [
       {
        "current": "3.1.0",
        "channel": "stable",
        "releases": [
          "3.1.0"
          "3.0.1"
        ]
       },
      ],
      "available_versions": [
        "3.2.0-rc"
        "3.1.0",
        "3.0.1"
      ],
      "dependencies": [
        "ns/dep1",
        "ns/dep2",
        "ns/dep3"
       ],
       "variables": {
         "replicas": 1,
         "image": "ns/mypackage:latest",
         "namespace": "default",
         "cluster": "cluster.local",
         "mail_url": "smtp://"
       },
      "manifest": "---...."
       }

    Raises:
      :obj:`kpm.exception.PackageNotFound`: package not found
      :obj:`kpm.exception.InvalidVersion`: version-query malformated
      :obj:`kpm.exception.PackageVersionNotFound`: version-query didn't match any release

    See Also:
       * :obj:`kpm.api.registry.show_package`
    """
    stable = False
    packagemodel = _get_package(package, version, package_class)
    manifest = packagemodel.manifest()
    response = {"manifest": packagemodel.packager.manifest,
                "version": packagemodel.version,
                "name":  package,
                "created_at": packagemodel.created_at,
                "digest": packagemodel.digest,
                "variables": manifest.variables,
                "dependencies": manifest.dependencies,
                "channels": packagemodel.channels(channel_class),
                "all_channels": channel_class.all_channels(package).values(),
                "available_versions": [str(x) for x in sorted(semver.versions(packagemodel.versions(), stable),
                                                              reverse=True)]}
    if pullmode:
        response['kub'] = packagemodel.blob
    return response


# CHANNELS
def list_channels(package, channel_class=Channel):
    """
    List all channels for a given package

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      channel_class (:obj:`kpm.models.channel_base:ChannelBase`): the implemented Channel class to use

    Returns:
      :obj:`list of dict`: list channels:
        * channel (str): channel name
        * current (str): latest/default release associated to the channel
        * releases (list): list channel's releases

    Example:
      >>> kpm.api.impl.registry.list_channels("myns/package")
      [{'channel': u'stable', 'current': '1.10.2', 'releases': [u'1.10.2']},
       {'channel': u'dev', 'current': 2.0.0-beta, 'releases': [1.10.2, 2.0.0-beta]}]

    See Also:
       * :obj:`kpm.api.registry.list_channels`
    """
    channels = channel_class.all_channels(package).values()
    return channels


def show_channel(package, name, channel_class=Channel):
    """
    Show channel info
    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      name (:obj:`str`): channel name to inspect
      channel_class (:obj:`kpm.models.channel_base:ChannelBase`): the implemented Channel class to use

    Returns:
      :obj:`dict`: channel info
        * channel (str): channel name
        * current (str): latest/default release associated to the channel
        * releases (list): list channel's releases

    Example:
      >>> kpm.api.impl.registry.list_channels("tit/rocketchat", 'dev')
      {'channel': u'dev', 'current': '2.0.0-beta', 'releases': [u'1.10.2']}

    Raises:
      :obj:`kpm.api.exception.ChannelNotFound`: channel not found

    See Also:
       * :obj:`kpm.api.registry.show_channel`
    """
    c = channel_class(name, package)
    return c.to_dict()


def add_channel_release(package, name, release, channel_class=Channel, package_class=Package):
    """
    Add a package-release to a channel
    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      name (:obj:`str`): channel name to inspect
      release (:obj:`str`): package version to add
      channel_class (:obj:`kpm.models.channel_base:ChannelBase`): the implemented Channel class to use
      package_class (:obj:`kpm.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: channel info
        * channel (str): channel name
        * current (str): latest/default release associated to the channel
        * releases (list): list channel's releases

    Example:
      >>> kpm.api.impl.registry.list_channels("tit/rocketchat", 'dev')
      {'channel': u'dev', 'current': '2.0.0-beta', 'releases': [u'1.10.2']}

    Raises:
      :obj:`kpm.api.exception.ChannelNotFound`: channel not found

    See Also:
       * :obj:`kpm.api.registry.add_channel_release`
    """
    channel = channel_class(name, package)
    channel.add_release(release, package_class)
    return channel.to_dict()


def delete_channel_release(package, name, release, channel_class=Channel, package_class=Package):
    """
    Remove a release from a channel

    Args:
      package (:obj:`str`): package name in the format "namespace/name" or "domain.com/name"
      name (:obj:`str`): channel name to inspect
      release (:obj:`str`): package version to add
      channel_class (:obj:`kpm.models.channel_base:ChannelBase`): the implemented Channel class to use
      package_class (:obj:`kpm.models.package_base:PackageBase`): the implemented Package class to use

    Returns:
      :obj:`dict`: channel info
        * channel (str): channel name
        * current (str): latest/default release associated to the channel
        * releases (list): list channel's releases

    Example:
      >>> kpm.api.impl.registry.list_channels("tit/rocketchat", 'dev')
      {'channel': u'dev', 'current': '2.0.0-beta', 'releases': [u'1.10.2']}

    Raises:
      :obj:`kpm.api.exception.ChannelNotFound`: channel not found

    See Also:
       * :obj:`kpm.api.registry.delete_channel_release`
    """
    channel = channel_class(name, package)
    channel.remove_release(release)
    return channel.to_dict()


def create_channel(package, name, channel_class=Channel):
    channel = channel_class(name, package)
    channel.save()
    return channel.to_dict()


def delete_channel(package, name, channel_class=Channel):
    channel = channel_class(name, package)
    channel.delete()
    return {"channel": channel.name, "package": package, "action": 'delete'}


def delete_package(package, version="latest", package_class=Package, channel_class=Channel):
    packagemodel = _get_package(package, version, package_class)
    package_class.delete(packagemodel.package, packagemodel.version, channel_class)
    return {"status": "delete", "package": packagemodel.package, "version": packagemodel.version}
