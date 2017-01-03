### Channels

##### List Channels for a package
```
$ kpm channel ant31/rocketchat
name   releases current       default
stable 4        v1.2.0        -
prod   2        v1.1.0        -
beta   6        v1.4.0-beta.2 yes
```

```
$ kpm channel ant31/rocketchat -n stable
version  date       digest
1.0.0  2016-08-02 h324052fds
1.1.0  2016-08-01 zs32t45l23
```
##### Create a new channel
```
$ kpm channel ant31/rocketchat -n beta --create
# alt:
$ kpm push ant31/rocketchat:stable
$ kpm push kpm.sh/ant31/rocketchat  --channel stable
$ kpm delete-package kpm.sh/ant31/rocketchat:stable
$ kpm channel --delete kpm.sh/ant31/rocketchat:stable

```
##### Add/Remove releases
```
kpm channel ant31/rocketchat -n beta --add v1.3.0
kpm channel ant31/rocketchat -n beta --remove v1.0.0
```

### Deploy
###### default channel, default release
`$ kpm deploy ant31/rocketchat`

###### default channel, select release
`$ kpm deploy ant31/rocketchat@v1.1.0`

###### Use directly the digest
`$ kpm deploy ant31/rocketchat@sha256:0ecb2ad60`

###### stable channel, default release
`$ kpm deploy ant31/rocketchat:stable`

###### stable channel, select release
`$ kpm deploy ant31/rocketchat@v1.1.0 --in-channel stable`

###### stable channel, release not in the channel
```
$ kpm deploy ant31/rocketchat@v1.4.0-beta.2 --in-channel stable
--> Error v1.4.0-beta.2 doesn't exist in chan stable
```

### Push
##### Push a new release
```
kpm push ant31/rocketchat@v1.1.0 [--channels stable,prod,beta]
--> New release v1.1.0 pushed
--> Added to channels stable, prod and beta
```

##### Push an existing release
```
kpm push ant31/rocketchat@v1.1.0
--> Error the release v1.1.0 already exist,  use --force
```
