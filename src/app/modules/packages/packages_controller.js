app.controller('PackagesController', function($scope, $stateParams, KpmApi) {

  var package_name = $stateParams.name;
  if (package_name) {
    KpmApi.get('packages/' + package_name)
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
