local kubecfg = import "kubecfg.libsonnet";
local opencompose = kubecfg.opencompose;


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
    resources: opencompose.createServices()

    } + {'deployment.json'+: addSideCar())

    }
}, params)







