import yaml
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
    assert k.token('*') is None
    assert k.tokens is None


def test_delete_empty_token(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    assert k.delete_token('*') is None


def test_delete_token(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    k.add_token('*', "titid")
    assert k.token('*') == "titid"
    assert k.delete_token('*') == "titid"
    assert k.token('*') is None

def test_create_token_value(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    k.add_token('a', "titic")
    k.add_token('b', "titib")
    assert k.token('a') == "titic"
    assert k.token('a') == "titic"
    assert k.token('c') is None


def test_create_token_file(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    k.add_token('a', "titib")
    assert os.path.exists(k.tokenfile) is True
    f = open(k.tokenfile, 'r')
    r = f.read()
    assert  {'auths': {'a': 'titib'}} == yaml.load(r)



def test_create_delete_get_token(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    k.add_token('a', "titia")
    assert k.token('a') == "titia"
    k.delete_token('a')
    assert k.token('a') is None


def test_get_token_from_file(fake_home):
    """ Should not fail if there is no token """
    k = KpmAuth()
    f = open(k.tokenfile, 'w')
    f.write("{'auths': {'a': 'titib'}}")
    f.close()
    assert k.token('a') == "titib"
