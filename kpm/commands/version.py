import kpm
from cnrclient.commands.version import VersionCmd as CnrVersionCmd


class VersionCmd(CnrVersionCmd):
    def _cli_version(self):
        return kpm.__version__
