local kubeapi = import "kubeapi.libsonnet";
local utils = kubeapi.utils;
local k8s = kubeapi.k8s;

function (variables={})
local expandConfig(conf) = utils.expanders.jinja2(conf, variables);

local data = utils.objectMap(expandConfig, {
        "001-input-kinesis-stream.cfg":
                importstr "config/001-input-kinesis-stream.cfg",
        "100-output-elasticsearch.cfg":
                importstr "config/100-output-elasticsearch.cfg",
        "010-filter-quay-plain.cfg":
                importstr "config/010-filter-quay-plain.cfg",
});

k8s.configMap.New("logstash-indexer") +
k8s.configMap.mergeData(data)

