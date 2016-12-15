from kpm.commands.push import PushCmd
from kpm.commands.pull import PullCmd
from kpm.commands.version import VersionCmd
from kpm.commands.new import NewCmd
from kpm.commands.show import ShowCmd
from kpm.commands.login import LoginCmd
from kpm.commands.logout import LogoutCmd
from kpm.commands.deploy import DeployCmd
from kpm.commands.channel import ChannelCmd
from kpm.commands.list_package import ListPackageCmd
from kpm.commands.remove import RemoveCmd
from kpm.commands.delete_package import DeletePackageCmd
from kpm.commands.kexec import ExecCmd
from kpm.commands.generate import GenerateCmd
from kpm.commands.jsonnet import JsonnetCmd


all_commands = {
    PushCmd.name: PushCmd,
    VersionCmd.name: VersionCmd,
    PullCmd.name: PullCmd,
    NewCmd.name: NewCmd,
    ShowCmd.name: ShowCmd,
    LoginCmd.name: LoginCmd,
    LogoutCmd.name: LogoutCmd,
    DeployCmd.name: DeployCmd,
    ChannelCmd.name: ChannelCmd,
    DeletePackageCmd.name: DeletePackageCmd,
    ListPackageCmd.name: ListPackageCmd,
    RemoveCmd.name: RemoveCmd,
    ExecCmd.name: ExecCmd,
    JsonnetCmd.name: JsonnetCmd,
    GenerateCmd.name: GenerateCmd,
}
