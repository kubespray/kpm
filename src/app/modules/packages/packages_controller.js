app.controller('PackagesController', function($scope, $stateParams, KpmApi) {

  var package_name = $stateParams.name;
  if (package_name) {
    $scope.ui.loading = true;
    KpmApi.get('packages/' + package_name)
    .success(function(data) {
      $scope.ui.loading = false;
      $scope.package = data;
    })
    .error(function(data) {
      $scope.ui.loading = false;
      $scope.error = 'Package ' + package_name + ' not found';
    });
  }
  else {
    $scope.loading = true;
    KpmApi.get('packages')
    .success(function(data) {
      $scope.ui.loading = false;
      $scope.packages = data;
    })
    .error(function(data) {
      $scope.ui.loading = false;
    });
  }

  $scope.toggleResource = function(resource) {
    if (resource.content) {
      delete resource.content;
    }
    else {
      KpmApi.get('packages/' + $scope.package.name + '/file/templates/' + resource.file)
      .success(function(data) {
        resource.content = data;
      });
    }
  };
});
