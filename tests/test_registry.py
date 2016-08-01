import json
import pytest
import requests
import requests_mock
from base64 import b64encode
from conftest import get_response
from kpm.registry import Registry
import kpm


def test_headers_without_auth():
    r = Registry()
    assert sorted(r.headers.keys()) == ['Content-Type', 'User-Agent']
    assert r.headers["Content-Type"] == "application/json"
    assert r.headers["User-Agent"] == "kpmpy-cli: %s" % kpm.__version__


def test_headers_with_auth():
    r = Registry()
    r.auth.token = "titi"
    assert sorted(r.headers.keys()) == ["Authorization", 'Content-Type', 'User-Agent']
    assert r.headers["Authorization"] == "titi"
    assert r.headers["Content-Type"] == "application/json"
    assert r.headers["User-Agent"] == "kpmpy-cli: %s" % kpm.__version__


def test_default_endpoint():
    r = Registry(endpoint=None)
    assert r.endpoint.geturl() == "https://api.kpm.sh"


def test_url():
    r = Registry(endpoint="http://test.com")
    assert r._url("/test") == "http://test.com/api/v1/test"


def test_pull():
    r = Registry()
    with requests_mock.mock() as m:
        response = 'package_data'
        m.get("https://api.kpm.sh/api/v1/packages/orga/p1/pull", text=response)
        assert r.pull("orga/p1") == response


def test_pull_discovery_https(discovery_html):
    r = Registry()
    with requests_mock.mock() as m:
        response = 'package_data'
        m.get("https://kpm.sh/?kpm-discovery=1", text=discovery_html, complete_qs=True)
        m.get("https://api.kubespray.io/api/v1/packages/orga/p1/pull", text=response)
        assert r.pull("kpm.sh/orga/p1") == response


def test_pull_discovery_http(discovery_html):
    r = Registry()
    with requests_mock.mock() as m:
        response = 'package_data'
        m.get("https://kpm.sh/?kpm-discovery=1", text="<html/>", complete_qs=True)
        m.get("http://kpm.sh/?kpm-discovery=1", text=discovery_html, complete_qs=True)
        m.get("https://api.kubespray.io/api/v1/packages/orga/p1/pull", text=response)
        assert r.pull("kpm.sh/orga/p1") == response


def test_pull_with_version():
    r = Registry()
    with requests_mock.mock() as m:
        response = 'package_data'
        m.get("https://api.kpm.sh/api/v1/packages/orga/p1/pull?version=1.0.1", complete_qs=True, text=response)
        assert r.pull("orga/p1", version="1.0.1") == response


def test_list_packages():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get("https://api.kpm.sh/api/v1/packages", text=response)
        assert json.dumps(r.list_packages()) == response


def test_list_packages_username():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get("https://api.kpm.sh/api/v1/packages?username=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages(user="ant31")) == response


def test_list_packages_orga():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get("https://api.kpm.sh/api/v1/packages?organization=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages(organization="ant31")) == response


def test_list_packages_orga_and_user():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get("https://api.kpm.sh/api/v1/packages?username=titi&organization=ant31", complete_qs=True, text=response)
        assert json.dumps(r.list_packages(user="titi", organization="ant31")) == response


def test_generate():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get("https://api.kpm.sh/api/v1/packages/ant31/kube-ui/generate", complete_qs=True, text=response)
        assert json.dumps(r.generate(name="ant31/kube-ui")) == response


def test_generate_with_params():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.get("https://api.kpm.sh/api/v1/packages/ant31/kube-ui/generate?tarball=true&version=1.3.4&namespace=testns", complete_qs=True, text=response)
        assert json.dumps(r.generate(name="ant31/kube-ui", namespace="testns", variables={"a": "b", "c": "d"}, version="1.3.4", tarball=True)) == response


def test_signup():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"email": "al@kpm.sh", "token": "signup_token"}'
        m.post("https://api.kpm.sh/api/v1/users?user%5Bpassword%5D=plop&user%5Busername%5D=ant31&user%5Bpassword_confirmation%5D=plop&user%5Bemail%5D=al%40kpm.sh", complete_qs=True, text=response)
        sign_r = r.signup("ant31", "plop", "plop", "al@kpm.sh")
        assert json.dumps(sign_r) == json.dumps(json.loads(response))
        assert r.auth.token == "signup_token"


# @TODO
def test_signup_existing():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"email": "al@kpm.sh", "token": "signup_token"}'
        m.post("https://api.kpm.sh/api/v1/users?user%5Bpassword%5D=plop&user%5Busername%5D=ant31&user%5Bpassword_confirmation%5D=plop&user%5Bemail%5D=al%40kpm.sh", complete_qs=True, text=response, status_code=401)
        with pytest.raises(requests.HTTPError):
            sign_r = r.signup("ant31", "plop", "plop", "al@kpm.sh")


def test_login():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"email": "al@kpm.sh", "token": "login_token"}'
        m.post("https://api.kpm.sh/api/v1/users/login?user%5Bpassword%5D=plop&user%5Busername%5D=ant31", complete_qs=True, text=response)
        login_r = r.login("ant31", "plop")
        assert json.dumps(login_r) == json.dumps(json.loads(response))
        assert r.auth.token == "login_token"


def test_login_failed():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"email": "al@kpm.sh", "token": "login_token"}'
        m.post("https://api.kpm.sh/api/v1/users/login?user%5Bpassword%5D=plop&user%5Busername%5D=ant31",
              complete_qs=True,
              text=response, status_code=401)
        with pytest.raises(requests.HTTPError):
            login_r = r.login("ant31", "plop")


def test_delete_package():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete("https://api.kpm.sh/api/v1/packages/ant31/kube-ui", complete_qs=True, text=response)
        assert r.delete_package(name="ant31/kube-ui") is True


def test_delete_package_version():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete("https://api.kpm.sh/api/v1/packages/ant31/kube-ui?version=1.4.3", complete_qs=True, text=response)
        assert r.delete_package(name="ant31/kube-ui", version="1.4.3") is True


def test_delete_package_unauthorized():
    r = Registry()
    with requests_mock.mock() as m:
        response = '{"packages": "true"}'
        m.delete("https://api.kpm.sh/api/v1/packages/ant31/kube-ui",
                 complete_qs=True,
                 text=response,
                 status_code=401)
        with pytest.raises(requests.HTTPError):
            r.delete_package(name="ant31/kube-ui")


def test_push_unauthorized(kubeui_blob):
    r = Registry()
    with requests_mock.mock() as m:
        body = {"blob": b64encode(kubeui_blob)}
        response = '{"packages": "true"}'
        m.post("https://api.kpm.sh/api/v1/packages/ant31/kube-ui?force=false",
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
        m.post("https://api.kpm.sh/api/v1/packages/ant31/kube-ui?force=false",
               complete_qs=True,
               text=response)
        assert json.dumps(r.push(name="ant31/kube-ui", body=body)) == json.dumps(json.loads(response))



def test_push_force(kubeui_blob):
    body = {"blob": b64encode(kubeui_blob)}
    r = Registry()
    response = '{"packages": "true"}'
    with requests_mock.mock() as m:
        m.post("https://api.kpm.sh/api/v1/packages/ant31/kube-ui?force=true",
               complete_qs=True,
               text=response)
        assert json.dumps(r.push(name="ant31/kube-ui", body=body, force=True)) == json.dumps(json.loads(response))
