import pytest
import os
from kpm.new import new_package


@pytest.fixture()
def home_dir(monkeypatch, fake_home):
    monkeypatch.chdir(str(fake_home))
    return str(fake_home)


@pytest.fixture()
def new(home_dir):
    new_package("organization/newpackage")


@pytest.fixture()
def new_with_comments(home_dir):
    new_package("organization/newpackage2", with_comments=True)


def test_directory(new):
    assert os.path.exists("organization/newpackage")


def test_directory_comments(new_with_comments):
    assert os.path.exists("organization/newpackage2")


def test_files_created(new):
    for f in ["templates", "manifest.yaml", "README.md"]:
        assert os.path.exists(os.path.join("organization/newpackage", f))


def test_load_manifest(new):
    import kpm.manifest
    m = kpm.manifest.Manifest(path="organization/newpackage")
    assert m.package["name"] == "organization/newpackage"
    assert m.deploy == [{'name': "$self"}]


def test_load_manifest_comments(new_with_comments):
    import kpm.manifest
    m = kpm.manifest.Manifest(path="organization/newpackage2")
    assert m.package["name"] == "organization/newpackage2"
    assert m.deploy == [{'name': "$self"}]
