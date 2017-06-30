function(commandline_vars)

{
  stream_name: "kinesis",
  image: "quay.io/ant31/logstash:5.2.2",
  elasticsearch_hosts: '"elasticsearch.%s.svc.cluster.local:9200"' % self.namespace,
  logstash_conf_volume: {
    name: "logstashconf",
    configMap: {
      name: "logstash",
    },
  },
} + commandline_vars