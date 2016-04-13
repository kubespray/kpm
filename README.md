[![Build Status](https://travis-ci.org/kubespray/kpm.svg?branch=master)](https://travis-ci.org/kubespray/kpm) [![Code Climate](https://codeclimate.com/github/kubespray/kpm/badges/gpa.svg)](https://codeclimate.com/github/kubespray/kpm) [![Coverage Status](https://coveralls.io/repos/github/kubespray/kpm/badge.svg?branch=master)](https://coveralls.io/github/kubespray/kpm?branch=master)


# KPM

KPM is a tool to deploy and manage applications stack on kubernetes.

KPM provides the glue between kubernetes resources (ReplicatSet, DaemonSet, Secrets...). it defines a package has a composition of kubernetes resources and dependencies to other packages.

### Why we built KPM (instead of using Helm) ?

We started the project to manage our production cluster and applications deployments. 
We wanted a simple way to deploy and upgrade a complete applications stack, including databases. Helm was not ready for our usecases.

##### Versionning and rollbacks
Helm uses git repository to store packages, it's complex to perform search and browsing. 
Deploying any previous package version isn't possible yet (https://github.com/helm/helm/issues/199).

--> KPM uses a global registry, packages are immediatly accessible and visible to the community. Versionning is strong and was easy to implement: https://hub.kubespray.io


##### Clustered applications and persistent-storage ! 
We had hard time to operate our persistent services on kuberentes, it was a key motivation to start kpm. 
Helm doesn't address it at all.

  - How to scale database slaves(postgresql/mysql/redis) ? 
  - How to deploy a production-grade elasticsearch/rabbitmq/zookeep/etcd/ clusters on kubernetes? 
It requires stable network identity and a unique storage per pod!

---> KPM creates multiple variation of a single template with simplicity

Creating a 3 nodes rabbitmq cluster is easy:

1. List the resources
2. Add the keyword `sharded: true` to enable unique variation
3. List the shards and define

```
resources:
  - name: rabbitmq
    file: rabbitmq-rc.yaml
    type: replicationcontroller
    sharded: yes

  - name: rabbitmq
    file: rabbitmq-svc.yaml
    type: service
    sharded: yes
    
  # LB to any of the rabbitmq shard
  - name: rabbitmq
    file: rabbitmq-umbrella-svc.yaml
    type: service

shards:
  - name: hare
    variables:
      data_volume: {name: data, persistentVolumeClaim: {claimName: claim-hare}}
  - name: bunny
    variables:
      data_volume:  {name: data, persistentVolumeClaim: {claimName: claim-bunny}}
  - name: rabbit-on-ram
    variables:
       data_volume: {name: data, emptyDir: ""}
       args: [--ram]
```
Demo: 
[![asciicast](https://asciinema.org/a/2ktj7kr2d2m3w25xrpz7mjkbu.png)](https://asciinema.org/a/2ktj7kr2d2m3w25xrpz7mjkbu?speed=2)


##### Helm is a client-side tool
KPM is an api with an command line interface, it's major difference in terms of design and possible integration. 
Helm is performing all actions client-side, integration to third-party software isn't easy.

--> We wanted a tool that could be integrated anywhere, for that KPM is building the package server side.
Clients are brainless and easy to implements. As a POC we integrated KPM to a fork of https://github.com/kubernetes/dashboard in less than a day: 
https://youtu.be/7SJ6p38W-WM


##### Patch vs Templates
Helm, KPM and many others are using templates/parametrization. 
KPM added the concept of patch for packages. 
Templates are a good way to improve reusabilty but it's not enough. Often the values we want to edit aren't parametrized. In such case, the only option with Helm is to fork the package and maintain its own version of it. 

--> To use and reuse directly 'upstream' packages: KPM can apply a [json-patch](https://tools.ietf.org/html/rfc6902) to the resource with its own personnal requirements.

To add an environment variable that was not included in the original package:

```
deploy: 
 - name: rabbitmq/rabbitmq
    resources:
      - file: rabbitmq-rc.yaml
        patch: 
        - op: add,
          path: "/spec/template/spec/containers/0/env/-"
          value: {name: RABBITMQ_DEFAULT_VHOST, value: logs}
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

### List packages

- All packages: `kpm list`
- Filter by user: `kpm -u username`

The website [https://kpm.kubespray.io](https://kpm.kubespray.io) has more advanced search and browsing featutres than the CLI.

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

 
