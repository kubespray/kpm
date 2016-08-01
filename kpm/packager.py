import logging
import tarfile
import glob
import io

__all__ = ['pack_kub', 'unpack_kub', 'Package']

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
AUTHORIZED_FILES = ["templates/*.yaml",
                    "templates/*.yml",
                    "templates/*.j2",
                    "templates/*.yaml.j2",
                    "templates/*.yml.j2",
                    "README.md",
                    "manifest.yaml",
                    "LICENSE",
                    "deps/*.kub"]


def pack_kub(kub):
    tar = tarfile.open(kub, "w:gz")
    for name in AUTHORIZED_FILES:
        for f in glob.glob(name):
            tar.add(f)
    tar.close()


def unpack_kub(kub, dest="."):
    tar = tarfile.open(kub, "r:gz")
    tar.extractall(dest)
    tar.close()


class Package(object):
    def __init__(self, blob=None):
        self.files = {}
        self.tar = None
        self.blob = None
        if blob is not None:
            self.load(blob)

    def load(self, blob):
        self.blob = blob
        self.tar = tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz')
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

    @property
    def manifest(self):
        return self.files['manifest.yaml']
