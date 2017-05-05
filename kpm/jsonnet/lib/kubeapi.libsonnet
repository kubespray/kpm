local core = import "core.libsonnet";
local kubeUtil = import "util.libsonnet";
local kpm = import "kpm.libsonnet";

local utils = {
    resource: {
      getName(obj)::
        obj['metadata']['name'],
      getLabels(obj)::
        obj['metadata']['labels'],
      setNamespace(namespace)::
       { metadata+: {namespace: namespace } },
      setName(name)::
       { metadata+: {name: name} },
    },

    expanders: {
        jinja2:: kpm.jinja2,
        jsonnet:: kpm.jsonnet,
    },

} + kpm;

local portUtils = {
    portName(port):: "port-%s" % port,
    containerPorts(ports)::
        [core.v1.port.container.Named(self.portName(port), port) for port in ports],
    servicePorts(ports)::
        [core.v1.port.service.Named(self.portName(port), port, port) for port in ports],
};

local configMapUtil = {
    Create(name, data={})::
        self.Name(name) +
        self.mergeData(data),
    New(name)::
        core.v1.configMap.Default("default", name, data={}),
    mergeData(data)::
          {data+: data}
};

local serviceUtil = {
    Create(name, ports=[], selector=null, type="ClusterIP"):: (
      local local_selector =
        if selector == null then
            {app: name}
        else
            selector;
      self.New(name) +
      self.setType(type) +
      self.setSelector(local_selector) +
      self.setPorts(ports)),
    New(name)::
      core.v1.service.Default(name, [],),
    setType(type)::
      core.v1.service.mixin.spec.Type(type),
    setSelector(obj)::
      core.v1.service.mixin.spec.Selector(obj),
    _ports(ports):: [
       if std.type(port) == "number" then
        core.v1.port.service.Named(portUtils.portName(port), port, port)
       else
        core.v1.port.service.Named(
         if std.objectHas(port, 'name') then port.name else portUtils.portName(port.port),
         port.port,
         if std.objectHas(port, 'targetPort') then port.targetPort else port.port)
        for port in ports
       ],
    setPorts(ports):: {spec+: {ports: serviceUtil._ports(ports)}},
    mergePorts(ports):: {spec+: {ports+: serviceUtil._ports(ports)}},

};

// This is CRAZY imports
local k8s_resources = {
    deployment: core.extensions.v1beta1.deployment + kubeUtil.app.v1beta1.deployment, // Join util by default
    container: core.v1.container, // get ride of the v1
    claim: core.v1.volume.claim,
    probe: core.v1.probe,
    pod: core.v1.pod + kubeUtil.app.v1.pod,
    port: core.v1.port + kubeUtil.app.v1.port + portUtils,
    service: core.v1.service + serviceUtil,
    secret: core.v1.secret,
    metadata: core.v1.metadata,
    persistent: core.v1.volume.persistent,
    volume: core.v1.volume,
    configMap: core.v1.configMap + configMapUtil,
    mount: core.v1.volume.mount,
};
local render_utils = {
   setResource(res, params):: (
     local resource =
        if std.objectHas(res, 'content') == false then
           {content: res} else res;
     resource['content'] +
     utils.resource.setNamespace(params.variables.namespace) +
     if std.objectHas(resource, 'name') then
        utils.resource.setName(resource['name']) else {} ),


   createList(app, params):: {
         apiVersion: "v1",
         kind: "List",
         items: [render_utils.setResource(resource, params)
                 for resource in utils.objectValues(app.resources)]
  },
};

local render(app, params) = (
    if std.objectHas(params.variables, 'action') && params.variables.action == "generate" then
      render_utils.createList(app, params)
    else
      app
);

{
    utils: utils,
    k8s: k8s_resources,
    render:: render,
}
