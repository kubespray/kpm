'use strict';

app.controller('OrganizationController', function($scope, $stateParams, KpmApi,
      User) {

  // Methods

  /**
   * Load organization and associated users
   */
  $scope.loadOrganization = function(name) {
    KpmApi.get('organizations/' + name)
    .success(function(data) {
      $scope.organization = data;
    })
    .error(function(data) {
      $scope.error = $scope.build_error(data);
    });

    KpmApi.get('/organizations/' + name + '/users')
    .success(function(data) {
      $scope.users = data.map(function(hash) {
        return new User(hash);
      });
    })
    .error(function(data) {
      $scope.error = $scope.build_error(data);
    });
  };

  // Init

  $scope.loadOrganization($stateParams.name);
});
