local kpm = import "kpm.libjsonnet";

function(
  params={}
)

kpm.package({
  package: {
    name: "ant31/wordpress",
    expander: "jinja2",
    format: 'docker-compose',
    author: "Antoine Legrand",
    version: "0.1.0",
    description: "wordpress",
    license: "Apache 2.0",
  },

  variables: {
    db: {
      image: "mysql:5.7",
      mount_volume: "/tmp/wordpress/data/db",
      restart_policy: "always",
      dbname: "wordpress",
      root_password: "wordpress",
      user: "wordpress",
      password: "wordpress",
      },

      wordpress: {
        image: "wordpress:latest",
        port: 30206,
        restart_policy: "always",
        },
      },

  resources: [
    {
      file: "docker-compose.yml",
      template: (importstr "templates/compose-wordpress.yaml"),
      name: "compose-wordpress",
      type: "docker-compose",
    },
  ],

  deploy: [
    {
      name: "$self",
    },
  ]
}, params)
