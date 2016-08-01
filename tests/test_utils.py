import pytest
import kpm.utils
import os.path


def test_mkdirp_on_existing_dir(tmpdir):
    exists = str(tmpdir.mkdir("dir1"))
    kpm.utils.mkdir_p(exists)
    assert os.path.exists(exists)


def test_mkdirp(tmpdir):
    path = os.path.join(str(tmpdir), "new/directory/tocreate")
    kpm.utils.mkdir_p(path)
    assert os.path.exists(path)


def test_mkdirp_unauthorized(tmpdir):
    import os
    d = str(tmpdir.mkdir("dir2"))
    path = os.path.join(d, "directory/tocreate")
    os.chmod(d, 0)
    with pytest.raises(OSError):
        kpm.utils.mkdir_p(path)


def test_colorize():
    assert kpm.utils.colorize('ok') == "\x1b[32mok\x1b[0m"


def test_parse_cmdline_variables():
    l = ["titi=tata"]
    assert {"titi": "tata"} == kpm.utils.parse_cmdline_variables(l)


def test_parse_cmdline_variables_comma():
    l = ["titi=tata,lola=popa"]
    assert {"titi": "tata", "lola": "popa"} == kpm.utils.parse_cmdline_variables(l)


def test_parse_cmdline_variables_multi():
    l = ["titi=tata,lola=popa", "mami=papi"]
    assert {"titi": "tata",
            "lola": "popa",
            "mami": "papi"} == kpm.utils.parse_cmdline_variables(l)


def test_parse_cmdline_variables_multi_overwrite():
    l = ["titi=tata,lola=popa", "titi=papi"]
    assert {"titi": "papi", "lola": "popa"} == kpm.utils.parse_cmdline_variables(l)


def test_parse_cmdline_variables_bad():
    l = ["titi=tata,lola=popa", "titipapi"]
    with pytest.raises(ValueError):
        assert {"titi": "papi", "lola": "popa"} == kpm.utils.parse_cmdline_variables(l)


def test_parse_cmdline_variables_json():
    l = ['{"titi": ["tata", "lola"]}']
    assert {"titi": ["tata", "lola"]} == kpm.utils.parse_cmdline_variables(l)


def test_parse_cmdline_variables_mixjson():
    l = ['{"titi": ["tata", "lola"]}', "test=test2"]
    assert {"titi": ["tata", "lola"], "test": "test2"} == kpm.utils.parse_cmdline_variables(l)


def test_convert_utf8():
    data = {u"test": {u"test2": u"test3"},
            u"array": [u"a1", u"a2"], u"int": 5}
    assert {"test": {"test2": "test3"},
            "array": ["a1", "a2"], "int": 5} == kpm.utils.convert_utf8(data)
