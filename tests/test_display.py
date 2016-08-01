import pytest
from kpm.display import print_packages, print_deploy_result


@pytest.fixture()
def package_list():
    h = [{"name": "o1/p1",
          "version": "1.4.0",
          "downloads": 45,
          "available_versions": ["1.3.0", "1.2.0"]},
         {"name": "o1/p2",
          "version": "1.4.0",
          "downloads": 45,
          "available_versions": ["1.3.0", "1.2.0"]}]
    return h


@pytest.fixture()
def deploy_result():
    from collections import OrderedDict
    h = [OrderedDict([("name", "o1/p1"),
                      ("version", "1.4.0"),
                      ("type", "replicationcontroller"),
                      ("name", "p1"),
                      ("namespace", "testns"),
                      ("status", "ok")]).values(),
         OrderedDict([("name", "o1/p1"),
                      ("version", "1.4.0"),
                      ("type", "svc"),
                      ("name", "p1"),
                      ("namespace", "testns"),
                      ("status", "updated")]).values(),

         ]
    return h


def test_empty_list(capsys):
    print_packages([])
    out, err = capsys.readouterr()
    res = unicode("\n".join(["app    version    downloads",
                     "-----  ---------  -----------",""]))
    assert out == res


def test_print_packages(package_list, capsys):
    print_packages(package_list)
    out, err = capsys.readouterr()
    res = unicode("\n".join(["app    version      downloads",
                             "-----  ---------  -----------",
                             "o1/p1  1.4.0               45",
                             "o1/p2  1.4.0               45", ""]))

    assert out == res


def test_print_empty_deploy_result(capsys):
    print_deploy_result([])
    out, err = capsys.readouterr()
    res = u'\n'.join(["\n", "package    version    type    name    namespace    status",
                      "---------  ---------  ------  ------  -----------  --------", ""])
    assert out == res


def test_print_deploy_result(deploy_result, capsys):
    print_deploy_result(deploy_result)
    out, err = capsys.readouterr()
    res = "\n".join(["\n",
                     "package    version    type                   name    namespace",
                     "---------  ---------  ---------------------  ------  -----------",
                     "p1         1.4.0      replicationcontroller  testns  \x1b[32mok\x1b[0m",
                     "p1         1.4.0      svc                    testns  \x1b[33mupdated\x1b[0m",
                     ""])
    assert out == res
