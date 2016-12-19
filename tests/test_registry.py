import json
import pytest
import requests
import requests_mock
from base64 import b64encode
from conftest import get_response
from kpm.registry import Registry, DEFAULT_REGISTRY
import kpm

def test_headers_without_auth(fake_home):
    r = Registry()
    assert sorted(r.headers.keys()) == ['Content-Type', 'User-Agent']
    assert r.headers["Content-Type"] == "application/json"
    assert r.headers["User-Agent"] == "kpmpy-cli: %s" % kpm.__version__


def test_headers_with_auth(fake_home):
    r = Registry()
    r.auth.add_token(DEFAULT_REGISTRY, "titi")
    assert sorted(r.headers.keys()) == ["Authorization", 'Content-Type', 'User-Agent']
    assert r.headers["Authorization"] == "titi"
    assert r.headers["Content-Type"] == "application/json"
    assert r.headers["User-Agent"] == "kpmpy-cli: %s" % kpm.__version__


def test_default_endpoint():
    r = Registry()
    assert r.endpoint.geturl() == DEFAULT_REGISTRY


def test_url():
    r = Registry(endpoint="http://test.com")
    assert r._url("/test") == "http://test.com/test"


def test_pull():
    r = Registry()
    with requests_mock.mock() as m:
        response = 'package_data'
        m.get(DEFAULT_REGISTRY + "/api/v1/packages/orga/p1/1.0.1/kpm/pull", text=response)
        assert r.pull("orga/p1", "1.0.1", "kpm") == response


def test_pull_discovery_https(discovery_html):
    r = Registry()
    with requests_mock.mock() as m:
        response = 'package_data'
        m.get("https://cnr.sh/?cnr-discovery=1", text=discovery_html, complete_qs=True)
        m.get("https://api.kubespray.io/api/v1/packages/orga/p1/1.0.1/kpm/pull", text=response)
        assert r.pull("cnr.sh/orga/p1", "1.0.1", "kpm") == response


def test_pull_discovery_http(discovery_html):
    r = Registry()
    with requests_mock.mock() as m:
        response = 'package_data'
        m.get("https://cnr.sh/?cnr-discovery=1", text="<html/>", complete_qs=True)
        m.get("http://cnr.sh/?cnr-discovery=1", text=discovery_html, complete_qs=True)
        m.get("https://api.kubespray.io/api/v1/packages/orga/p1/1.0.1/kpm/pull", text=response)
        assert r.pull("cnr.sh/orga/p1", "1.0.1", "kpm") == response


def test_pull_with_version():
    r = Registry()
    with requests_mock.mock() as m:
        response = 'package_data'
        m.get(DEFAULT_REGISTRY + "/api/v1/packages/orga/p1/1.0.1/kpm/pull", complete_qs=True, text=response)
        assert r.pull("orga/p1", version="1.0.1", media_type="kpm") == response


def test_list_packages():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + "/api/v1/packages", text=response)
        assert json.dumps(r.list_packages()) == response


def test_list_packages_username():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + "/api/v1/packages?username=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages(user="ant31")) == response


def test_list_packages_orga():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + "/api/v1/packages?organization=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages(organization="ant31")) == response


def test_list_packages_orga_and_user():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + "/api/v1/packages?username=titi&organization=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages(user="titi", organization="ant31")) == response


def test_generate():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + "/api/v1/packages/ant31/kube-ui/generate", complete_qs=True, text=response)
        assert json.dumps(r.generate(name="ant31/kube-ui")) == response


def test_generate_with_params():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get(DEFAULT_REGISTRY + "/api/v1/packages/ant31/kube-ui/generate?version=1.3.4&namespace=testns", complete_qs=True, text=response)
        assert json.dumps(r.generate(name="ant31/kube-ui", namespace="testns", variables={"a": "b", "c": "d"}, version="1.3.4")) == response


def test_signup(fake_home):
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"email": "al@cnr.sh", "token": "signup_token"}'
        m.post(DEFAULT_REGISTRY + "/api/v1/users", complete_qs=True, text=response)
        sign_r = r.signup("ant31", "plop", "plop", "al@cnr.sh")
        assert json.dumps(sign_r) == json.dumps(json.loads(response))
        assert r.auth.token(DEFAULT_REGISTRY) == "signup_token"


# @TODO
def test_signup_existing():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"email": "al@cnr.sh", "token": "signup_token"}'
        m.post(DEFAULT_REGISTRY + "/api/v1/users", complete_qs=True, text=response, status_code=401)
        with pytest.raises(requests.HTTPError):
            sign_r = r.signup("ant31", "plop", "plop", "al@cnr.sh")


def test_login(fake_home):
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"email": "al@cnr.sh", "token": "login_token"}'
        m.post(DEFAULT_REGISTRY + "/api/v1/users/login", complete_qs=True, text=response)
        login_r = r.login("ant31", "plop")
        assert json.dumps(login_r) == json.dumps(json.loads(response))
        assert r.auth.token(DEFAULT_REGISTRY) == "login_token"


def test_login_failed(fake_home):
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"email": "al@cnr.sh", "token": "login_token"}'
        m.post(DEFAULT_REGISTRY + "/api/v1/users/login",
              complete_qs=True,
              text=response, status_code=401)
        with pytest.raises(requests.HTTPError):
            login_r = r.login("ant31", "plop")


def test_delete_package():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete(DEFAULT_REGISTRY + "/api/v1/packages/ant31/kube-ui/default/kpm", complete_qs=True, text=response)
        assert r.delete_package("ant31/kube-ui", "default", "kpm") == {"packages": "true"}


def test_delete_package_version():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete(DEFAULT_REGISTRY + "/api/v1/packages/ant31/kube-ui/1.4.3/kpm", complete_qs=True, text=response)
        assert r.delete_package(name="ant31/kube-ui", version="1.4.3", media_type="kpm") == {"packages": "true"}


def test_delete_package_unauthorized(fake_home):
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete(DEFAULT_REGISTRY + "/api/v1/packages/ant31/kube-ui/1.2.0/kpm",
                 complete_qs=True,
                 text=response,
                 status_code=401)
        with pytest.raises(requests.HTTPError):
            r.delete_package(name="ant31/kube-ui", version="1.2.0", media_type="kpm")


def test_push_unauthorized(kubeui_blob):
    r = Registry()
    with requests_mock.mock() as m:
        body = {"blob": b64encode(kubeui_blob)}
        response = '{"packages": "true"}'
        m.post(DEFAULT_REGISTRY + "/api/v1/packages/ant31/kube-ui?force=false",
                 complete_qs=True,
                 text=response,
                 status_code=401)
        with pytest.raises(requests.HTTPError):
            r.push(name="ant31/kube-ui", body=body)


def test_push(kubeui_blob):
    body = {"blob": b64encode(kubeui_blob)}
    r = Registry()
    response = '{"packages": "true"}'
    with requests_mock.mock() as m:
        m.post(DEFAULT_REGISTRY + "/api/v1/packages/ant31/kube-ui?force=false",
               complete_qs=True,
               text=response)
        assert json.dumps(r.push(name="ant31/kube-ui", body=body)) == json.dumps(json.loads(response))



def test_push_force(kubeui_blob):
    body = {"blob": b64encode(kubeui_blob)}
    r = Registry()
    response = '{"packages": "true"}'
    with requests_mock.mock() as m:
        m.post(DEFAULT_REGISTRY + "/api/v1/packages/ant31/kube-ui?force=true",
               complete_qs=True,
               text=response)
        assert json.dumps(r.push(name="ant31/kube-ui", body=body, force=True)) == json.dumps(json.loads(response))
