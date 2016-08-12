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
