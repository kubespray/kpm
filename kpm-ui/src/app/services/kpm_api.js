app.service('KpmApi', function($http) {

  this.get = function(target, params) {
    return this.perform('GET', target, {
      params: angular.copy(params),
      // Serialize JSON parameters in URL
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
    config.url = Config.backend_url + target;
    config.method = method;

    // Apply Authorization header if token provided
    if (this.authentication_token) {
      config.headers =  {
        'Authorization': this.authentication_token
      }
    }
    return $http(config);
  };
});
