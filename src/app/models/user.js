'use strict';

app.factory('User', function(KpmApi) {
  /**
   * Ctor
   */
  function User(hash) {
    for (var key in hash) {
      this[key] = hash[key];
    }
    this.setGravatarUrl();
  }

  /**
   * Set up gravatar url from user email
   */
  User.prototype.setGravatarUrl = function() {
    if (this.email) {
      var hash = Crypto.MD5(this.email.toLowerCase());
      this.gravatar = 'http://www.gravatar.com/avatar/' + hash;
    }
  };

  return User;
});
