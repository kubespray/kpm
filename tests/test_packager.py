import pytest
import os.path

from kpm.packager import pack_kub, unpack_kub, Package
import hashlib


TAR_MD5SUM = "0031d193dcb4782bcce087810c2498b2"
KUBEUI_FILES = ["manifest.yaml",
                "README.md",
                "templates/kube-ui-rc.yaml",
                "templates/kube-ui-svc.yaml"]

@pytest.fixture()
def package_dir(monkeypatch):
    monkeypatch.chdir("tests/data/kube-ui")


@pytest.fixture()
def pack_tar(package_dir, tmpdir):
    kub = os.path.join(str(tmpdir.mkdir("tars")), "kube-ui.tar")
    pack_kub(kub)
    return kub


def test_pack_kub(pack_tar):
    assert hashlib.md5(open(pack_tar, "r").read()).hexdigest() == TAR_MD5SUM


def test_pack_kub_with_authorized_only(pack_tar, tmpdir):
    import tarfile
    tar = tarfile.open(pack_tar, "r")
    tar.extractall(str(tmpdir))
    assert os.path.exists(os.path.join(str(tmpdir), "file_to_ignore.yaml")) is False
    assert os.path.exists(os.path.join(str(tmpdir), "manifest.yaml")) is True


def _check_kub(path):
    for f in KUBEUI_FILES:
        assert os.path.exists(os.path.join(str(path), f))
    assert os.path.exists(os.path.join(str(path), "templates/another_file_to_ignore.cfg")) is False
    assert os.path.exists(os.path.join(str(path), "file_to_ignore.yaml")) is False


def test_unpack_kub(pack_tar, tmpdir):
    unpack_kub(pack_tar, str(tmpdir))
    _check_kub(str(tmpdir))


def test_extract(kubeui_package, tmpdir):
    d = tmpdir.mkdir("extract")
    kubeui_package.extract(str(d))
    _check_kub(str(d))


def test_pack(kubeui_package, tmpdir):
    d = str(tmpdir.mkdir("pack")) + "/kube-ui.tar"
    kubeui_package.pack(d)
    assert hashlib.md5(open(d, "r").read()).hexdigest() == TAR_MD5SUM


def test_tree(kubeui_package):
    files = kubeui_package.tree()
    assert sorted(files) == sorted(KUBEUI_FILES)


def test_tree_filter(kubeui_package):
    files = kubeui_package.tree("templates")
    assert sorted(files) == sorted(["templates/kube-ui-rc.yaml", "templates/kube-ui-svc.yaml"])


def test_file(kubeui_package):
    manifest = kubeui_package.file("manifest.yaml")
    assert manifest == open("tests/data/kube-ui/manifest.yaml", "r").read()


def test_manifest(kubeui_package):
    assert kubeui_package.manifest == open("tests/data/kube-ui/manifest.yaml", "r").read()
