app.controller('HomeController', function($scope, KpmApi) {
  $scope.countPackages = function() {
    KpmApi.get('packages/count')
    .success(function(data) {
      $scope.count = data.count;
    })
    .error(function() {

    });
  };

  $scope.countPackages();
});
