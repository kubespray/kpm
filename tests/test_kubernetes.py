import json
import pytest
import requests
import requests_mock
from conftest import get_response
from kpm.kubernetes import get_endpoint, Kubernetes


NAMESPACE="testns"


def test_endpoints():
    a = get_endpoint("po")
    b = get_endpoint("pods")
    c = get_endpoint("pod")
    assert a == b
    assert b == c


def test_endpoints_missing():
    with pytest.raises(KeyError):
        get_endpoint("bad")


def test_protected_is_true_when_annoted(ns_resource):
    k = Kubernetes(body=ns_resource['body'])
    assert k.protected is True


def test_protected_is_false(svc_resource):
    k = Kubernetes(body=svc_resource['body'])
    assert k.protected is False


def test_force_namespace(ns_resource):
    k = Kubernetes(namespace="test", body=ns_resource['body'])
    assert k.namespace == "test"


def test__namespace(ns_resource):
    k = Kubernetes(body=ns_resource['body'])
    assert k._namespace() == "default"


def test__namespace_annotate(svc_resource):
    k = Kubernetes(body=svc_resource['body'])
    assert k._namespace() == "testns"


def test__namespace_params(svc_resource):
    k = Kubernetes(namespace="test", body=svc_resource['body'])
    assert k._namespace(k.namespace) == "test"


def test_load_obj(svc_resource):
    k = Kubernetes(namespace="test", body=svc_resource['body'])
    assert json.dumps(k.obj) == json.dumps(json.loads(svc_resource['body']))


def test_kind(svc_resource, rc_resource, ns_resource):
    ks = Kubernetes(body=svc_resource['body'])
    kr = Kubernetes(body=rc_resource['body'])
    kn = Kubernetes(body=ns_resource['body'])
    assert kr.kind == "replicationcontroller"
    assert kn.kind == "namespace"
    assert ks.kind == "service"


def test_get_hash(svc_resource):
    ks = Kubernetes(body=svc_resource['body'])
    kbody = json.loads(svc_resource['body'])
    assert ks.kpmhash == ks._get_kpmhash(kbody)
    assert ks.kpmhash == kbody['metadata']['annotations']['kpm.hash']


def test_get_empty(ns_resource):
    k = Kubernetes(body=ns_resource['body'])
    assert k.kpmhash is None


def test_check_cmd(svc_resource, subcall_cmd):
    k = Kubernetes(body=svc_resource['body'])
    assert k._call(["get", "svc", "kube-ui"]) == "kubectl get svc kube-ui --namespace testns"


def test_get_cmd_error(svc_resource, subcall_cmd_error):
    k = Kubernetes(body=svc_resource['body'])
    assert k.get() is None


def test_get_rc(subcall_get_assert, rc_resource):
    k = Kubernetes(body=rc_resource['body'])
    assert json.dumps(k.get()) == json.dumps(json.loads(get_response(k.name, k.kind)))


def test_get_svc(subcall_get_assert, svc_resource):
    k = Kubernetes(body=svc_resource['body'])
    assert json.dumps(k.get()) == json.dumps(json.loads(get_response(k.name, k.kind)))


def test_get_ns(subcall_get_assert, ns_resource):
    k = Kubernetes(body=ns_resource['body'], namespace="testns")
    assert json.dumps(k.get()) == json.dumps(json.loads(get_response(k.name, k.kind)))


def test_delete_ns_protected(subcall_delete, ns_resource):
    k = Kubernetes(body=ns_resource['body'])
    assert k.delete() == "protected"


def test_delete_existing_resource(subcall_delete, svc_resource):
    k = Kubernetes(body=svc_resource['body'])
    assert k.delete() == "deleted"


def test_delete_non_existing_resource(subcall_cmd_error, svc_resource):
    k = Kubernetes(body=svc_resource['body'])
    assert k.delete() == "absent"


def test_exists_true(subcall_get_assert, svc_resource):
    k = Kubernetes(body=svc_resource['body'])
    assert k.exists() is True


def test_exists_false(subcall_cmd_error, svc_resource):
    k = Kubernetes(body=svc_resource['body'])
    assert k.exists() is False


def test_get_proxy(svc_resource):
    proxy = "http://localhost:8001"
    k = Kubernetes(body=svc_resource['body'], proxy=proxy, endpoint=svc_resource['endpoint'])
    url = "%s/%s/%s" % (proxy, svc_resource['endpoint'][1:-1], svc_resource['name'])
    url2 = "%s/%s/%s" % (k.proxy.geturl(), k.endpoint, k.name)
    assert url == url2
    with requests_mock.mock() as m:
        response = get_response(svc_resource["name"], svc_resource["kind"])
        m.get(url, text=response)
        assert json.dumps(k.get()) == json.dumps(json.loads(response))


def test_get_proxy_404(svc_resource):
    proxy = "http://localhost:8001"
    k = Kubernetes(body=svc_resource['body'], proxy=proxy, endpoint=svc_resource['endpoint'])
    url = "%s/%s/%s" % (proxy, svc_resource['endpoint'][1:-1], svc_resource['name'])
    with requests_mock.mock() as m:
        response = get_response(svc_resource["name"], svc_resource["kind"])
        m.get(url, text=response, status_code=404)
        assert k.get() is None


def test_get_proxy_500_raise(svc_resource):
    proxy = "http://localhost:8001"
    k = Kubernetes(body=svc_resource['body'], proxy=proxy, endpoint=svc_resource['endpoint'])
    url = "%s/%s/%s" % (proxy, svc_resource['endpoint'][1:-1], svc_resource['name'])
    with requests_mock.mock() as m:
        response = get_response(svc_resource["name"], svc_resource["kind"])
        m.get(url, text=response, status_code=500)
        with pytest.raises(requests.exceptions.HTTPError):
            k.get()


def test_call_dry(svc_resource):
    k = Kubernetes(body=svc_resource['body'])
    assert k._call(["get", "rc", "kube-ui"], dry=True)


def test_create_cmd(svc_resource, subcall_cmd, monkeypatch):
    def get(*args):
        return None
    monkeypatch.setattr("kpm.kubernetes.Kubernetes.get", get)
    k = Kubernetes(body=svc_resource['body'])
    assert k.create() == "created"


def test_create_update(svc_resource, subcall_cmd, monkeypatch):
    def get(*args):
        svc2 = json.loads(svc_resource['body'])
        svc2['metadata']['annotations']['kpm.hash'] = 'dummy'
        return svc2

    monkeypatch.setattr("kpm.kubernetes.Kubernetes.get", get)
    k = Kubernetes(body=svc_resource['body'])
    assert k.create() == "updated"


def test_create_ok(svc_resource, subcall_cmd, monkeypatch):
    def get(*args):
        svc2 = json.loads(svc_resource['body'])
        return svc2

    monkeypatch.setattr("kpm.kubernetes.Kubernetes.get", get)
    k = Kubernetes(body=svc_resource['body'])
    assert k.create() == "ok"


def test_create_force(svc_resource, subcall_cmd, monkeypatch):
    def get(*args):
        svc2 = json.loads(svc_resource['body'])
        return svc2

    monkeypatch.setattr("kpm.kubernetes.Kubernetes.get", get)
    k = Kubernetes(body=svc_resource['body'])
    assert k.create(force=True) == "updated"


def test_create_ok_nohash(ns_resource, subcall_cmd, monkeypatch):
    def get(*args):
        r = json.loads(ns_resource['body'])
        return r

    monkeypatch.setattr("kpm.kubernetes.Kubernetes.get", get)
    k = Kubernetes(body=ns_resource['body'])
    assert k.create() == "ok"


def test_create_nohash(ns_resource, subcall_cmd, monkeypatch):
    def get(*args):
        return None
    monkeypatch.setattr("kpm.kubernetes.Kubernetes.get", get)
    k = Kubernetes(body=ns_resource['body'])
    assert k.create() == "created"


def test_create_force_protected(ns_resource, subcall_cmd, monkeypatch):
    def get(*args):
        svc2 = json.loads(ns_resource['body'])
        return svc2

    monkeypatch.setattr("kpm.kubernetes.Kubernetes.get", get)
    k = Kubernetes(body=ns_resource['body'])
    assert k.create(force=True) == "protected"


def test_create_proxy(svc_resource):
    proxy = "http://localhost:8001"
    k = Kubernetes(body=svc_resource['body'], proxy=proxy, endpoint=svc_resource['endpoint'])
    url = "%s/%s" % (proxy, svc_resource['endpoint'][1:-1])
    url2 = "%s/%s" % (k.proxy.geturl(), k.endpoint)
    assert url == url2
    with requests_mock.mock() as m:
        response = get_response(svc_resource["name"], svc_resource["kind"])
        m.post(url, text=response)
        m.get(url + "/" + svc_resource['name'], status_code=404)
        assert k.create() == "created"


def test_wait(svc_resource, monkeypatch):
    import time
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    proxy = "http://localhost:8001"
    k = Kubernetes(body=svc_resource['body'], proxy=proxy, endpoint=svc_resource['endpoint'])
    url = "%s/%s/%s" % (proxy, svc_resource['endpoint'][1:-1], svc_resource['name'])
    url2 = "%s/%s/%s" % (k.proxy.geturl(), k.endpoint, k.name)
    assert url == url2
    with requests_mock.mock() as m:
        response = get_response(svc_resource["name"], svc_resource["kind"])
        m.get(url, [{'status_code': 404}, {'text': response, 'status_code': 200}])
        assert json.dumps(k.wait()) == json.dumps(json.loads(response))
        assert m.call_count == 2
