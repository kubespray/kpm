app.service('KpmApi', function($http) {

  this.get = function(target, params) {
    // GET requests don't support JSON payload
    return this.perform('GET', target, {
      params: angular.copy(params),
      paramSerializer: '$httpParamSerializerJQLike'
    });
  };

  this.post = function(target, params) {
    return this.perform('POST', target, {data: params});
  };

  this.put = function(target, params) {
    return this.perform('PUT', target, {data: params});
  };

  this.delete = function(target) {
    return this.perform('DELETE', target, {});
  };

  this.perform = function(method, target, config) {
    config.url = Config.backend_url + '/' + target + '.json';
    config.method = method;

    /*
      config.headers =  {
        'Authorization': this.authorization_token
      }
    */
    return $http(config);
  };
});
