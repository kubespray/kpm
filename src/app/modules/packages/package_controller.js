'use strict';

app.controller('PackageController', function($scope, $state, $stateParams,
      $mdDialog, KpmApi, Package, Session) {

  // Methods

  $scope.selectVersion = function() {
    var name = $scope.package.name + '/' + $scope.package.version;
    $state.go('package', {name: name});
  };

  $scope.toggleStar = function() {
    if (Session.isAuthenticated()) {
      var action = $scope.package.starred ? 'unstar' : 'star'
      KpmApi.put('packages/' + $scope.package.name + '/' + action)
      .success(function(data) {
        // Refresh attributes
        $scope.package.starred = !$scope.package.starred;
        $scope.package.stars = data.stars;
      })
      .error(function() {
        console.log('Cannot ' + action + ' package');
      });
    }
    else {
      $state.go('login');
    }
  };

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
  };

  $scope.setPackage = function(object) {
    console.log("set package");
    $scope.package = new Package(object);
  };

  // Init

  var package_name = $stateParams.name;
  if (package_name) {
    $scope.ui.loading = true;
    KpmApi.get('packages/' + package_name)
    .success(function(data) {
      $scope.ui.loading = false;
      $scope.setPackage(data);
    })
    .error(function(data) {
      $scope.ui.loading = false;
      $scope.error = $scope.build_error(data);
    });
  }
});
