'use strict';

app.service('Session', function($rootScope, $cookies, $state, KpmApi, User) {

  var self = this;

  /**
   * Authenticate user on KPM API from token
   */
  this.connectFromCookie = function() {
    var token = $cookies.get('authentication_token');
    if (token) {
      console.log('[Session] token ' + token + ' found in cookie, checking status...');
      KpmApi.authentication_token = token;

      KpmApi.get('account/status')
      .success(function(data) {
        console.log('[Session] token is valid, logged as ' + data.username);
        self.user = new User(data);
      })
      .error(function(data) {
        delete KpmApi.authentication_token;
        console.log('[Session] Token rejected.');
      });
    }
  };

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
      KpmApi.authentication_token = data.token;

      $cookies.put('authentication_token', data.token);

      // Broadcast success event
      $rootScope.$broadcast('login_success', data);
    })
    .error(function(data) {
      delete KpmApi.authentication_token;

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
      delete KpmApi.authentication_token;

      $cookies.remove('authentication_token');
      $state.go('home');
    })
    .error(function(data) {
    });
  };

  /**
   * Check is user has been authenticated
   * @return {boolean}
   */
  this.isAuthenticated = function() {
    return KpmApi.authentication_token != null;
  };

  this.isCurrent = function(token) {
    return KpmApi.authentication_token === token.authentication_token;
  };
});
