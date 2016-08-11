app.controller('LoginController', function($scope, $state, KpmApi, Session) {

  // Listeners

  $scope.$on('login_success', function(event, data) {
    // Redirect user
    $state.go('packages');
  });

  $scope.$on('login_failure', function(event, data) {
    $scope.error = data.message;
  });

  // Methods

  $scope.submit = function() {
    Session.login($scope.username, $scope.password);
  };
});
