## Create a new package
The command `new` create the directory structure and an example `manifest.yaml`.

```
kpm new namespace/packagename [--with-comments]
```

To get started, some examples are available in the repo https://github.com/kubespray/kpm-packages

#### Directory structure
A package is composed of a `templates` directory and a `manifest.yaml`.
```
.
├── manifest.yaml
└── templates
    ├── heapster-rc.yaml
    └── heapster-svc.yaml
```
Optionaly, it's possible to add a `README.md` and a `LICENSE`.

#### Templates
The `templates` directory contains the kubernetes resources to deploy.
It accepts every kind of resources (rc,secrets,pods,svc...).

Resources can be templated with Jinja2.

-> We recommend to parametrize only values that should be overrided.
Having a very light templated resources improve readability and quickly point to users which values are
important to look at and change. User can use 'patch' to add their custom values.

You can declare the deploy order inside the `manifest.yaml`



#### Manifest
The `manifest.yaml` contains the following keys:

- package: metadata around the package and the packager
- variables: map jinja2 variables to default value
- resources: the list of resources, `file` refers to a filename inside the 'template' directory
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

deploy:
  - name: $self
```


#### Publish

In the root directory of the package execute the command: `kpm push`
It will upload the package to the registry and it's immediatly available for use.

To reupload and overwrite a version it's currently possible to force push: `kpm push -f`
This option to force reupload will probably be restricted in the future.

```
kpm push -f
package: kubespray/kpm-backend (0.4.12) pushed
```
