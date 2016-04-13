'use strict';

app.controller('PackageDetailsController', function($scope, $stateParams,
      $mdDialog, KpmApi, Package) {

  // Methods

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

  $scope.downloadTarball = function(ev) {
    var confirm = $mdDialog.prompt()
      .title('Select namespace')
      .textContent('The name of your Kubernetes namespace.')
      .placeholder('namespace')
      .targetEvent(ev)
      .ok('Download')
      .cancel('Cancel');

    $mdDialog.show(confirm).then(function(result) {
      // Trigger download from URL with FileSaver library
      var url = Config.backend_url + 'packages/' + $scope.package.name +
        '/generate?tarball=true&namespace=' + result;
      window.location = url;
    }, function() {
    });
  }

  // Init

  var package_name = $stateParams.name;
  if (package_name) {
    $scope.ui.loading = true;
    KpmApi.get('packages/' + package_name)
    .success(function(data) {
      $scope.ui.loading = false;
      $scope.package = new Package(data);
    })
    .error(function(data) {
      $scope.ui.loading = false;
      $scope.error = $scope.build_error(data);
    });
  }
});
