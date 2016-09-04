app.service('Session', function($rootScope, KpmApi, User) {

  var self = this;

  /**
   * Authenticate user on KPM API
   * @param {string} username: user login
   * @param {string} password: user password
   */
  this.login = function(username, password) {
    KpmApi.post('users/login', {
      user: {
        username: username,
        password: password
      }
    })
    .success(function(data) {
      self.user = new User(data);
      KpmApi.authorization_token = data.token;

      // Broadcast success event
      $rootScope.$broadcast('login_success', data);
    })
    .error(function(data) {
      KpmApi.authorization_token = null;

      // Broadcast failure event
      $rootScope.$broadcast('login_failure', data);
    });
  };

  /**
   * Deauthenticate a connected user
   */
  this.logout = function() {
    KpmApi.delete('users/logout')
    .success(function(data) {
      delete self.user;
      KpmApi.authorization_token = null;

      $rootScope.$broadcast('logout_success', data);
    })
    .error(function(data) {
      $rootScope.$broadcast('logout_failure', data);
    });
  };

  /**
   * Check is user has been authenticated
   * @return {boolean}
   */
  this.isAuthenticated = function() {
    return KpmApi.authorization_token != null;
  };
});
