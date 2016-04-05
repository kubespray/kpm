import pytest
import os.path
from kpm.auth import KpmAuth


def test_fake_home(fake_home):
    assert os.path.expanduser("~") == fake_home


def test_init_create_dir(fake_home):
    KpmAuth()
    assert os.path.exists(os.path.join(str(fake_home), ".kpm"))


def test_init_token_empty(fake_home):
    k = KpmAuth()
    assert os.path.exists(k.tokenfile) is False


def test_get_empty_token(fake_home):
    k = KpmAuth()
    assert k.token is None


def test_delete_empty_token(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    assert k.delete_token() is None


def test_delete_token(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    k.token = "titid"
    assert k.delete_token() == "titid"
    assert os.path.exists(k.tokenfile) is False


def test_create_token_value(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    k.token = "titic"
    assert k.token == "titic"


def test_create_token_file(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    k.token = "titib"
    assert os.path.exists(k.tokenfile) is True
    f = open(k.tokenfile, 'r')
    r = f.read()
    f.close()
    assert r == "titib"


def test_create_delete_get_token(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    k.token = "titia"
    assert k.token == "titia"
    k.delete_token()
    assert k.token is None


def test_get_token_from_file(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    f = open(k.tokenfile, 'w')
    f.write("mytoken")
    f.close()
    assert k.token == "mytoken"
