import pytest
import requests
import requests_mock
import json
from collections import OrderedDict
from kpm.deploy import deploy, _process, delete


@pytest.fixture(autouse=True)
def nosleep(monkeypatch):
    import time
    monkeypatch.setattr(time, 'sleep', lambda s: None)


@pytest.fixture()
def deploy_result():
    return [OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'namespace'), ('dry', False), ('name', u'testns'), ('namespace', u'testns'), ('status', 'ok')]), OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'replicationcontroller'), ('dry', False), ('name', u'kube-ui'), ('namespace', u'testns'), ('status', 'ok')]), OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'service'), ('dry', False), ('name', u'kube-ui'), ('namespace', u'testns'), ('status', 'updated')])]


@pytest.fixture()
def deploy_dry_result():
    return [OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'namespace'), ('dry', True), ('name', u'testns'), ('namespace', u'testns'), ('status', 'ok')]), OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'replicationcontroller'), ('dry', True), ('name', u'kube-ui'), ('namespace', u'testns'), ('status', 'ok')]), OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'service'), ('dry', True), ('name', u'kube-ui'), ('namespace', u'testns'), ('status', 'updated')])]



@pytest.fixture()
def remove_result():
    return [OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'namespace'), ('dry', False), ('name', u'testns'), ('namespace', u'testns'), ('status', 'protected')]), OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'replicationcontroller'), ('dry', False), ('name', u'kube-ui'), ('namespace', u'testns'), ('status', 'deleted')]), OrderedDict([('package', u'ant31/kube-ui'), ('version', u'1.0.1'), ('kind', u'service'), ('dry', False), ('name', u'kube-ui'), ('namespace', u'testns'), ('status', 'deleted')])]


def test_deploy(deploy_json, deploy_result, subcall_all):
    url = "https://api.kpm.sh/api/v1/packages/%s/%s/generate" % ("ant31", "kube-ui")
    with requests_mock.mock() as m:
        m.get(url, text=deploy_json)
        r = deploy("ant31/kube-ui",
                   version="1.0.1",
                   namespace=None,
                   force=False,
                   dry=False,
                   endpoint=None)
        assert json.dumps(r) == json.dumps(deploy_result)


def test_remove(deploy_json, remove_result, subcall_all):
    url = "https://api.kpm.sh/api/v1/packages/%s/%s/generate" % ("ant31", "kube-ui")
    with requests_mock.mock() as m:
        m.get(url, text=deploy_json)
        r = delete("ant31/kube-ui",
                   version=None,
                   namespace=None,
                   force=False,
                   dry=False,
                   endpoint=None)
        print r
        assert json.dumps(r) == json.dumps(remove_result)


def test_deploy_dry(deploy_json, deploy_dry_result, subcall_all):
    url = "https://api.kpm.sh/api/v1/packages/%s/%s/generate" % ("ant31", "kube-ui")
    with requests_mock.mock() as m:
        m.get(url, text=deploy_json)
        r = deploy("ant31/kube-ui",
                   version=None,
                   namespace=None,
                   force=False,
                   dry=True,
                   endpoint=None)
        assert json.dumps(r) == json.dumps(deploy_dry_result)
