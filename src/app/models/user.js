app.factory('User', function(KpmApi) {
  /**
   * Ctor
   */
  function User(hash) {
    for (var key in hash) {
      this[key] = hash[key];
    }
    this.setGravatarUrl();
    this.getPackages();
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

  /**
   * Get packages for user
   */
  User.prototype.getPackages = function() {
    var self = this;
    KpmApi.get('packages/' + this.username)
    .success(function(data) {
      self.packages = data;
    })
    .error(function(data) {
      console.log('[User] cannot get packages');
    });
  };

  return User;
});
