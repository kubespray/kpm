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


def test_load_manifest(new, monkeypatch, fake_home):
    import kpm.manifest
    name = "organization/newpackage"
    monkeypatch.chdir(os.path.join(str(fake_home), name))

    m = kpm.manifest.Manifest()
    assert m.package["name"] == "organization/newpackage"
    assert m.deploy == [{'name': "$self"}]


def test_load_manifest_comments(new_with_comments, monkeypatch, fake_home):
    import kpm.manifest
    name = "organization/newpackage2"
    monkeypatch.chdir(os.path.join(str(fake_home), name))
    m = kpm.manifest.Manifest()
    assert m.package["name"] == name
    assert m.deploy == [{'name': "$self"}]
