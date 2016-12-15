import base64
import gzip
import hashlib
import logging
import tarfile
import glob
import io
import os
import fnmatch

__all__ = ['pack_kub', 'unpack_kub', 'Package', "authorized_files"]

logger = logging.getLogger(__name__)

# 1. download the package
# 2. untar it to dest directory with the packagename_version/
# 3. open and read manifest.yaml
# 4. interate on deploy and download if not present (packagename_version/deps/deppackagename_version.kub) and extract
#    the packages to packagename_version/deps/deppackagename_version/.
# 5. interate on deploy and load manifest.yml of all packages
# 6. foreach manifest create the files to packagename_version/resources
# 7. foreach manifest check if resources exists are create it
#
#
#
AUTHORIZED_FILES = ["*.libjsonnet",
                    "*.jsonnet",
                    "*.yaml",
                    "README.md",
                    "LICENSE",
                    "AUTHORS",
                    "NOTICE",
                    "manifests",
                    "deps/*.kub"]


AUTHORIZED_TEMPLATES = ["*.yaml",
                        "*.jsonnet",
                        "*.libjsonnet",
                        "*.yml",
                        "*.j2"]


def authorized_files():
    files = []
    for name in AUTHORIZED_FILES:
        for f in glob.glob(name):
            files.append(f)
    for root, _, filenames in os.walk('templates'):
        for name in AUTHORIZED_TEMPLATES:
            for filename in fnmatch.filter(filenames, name):
                files.append(os.path.join(root, filename))
    return files


def all_files():
    files = []
    for root, _, filenames in os.walk('.'):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


def pack_kub(kub, filter_files=True, prefix=None):
    tar = tarfile.open(kub, "w:gz")
    if filter_files:
        files = authorized_files()
    else:
        files = all_files()
    for filepath in files:
        arcname = None
        if prefix:
            arcname = os.path.join(prefix, filepath.replace("./", ""))
        tar.add(filepath, arcname=arcname)

    tar.close()


def unpack_kub(kub, dest="."):
    tar = tarfile.open(kub, "r:gz")
    tar.extractall(dest)
    tar.close()


class Package(object):
    def __init__(self, blob=None, b64_encoded=True):
        self.files = {}
        self.tar = None
        self.blob = None
        self.io_file = None
        self._digest = None
        self.b64blob = None
        if blob is not None:
            self.load(blob, b64_encoded)

    def _load_blob(self, blob, b64_encoded):
        if b64_encoded:
            self.b64blob = blob
            self.blob = base64.b64decode(blob)
        else:
            self.b64blob = base64.b64encode(blob)
            self.blob = blob

    def load(self, blob, b64_encoded=True):
        self._digest = None
        self._load_blob(blob, b64_encoded)
        self.io_file = io.BytesIO(self.blob)
        self.tar = tarfile.open(fileobj=self.io_file, mode='r:gz')
        for m in self.tar.getmembers():
            tf = self.tar.extractfile(m)
            if tf is not None:
                self.files[tf.name] = tf.read()

    def extract(self, dest):
        self.tar.extractall(dest)

    def pack(self, dest):
        f = open(dest, "wb")
        f.write(self.blob)
        f.close()

    def tree(self, directory=None):
        files = self.files.keys()
        files.sort()
        if directory is not None:
            filtered = [x for x in files if x.startswith(directory)]
        else:
            filtered = files
        return filtered

    def file(self, filename):
        return self.files[filename]

    def isjsonnet(self):
        if "manifest.yaml" in self.files:
            return False
        elif "manifest.jsonnet" in self.files:
            return True
        else:
            raise RuntimeError("Unknown manifest format")

    @property
    def manifest(self):
        if "manifest.yaml" in self.files:
            return self.files['manifest.yaml']
        elif "manifest.jsonnet" in self.files:
            return self.files['manifest.jsonnet']
        else:
            raise RuntimeError("Unknown manifest format")

    @property
    def digest(self):
        if self._digest is None:
            self.io_file.seek(0)
            gunzip = gzip.GzipFile(fileobj=self.io_file, mode='r').read()
            self._digest = hashlib.sha256(gunzip).hexdigest()
        return self._digest
