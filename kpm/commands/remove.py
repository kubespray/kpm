from kpm.commands.deploy import DeployCmd


class RemoveCmd(DeployCmd):
    name = 'remove'
    help_message = "remove a package from kubernetes"

    def _call(self):
        self.status = self.kub().delete(dest=self.tmpdir,
                                        force=self.force,
                                        dry=self.dry_run,
                                        proxy=self.api_proxy,
                                        fmt=self.output)
