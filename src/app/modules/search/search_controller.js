app.controller('SearchController', function($scope, $state, $q, KpmApi) {

  var self = this;

  /**
   * Callback when 'Return' key is pressed
   * Redirect to the package list page
   */
  this.submit = function() {
    $state.go('packages', {search: this.searchText});
  };

  /**
   * Callback when a suggested item is selected
   * Redirect to the package view page
   */
  this.itemSelected = function(item) {
    $state.go('package', {name: item.name});
  };

  /**
   * Autocomplete suggestion callback
   * @return promise
   */
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
});
