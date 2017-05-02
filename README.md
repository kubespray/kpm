## <img src="Documentation/achtung.png" alt="WARNING" width="30" height="30"><img src="Documentation/achtung.png" alt="WARNING" width="30" height="30"><img src="Documentation/achtung.png" alt="WARNING" width="30" height="30"> Deprecation warning <img src="Documentation/achtung.png" alt="WARNING" width="30" height="30"><img src="Documentation/achtung.png" alt="WARNING" width="30" height="30"><img src="Documentation/achtung.png" alt="WARNING" width="30" height="30"><a name="deprecation-warning"></a>
kpm is no longer developed or maintained by CoreOS.

[![Build Status](https://travis-ci.org/coreos/kpm.svg?branch=master)](https://travis-ci.org/coreos/kpm)

if you have any question you can **chat** with us  [![SlackStatus](https://slack.kubespray.io/badge.svg)](https://kubespray.slack.com)

# KPM

KPM is a tool to deploy and manage application stacks on kubernetes.

KPM provides the glue between kubernetes resources (ReplicaSet, DaemonSet, Secrets...). It defines a package as a composition of kubernetes resources and dependencies to other packages.

##### Versioning and rollbacks

KPM uses a global registry, packages are immediately accessible and visible to the community. Versioning is strong and was easy to implement: https://cnr.kubespray.com


##### Clustered applications and persistent-storage !

  - How to scale database slaves(postgresql/mysql/redis) ?
  - How to deploy a production-grade elasticsearch/rabbitmq/zookeep/etcd/ clusters on kubernetes?
It requires stable network identity and a unique storage per pod!

---> KPM creates multiple variation of a single template with simplicity

Creating a 3 node rabbitmq cluster is easy:

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


##### Server-side
KPM is an API with an command line interface, its major difference in terms of design and possible integration.

--> We wanted a tool that could be integrated anywhere, for that KPM is building the package server side.
Clients are brainless and easy to implement. As a POC we integrated KPM to a fork of https://github.com/kubernetes/dashboard in less than a day:
https://youtu.be/7SJ6p38W-WM


## Install kpm

##### From Pypi

kpm is a python2 package and available on pypi
```
$ sudo pip install kpm -U
````

##### From git

```
git clone https://github.com/coreos/kpm.git kpm-cli
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
