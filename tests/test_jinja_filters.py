import pytest
import base64
import jinja2
import kpm.jinja_filters as filters


def test_get_hash(jinja_env):
    t = jinja_env.from_string("hello {{'titi' | get_hash}}")
    assert t.render() == "hello f7e79ca8eb0b31ee4d5d6c181416667ffee528ed"


def test_get_hash_md5(jinja_env):
    t = jinja_env.from_string("hello {{'titi' | get_hash('md5')}}")
    assert t.render() == "hello 5d933eef19aee7da192608de61b6c23d"


def test_get_hash_unknown(jinja_env):
    t = jinja_env.from_string("hello {{'titi' | get_hash('unknown')}}")
    with pytest.raises(ValueError):
        assert t.render() == "hello 5d933eef19aee7da192608de61b6c23d"


def test_b64encode(jinja_env):
    t = jinja_env.from_string("hello {{'titi' | b64encode}}")
    assert t.render() == "hello %s" % base64.b64encode('titi')


def test_b64decode(jinja_env):
    b64 = 'dGl0aQo='
    t = jinja_env.from_string("hello {{'%s' | b64decode}}" % b64)
    assert t.render() == "hello %s" % base64.b64decode(b64)


def test_b64chain(jinja_env):
    t = jinja_env.from_string("hello {{'titi' | b64encode | b64decode}}")
    assert t.render() == "hello titi"


# @TODO improve keygen tests
def test_gen_rsa(jinja_env):
    t = jinja_env.from_string("{{'rsa' | gen_privatekey}}")
    r = t.render()
    assert r.splitlines()[0] == "-----BEGIN RSA PRIVATE KEY-----"
    assert r.splitlines()[-1] == "-----END RSA PRIVATE KEY-----"


def test_gen_dsa(jinja_env):
    t = jinja_env.from_string("{{'dsa' | gen_privatekey}}")
    r = t.render()
    assert r.splitlines()[0] == "-----BEGIN DSA PRIVATE KEY-----"
    assert r.splitlines()[-1] == "-----END DSA PRIVATE KEY-----"


def test_gen_ecdsa(jinja_env):
    t = jinja_env.from_string("{{'ecdsa' | gen_privatekey}}")
    r = t.render()
    assert r.splitlines()[0] == "-----BEGIN EC PRIVATE KEY-----"
    assert r.splitlines()[-1] == "-----END EC PRIVATE KEY-----"


def test_gen_private_unknow(jinja_env):
    t = jinja_env.from_string("{{'unknown' | gen_privatekey}}")
    with pytest.raises(ValueError):
        assert t.render() == "raise error"


def test_rand_alphanum32(jinja_env):
    import re
    t = jinja_env.from_string("{{'32' | rand_alphanum}}")
    r = t.render()
    assert re.match("^([a-zA-Z0-9]{32})$", r) is not None


def test_rand_alpha32(jinja_env):
    import re
    t = jinja_env.from_string("{{'32' | rand_alpha}}")
    r = t.render()
    assert re.match("^([a-zA-Z]{32})$", r) is not None
