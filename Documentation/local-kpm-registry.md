## Running a local registry

You may want to run a kpm registry locally, and then deploy your kpm registry to k8s from this "bootstrapping registry" if-you-will.

## Run local registry with filesystem backend

You can run a local registry simply with the local filesystem backend using the `run-server.sh` script.

```
$ PORT=5000 DATABASE_URL="$HOME/.kpm/packages"  STORAGE=filesystem ./run-server.sh
```

## Run local registry with default etcd backend

If you're using the default backend, etcd needs be present:

```
$ docker run --name tempetcd -dt -p 2379:2379 -p 2380:2380 quay.io/coreos/etcd:v3.0.6 /usr/local/bin/etcd -listen-client-urls http://0.0.0.0:2379,http://0.0.0.0:4001 -advertise-client-urls http://$127.0.0.1:2379,http://127.0.0.1:4001
```

And with etcd in place, you can now run the registry API server with gunicorn, a la:

```
$ pwd
/usr/src
$ gunicorn kpm.api.wsgi:app -b :5555
```

And then you can push the kpm-registry packages. Double check the image tag in the `manifest.jsonnet` to make sure it's a tag available from the Docker registry.

## Pushing kpm-registry packages and etcd dependency

```
$ pwd
/usr/src/kpm/deploy/kpm-registry
$ kpm push -H http://localhost:5555 -f
package: coreos/kpm-registry (0.21.2-4) pushed
```

Can we it deploy kpm-registry now? Not quite... We also have to push the `coreos/etcd` package to our bootstrapping registry. And I found the manifest for it in the `kubespray/kpm-packages` repo.

```
$ cd /usr/src/
$ git clone https://github.com/kubespray/kpm-packages.git
$ cd kpm-packages/
$ cd coreos/etcdv3
$ pwd
/usr/src/kpm-packages/coreos/etcdv3
$ kpm push -H http://localhost:5555 -f
$ kpm list -H http://localhost:5555
app                  version    downloads
-------------------  ---------  -----------
coreos/etcd          3.0.6-1    -
coreos/kpm-registry  0.21.2-4   -
```

Now you should be able to deploy a kpm registry from the bootstrapping registry via:

```
$ kpm deploy coreos/kpm-registry --namespace kpm -H http://localhost:5555
create coreos/kpm-registry 

 01 - coreos/etcd:
 --> kpm (namespace): created
 --> etcd-kpm-1 (deployment): created
 --> etcd-kpm-2 (deployment): created
 --> etcd-kpm-3 (deployment): created
 --> etcd-kpm-1 (service): created
 --> etcd-kpm-2 (service): created
 --> etcd-kpm-3 (service): created
 --> etcd (service): created

 02 - coreos/kpm-registry:
 --> kpm (namespace): ok
 --> kpm-registry (deployment): created
 --> kpm-registry (service): created

```

Voila! Now you can tear down the bootstrapping registry if you'd like, e.g. stop the docker container and the API server as run by gunicorn.