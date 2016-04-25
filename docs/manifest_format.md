## Manifest format

### Manifest
The `manifest.yaml` contains the following keys:

- package: metadata around the package and the packager
- variables: map jinja2 variables to default value
- resources: the list of resources, `file` refers to a filename inside the 'template' directory
- shards: see [shards-doc.md](#shards.md)
- deploy: list the dependencies, a special keyword `$self` indicate to deploy current package.

```yaml
package:
  name: ant31/heapster
  author: "Antoine Legrand <2t.antoine@gmail.com>"
  version: 0.18.2
  description: Kubernetes data
  license: MIT

variables:
  namespace: kube-system
  replicas: 1
  image: "gcr.io/google_containers/heapster:v0.18.2"
  svc_type: "NodePort"

resources:
  - file: heapster-svc.yaml
    name: heapster
    type: svc

  - file: heapster-rc.yaml
    name: heapster
    type: rc

shards: []

deploy:
  - name: $self
```


#### Package

The `package` part let you list the meta-data of the package.
The two important fields are `name` and `version`, others are informative only.

name:
```yaml
package:
# identify the package
# composed of two part: "namespace/name",
# format: "[a-z0-9-_]{3,63}/[a-z0-9-_]{3,63}
  name: example/package1

# Maintainer, no format
  author: Foo Bar <foo.bar@example.com>

# Short description of the package/application
  description: Great application of the organization example

# License of the package
  license: opensourceLiense

# Version of the package
# format: semver 2.0
  version: 1.4.0-alpha.1
```


#### Variables

Default values of your templates lives under `variables`.
Templates are resolved twice then a variable can reference an another variable

```yaml
variables:
	image: registry/myapp-container:v1.4.0-aplha.1
	database_url: db.{{namespace}}.svc.cluster.local    # use variables inside other variable's value
	data_volme:   # can use hash/array too
	  - name: data
	    emptyDir: {medium: ""}

```


#### Resources

The resources list


#### Shards


#### Deploy
