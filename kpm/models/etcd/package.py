import datetime
import json
import etcd
import re
import kpm.semver as semver
from kpm.models.package_base import PackageBase
from kpm.exception import PackageAlreadyExists, ChannelNotFound
from kpm.models.etcd import ETCD_PREFIX, etcd_client


class Package(PackageBase):
    index_path = "/kpm/search/index"

    def __init__(self, package_name, version=None, blob=None):

        super(Package, self).__init__(package_name,
                                      version=version,
                                      blob=blob)

    @classmethod
    def _fetch(self, package, version):
        path = self._etcdkey(package, str(version))
        try:
            package_data = json.loads(etcd_client.read(path).value)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(package, version)
        return package_data

    @classmethod
    def all_versions(self, package):
        path = ETCD_PREFIX + package + "/releases"
        try:
            r = etcd_client.read(path, recursive=True)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(package, None)

        versions = []
        for child in r.children:
            m = re.match("^/%s(.+)/(.+)/releases/(.+)$" % ETCD_PREFIX, child.key)
            if m is None:
                continue
            version = m.group(3)
            versions.append(version)
        return versions

    @classmethod
    def deleted_releases(self, package):
        path = ETCD_PREFIX + "%s/deleted" % package
        r = []
        try:
            deleted_releases = etcd_client.get(path)
            for child in deleted_releases.children:
                m = re.match("^/%s/(.+)$" % path, child.key)
                if m is None:
                    continue
                r.append(m.group(1))
        except etcd.EtcdKeyNotFound:
            pass
        return r

    @classmethod
    def all(self, organization=None):
        path = ETCD_PREFIX
        r = {}
        if organization is not None:
            path += "/%s" % organization
        try:
            packages = etcd_client.read(path, recursive=True)
        except etcd.EtcdKeyNotFound:
            etcd_client.write(path, None, dir=True)

        for child in packages.children:
            m = re.match("^/%s(.+)/(.+)/releases/(.+)$" % ETCD_PREFIX, child.key)
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
        return r.values()

    @classmethod
    def isdeleted_release(self, package, version):
        if version in self.deleted_releases(package):
            return True
        else:
            return False

    def _save(self, force=False):
        v = self._push_etcd(self.package, self.version, json.dumps(self.data), force=force)
        try:
            digest_path = self._etcdkey(self.package, self.data['digest'], 'digests')
            etcd_client.write(digest_path, str(v.key))
        except etcd.EtcdAlreadyExist as e:
            raise PackageAlreadyExists(e.message, {"package": self.package, "version": self.version})

    @classmethod
    def search_index(self):
        try:
            r = json.loads(etcd_client.get(self.index_path).value)
        except etcd.EtcdKeyNotFound:
            r = []
            self.write_index(r)
        return r

    @classmethod
    def add_index(self, name):
        r = set(self.search_index())
        r.add(name)
        self.write_index(r)

    @classmethod
    def write_index(self, r):
        etcd_client.write(self.index_path, json.dumps(list(r)))

    @classmethod
    def remove_index(self, name):
        r = set(self.search_index())
        r.remove(name)
        self.write_index(r)

    @classmethod
    def search(self, query):
        r = '\n'.join(self.search_index())
        return re.findall(r"(.*%s.*)" % query, r)

    @classmethod
    def _delete_from_channels(self, package, version, channel_class):
        p = self(package, version)
        for channel in p.channels(channel_class):
            c = channel_class(channel, package)
            try:
                c.remove_release(version)
            except ChannelNotFound:
                pass

    @classmethod
    def _delete(self, package, version):
        path = self._etcdkey(package, str(version))
        try:
            self._fetch(package, version)
            etcd_client.write(path.replace("releases", "deleted"),
                              json.dumps({"deleted_at": datetime.datetime.utcnow().isoformat()}))
            etcd_client.delete(path)
        except etcd.EtcdKeyNotFound:
            self._raise_not_found(package, version)

    @classmethod
    def _etcdkey(self, package, key, directory='releases'):
        return ETCD_PREFIX + "%s/%s/%s" % (package, directory, key)

    def _push_etcd(self, package, version, data, force=False):
        path = self._etcdkey(package, version)
        try:
            r = etcd_client.write(path, data, prevExist=force)
        except etcd.EtcdAlreadyExist as e:
            raise PackageAlreadyExists(e.message, {"package": path})
        except etcd.EtcdKeyNotFound as e:
            r = etcd_client.write(path, data, prevExist=False)
        return r
