from kpm.commands.deploy import DeployCmd


class GenerateCmd(DeployCmd):
    name = 'generate'
    help_message = "Generate a package json"

    def _call(self):
        k = self.kub()
        if k.target == "docker-compose":
            self.output = 'yaml'
        self._generate()

    def _generate(self):
        k = self.kub()
        filename = "%s_%s.tar.gz" % (k.name.replace("/", "_"), k.version)
        with open(filename, 'wb') as f:
            f.write(k.build_tar("."))

    def _render_dict(self):
        return self.kub().build()

    def _render_console(self):
        self._render_json()
