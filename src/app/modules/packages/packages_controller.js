app.controller('PackagesController', function($scope, $stateParams, KpmApi) {

  var package_id = $stateParams.id;
  if (package_id) {
    KpmApi.get('packages/' + package_id)
    .success(function(data) {
      $scope.package = data;
    });
  }
  else {
    KpmApi.get('packages')
    .success(function(data) {
      $scope.packages = data;
    });
  }
});
