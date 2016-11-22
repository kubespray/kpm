import os
import json
import subprocess
import pytest

from kpm.api.app import create_app


@pytest.fixture
def discovery_html():
    return """<html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="cnr-package" content="cnr.sh/{name} https://api.kubespray.io/api/v1/packages/{name}/{version}/{mediatype}/pull">
    </head>
    <body>
    <a href=https://github.com/coreos/kpm>coreos/kpm</a>
    </body>
    </html>"""


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture(scope='module')
def jinja_env():
    import kpm.template_filters
    return kpm.template_filters.jinja_env()


@pytest.fixture()
def fake_home(monkeypatch, tmpdir):
    home = tmpdir.mkdir('home')
    monkeypatch.setenv("HOME", home)
    return home


def get_response(name, kind):
    f = open("tests/data/responses/%s-%s.json" % (name, kind))
    r = f.read()
    f.close()
    return r


@pytest.fixture(scope="module")
def kubeui_package():
    import base64
    import kpm.packager
    with open("./tests/data/kube-ui.tar.gz", "rb") as f:
        package = kpm.packager.Package(base64.b64encode(f.read()))
    return package


@pytest.fixture(scope='module')
def package_data():
    return 'H4sICF8BsVcC/3RpdF9yb2NrZXRjaGF0XzEuMTAuMGt1Yi50YXIA7Zddb9MwFIZ7nV9hlYve0DRpmgZFgJjGhCat2zQGNwhNXup1Vu04st1IVZX/znGTtMnYWAWj08DPRT6Ofezjr/ckF0cHHydHLp92/h4eMB6PzN2PQq95L4lGHX84HkfjcBz4YPeDKPA6yOvsgYXSWCLUwYzMJE4fnIfHyquhbO4vBEeKZE50cou1826L47xCxylMDWOOM884ouULalR3OpYXD8cpvSFKu0vM2fOcf98LAjj/URgE/ggK4PyHPpjs+d8D/X7fyXAyxzMSOwilmJMYdTXVg+1J70IBXuhbIWN0kGpBU4JOytlAb4faxaXtw4xjytxE8PfgkBOpqEhj5Lu+53pgmRKVSJrptbWhIwgxmpBUQceT40vHybGk+JoRZQKSJINSrKAdeKPcxNlwrqJ0zXPMsIadXI1CwajInX5MfFcLyWKkuM7iwQBsCYMdQGBk1YPLRIKZqSzSmZhel/WrF3CpntzVatNLUbgqT8BSNVEU8TCCLT5oiqUkSixkUo6qj24oa0XXNy0suem4XoVW6AjpZQZGqObc34DcyV+C+xTmVCzLOMqqoPCuuh3AQgZ+PUIr7/8DmvBsfW4GP22lvel/4Jnvv8gLQ89cQP+jyB9a/d+X/uOMfq3VOvedOU2nMboohdeo9aFItRSMEelwovEUa7zNFW0hx9eEgVavevM3qo+zrBej3rZG7zXqVXnBFOR+r2irdUtUHZWRpJ0DVqv6uTCeijCSaJOWHurQ1Kq3eLyWweYIDL8VMnRdxWZIYH4wJECpakv/fgk27JjCSlpJo4ZRTnXLAiFkC8iQnsdbVk64kMsYBZ43oZsSkuZN5zrWydnpp7OrLxcnrSZyzBbrhWmkw6K4z/3g+OQX3lXmbbhmQsIo0LdVL5NCi0QwM8GXh+dmyjdTeg61eusReGA2Xd1d4e82UT21/lffIk+q/6OH//9Hw9D8/0ejcBSGQ7AP4Z9gbPX/OfS/m/vdKgN0PxOZw5d5909VfyeR31HL1x+xp2JKjDA4j6gIrOyM6EclBKzZto4VFIvFYrFYLBaLxWKxWCwWi8Xyb/ADcPSUWQAoAAA='


@pytest.fixture(scope="module")
def kubeui_blob():
    import kpm.packager
    with open("./tests/data/kube-ui.tar.gz", "rb") as f:
        package = f.read()
    return package


@pytest.fixture(scope="module")
def deploy_json():
    f = open("tests/data/kube-ui_release.json", 'r')
    r = f.read()
    f.close()
    return r


@pytest.fixture()
def package_dir(monkeypatch):
    monkeypatch.chdir("tests/data/kube-ui")


@pytest.fixture()
def bad_package_dir(monkeypatch):
    monkeypatch.chdir("tests/data/bad_manifest")

@pytest.fixture()
def empty_package_dir(monkeypatch):
    monkeypatch.chdir("tests/data")


@pytest.fixture()
def pack_tar(package_dir, tmpdir):
    from kpm.packager import pack_kub
    kub = os.path.join(str(tmpdir.mkdir("tars")), "kube-ui.tar.gz")
    pack_kub(kub)
    return kub


@pytest.fixture(scope="module")
def deploy(deploy_json):
    return json.loads(deploy_json)


@pytest.fixture(scope="module")
def ns_resource(deploy):
    kubeui = deploy["deploy"][0]
    return kubeui['resources'][0]


@pytest.fixture(scope="module")
def rc_resource(deploy):
    kubeui = deploy["deploy"][0]
    return kubeui['resources'][1]


@pytest.fixture(scope="module")
def svc_resource(deploy):
    kubeui = deploy["deploy"][0]
    return kubeui['resources'][2]


@pytest.fixture()
def subcall_cmd(monkeypatch):
    def get_cmd(cmd, stderr="err"):
        return " ".join(cmd)
    monkeypatch.setattr("subprocess.check_output", get_cmd)


@pytest.fixture()
def subcall_cmd_error(monkeypatch):
    def get_cmd(cmd, stderr="err"):
        raise subprocess.CalledProcessError("a", "b", "c")
    monkeypatch.setattr("subprocess.check_output", get_cmd)



@pytest.fixture()
def subcall_get_assert(monkeypatch):
    def get_cmd(cmd, stderr="err"):
        kind, name = cmd[2], cmd[3]
        assert " ".join(cmd) == "kubectl get %s %s -o json --namespace testns" % (kind, name)
        return get_response(name, kind)
    monkeypatch.setattr("subprocess.check_output", get_cmd)


@pytest.fixture()
def subcall_all(monkeypatch):
    def get_cmd(cmd, stderr="err"):
        action, kind, name = cmd[1], cmd[2], cmd[3]
        if action != "create":
            return get_response(name, kind)
        else:
            with open(name, 'r') as f:
                return f.read()
    monkeypatch.setattr("subprocess.check_output", get_cmd)


@pytest.fixture()
def subcall_delete(monkeypatch):
    def get_cmd(cmd, stderr="err"):
        action, kind, name = cmd[1], cmd[2], cmd[3]
        if action == "get":
            assert " ".join(cmd) == "kubectl get %s %s -o json --namespace testns" % (kind, name)
        elif action == "delete":
            assert " ".join(cmd) == "kubectl delete %s %s --namespace testns" % (kind, name)
        return get_response(name, kind)
    monkeypatch.setattr("subprocess.check_output", get_cmd)
