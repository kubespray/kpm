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
