local kpm = import "kpm.libjsonnet";

function(
  params={}
)

  kpm.package({
    package: {
      name: "coreos/kpm-registry",
      expander: "jinja2",
      author: "Antoine Legrand",
      version: "0.23.1-1",
      description: "kpm-registry",
      license: "Apache 2.0",
    },

    variables: {
      etcd_cluster_size: 3,
      namespace: 'default',
      image: "quay.io/kubespray/kpm:v0.23.1-1",
      image_etcd: "quay.io/coreos/etcd:v3.0.12",
      kpm_uri: "http://kpm-registry.%s.svc.cluster.local" % $.variables.namespace,
      initial_cluster: "etcd=http://etcd.%s.svc.cluster.local:2380" % $.variables.namespace,
      svc_type: "LoadBalancer",
      etcd_volumes: "emptydir",
    },

    resources: [
      {
        file: "kpm-registry-dp.yaml",
        template: (importstr "templates/kpm-registry-dp.yaml"),
        name: "kpm-registry",
        type: "deployment",
      },

      {
        file: "kpm-registry-svc.yaml",
        template: (importstr "templates/kpm-registry-svc.yaml"),
        name: "kpm-registry",
        type: "service",
      }
      ],


    deploy: [
      if $.variables.etcd_volumes == "pvc" then
        {
          name: "base/persistent-volume-claims",
          shards: [{ name: "kpm-%s" % i } for i in std.range(1, $.variables.etcd_cluster_size)],
          variables: {
            storage_class: $.variables.storage_class
              }
        },
      {
        name: "coreos/etcd",

        shards: {
          etcd: [{ name: "kpm-%s" % x,
                   variables: if $.variables.etcd_volumes == "pvc" then
            {
              data_volumes: [{ name: "varetcd", persistentVolumeClaim: {
                claimName: "pvc-kpm-%s" % x } }],
            } else {},
          } for x in std.range(1, $.variables.etcd_cluster_size)],
        },
        variables:
          {
            image: $.variables.image_etcd,
          },
      },
      {
        name: "$self",
      },
    ],


  }, params)
