import kpm
from appr.commands.version import VersionCmd as ApprVersionCmd


class VersionCmd(ApprVersionCmd):

    def _cli_version(self):
        return kpm.__version__
