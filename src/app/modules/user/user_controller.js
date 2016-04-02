app.controller('UserController', function($scope, $stateParams, KpmApi, User) {

  // Methods

  /**
   * Load user profile
   */
  $scope.loadUser = function(username) {
    KpmApi.get('users/' + username)
    .success(function(data) {
      $scope.user = new User(data);
    })
    .error(function(data) {
      $scope.error = 'User not found';
    });
  };

  // Init

  $scope.loadUser($stateParams.username);
});
