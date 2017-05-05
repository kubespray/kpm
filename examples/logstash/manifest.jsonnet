local kubeapi = import "kubeapi.libsonnet";

function(
  params={},
)

kubeapi.render({
    local application = self,
    // metadata import
    package: import "Chart.jsonnet",
    // default parametrized values
    variables: (import "values.jsonnet")(params.variables),
    // resources to deploy
    resources: {
      "logstash-svc.json": kubeapi.k8s.service.Create(name="logstash", ports=[5044]),
      "logstash-configmap.json": (import "templates/logstash-configmap.jsonnet")(application.variables),
    }
}, params)







