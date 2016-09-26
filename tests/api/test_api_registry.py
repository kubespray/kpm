import base64
import pytest
import etcd
from kpm.models.etcd.package import Package
from kpm.exception import (
    InvalidVersion,
    PackageAlreadyExists,
    )


class MockEtcdResult(object):
    def __init__(self, result):
        self.result = result

    @property
    def key(self):
        return self.result

    @property
    def value(self):
        return "value"


class MockEtcdResults(object):
    def __init__(self, results):
        self.results = results

    @property
    def children(self):
        return [MockEtcdResult(x) for x in self.results]

@pytest.fixture
def etcd_package():
    pass

def test_showversion(client):
    import kpm
    res = client.get("/version")
    assert res.json == {"kpm-api": kpm.__version__}


def test_etcdkey():
    assert Package._etcdkey("a/b", "1.4.3") == "kpm/packages/a/b/releases/1.4.3"


def test_check_data_validversion():
    assert Package.check_version("1.4.5-alpha") is None


def test_check_data_invalidversion():
    with pytest.raises(InvalidVersion):
        assert Package.check_version("1.4.5a-alpha")


@pytest.fixture()
def getversions(monkeypatch):
    def read(path, recursive=True):
        assert path == "kpm/packages/ant31/rocketchat/releases"
        return MockEtcdResults(["/kpm/packages/ant31/rocketchat/releases/1.3.0",
                                "/kpm/packages/ant31/rocketchat/releases/1.3.2-rc2",
                                "/kpm/packages/ant31/rocketchat/releases/1.8.2-rc2",
                                "/kpm/packages/ant31/rocketchat/releases/1.4.2",
                                "/kpm/packages/ant31/rocketchat/releases/1.0.0",
                                "/kpm/packages/ant31/rocketchat/releases/1.2.0"])
    monkeypatch.setattr("kpm.models.etcd.etcd_client.read", read)


def test_getversions(getversions):
    assert Package.all_versions("ant31/rocketchat") == ['1.3.0', '1.3.2-rc2', '1.8.2-rc2', '1.4.2', '1.0.0', '1.2.0']


def test_getversions_empty(monkeypatch):
    def read(path, recursive=True):
        assert path == "kpm/packages/ant31/rocketchat/releases"
        return MockEtcdResults([])
    monkeypatch.setattr("kpm.models.etcd.etcd_client.read", read)
    assert Package.all_versions("ant31/rocketchat") == []


def test_getversion_latest(getversions):
    assert str(Package.get_version("ant31/rocketchat", "latest")) == "1.8.2-rc2"


def test_getversion_stable_none(getversions):
    assert str(Package.get_version("ant31/rocketchat", None, True)) == "1.4.2"


def test_getversion_invalid(getversions):
    with pytest.raises(InvalidVersion):
        str(Package.get_version("ant31/rocketchat", "==4.25a"))


def test_getversion_prerelease(getversions):
    str(Package.get_version("ant31/rocketchat", ">=0-")) == "1.8.2-rc2"


def test_push_etcd(monkeypatch, package_data):
    def write(path, data, prevExist):
        assert path == "kpm/packages/a/b/releases/4"
        assert data == "value"
        return True
    monkeypatch.setattr("kpm.models.etcd.etcd_client.write", write)
    p = Package('a/b', 4, package_data)
    p._push_etcd("a/b", 4, "value")


def test_push_etcd_exist(monkeypatch, package_data):
    def write(path, data, prevExist):
        assert path == "kpm/packages/a/b/releases/4"
        assert data == "value"
        raise etcd.EtcdAlreadyExist
    monkeypatch.setattr("kpm.models.etcd.etcd_client.write", write)
    with pytest.raises(PackageAlreadyExists):
        p = Package('a/b', 4, package_data)
        p._push_etcd("a/b", 4, "value")
