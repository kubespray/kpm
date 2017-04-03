class ManifestBase(dict):

    def __init__(self):
        super(ManifestBase, self).__init__()

    @property
    def resources(self):
        return self.get("resources", [])

    @property
    def deploy(self):
        return self.get("deploy", [])

    @property
    def dependencies(self):
        return [x['name'] for x in self.deploy if x['name'] != "$self"]

    @property
    def variables(self):
        return self.get("variables", {})

    @property
    def package(self):
        return self.get("package", {})

    @property
    def shards(self):
        return self.get("shards", [])

    def kubname(self):
        spl = self.package['name'].split('/')
        name = "%s_%s" % (spl[0], spl[1])
        return name

    def package_name(self):
        package = ("%s_%s" % (self.kubname(), self.package['version']))
        return package

    def to_dict(self):
        return ({
            "package": self.package,
            "variables": self.variables,
            "resources": self.resources,
            "shards": self.shards,
            "deploy": self.deploy
        })

    def metadata(self):
        return {
            'variables': self.variables,
            'resources': self.resources,
            "shards": self.shards,
            'dependencies': self.dependencies
        }
