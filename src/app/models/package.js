app.factory('Package', function(KpmApi) {
  // ctor
  function Package(hash) {
    for (var key in hash) {
      this[key] = hash[key];
    }
  }

  return Package;
});
