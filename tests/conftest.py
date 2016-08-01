import json
import subprocess
import pytest
import os
from kpm.api.app import create_app


@pytest.fixture
def discovery_html():
    return """<html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="kpm-package" content="kpm.sh/{name} https://api.kubespray.io/api/v1/packages/{name}/pull">
    </head>
    <body>
    <a href=https://github.com/kubespray/kpm>kubespray/kpm</a>
    </body>
    </html>"""


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture(scope='module')
def jinja_env():
    import kpm.kub
    return kpm.kub.jinja_env


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
    import kpm.packager
    with open("./tests/data/kube-ui.tar.gz", "rb") as f:
        package = kpm.packager.Package(f.read())
    print package.files
    return package


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
