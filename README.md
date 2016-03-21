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

kpm uses `kubectl` to communicate with the kubernetes cluster.

```bash
$ kubectl version
Client Version: version.Info{Major:"1", Minor:"1", GitVersion:"v1.1.4", GitCommit:"a5949fea3a91d6a50f40a5684e05879080a4c61d", GitTreeState:"clean"}
Server Version: version.Info{Major:"1", Minor:"1", GitVersion:"v1.1.4", GitCommit:"a5949fea3a91d6a50f40a5684e05879080a4c61d", GitTreeState:"clean"}

```

### Customize an existing package
 1. Create a new package
 2. Edit manifest
 3. Change variables
 4. Patch custom metric
5. Upload package
 6.  login
 7.  push
 8.Test

## Account registration
### Signup
### Login/Logout

## Search and deploy a package
### List a user package
#### Show/Pull
### deploy

## Create a new package
#### Directory structure
#### Manifest
#### Templates
#### Publish

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
