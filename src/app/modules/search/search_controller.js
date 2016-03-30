app.controller('SearchController', function($scope, $state, $q, KpmApi) {

  var self = this;

  this.querySearch = function(search) {
    var deferred = $q.defer();
    KpmApi.get('packages', {
      named_like: search
    })
    .success(function(data) {
      deferred.resolve(data);
    });
    return deferred.promise;
  };

  this.itemSelected = function(item) {
    $state.go('package', {name: item.name});
  };
});
