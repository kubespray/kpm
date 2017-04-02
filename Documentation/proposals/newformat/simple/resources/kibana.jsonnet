// Kibana is a stateless webservice
// At most it will requires:
// 1. configmap to configure it
// 2. secrets for creds ?
// 3. Service for LB (anyType) to 1 ports (let's make it 2)
// 4. a network policy to allow connection to the ES
// 5. an Ingress
// 6. Custom env vars
// 7. A deployment


{
    name: "kibana",
    type: "Deployment",
    exposes: [{port: 5601, type: "NodePort", domain: "kibana.kubespray.com", tls: true},
              {port: 8090, type: "ClusterIP"}],
    configmaps: {
        "kibana-conf": {"kibana.yaml": importstr "kibana-conf.yaml"}
    },
    containers: {self.name:
                 {image: "kibana:5", envs: []}}

}
