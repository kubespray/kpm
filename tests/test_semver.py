import pytest
import kpm.semver as semver
import random
import copy


@pytest.fixture(scope='module')
def version_list():
    l = ["1.4.0",
         "1.6.0-alpha",
         "1.6.0-alpha.1",
         "1.6.0-alpha.beta",
         "1.6.0-beta",
         "1.6.0-beta.2",
         "1.6.0-beta.11",
         "1.6.0-rc.1",
         "1.6.0",
         "1.7.0-rc"]
    return l


@pytest.fixture(scope='module')
def version_query():
    return ['0.1.0',
            '0.3.0',
            '0.3.2-rc',
            '0.5.0',
            '0.5.2-rc',
            '0.7.0',
            '0.8.0-rc']


def test_ordering(version_list):
    l2 = copy.copy(version_list)
    random.seed(1)
    random.shuffle(l2)
    assert str(semver.versions(l2, stable=False)) != str(semver.versions(version_list, stable=False))
    assert str(sorted(semver.versions(l2, stable=False))) == str(semver.versions(version_list, stable=False))


def test_stable_only(version_list):
    assert semver.versions(version_list, stable=True) == semver.versions(["1.4.0", "1.6.0"])


def test_last_stable_version(version_list):
    assert str(semver.last_version(version_list, True)) == "1.6.0"


def test_last_unstable_version(version_list):
    assert str(semver.last_version(version_list, False)) == "1.7.0-rc"


def test_select_version(version_query):
    expected_results = [("==0.5.0", "0.5.0"),
                        (">=0.1.0", "0.7.0"),
                        ("<0.4.0", "0.3.0"),
                        (">=0.3.0,<0.6.0", "0.5.0"),
                        ([">=0.3.0", "<0.6.0"], "0.5.0"),
                        (">=0.1.0-", "0.8.0-rc"),
                        ("<0.4.0-", "0.3.2-rc"),
                        (">=0.3.0-,<0.6.0", "0.5.2-rc"),
                        (">=0.3.0,<0.6.0-", "0.5.2-rc"),
                        ("==10.0.0", 'None')]
    for query, expected in expected_results:
        assert str(semver.select_version(version_query, query)) == expected
