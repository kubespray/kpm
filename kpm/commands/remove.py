import kpm.platforms.kubernetes
from kpm.dockercompose import DockerCompose
from kpm.commands.deploy import DeployCmd
from kpm.formats.kubcompose import KubCompose


class RemoveCmd(DeployCmd):
    name = 'remove'
    help_message = "remove a package from kubernetes"

    def _remove_dockercompose(self):
        if self.format == "kpm":
            k = KubCompose(self.package,
                           endpoint=self.registry_host,
                           variables=self.variables,
                           namespace=self.namespace,
                           shards=self.shards,
                           version=self.version)
            self.status = DockerCompose(k).delete()

    def _remove_kubernetes(self):
        if self.format == "kpm":
            packages = self._k8s_packages()

        elif self.format == "docker-compose":
            k = KubCompose(self.package,
                           endpoint=self.registry_host,
                           variables=self.variables,
                           namespace=self.namespace,
                           shards=self.shards,
                           version=self.version)
            packages = k.convert_to_kub().build()

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

    def _call(self):
        if self.target == "kubernetes":
            self._remove_kubernetes()

        elif self.target == "docker-compose":
            self._remove_dockercompose()
