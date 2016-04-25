[![Build Status](https://travis-ci.org/kubespray/kpm.svg?branch=master)](https://travis-ci.org/kubespray/kpm) [![Code Climate](https://codeclimate.com/github/kubespray/kpm/badges/gpa.svg)](https://codeclimate.com/github/kubespray/kpm) [![Coverage Status](https://coveralls.io/repos/github/kubespray/kpm/badge.svg?branch=master)](https://coveralls.io/github/kubespray/kpm?branch=master)


# KPM

KPM is a tool to deploy and manage applications stack on kubernetes.

KPM provides the glue between kubernetes resources (ReplicatSet, DaemonSet, Secrets...). it defines a package has a composition of kubernetes resources and dependencies to other packages.

## Key concepts

### Simplicity

Keep it simple for both users and packagers.

### Declarative and idempotent

Declare what should be deployed and let the system apply only required changes.

### Reproducible deployment

For production and QA, control of each components is fundamental.
Both, dependency declaration and version control in KPM allows to have a predictable application stack deployment.

### Dependencies management

To propose 'ready-to-deploy' applications, the 'packager' can set a dependency list.

### Patch/Paramaterization

KPM encourages to use and reuse directly the 'upstream' package of a component and adapt it to its own requirement:
- <b>Templates:</b> quickly replace values in a resource via jinja2 templates.
- <b>Patch:</b>  While template is good, it's not enough. Sometime the value to be edited is not parametrized. In such case, KPM proposes to apply a 'patch' on the resource

### Packages Hub
Quickly compose an application by searching and pick existing components from a registry.

## Quick start

### Deploy application

In this example we will deploy [rocket.chat](https://github.com/RocketChat/Rocket.Chat) an opensource webchat platform:

```
$ pip install kpm
$ kpm deploy ant31/rocketchat --namespace rocket-chat
-> Deploying ant31/rocketchat
 app               version type  name         namespace   status
------------------ ------- ---- ------------ ----------- --------
ant31/mongodb       1.0.0   svc  mongodb      rktchat     changed
ant31/mongodb       1.0.0   rc   mongodb      rktchat     changed
ant31/rocketchat    1.2.0   svc  rocketchat   rktchat     changed
ant31/rocketchat    1.2.0   rc   rocketchat   rktchat     changed
```

KPM can be use to deploy complex stack without effort, as an example the following package deploy a logging platform on kubernetes:
The package is composed by:

1. Elasticsearch cluster: 1master/1client/ 2xdata node managed by separated RC
2. RabbitMQ cluster: 2 HA nodes
3. Logstash shipper: A daemonset to start a logstash agents on all nodes and ship logs to RabbitMQ
4. Logstash indexer: Logstash agents to read/process logs from RabbitMQ and store them in Elasticsearch
5. Shipper configmap:  Logstash shipper configuration
6. Indexer configmap: Logstash indexer configuration
7. Kibana: The kibana dashboard to browse the logs

```
kpm deploy ant31/k8s-elk --namespace=kubelog
create ant31/k8s-elk

 01 - ant31/rabbitmq:
 --> kubelog (namespace): created
 --> rabbitmq (service): created
 --> rabbitmq-mgt (service): created
 --> rabbitmq-rabbit (replicationcontroller): created
 --> rabbitmq-bunny (replicationcontroller): created
 --> rabbitmq-rabbit (service): created
 --> rabbitmq-bunny (service): created

 02 - ant31/elasticsearch:
 --> kubelog (namespace): ok
 --> elasticsearch (serviceaccount): created
 --> elasticsearch-discovery (service): created
 --> elasticsearch (service): created
 --> es-client (replicationcontroller): created
 --> es-master (replicationcontroller): created
 --> es-data-2 (replicationcontroller): created
 --> es-data-1 (replicationcontroller): created

 03 - ant31/k8s-elk:
 --> kubelog (namespace): ok
 --> elk-shipper (configmap): created
 --> elk-indexer (configmap): created

 04 - ant31/kube-logstash:
 --> kubelog (namespace): ok
 --> kube-logstash (configmap): created
 --> kube-logstash (daemonset): created

 05 - ant31/logstash:
 --> kubelog (namespace): ok
 --> logstash-indexer (configmap): created
 --> logstash-indexer (replicationcontroller): created

 06 - ant31/kibana:
 --> kubelog (namespace): ok
 --> kibana (replicationcontroller): created
 --> kibana (service): created
```

## Install kpm

##### From Pypi

kpm is a python2 package and available on pypi
```
$ sudo pip install kpm -U
````

##### From git

```
git clone https://github.com/kubespray/kpm.git kpm-cli
cd kpm-cli
sudo make install
```

### Configuration

KPM uses `kubectl` to communicate with the kubernetes cluster.
Check if the cluster is accessible:
```bash
$ kubectl version
Client Version: version.Info{Major:"1", Minor:"1", GitVersion:"v1.1.4", GitCommit:"a5949fea3a91d6a50f40a5684e05879080a4c61d", GitTreeState:"clean"}
Server Version: version.Info{Major:"1", Minor:"1", GitVersion:"v1.1.4", GitCommit:"a5949fea3a91d6a50f40a5684e05879080a4c61d", GitTreeState:"clean"}

```

## Account registration
### Signup

1. From a browser: go to [https://kpm.kubespray.io](https://kpm.kubespray.io) and sign-up
2. From the command-line:  `kpm login --signup`

### Login/Logout

The commands are `kpm login` and `kpm logout`.
The login creates a session-token stored in `~/.kpm/auth_token`
It's possible to set user/password as arguments: `kpm login -u $USER -p $PASSWORD`

## Search and deploy a package

The website [https://kpm.kubespray.io](https://kpm.kubespray.io) has more advanced search and browsing featutres than the CLI.


### List packages

- All packages: `kpm list`
- Filter by user: `kpm -u username`

#### Show

To quickly inspect a package, it's possible to use the show command.
By default it prints the `manifest.yaml` inside the selected package.
Option `--tree`, list the files, and `--file FILE` prints any file inside the package.

- `kpm show ant31/rocketchat`
- `kpm show --tree ant31/rocketchat`
- `kpm show --file README.md ant31/rocketchat`

#### Pull

Ti's possible to download and extract any package with the pull command:
```
$ kpm pull ant31/rocketchat
$ tree
.
└── ant31_rocketchat_1.6.2
    ├── manifest.yaml
    ├── README.md
    └── templates
        ├── rocketchat-rc.yml
        └── rocketchat-svc.yml
```

### Deploy an application

`kpm deploy package_name [-v VERSION] [--namespace namespace]`
```
$ kpm deploy ant31/rocketchat --namespace myns
create ant31/rocketchat

package           version    type                   name        namespace    status
----------------  ---------  ---------------------  ----------  -----------  --------
ant31/mongodb     1.0.0      namespace              myns        myns         created
ant31/mongodb     1.0.0      service                mongodb     myns         created
ant31/mongodb     1.0.0      replicationcontroller  mongodb     myns         created
ant31/rocketchat  1.6.2      namespace              myns        myns         ok
ant31/rocketchat  1.6.2      service                rocketchat  myns         created
ant31/rocketchat  1.6.2      replicationcontroller  rocketchat  myns         created
```

It deploys the package and its dependencies.
The command can be executed multiple times, kpm detects changes in resource and apply only the modified ones.

### Uninstall an application

The opposite action to `deploy` is the `remove` command. It performs a delete on all resources created by `deploy`.  It's possible to mark some resources as `protected`.

`Namespace` resources are protected by default.

```
kpm remove ant31/rocketchat --namespace demo
package           version    type                   name        namespace    status
----------------  ---------  ---------------------  ----------  -----------  ---------
ant31/mongodb     1.0.0      namespace              myns        myns         protected
ant31/mongodb     1.0.0      service                mongodb     myns         deleted
ant31/mongodb     1.0.0      replicationcontroller  mongodb     myns         deleted
ant31/rocketchat  1.6.2      namespace              myns        myns         protected
ant31/rocketchat  1.6.2      service                rocketchat  myns         deleted
ant31/rocketchat  1.6.2      replicationcontroller  rocketchat  myns         deleted
```

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

## Compose a package
### Dependency
#### Show manifest
#### variables
#### Patch
#### Shards

## Clustered applications/Shards
### Introduction
### Sharded: yes
### Shard list
