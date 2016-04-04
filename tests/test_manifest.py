import pytest
from kpm.manifest import Manifest


@pytest.fixture(scope="module")
def manifest(kubeui_package):
    return Manifest(kubeui_package)


@pytest.fixture(scope="module")
def empty_manifest():
    return Manifest(None, None)


def test_empty_resources(empty_manifest):
    assert empty_manifest.resources == []


def test_empty_variables(empty_manifest):
    assert empty_manifest.variables == {}


def test_empty_package(empty_manifest):
    assert empty_manifest.package == {}


def test_empty_shards(empty_manifest):
    assert empty_manifest.shards == []


def test_empty_deploy(empty_manifest):
    assert empty_manifest.deploy == []


def test_package_name(manifest):
    assert manifest.package_name() == "kube-system_kube-ui_1.0.1"


def test_kubename(manifest):
    assert manifest.kubname() == "kube-system_kube-ui"


def test_load_from_path(manifest):
    m = Manifest(path="tests/data/kube-ui")
    assert m == manifest


def test_load_bad_manifest(manifest):
    import yaml
    with pytest.raises(yaml.YAMLError):
        Manifest(path="tests/data/bad_manifest")
