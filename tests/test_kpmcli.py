import json
import subprocess
import pytest
import os
import pytest
import requests
from kpm.utils import colorize
from kpm.command import (new,
                         show,
                         install,
                         remove,
                         pull,
                         push,
                         list_packages,
                         login,
                         logout,
                         delete_package,
                         get_parser)


# 1. signup with uniq-test-id account
# 2. push package with test-id as organization
# 3. logout -> check ~/.kpm/auth is not exists
# 4. try to push -> failed
# 5. login
# 7. list -u test-id
# -  delete package
# -  list -u test-id
# -  push again
# -  pull
# -  install package
# -  remove package
# 9. show test-1/package == manifest
# 10. show --tree
# 11. show file template/kube-ui-svc.yaml
PROJECT_DIR=os.getcwd()


@pytest.fixture(scope="module")
def project_dir():
    return PROJECT_DIR

@pytest.fixture(scope="module")
def testid():
    import random
    import uuid
    a = list(uuid.uuid1().hex)
    random.shuffle(a)
    return "".join(a)[0:8]


@pytest.fixture(scope="module")
def parser():
    return get_parser()


@pytest.fixture(scope="module")
def pkgname(testid):
    return "org-%s/pkg-%s" % (testid, testid)


@pytest.fixture(scope="module")
def cli_home(tmpdir_factory):
    home = str(tmpdir_factory.mktemp('home'))
    os.environ['HOME'] = home
    return home


@pytest.fixture(scope="module")
def package_home(pkgname, cli_home):
    import shutil

    package_home = str(cli_home) + "/kube-ui"
    if os.path.exists(package_home) is False:
        manifestpath = package_home + "/manifest.yaml"
        shutil.copytree("tests/data/kube-ui", package_home)
        # Read in the file
        filedata = None
        with open(manifestpath, 'r') as f:
            filedata = f.read()
        filedata = filedata.replace('kube-system/kube-ui', pkgname)
        with open(manifestpath, 'w') as file:
            file.write(filedata)

    return package_home


@pytest.fixture(scope="module")
def email(testid):
    return "%s@kubespray.io" % testid


@pytest.fixture(scope="module")
def user(testid):
    return "user-%s" % testid


@pytest.fixture(scope="module")
def password(testid):
    return "%s" % testid


@pytest.fixture(scope="module")
def api_stg():
    host = os.environ.get("KPM_API", "https://api-stg.kpm.sh")
    return ["-H", host]


@pytest.mark.cli
@pytest.mark.last
def test_signup(user, email, password, parser, api_stg, package_home, capsys):
    cmd = "login -u %s -p %s -e %s --signup" % (user, password, email)
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    response = ' >>> Registration complete\n'
    out, err = capsys.readouterr()
    assert out == response


@pytest.mark.cli
@pytest.mark.last
def test_push_1(package_home, parser, monkeypatch, pkgname, api_stg, capsys):
    os.chdir(package_home)
    cmd = "push"
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    assert out == "package: %s (1.0.1) pushed\n" % pkgname


@pytest.mark.cli
@pytest.mark.last
def test_push_1_existing(package_home, parser, monkeypatch, pkgname, api_stg, capsys):
    os.chdir(package_home)
    cmd = "push"
    args = parser.parse_args(cmd.split(" ") + api_stg)
    with pytest.raises(requests.HTTPError):
        args.func(args)


@pytest.mark.cli
@pytest.mark.last
def test_push_1_force(package_home, parser, monkeypatch, pkgname, api_stg, capsys):
    os.chdir(package_home)
    cmd = "push --force"
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    assert out == "package: %s (1.0.1) pushed\n" % pkgname


@pytest.mark.cli
@pytest.mark.last
def test_list_packages_ok(package_home, user, parser, pkgname, api_stg, capsys):
    cmd = "list -u %s" % user
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    response = """app                        version      downloads
-------------------------  ---------  -----------
{pkgname}  1.0.1                0\n""".format(pkgname=pkgname)
    assert out == response


@pytest.mark.cli
@pytest.mark.last
def test_show(package_home, parser, pkgname, api_stg, capsys):
    os.chdir(package_home)
    cmd = "show %s" % pkgname
    manifestpath = package_home + "/manifest.yaml"
    # Read in the file
    filedata = None
    with open(manifestpath, 'r') as f:
        filedata = f.read()

    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)

    out, err = capsys.readouterr()
    assert out == filedata + "\n"


@pytest.mark.cli
@pytest.mark.last
def test_show_tree(package_home, parser, pkgname, api_stg, capsys):
    os.chdir(package_home)
    cmd = "show --tree %s" % pkgname
    manifestpath = package_home + "/manifest.yaml"
    # Read in the file
    filedata = None
    with open(manifestpath, 'r') as f:
        filedata = f.read()

    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)

    out, err = capsys.readouterr()
    assert out == """README.md
manifest.yaml
templates/kube-ui-rc.yaml
templates/kube-ui-svc.yaml\n"""


@pytest.mark.cli
@pytest.mark.last
def test_show_file(package_home, parser, pkgname, api_stg, capsys):
    os.chdir(package_home)
    cmd = "show -f templates/kube-ui-rc.yaml %s" % pkgname
    path = package_home + "/templates/kube-ui-rc.yaml"
    # Read in the file
    filedata = None
    with open(path, 'r') as f:
        filedata = f.read()

    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)

    out, err = capsys.readouterr()
    assert out == filedata + "\n"


@pytest.mark.cli
@pytest.mark.last
def test_logout(cli_home, parser, api_stg, capsys):
    os.chdir(str(cli_home))
    assert os.path.exists(".kpm/auth_token")
    cmd = "logout"
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    assert out == ' >>> Logout complete\n'
    assert not os.path.exists(".kpm/auth_token")


@pytest.mark.cli
@pytest.mark.last
def test_login(cli_home, user, password, parser, api_stg, capsys):
    os.chdir(str(cli_home))
    cmd = "login -u %s -p %s" % (user, password)
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    assert out == ' >>> Login succeeded\n'
    assert os.path.exists(".kpm/auth_token")


@pytest.mark.cli
@pytest.mark.last
def test_pull(package_home, parser, pkgname, api_stg):
    cmd = "pull %s" % pkgname
    os.chdir(str(package_home))
    manifestpath = package_home + "/manifest.yaml"
    # Read in the file
    filedata = None
    with open(manifestpath, 'r') as f:
        filedata = f.read()

    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    pulldata = None
    with open(package_home + ("/%s_1.0.1/manifest.yaml" % pkgname.replace("/", "_")), 'r') as f:
        pulldata = f.read()
    assert pulldata == filedata


@pytest.mark.cli
@pytest.mark.last
def test_new(cli_home, parser, pkgname, api_stg):
    os.chdir(str(cli_home))
    cmd = "new t2/test"
    args = parser.parse_args(cmd.split(" "))
    args.func(args)
    assert os.path.exists("t2/test/manifest.yaml")


@pytest.mark.cli
@pytest.mark.last
def test_deploy(project_dir, subcall_all, user, parser, pkgname, api_stg, capsys):
    os.chdir(project_dir)
    cmd = "deploy %s --namespace=testns" % pkgname
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    response = """create {pkgname} \n
 01 - {pkgname}:
 --> testns (namespace): {ok}
 --> kube-ui (replicationcontroller): {ok}
 --> kube-ui (service): {updated}


package                    version    type                   name     namespace    status
-------------------------  ---------  ---------------------  -------  -----------  --------
{pkgname}  1.0.1      namespace              testns   testns       {ok}
{pkgname}  1.0.1      replicationcontroller  kube-ui  testns       {ok}
{pkgname}  1.0.1      service                kube-ui  testns       {updated}\n""".format(pkgname=pkgname,
                                                                                         ok=colorize('ok'),
                                                                                         updated=colorize('updated'))

    # with open("/tmp/r", "w") as f:
    #     f.write(out)
    # with open("/tmp/r2", "w") as f:
    #     f.write(response)

    assert out == response


@pytest.mark.cli
@pytest.mark.last
def test_remove(project_dir, subcall_all, user, parser, pkgname, api_stg, capsys):
    os.chdir(project_dir)
    cmd = "remove %s --namespace=testns" % pkgname
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    response = """delete {pkgname} \n
 01 - {pkgname}:
 --> testns (namespace): {protected}
 --> kube-ui (replicationcontroller): {deleted}
 --> kube-ui (service): {deleted}


package                    version    type                   name     namespace    status
-------------------------  ---------  ---------------------  -------  -----------  ---------
{pkgname}  1.0.1      namespace              testns   testns       {protected}
{pkgname}  1.0.1      replicationcontroller  kube-ui  testns       {deleted}
{pkgname}  1.0.1      service                kube-ui  testns       {deleted}\n""".format(pkgname=pkgname,
                                                                                         protected=colorize('protected'),
                                                                                         deleted=colorize('deleted'))
    assert out == response


@pytest.mark.cli
@pytest.mark.last
def test_delete_package(package_home, user, parser, pkgname, api_stg, capsys):
    cmd = "delete-package %s" % pkgname
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    assert out == "Package %s deleted\n" % pkgname


@pytest.mark.cli
@pytest.mark.last
def test_list_packages_missing(package_home, user, parser, pkgname, api_stg, capsys):
    cmd = "list -u %s" % user
    args = parser.parse_args(cmd.split(" ") + api_stg)
    args.func(args)
    out, err = capsys.readouterr()
    response = """app    version    downloads
-----  ---------  -----------\n"""

    assert out == response
