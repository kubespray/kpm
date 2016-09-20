app.factory('Package', function(KpmApi) {
  // ctor
  function Package(hash) {
    for (var key in hash) {
      this[key] = hash[key];
    }

    // Split name => organization/app
    var index = this.name.indexOf('/');
    this.organization = this.name.substr(0, index);
    this.appname = this.name.substr(index + 1);

    // Set up dummy icon
    this.icon_url = 'http://lorempixel.com/100/100/cats';
  }

  return Package;
});
