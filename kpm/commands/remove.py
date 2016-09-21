import kpm.platforms.kubernetes
from kpm.commands.deploy import DeployCmd


class RemoveCmd(DeployCmd):
    name = 'remove'
    help_message = "remove a package from kubernetes"

    def _call(self):
        packages = self._packages()
        self.status = kpm.platforms.kubernetes.delete(self.package,
                                                      version=self.version,
                                                      dest=self.tmpdir,
                                                      namespace=self.namespace,
                                                      force=self.force,
                                                      dry=self.dry_run,
                                                      endpoint=self.registry_host,
                                                      proxy=self.api_proxy,
                                                      variables=self.variables,
                                                      shards=self.shards,
                                                      fmt=self.output,
                                                      packages=packages)
