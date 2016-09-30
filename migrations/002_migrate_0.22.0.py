#!/usr/bin/env python
import etcd


etcd_client = etcd.Client(port=2379)
ETCD_PREFIX = "kpm/packages/"
NEW_PREFIX = "cnr/packages/"

path = ETCD_PREFIX
r = {}
packages = etcd_client.read(path, recursive=True)


for child in packages.children:
    new_path = child.key.replace(ETCD_PREFIX, NEW_PREFIX)
    if not child.dir:
        etcd_client.write(new_path, child.value)
        print "moved %s to %s" % (child.key, new_path)

print "complete the migration with:  etcdctl rm /kpm --recursive"
