app.controller('LoginController', function($scope, $state, KpmApi, Session) {

  // Listeners

  $scope.$on('login_success', function(event, data) {
    $scope.ui.loading = false;
    // Redirect user to his profile page
    $state.go('user', {username: Session.user.username});
  });

  $scope.$on('login_failure', function(event, data) {
    $scope.ui.loading = false;
    $scope.error = data.message;
  });

  // Methods

  $scope.submit = function() {
    $scope.ui.loading = true;
    Session.login($scope.username, $scope.password);
  };
});
