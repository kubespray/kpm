## Hacking on the registry

1. Install etcd from a [recent release](https://github.com/coreos/etcd) and simply run `etcd` with no arguments.
2. Move into a checkout of kpm `git clone https://github.com/coreos/kpm.git && cd kpm`
2. Install python requirements for KPM `pip install -r requirements_dev.txt`
3. Run the KPM registry on port 5000 `gunicorn kpm.api.wsgi:app -b :5000`
4. Test it out `kpm new foobar/baz; cd foobar/baz; kpm push -H http://localhost:5000`
