import pytest


@pytest.fixture(scope="module")
def kubeui_package():
    import kpm.packager
    with open("./tests/data/kube-ui.tar", "rb") as f:
        package = kpm.packager.Package(f.read())
    return package
