'use strict';

app.controller('OrganiaztionController', function($scope, $stateParams, KpmApi) {
  // Methods

  $scope.loadOrganization = function(name) {
    KpmApi.get('organizations/' + name)
    .success(function(data) {
      $scope.organization = data;
    })
    .error(function(data) {
      $scope.error = $scope.build_error(data);
    });

  };

  // Init

  $scope.loadOrganization($stateParams.name);
});
